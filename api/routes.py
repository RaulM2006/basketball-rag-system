import os
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Header
from core.generator import generate_coaching_feedback

router = APIRouter(prefix="/coach", tags=["Coaching"])

# Get maximum video size, convert to bytes (1MB = 1,024 * 1,024 bytes)
MAX_SIZE_MB = int(os.getenv("MAX_VIDEO_UPLOAD_SIZE_MB", "10"))
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

# Allowed video extensions and mime types
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}
ALLOWED_MIME_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska"}

@router.post("/analyze")
async def analyze_shot(
    file: UploadFile = File(...),
    x_access_key: str = Header(None)
):
    """
    Endpoint to upload a basketball jump shot video and receive 
    biomechanical feedback and coaching RAG recommendations.
    """
    # 0. Validate Access Key if configured in the environment
    expected_key = os.getenv("COACH_ACCESS_KEY")
    if expected_key:
        if not x_access_key or x_access_key != expected_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access Denied: Invalid or missing Coach Access Key."
            )

    # 1. Validate File Extension
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{file_ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 2. Validate MIME Type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported MIME type '{file.content_type}'. Must be a video file."
        )

    # 3. Validate File Size in chunks (Streaming)
    # Why this approach: Checking the content-length header is insecure as it can be spoofed.
    # Reading the file stream in chunks ensures we catch oversize files immediately without
    # overloading server memory.
    temp_dir = Path("data/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file_path = temp_dir / f"upload_{file.filename}"

    total_bytes = 0
    try:
        with open(temp_file_path, "wb") as buffer:
            while chunk := await file.read(8192):  # Read in 8KB chunks
                total_bytes += len(chunk)
                if total_bytes > MAX_SIZE_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds maximum upload size of {MAX_SIZE_MB}MB."
                    )
                buffer.write(chunk)
    except HTTPException:
        # Re-raise HTTPExceptions (like size limit) so they aren't caught by the general catch-all
        if temp_file_path.exists():
            os.remove(temp_file_path)
        raise
    except Exception as e:
        if temp_file_path.exists():
            os.remove(temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write file to disk: {str(e)}"
        )

    # 4. Process RAG feedback and clean up local temp storage
    try:
        # Call our orchestrated pipeline
        feedback_report = generate_coaching_feedback(str(temp_file_path))
        
        return {
            "status": "success",
            "filename": file.filename,
            "size_bytes": total_bytes,
            "report": feedback_report
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing RAG pipeline: {str(e)}"
        )
    finally:
        # Crucial architectural cleanup: always remove local temp video files
        # to prevent hard-drive space exhaustion.
        if temp_file_path.exists():
            os.remove(temp_file_path)
            print(f"Cleaned up local temp file: {temp_file_path}")

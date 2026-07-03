import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("MULTIMODAL_LLM_API_KEY")
if not api_key:
    raise ValueError("MULTIMODAL_LLM_API_KEY is not set.")

client = genai.Client(api_key=api_key)

def analyze_video_mechanics(video_path: str) -> str:
    print(f"Uploading video file: {video_path}...")
    uploaded_file = client.files.upload(file=video_path)
    
    while uploaded_file.state.name == "PROCESSING":
        print("Waiting for video processing to complete...")
        time.sleep(2)
        uploaded_file = client.files.get(name=uploaded_file.name)
        
    if uploaded_file.state.name != "ACTIVE":
        raise ValueError(f"Video processing failed with state: {uploaded_file.state.name}")
        
    print("Video is ready for analysis. Querying Gemini...")
    
    prompt = (
        "Analyze this basketball jump shot video frame by frame. Focus on the following markers:\n"
        "1. Base (stance and knees)\n"
        "2. Elbow Position (tucked vs flared)\n"
        "3. Release & Guide Hand (wrist flick, guide hand interference)\n"
        "Identify any form flaws under these categories."
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[uploaded_file, prompt]
        )
        analysis = response.text
    finally:
        print("Cleaning up file from cloud storage...")
        client.files.delete(name=uploaded_file.name)
        
    return analysis

if __name__ == "__main__":
    test_video = "data/sample_shot_2.mp4"
    
    if not os.path.exists(test_video):
        print(f"Please place a sample basketball shooting video at: {test_video}")
    else:
        print(f"Found test video. Running biomechanical analysis...")
        analysis_result = analyze_video_mechanics(test_video)
        print("\n--- Biomechanical Analysis Result ---")
        print(analysis_result)


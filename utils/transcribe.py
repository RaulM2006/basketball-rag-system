from pathlib import Path
import os
import whisper
import json

def process_audio_files():
    audio_dir = Path("../data/audio")
    transcript_dir = Path("../data/transcriptions")

    model = whisper.load_model("base")

    for audio_file in audio_dir.glob("*.mp3"):
        video_id = audio_file.stem
        video_url = f"https://youtu.be/{video_id}"

        result = model.transcribe(str(audio_file))

        chunked_data = chunk_whisper_segments(
            segments=result["segments"], 
            target_length=500, 
            overlap_segments=1
        )

        transcript_data = {
            "video_id": video_id,
            "source_url": video_url,
            "chunks": chunked_data 
        }
        
        output_file = transcript_dir / f"{video_id}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, indent=4)
    


def chunk_whisper_segments(segments, target_length=500, overlap_segments=1):
    """
    Takes raw Whisper segments and groups them into larger, contextual chunks.
    overlap_segments: How many segments to keep in the bucket for the next chunk.
    """
    chunks = []
    current_bucket = []
    current_char_count = 0

    for idx, segment in enumerate(segments):
        current_bucket.append(segment)
        current_char_count += len(segment["text"])

        if current_char_count >= target_length or idx == len(segments) - 1:
            
            chunk_start = current_bucket[0]["start"]
            chunk_end = current_bucket[-1]["end"]
                        
            chunk_text = " ".join([s["text"] for s in current_bucket])
            
            chunks.append({
                "start_time": chunk_start,
                "end_time": chunk_end,
                "text": chunk_text
            })

            current_bucket = current_bucket[-overlap_segments:]
            
            current_char_count = sum(len(s["text"]) for s in current_bucket)

    return chunks

if __name__ == "__main__":
    process_audio_files()
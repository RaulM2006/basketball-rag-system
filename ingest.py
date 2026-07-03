from pathlib import Path
from dotenv import load_dotenv
import os
import json
import time
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

def get_vectorstore():
    api_key = os.getenv("MULTIMODAL_LLM_API_KEY")
    if not api_key:
        raise ValueError(
            "MULTIMODAL_LLM_API_KEY is not set in the environment variables. "
            "Please check that your .env file is populated correctly."
        )

    os.environ["GOOGLE_API_KEY"] = api_key

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")

    persist_directory = os.getenv("CHROMA_DB_DIRECTORY", "./db")

    return Chroma(
        collection_name="bball_coach",
        embedding_function=embeddings,
        persist_directory=persist_directory
    )

def process_json_files(db):
    transcript_dir = Path("data/transcriptions")

    texts = []
    metadatas = []
    ids = []

    if not transcript_dir.exists():
        print(f"Transcript directory not found at: {transcript_dir.absolute()}")
        return

    for json_file in transcript_dir.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        video_id = data["video_id"]
        source_url = data["source_url"]

        for index, chunk in enumerate(data.get("chunks", [])):
            text = chunk["text"]
            start_time = chunk["start_time"]
            end_time = chunk["end_time"]

            timestamped_url = f"{source_url}?t={int(start_time)}"

            body_parts = []
            text_lower = text.lower()
            for part in ["elbow", "wrist", "hand", "finger", "shoulder", "knee", "foot", "feet", "hip"]:
                if part in text_lower:
                    body_parts.append(part)
            
            metadata = {
                "video_id": video_id,
                "source_url": source_url,
                "start_time": start_time,
                "end_time": end_time,
                "timestamped_url": timestamped_url,
                "body_parts": ", ".join(body_parts) if body_parts else "general"
            }

            texts.append(text)
            
            ids.append(f"{video_id}_chunk_{index}")
            metadatas.append(metadata)
    
    if not texts:
        print("No transcription chunks found to ingest. Skipping database write.")
        return

    print(f"Ingesting {len(texts)} chunks into ChromaDB in batches...")
    
    batch_size = 20
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        batch_metadatas = metadatas[i : i + batch_size]
        batch_ids = ids[i : i + batch_size]
        
        batch_num = (i // batch_size) + 1
        total_batches = (len(texts) + batch_size - 1) // batch_size
        print(f"-> Ingesting batch {batch_num}/{total_batches} ({len(batch_texts)} chunks)...")
        
        db.add_texts(
            texts=batch_texts,
            metadatas=batch_metadatas,
            ids=batch_ids
        )
        
        if i + batch_size < len(texts):
            sleep_duration = 10
            print(f"   Sleeping {sleep_duration} seconds to respect API rate limits...")
            time.sleep(sleep_duration)
            
    print("Ingestion complete!")

def verify_db(db):
    """
    Verifies that data was successfully ingested by checking count and running a test search.
    """
    count = db._collection.count()
    print(f"\n--- Database Verification ---")
    print(f"Total documents in collection: {count}")
    
    if count == 0:
        print("Warning: Collection is empty!")
        return

    test_query = "elbow tucking and shooting alignment"
    print(f"Running semantic test query: '{test_query}'...")
    
    # Retrieve the top similar document to verify query path works
    results = db.similarity_search(test_query, k=1)
    
    if results:
        doc = results[0]
        print("Match found!")
        print(f"-> Text: {doc.page_content[:200]}...")
        print(f"-> Metadata: {doc.metadata}")
    else:
        print("No matches found.")

if __name__ == "__main__":
    # Setup database and ingest transcripts
    db_instance = get_vectorstore()
    process_json_files(db_instance)
    
    # Run verification to inspect collection state
    verify_db(db_instance)


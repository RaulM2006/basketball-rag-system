import os
from google import genai
from core.extractor import client, analyze_video_mechanics
from core.retriever import retrieve_coaching_tips

def extract_search_query(analysis_text: str) -> str:
    prompt = (
        "You are an assistant for a basketball coaching RAG pipeline.\n"
        "Analyze the following shooting form assessment and identify the single most "
        "prominent mechanical flaw that needs fixing.\n"
        "Return ONLY a concise, 2-to-4 word search query targeting this flaw (e.g., 'flared elbow', "
        "'guide hand interference', 'low release point', 'flat shooting arc').\n"
        "Do not include quotes, punctuation, or any introductory text.\n\n"
        f"Shooting Form Assessment:\n{analysis_text}"
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    query = response.text.strip().replace('"', '').replace("'", "")
    return query

def generate_coaching_feedback(video_path: str) -> str:
    # Step 1: Run the visual video analysis
    print("\n[RAG Pipeline] Step 1: Extracting mechanics from shooting video...")
    analysis = analyze_video_mechanics(video_path)
    print("-> Video analysis complete.")
    
    # Step 2: Formulate the search query from the analysis
    print("\n[RAG Pipeline] Step 2: Extracting core form flaw search query...")
    search_query = extract_search_query(analysis)
    print(f"-> Extracted search query: '{search_query}'")
    
    # Step 3: Query the vector database for coaching guidelines
    print("\n[RAG Pipeline] Step 3: Retrieving coaching guidelines from ChromaDB...")
    coaching_tips = retrieve_coaching_tips(search_query, k=2)
    print(f"-> Retrieved {len(coaching_tips)} relevant guidelines.")
    
    formatted_tips = ""
    for idx, tip in enumerate(coaching_tips):
        formatted_tips += (
            f"Guideline {idx + 1}:\n"
            f"- Video URL: {tip['timestamped_url']}\n"
            f"- Body Focus: {tip['body_parts']}\n"
            f"- Coach Advice: {tip['text']}\n\n"
        )
        
    # Step 4: Synthesize the final coaching feedback
    print("\n[RAG Pipeline] Step 4: Synthesizing final coaching report...")
    synthesis_prompt = (
        "You are an elite basketball shooting coach. You are writing a feedback report "
        "for a player based on a visual biomechanical analysis of their shot video "
        "and verified guidelines from your coaching knowledge base.\n\n"
        "--- Player's Video Analysis ---\n"
        f"{analysis}\n\n"
        "--- Verified Coaching Guidelines & Video Resources ---\n"
        f"{formatted_tips}\n"
        "------------------------------------\n\n"
        "Your Task:\n"
        "Write a structured, encouraging, and highly technical feedback report for the player.\n"
        "1. Commend what they did well (e.g. base, elbow alignment, follow-through).\n"
        "2. Clearly explain the form flaw identified (if any) and WHY it hurts their shot.\n"
        "3. Provide specific corrective actions/drills using the retrieved coaching guidelines.\n"
        "4. CRITICAL: You MUST embed clickable Markdown links directly to the specific YouTube video resources "
        "at their exact timestamps so the player can watch the drills. Use the exact 'Video URL' provided in the guidelines.\n"
        "   Example Link Format: [Watch Coach Dunn demonstrate the proper release hand drills here](Video URL).\n\n"
        "Format the report beautifully in Markdown. Keep the tone inspiring, professional, and coach-like."
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=synthesis_prompt
    )
    
    return response.text

if __name__ == "__main__":
    test_video = "data/sample_shot_1.mp4"
    
    if not os.path.exists(test_video):
        print(f"Please place a sample basketball shooting video at: {test_video}")
    else:
        print("Starting Multimodal RAG Pipeline Test...")
        final_report = generate_coaching_feedback(test_video)
        print("\n================ FINAL COACHING REPORT ================")
        print(final_report)
        print("======================================================")

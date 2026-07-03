# Retriever Module
from ingest import get_vectorstore


db = get_vectorstore()

def retrieve_coaching_tips(query: str, body_part: str = None, k: int = 3):
    search_filter = {"body_parts": body_part} if body_part else None

    results = db.similarity_search(query, k=k, filter=search_filter)
    
    formatted_results = []
    for doc in results:
        formatted_results.append({
            "text": doc.page_content,
            "timestamped_url": doc.metadata.get("timestamped_url"),
            "start_time": doc.metadata.get("start_time"),
            "end_time": doc.metadata.get("end_time"),
            "body_parts": doc.metadata.get("body_parts")
        })
    return formatted_results

if __name__ == "__main__":
    query_str = "how to tuck elbow"
    print(f"Testing retriever with query:'{query_str}'...")

    results = retrieve_coaching_tips(query_str, k=2)

    import pprint
    pprint.pprint(results)
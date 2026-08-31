from vibmo.ai.rag_index import RAGDatabase
from vibmo.ai.langgraph_agent import build_agent

def main():
    print("--- 1. Initializing RAG Database ---")
    db = RAGDatabase()
    
    # Check if populated, otherwise seed
    try:
        # Just upsert to ensure we have data
        db.seed_vibmo_assets()
        db.index_video_file("raw_broll_forest.mp4", [
            (0.0, 5.0, "Drone shot flying over a dense green pine forest in morning mist."),
            (5.0, 10.0, "Close up of a stream flowing over rocks covered in moss.")
        ])
    except Exception as e:
        print(f"Seed error: {e}")

    print("\n--- 2. Initializing LangGraph Agent ---")
    app = build_agent()
    
    initial_state = {
        "prompt": "Create a hype reel of a forest using some animated text and a cool background.",
        "search_queries": [],
        "retrieved_media": [],
        "retrieved_tools": [],
        "script": "",
        "errors": [],
        "is_valid": False
    }
    
    print("\n--- 3. Invoking Agentic Workflow ---")
    result = app.invoke(initial_state)
    
    print("===========================================")
    print("FINAL SCRIPT OUTPUT FROM EDITOR NODE")
    print("===========================================\n")
    print(result["script"])

if __name__ == "__main__":
    main()

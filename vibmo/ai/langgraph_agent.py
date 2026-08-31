from typing import Dict, TypedDict, List, Any
from langgraph.graph import StateGraph, END
from vibmo.ai.rag_index import RAGDatabase

# --- Define State ---
class AgentState(TypedDict):
    prompt: str
    search_queries: List[str]
    retrieved_media: List[Dict[str, Any]]
    retrieved_tools: List[Dict[str, Any]]
    script: str
    errors: List[str]
    is_valid: bool

# --- Initialize Dependencies ---
db = RAGDatabase()

# --- Nodes ---

def planner_node(state: AgentState) -> Dict:
    """Extracts semantic keywords from the prompt to search the DBs."""
    print(f"\n[Planner] Analyzing prompt: '{state['prompt']}'")
    
    # In reality, an LLM would parse the prompt. We'll mock it here.
    prompt_lower = state["prompt"].lower()
    
    queries = []
    if "forest" in prompt_lower or "nature" in prompt_lower:
        queries.append("forest")
        queries.append("water")
    elif "cyber" in prompt_lower or "tech" in prompt_lower:
        queries.append("cyberpunk")
    else:
        queries.append(prompt_lower)
        
    print(f"[Planner] Generated search queries: {queries}")
    return {"search_queries": queries}

def media_retrieval_node(state: AgentState) -> Dict:
    """Searches the video database for relevant clips."""
    print("[Media Retrieval] Searching Video DB...")
    clips = []
    for q in state["search_queries"]:
        results = db.search_media(q, n_results=1)
        clips.extend(results)
    
    for c in clips:
        print(f"  -> Found Clip: {c['document']} ({c['metadata']['start_time']}s - {c['metadata']['end_time']}s)")
        
    return {"retrieved_media": clips}

def asset_retrieval_node(state: AgentState) -> Dict:
    """Searches Code-RAG for appropriate Vibmo components based on prompt vibe."""
    print("[Asset Retrieval] Searching Code-RAG for Vibmo Components...")
    tools = []
    # If the user wants a modern UI or dashboard, pull GlassCard. If they want text, pull KineticText.
    if "ui" in state["prompt"].lower() or "dashboard" in state["prompt"].lower():
        tools.extend(db.search_assets("glasscard", 1))
    
    tools.extend(db.search_assets("animated text", 1))
    tools.extend(db.search_assets("background", 1))
    
    for t in tools:
        print(f"  -> Found Component: {t['metadata']['class']}")
        
    return {"retrieved_tools": tools}

def editor_node(state: AgentState) -> Dict:
    """Writes the final Python script combining the media and tools."""
    print("[Editor] Drafting Python Script...")
    
    # In reality, this would be an LLM generation step injected with the retrieved context.
    # We will mock the output script.
    
    media_context = "\n".join([f"# Clip: {m['document']} (Start: {m['metadata']['start_time']}s, End: {m['metadata']['end_time']}s)" for m in state.get("retrieved_media", [])])
    tool_context = "\n".join([f"# Available Tool: {t['metadata']['class']} - {t['document']}" for t in state.get("retrieved_tools", [])])
    
    script = f"""from vibmo.agent_api import *

scene = Scene(width=1920, height=1080, duration=5.0)

# --- Media Context ---
{media_context}

# --- Tool Context ---
{tool_context}

# (Mock) Generated Video Assembly Code
bg = MeshGradientFlow()
scene.add(bg)

title = KineticText("Agentic Editing Complete!", font_size=48)
title.at(scene.width/2 - 200, scene.height/2)
scene.add(title)

# ... Otio Export Logic ...
"""
    print("[Editor] Script generated.")
    return {"script": script}

def reviewer_node(state: AgentState) -> Dict:
    """Validates the script syntax and timing."""
    print("[Reviewer] Validating script...")
    # Mocking a successful validation
    if len(state.get("script", "")) < 10:
        return {"is_valid": False, "errors": ["Script too short."]}
        
    print("[Reviewer] Script passed inspection!")
    return {"is_valid": True, "errors": []}

def route_validation(state: AgentState):
    """Conditional router based on reviewer output."""
    if state.get("is_valid"):
        return END
    else:
        return "editor_node"  # Loop back to fix errors

# --- Build Graph ---
def build_agent():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("planner_node", planner_node)
    workflow.add_node("media_retrieval_node", media_retrieval_node)
    workflow.add_node("asset_retrieval_node", asset_retrieval_node)
    workflow.add_node("editor_node", editor_node)
    workflow.add_node("reviewer_node", reviewer_node)
    
    workflow.set_entry_point("planner_node")
    
    workflow.add_edge("planner_node", "media_retrieval_node")
    workflow.add_edge("planner_node", "asset_retrieval_node")
    
    # Both retrievals must finish before editing
    workflow.add_edge("media_retrieval_node", "editor_node")
    workflow.add_edge("asset_retrieval_node", "editor_node")
    
    workflow.add_edge("editor_node", "reviewer_node")
    workflow.add_conditional_edges("reviewer_node", route_validation)
    
    return workflow.compile()

if __name__ == "__main__":
    # Test Agent
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
    
    print("--- Starting Agentic Workflow ---")
    result = app.invoke(initial_state)
    print("\n--- Final Script Output ---")
    print(result["script"])

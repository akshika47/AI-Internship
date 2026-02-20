"""
Backend API - FastAPI + Research Assistant with Langfuse
Demonstrates tracing, scoring, and session tracking.

Deploy this to Render.com
"""

from fastapi import FastAPI, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os
import time
from typing import Optional

# Langfuse integration - make it optional for compatibility
LANGFUSE_AVAILABLE = False
try:
    from langfuse.decorators import observe, langfuse_context
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except (ImportError, Exception) as e:
    # Create no-op decorator if Langfuse is not available
    def observe(func=None, **kwargs):
        if func is None:
            return lambda f: f
        return func
    
    class langfuse_context:
        @staticmethod
        def get_current_trace_id():
            return None
    
    Langfuse = None

app = FastAPI(title="Research Assistant API")

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) if os.getenv("OPENAI_API_KEY") else None

# Initialize Langfuse client if available
langfuse_client = Langfuse() if LANGFUSE_AVAILABLE and Langfuse else None


class Query(BaseModel):
    message: str


@observe()
def query_analysis(query: str) -> dict:
    """
    Analyze the query - creates a span in Langfuse.
    This demonstrates how each function becomes a traceable span.
    """
    # Simple analysis: check query length and type
    analysis = {
        "length": len(query),
        "word_count": len(query.split()),
        "has_question_mark": "?" in query,
        "query_type": "question" if "?" in query else "statement"
    }
    return analysis


@observe()
def generate_response(query: str) -> str:
    """
    Generate response using LLM - creates a span in Langfuse.
    This shows the LLM generation step in the trace tree.
    """
    if not llm:
        return "[Mock] Research summary about the query. This is a placeholder response."
    
    prompt = f"""You are a research assistant. Answer the following query concisely and accurately.

Query: {query}

Provide a clear, factual answer."""

    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    
    return response.content


@observe()
def validate_response(response: str) -> dict:
    """
    Validate the response - creates a span in Langfuse.
    This demonstrates validation as a separate traceable step.
    """
    validation = {
        "valid": True,
        "errors": [],
        "length": len(response),
        "has_content": len(response.strip()) > 0
    }
    
    # Simple validation checks
    if len(response) < 10:
        validation["valid"] = False
        validation["errors"].append("Response too short")
    
    if len(response) > 5000:
        validation["valid"] = False
        validation["errors"].append("Response too long")
    
    return validation


@observe()
def research_assistant(query: str, user_id: Optional[str] = None, session_id: Optional[str] = None) -> dict:
    """
    Main research assistant function - orchestrates multiple spans.
    This creates a trace with child spans for each step.
    """
    start_time = time.time()
    
    # Step 1: Analyze query (creates a span)
    analysis = query_analysis(query)
    
    # Step 2: Generate response (creates a span)
    response = generate_response(query)
    
    # Step 3: Validate response (creates a span)
    validation = validate_response(response)
    
    # Calculate latency
    latency = time.time() - start_time
    
    # Get trace ID for scoring
    trace_id = langfuse_context.get_current_trace_id() if LANGFUSE_AVAILABLE else None
    
    # Log scores to Langfuse
    if trace_id and langfuse_client:
        # Score: Relevance (simple check - response contains query keywords)
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        relevance_score = len(query_words.intersection(response_words)) / max(len(query_words), 1)
        relevance_score = min(relevance_score, 1.0)  # Cap at 1.0
        
        langfuse_client.score(
            trace_id=trace_id,
            name="relevance",
            value=relevance_score,
            comment=f"Query words found in response: {relevance_score:.2f}"
        )
        
        # Score: Latency (pass if under 3 seconds)
        latency_ok = latency < 3.0
        langfuse_client.score(
            trace_id=trace_id,
            name="latency_ok",
            value=1.0 if latency_ok else 0.0,
            comment=f"Response time: {latency:.2f}s"
        )
    
    result = {
        "response": response,
        "analysis": analysis,
        "validation": validation,
        "latency": latency,
        "user_id": user_id,
        "session_id": session_id
    }
    
    return result


@app.post("/chat")
async def chat(query: Query, request: Request, x_user_id: Optional[str] = Header(None), x_session_id: Optional[str] = Header(None)):
    """
    API endpoint for chat.
    Extracts user_id and session_id from headers for tracking.
    """
    user_id = x_user_id or request.headers.get("X-User-ID")
    session_id = x_session_id or request.headers.get("X-Session-ID")
    
    result = research_assistant(
        query.message,
        user_id=user_id,
        session_id=session_id
    )
    
    return {
        "response": result["response"],
        "latency": result["latency"]
    }


@app.get("/health")
async def health():
    """Health check endpoint for Render."""
    return {
        "status": "ok",
        "service": "research-assistant-api",
        "langfuse_available": LANGFUSE_AVAILABLE
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Research Assistant API",
        "description": "Demonstrates Langfuse tracing, scoring, and session tracking",
        "endpoints": {
            "chat": "/chat (POST)",
            "health": "/health (GET)"
        },
        "langfuse_features": {
            "tracing": "Multiple spans (query_analysis, generate_response, validate_response)",
            "scoring": "relevance, latency_ok",
            "sessions": "Track via X-Session-ID header",
            "users": "Track via X-User-ID header"
        }
    }


# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


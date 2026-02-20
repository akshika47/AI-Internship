"""
Frontend - Streamlit Chat Interface
Simple chat interface that demonstrates Langfuse session tracking.

Deploy this to Streamlit Cloud
"""

import streamlit as st
import requests
import uuid

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 AI Research Assistant")
st.caption("Ask me anything and I'll research it for you!")

# Get API URL from secrets (set in Streamlit Cloud)
# For local testing, you can use: API_URL = "http://localhost:8000"
API_URL = st.secrets.get("API_URL", "http://localhost:8000")

# Initialize session ID (for Langfuse session tracking)
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if query := st.chat_input("Ask me anything..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Display user message
    with st.chat_message("user"):
        st.write(query)
    
    # Get response from API with session tracking
    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            try:
                # Include session ID in headers for Langfuse tracking
                headers = {
                    "X-Session-ID": st.session_state.session_id,
                    "X-User-ID": "streamlit-user"  # Simple user ID for demo
                }
                
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"message": query},
                    headers=headers,
                    timeout=60
                )
                response.raise_for_status()
                result = response.json()
                assistant_response = result.get("response", "No response received")
                latency = result.get("latency", 0)
                
                st.write(assistant_response)
                if latency:
                    st.caption(f"⏱️ Response time: {latency:.2f}s")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_response
                })
                
            except requests.exceptions.ConnectionError:
                error_msg = f"❌ Could not connect to API at {API_URL}. Make sure your backend is running!"
                st.error(error_msg)
                st.info("For local testing, start your backend with: `python -m uvicorn main:app --reload`")
                
            except requests.exceptions.Timeout:
                error_msg = "⏱️ Request timed out. The query might be too complex."
                st.error(error_msg)
                
            except requests.exceptions.RequestException as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Sidebar with info
with st.sidebar:
    st.header("About")
    st.write("""
    This is a production-ready AI Research Assistant built with:
    - FastAPI backend (deployed on Render)
    - Streamlit frontend (deployed on Streamlit Cloud)
    - Langfuse for observability and tracing
    - OpenAI for research capabilities
    """)
    
    st.header("Langfuse Features")
    st.write("""
    This app demonstrates:
    - **Tracing**: Multiple spans (query analysis, generation, validation)
    - **Scoring**: Relevance and latency metrics
    - **Sessions**: Track conversations via session ID
    - **Users**: Track user interactions
    """)
    
    st.header("Session Info")
    st.code(f"Session ID: {st.session_state.session_id[:8]}...")
    st.caption("All messages in this chat are grouped in Langfuse by session ID")
    
    st.header("API Status")
    try:
        health_check = requests.get(f"{API_URL}/health", timeout=5)
        if health_check.status_code == 200:
            health_data = health_check.json()
            st.success("✅ Backend is online")
            if health_data.get("langfuse_available"):
                st.success("✅ Langfuse is enabled")
            else:
                st.warning("⚠️ Langfuse not available")
        else:
            st.warning("⚠️ Backend returned an error")
    except:
        st.error("❌ Backend is offline")
    
    st.header("Settings")
    st.write(f"**API URL:** `{API_URL}`")
    st.caption("Change this in Streamlit Cloud secrets")


"""
Streamlit UI for the ReAct Agent
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv()

# Add the current directory to path to import from notebook
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import agent components (these should match your notebook)
from typing import Annotated, Literal
from typing_extensions import TypedDict
import operator
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from datetime import datetime

# Import Tavily if available
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

# Load API keys
api_key = os.getenv("OPENAI_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

if tavily_key and TAVILY_AVAILABLE:
    tavily_client = TavilyClient(api_key=tavily_key)
else:
    tavily_client = None

# Define tools (same as notebook)
@tool
def tavily_search(query: str) -> str:
    """Search the web for current information using Tavily API."""
    if not tavily_client:
        return "Tavily API not available. Please set TAVILY_API_KEY in .env file."
    
    try:
        response = tavily_client.search(
            query=query,
            max_results=5,
            search_depth="advanced"
        )
        
        results = []
        if response.get('results'):
            for result in response['results']:
                title = result.get('title', 'No title')
                url = result.get('url', '')
                content = result.get('content', '')
                results.append(f"**{title}**\n{content[:200]}...\nSource: {url}")
        
        if results:
            return "\n\n".join(results)
        else:
            return f"No results found for query: {query}"
    except Exception as e:
        return f"Error searching: {str(e)}"

@tool
def get_todays_events() -> str:
    """Get today's calendar events from the calendar."""
    today = datetime.now().strftime("%Y-%m-%d")
    events = [
        {
            "time": "10:00 AM",
            "title": "Team Standup",
            "attendees": ["Team"],
            "location": "Zoom"
        },
        {
            "time": "2:00 PM",
            "title": "Meeting with Marc Kligen about Langfuse Eval",
            "attendees": ["Marc Kligen (Langfuse)", "You"],
            "location": "Google Meet",
            "topic": "Langfuse Eval features and integration"
        },
        {
            "time": "4:30 PM",
            "title": "Product Review",
            "attendees": ["Product Team"],
            "location": "Conference Room A"
        }
    ]
    
    formatted_events = [f"📅 {today} - Today's Events:\n"]
    for event in events:
        formatted_events.append(
            f"  ⏰ {event['time']}: {event['title']}\n"
            f"     👥 Attendees: {', '.join(event['attendees'])}\n"
            f"     📍 Location: {event['location']}"
        )
        if 'topic' in event:
            formatted_events.append(f"     💬 Topic: {event['topic']}")
        formatted_events.append("")
    
    return "\n".join(formatted_events)

@tool
def get_current_date() -> str:
    """Returns today's date and time for context."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

tools = [tavily_search, get_todays_events, get_current_date]

# Initialize LLM
if api_key:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools(tools)
else:
    llm = None
    llm_with_tools = None

# Define state
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    steps: Annotated[list, operator.add]
    final_answer: str

# Define nodes
def reasoner_node(state: AgentState) -> dict:
    """Reasoner node: LLM decides what to do next."""
    messages = state.get("messages", [])
    
    if not messages or state.get("final_answer"):
        return {}
    
    last_message = messages[-1]
    
    if not llm_with_tools or not llm:
        return {"messages": [AIMessage("LLM not available. Please set OPENAI_API_KEY in .env file.")]}
    
    try:
        if isinstance(last_message, ToolMessage):
            # Build clean message history for synthesis
            clean_messages = []
            i = len(messages) - 1
            while i >= 0:
                msg = messages[i]
                if isinstance(msg, ToolMessage):
                    clean_messages.insert(0, msg)
                    i -= 1
                    # Find the corresponding AIMessage with tool_calls
                    while i >= 0 and not (isinstance(messages[i], AIMessage) and hasattr(messages[i], 'tool_calls') and messages[i].tool_calls):
                        i -= 1
                    if i >= 0:
                        clean_messages.insert(0, messages[i])
                        i -= 1
                        # Find the HumanMessage
                        while i >= 0 and not isinstance(messages[i], HumanMessage):
                            i -= 1
                        if i >= 0:
                            clean_messages.insert(0, messages[i])
                        break
                i -= 1
            
            if not clean_messages:
                clean_messages = messages[-3:] if len(messages) >= 3 else messages
            
            response = llm.invoke(clean_messages)
            final_answer = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "messages": [response],
                "steps": [{"type": "reason", "content": "Synthesizing final answer from tool results."}],
                "final_answer": final_answer
            }
        else:
            response = llm_with_tools.invoke(messages)
            
            if hasattr(response, 'tool_calls') and response.tool_calls:
                return {
                    "messages": [response],
                    "steps": [{"type": "reason", "content": "Deciding to call a tool to gather more information."}]
                }
            else:
                final_answer = response.content if hasattr(response, 'content') else str(response)
                return {
                    "messages": [response],
                    "steps": [{"type": "reason", "content": "I have enough information to provide an answer."}],
                    "final_answer": final_answer
                }
    except Exception as e:
        return {
            "messages": [AIMessage(f"Error: {str(e)}")],
            "final_answer": f"Error: {str(e)}"
        }

def tool_node(state: AgentState) -> dict:
    """Tool node: Execute tool calls."""
    messages = state.get("messages", [])
    last_message = messages[-1]
    
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return {}
    
    tool_map = {tool.name: tool for tool in tools}
    tool_messages = []
    tool_steps = []
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_call_id = tool_call["id"]
        
        if tool_name in tool_map:
            try:
                result = tool_map[tool_name].invoke(tool_args)
                tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call_id))
                tool_steps.append({"type": "act", "tool": tool_name, "args": tool_args, "result": result})
            except Exception as e:
                tool_messages.append(ToolMessage(content=f"Error executing {tool_name}: {str(e)}", tool_call_id=tool_call_id))
    
    if tool_messages:
        return {"messages": tool_messages, "steps": tool_steps}
    return {}

def should_continue(state: AgentState) -> Literal["tool", "end"]:
    """Router: decide what to do next."""
    messages = state.get("messages", [])
    if state.get("final_answer"):
        return "end"
    
    if not messages:
        return "end"
    
    last_message = messages[-1]
    if isinstance(last_message, AIMessage):
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tool"
        else:
            return "end"
    
    return "end"

# Build graph
graph = StateGraph(AgentState)
graph.add_node("reasoner", reasoner_node)
graph.add_node("tool", tool_node)
graph.add_edge(START, "reasoner")
graph.add_conditional_edges("reasoner", should_continue, {"tool": "tool", "end": END})
graph.add_edge("tool", "reasoner")

checkpointer = MemorySaver()
react_app = graph.compile(checkpointer=checkpointer)

# Streamlit UI
st.set_page_config(
    page_title="ReAct Agent Demo",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 ReAct Agent - Interactive Demo")
st.markdown("Experience the ReAct pattern in action with real tools!")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    thread_id = st.text_input("Thread ID", value="default-thread", help="Same thread ID = shared memory")
    
    if st.button("🔄 New Conversation"):
        thread_id = f"thread-{os.urandom(4).hex()}"
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📚 Available Tools")
    st.markdown("- 🔍 **Tavily Search**: Web search")
    st.markdown("- 📅 **Calendar**: Today's events")
    st.markdown("- 🕐 **Date/Time**: Current timestamp")
    
    st.markdown("---")
    st.markdown("### 💡 Example Queries")
    st.code("What is Langfuse Eval?")
    st.code("What meetings do I have today?")
    st.code("What's the current date and time?")
    
    # API key status
    st.markdown("---")
    st.markdown("### 🔑 API Status")
    if api_key:
        st.success("✅ OpenAI API Key")
    else:
        st.error("❌ OpenAI API Key missing")
    
    if tavily_key and TAVILY_AVAILABLE:
        st.success("✅ Tavily API Key")
    else:
        st.warning("⚠️ Tavily API Key missing")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        if "steps" in message and message["steps"]:
            with st.expander("🔍 ReAct Trace"):
                for step in message["steps"]:
                    if step.get('type') == 'reason':
                        st.success(f"💭 **REASON**: {step.get('content')}")
                    elif step.get('type') == 'act':
                        st.info(f"🔧 **ACT**: {step.get('tool')}")
                        st.json(step.get('args'))
                        result_preview = str(step.get('result', ''))[:300]
                        st.code(result_preview)

# Chat input
if prompt := st.chat_input("Ask the agent anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "messages": [HumanMessage(prompt)],
        "steps": [],
        "final_answer": ""
    }
    
    with st.chat_message("assistant"):
        with st.spinner("🤔 Agent is thinking..."):
            try:
                result = react_app.invoke(initial_state, config)
                
                # Display ReAct trace
                steps = result.get("steps", [])
                if steps:
                    with st.expander("🔍 ReAct Trace", expanded=True):
                        for step in steps:
                            if step.get('type') == 'reason':
                                st.success(f"💭 **REASON**: {step.get('content')}")
                            elif step.get('type') == 'act':
                                st.info(f"🔧 **ACT**: {step.get('tool')}")
                                st.json(step.get('args'))
                                result_preview = str(step.get('result', ''))[:500]
                                st.code(result_preview)
                
                # Display final answer
                response = result.get("final_answer", "No answer generated")
                st.markdown(response)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "steps": steps
                })
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })


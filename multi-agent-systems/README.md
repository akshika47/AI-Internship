# Multi-Agent Systems Course

Welcome to the Multi-Agent Systems course repository! This repository contains code snippets, notebooks, and exercises for the Multi-Agent Mastery course.

## 📚 Course Structure

This course is organized by weeks, with each week containing:

- **Notebooks** - Interactive Jupyter notebooks with guided exercises
- **Code Examples** - Working implementations and patterns
- **Requirements** - Dependencies needed for each week
- **Documentation** - README files with setup instructions

## 📁 Directory Structure

```
multi-agent-systems/
├── README.md              # This file
├── week-1/                # LangGraph Foundations
│   ├── README.md
│   ├── requirements.txt
│   ├── week1_notebook.ipynb
│   └── .env.example
├── week-2/                # Single-Agent Mastery
│   ├── requirements.txt
│   ├── week2_notebook.ipynb
│   └── streamlit_app.py
├── week-3/                # Multi-Agent Orchestration
│   ├── README.md
│   ├── requirements.txt
│   └── week3_notebook.ipynb
└── week-4/                # Evaluation, Monitoring & Shipping
    ├── README.md
    ├── backend/           # FastAPI app with Langfuse tracing
    └── frontend/          # Streamlit chat interface
```

## 🎯 Course Overview

### Week 1: LangGraph Foundations
**Blueprint to Your First Agent**

- Learn the core building blocks: State, Nodes, and Edges
- Build your first simple graph
- Create a Customer Support Router with conditional routing
- Visualize graph execution

**Status:** ✅ Available

### Week 2: Single-Agent Mastery
**ReAct Pattern & Persistence**

- Typed State with proper reducers (append vs overwrite)
- Master the ReAct (Reason → Act → Observe → Repeat) pattern
- Conditional edges and agent termination logic
- Checkpointing — give agents memory and replay capabilities
- Build a Meeting Prep Agent with real Tavily web search
- Streamlit interactive UI (`streamlit_app.py`)

**Status:** ✅ Available

### Week 3: Multi-Agent Orchestration
**Supervisor Pattern, Subgraphs & Shared State**

- Learn the Supervisor Pattern for routing between specialist agents
- Design shared vs. scoped state schemas
- Build subgraphs and compose them into a parent graph
- Build a Company Research Assistant with 3 agents (Supervisor, Research, Writer)

**Status:** ✅ Available

### Week 4: Evaluation, Monitoring & Shipping
**Making Your Agent Production-Ready**

- Add Langfuse tracing, sessions, and scoring to a FastAPI + Streamlit app
- Track quality metrics like relevance and latency
- Deploy the backend (Render) and frontend (Streamlit Cloud)

**Status:** ✅ Available

## 🚀 Getting Started

1. **Navigate to the week you want to work on:**
   ```bash
   cd week-1
   ```

2. **Read the README:**
   ```bash
   cat README.md
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Open the notebook:**
   ```bash
   jupyter notebook
   ```

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Jupyter Notebook or JupyterLab
- (Optional) OpenAI API key for future exercises

## 🔗 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangSmith](https://smith.langchain.com) — Debug & trace your graphs
- [LangGraph Academy](https://academy.langchain.com/courses/intro-to-langgraph)

## 📝 Contributing

This repository is part of the AI Internship program. If you find issues or have suggestions:

1. Check existing issues first
2. Create a new issue with clear description
3. Follow the code structure and documentation style

## 📄 License

This repository contains educational materials for the AI Internship program.

---

**Happy Learning! 🎉**


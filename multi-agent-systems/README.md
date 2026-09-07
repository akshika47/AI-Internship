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
├── image/                 # Diagrams used in the week READMEs
├── week-1/                # LangGraph Foundations
│   ├── README.md
│   ├── requirements.txt
│   ├── week1_notebook.ipynb
│   ├── .env.example
│   └── .gitignore
├── week-2/                # Single-Agent Mastery
│   ├── requirements.txt
│   ├── week2_notebook.ipynb
│   ├── streamlit_app.py
│   └── .gitignore
├── week-3/                # Multi-Agent Orchestration
│   ├── README.md
│   ├── requirements.txt
│   ├── week3_notebook.ipynb
│   ├── .env.example
│   └── .gitignore
└── week-4/                # Production & Capstone
    ├── README.md
    ├── QUICK_START.md
    ├── DEPLOYMENT_GUIDE.md
    ├── RUN_LOCAL.md
    ├── requirements.txt
    ├── week4_notebook.ipynb
    ├── backend/           # FastAPI service (Render/Railway deploy configs)
    └── frontend/          # Streamlit chat UI
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
**Subgraphs & Agent Coordination**

- Learn subgraph patterns
- Coordinate multiple specialized agents
- Build complex multi-agent workflows

**Status:** ✅ Available

### Week 4: Production & Capstone
**Deploy to Production**

- Deploy multi-agent systems
- Add monitoring and observability
- Complete capstone project

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

- [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph/overview)
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


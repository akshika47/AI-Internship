# Week 1: LangGraph Foundations

## Blueprint to Your First Agent

Welcome to Week 1 of the Multi-Agent Mastery course! This notebook will guide you through building your first LangGraph application from scratch.

## 📋 Prerequisites

- Python 3.8 or higher
- Jupyter Notebook or JupyterLab installed
- OpenAI API key (optional for this week, but recommended for future exercises)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

Or install individually:
```bash
pip install langgraph langchain-core langchain-openai ipython jupyter
```

### 2. Set Up Environment (Optional)

If you plan to use OpenAI models in future exercises, create a `.env` file:

```bash
# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### 3. Open the Notebook

```bash
# Start Jupyter
jupyter notebook

# Or use JupyterLab
jupyter lab
```

Then open `week1_notebook.ipynb`

## 📚 What You'll Learn

1. **State** — The shared data structure that flows through your graph
2. **Nodes** — Functions that process and transform state
3. **Edges** — Control flow that connects nodes together
4. **StateGraph** — The orchestrator that ties everything together

## 🎯 Learning Objectives

By the end of this notebook, you will:

- ✅ Understand the core LangGraph architecture
- ✅ Build a simple echo agent from scratch
- ✅ Create a Customer Support Router with conditional routing
- ✅ Visualize your graph execution
- ✅ Be ready to tackle more complex multi-agent systems

## 📖 Notebook Structure

The notebook is organized into clear sections:

1. **Setup & Imports** - Get everything ready
2. **Step 1: Define STATE** - Create your data structure
3. **Step 2: Define NODES** - Build the worker functions
4. **Step 3: Build the GRAPH** - Connect everything with edges
5. **Step 4: Run the Graph** - Execute and see results
6. **Worked Example** - Customer Support Router with conditional edges

## 🔑 Key Concepts

| Concept | Analogy | Purpose |
|---------|---------|---------|
| **State** | Shared notebook | Data that all nodes can read/write |
| **Nodes** | Workers | Functions that do the actual work |
| **Edges** | Arrows | Define which node runs next |
| **StateGraph** | Manager | Orchestrates the entire flow |

## 🛠️ Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Make sure you're in the correct environment
pip install --upgrade langgraph langchain-core langchain-openai
```

**Visualization Not Working:**
```bash
# Install graphviz (for Mermaid diagrams)
# macOS
brew install graphviz

# Linux
sudo apt-get install graphviz

# Windows
# Download from: https://graphviz.org/download/
```

**API Key Issues:**
- This week's exercises don't require an API key
- For future weeks, ensure your `.env` file is in the same directory as the notebook

## 📝 Exercises

The notebook includes:
- ✅ Simple echo agent (linear graph)
- ✅ Customer Support Router (conditional routing)
- ✅ Multiple test cases to verify your implementation

## 🔗 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangSmith](https://smith.langchain.com) — Debug & trace your graphs
- [LangGraph Academy](https://academy.langchain.com/courses/intro-to-langgraph)

## 🆘 Need Help?

If you get stuck:
1. Review the code comments in each cell
2. Check the error messages carefully
3. Refer to the LangGraph documentation
4. Ask questions in the course discussion forum

## ✅ Next Steps

After completing this notebook:
- **Homework**: Build a Calculator Agent with the ReAct pattern
- **Week 2**: Single-agent mastery with persistence and memory
- **Week 3**: Multi-agent orchestration with subgraphs

---

**Happy Learning! 🎉**


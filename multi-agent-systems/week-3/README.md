# Week 3: Multi-Agent Orchestration

## Supervisor Pattern, Subgraphs & Shared State

Welcome to Week 3! This week you'll learn how to build multi-agent systems using LangGraph.

## 📚 What You'll Learn

1. **Why Multi-Agent?** — When and why to split work across agents
2. **Supervisor Pattern** — The coordinator that routes between specialist agents
3. **Shared vs Scoped State** — What each agent sees vs what stays private
4. **Subgraphs** — Agents as nodes in a parent graph
5. **Live Build** — Company Research Assistant with 3 agents

## 🎯 Learning Objectives

By the end of this week, you will:

- ✅ Understand when to use multi-agent systems
- ✅ Implement the Supervisor Pattern in LangGraph
- ✅ Design shared and scoped state schemas
- ✅ Build subgraphs and compose them into parent graphs
- ✅ Create a working Company Research Assistant
- ✅ Debug common multi-agent issues

## 📁 Files

- `week3_notebook.ipynb` - Main interactive notebook with all concepts and code
- `requirements.txt` - Python dependencies

## 🔧 Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the week-3 directory with:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

3. **Get API keys:**
   - OpenAI: https://platform.openai.com/api-keys
   - Tavily: https://tavily.com (free tier available)

## 🏗️ What We're Building

**Company Research Assistant** - A multi-agent system with:

- **Supervisor Agent** - Routes between specialist agents
- **Research Agent** (Subgraph) - Searches the web and summarizes findings
- **Writer Agent** - Creates structured company briefs

## 📖 How to Use This Notebook

1. **Run cells in order** - Each cell builds on the previous one
2. **Read the markdown cells** - They contain important explanations
3. **Experiment** - Try modifying the code to see what happens
4. **Complete the homework** - Extend the system with a third agent

## 🐛 Troubleshooting

### Common Issues

**Infinite loops:**
- Cause: Vague supervisor prompt, never reaches FINISH
- Fix: Use boolean state checks, not LLM inference

**State schema mismatch:**
- Cause: Parent calls it `task`, subgraph expects `query`
- Fix: Print state keys at every node during development

**Shared state noise:**
- Cause: All agents appending raw tool results to messages
- Fix: Only write clean outputs to shared state, keep internals scoped

**Subgraph output not reaching parent:**
- Cause: Field names don't match between schemas
- Fix: Field names and types must be identical in both state schemas

**Always debug with `app.stream()` not `app.invoke()`**

## 📝 Homework

Extend the Company Research Assistant with a third agent:

- **Option A — Critic Agent:** Reviews the draft, scores it 1-10. If below 7, routes back to writer for revision.
- **Option B — Outreach Agent:** Takes the completed brief, drafts a personalized cold email using research signals.
- **Option C — Comparison Agent:** Accept two company names. Run two research subgraphs in parallel. Compare side-by-side.

## 🔗 Resources

- [LangGraph Official Documentation](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph Subgraphs](https://langchain-ai.github.io/langgraph/how-tos/subgraphs/)
- [LangGraph State Management](https://langchain-ai.github.io/langgraph/concepts/low_level/#state)
- [LangSmith](https://smith.langchain.com) — Debug & trace your graphs

## ✅ Next Steps

After completing this notebook:
- **Complete the Homework** — Extend the system with a third agent
- **Week 4**: Production & Capstone — Deploy your multi-agent system

---

**Happy Learning! 🎉**


# RAG + Vector Databases - Live Session Notebook

This notebook contains a complete, self-contained guide to building Retrieval Augmented Generation (RAG) systems with LangChain and Vector Databases.

## 📚 Contents

- **Why RAG Exists** - Understanding LLM limitations and RAG solutions
- **RAG Architecture** - Complete flow from indexing to query
- **Embeddings Deep Dive** - How text becomes vectors
- **Vector Databases** - Storing and searching semantic data
- **Chunking Strategies** - Critical techniques for good retrieval
- **Live Build** - Step-by-step Document Q&A system
- **Evaluation** - How to test and improve your RAG system

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. **Open the notebook:**
   ```bash
   jupyter notebook rag_vector_databases_live_session.ipynb
   ```

4. **Run cells in order** - Each cell builds on the previous one

## 📋 Prerequisites

- Python 3.8 or higher
- Jupyter Notebook
- OpenAI API key (for embeddings and LLM calls)

## 🎯 Learning Objectives

By the end of this notebook, you will:
- Understand the complete RAG architecture
- Master embeddings and vector similarity search
- Build a production-ready Document Q&A system
- Know how to evaluate and debug RAG systems
- Be ready to build RAG applications on your own data

## 📖 Usage

This notebook is designed to be:
- **Self-contained** - All code and explanations included
- **Hands-on** - Run code as you learn
- **Production-ready** - Patterns you can use in real projects

## 🔧 Customization

To use with your own documents:
1. Replace the sample document with your PDF/text files
2. Adjust chunk sizes based on your document structure
3. Experiment with different embedding models
4. Add metadata filtering for your use case

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)

## ⚠️ Notes

- This notebook requires an OpenAI API key
- API calls will incur costs (embeddings and LLM calls)
- For production, consider using local embedding models or managed services

## 📝 License

This notebook is part of The AI Internship curriculum.


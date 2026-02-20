# Week 4: Evaluation, Monitoring & Shipping - Langfuse Examples

Simple examples demonstrating Langfuse features: tracing, scoring, and session tracking.

## Simple Example

### Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up API Keys**

   Create a `.env` file:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```

3. **Run Simple Script**
   ```bash
   python simple_openai_langfuse.py
   ```

   This script:
   - Calls OpenAI API with automatic tracing
   - Loads a prompt from Langfuse Prompt Management
   - Sends traces to Langfuse dashboard

## Advanced Examples

### FastAPI Backend + Streamlit Frontend

- `main.py` - FastAPI backend with Langfuse integration
- `app.py` - Streamlit frontend with session tracking

**Run Backend:**
```bash
python -m uvicorn main:app --reload
```

**Run Frontend:**
```bash
streamlit run app.py
```

## Langfuse Features Demonstrated

### Tracing
- Automatic tracing with `langfuse.openai` wrapper
- Manual tracing with `@observe()` decorator
- Multiple spans: `query_analysis`, `generate_response`, `validate_response`
- Full trace tree visible in Langfuse dashboard

### Prompt Management
- Load prompts from Langfuse Prompt Management
- Use prompt config (model, temperature, etc.)
- Version and label management

### Scoring
- `relevance` - How well response matches query (0-1)
- `latency_ok` - Whether response time is under 3 seconds (0 or 1)

### Sessions & Users
- Sessions tracked via `X-Session-ID` header
- Users tracked via `X-User-ID` header
- All traces grouped by session in Langfuse

## View in Langfuse

After making queries, check your Langfuse dashboard:
1. Go to **Observability → Tracing**
2. Click on any trace to see the full trace tree
3. View scores attached to each trace
4. See sessions grouped together

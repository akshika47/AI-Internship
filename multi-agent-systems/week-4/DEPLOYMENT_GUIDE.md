# Deployment Guide - Research Assistant

Complete guide to deploy your Research Assistant to production.

> **Note:** URLs like `https://your-app.onrender.com` and
> `https://your-app.streamlit.app` in this guide are
> `<placeholder — replace before use>`. Substitute the real URLs that Render and
> Streamlit Cloud assign to your own deployments.

## Architecture

```
[Streamlit Cloud]  ──HTTP──>  [Render]
   Frontend                    Backend API
   Free tier                  Free tier
   Chat UI                    FastAPI + Agent
```

**Why this setup:**
- Both completely free, no credit card needed
- Render runs your agent as a FastAPI API
- Streamlit Cloud gives you a clean chat UI
- Two repos, two deploys, fully decoupled

---

## Part 1: Deploy Backend to Render

### Step 1: Prepare Your Backend

1. Create a new directory: `backend/`
2. Copy files from `week-4/backend/`:
   - `main.py`
   - `requirements.txt`
   - `.env.example` (rename to `.env` and fill in your keys)

### Step 2: Create GitHub Repository

```bash
cd backend
git init
git add .
git commit -m "Initial commit: Research Assistant backend"
git branch -M main
git remote add origin https://github.com/yourusername/research-assistant-backend.git
git push -u origin main
```

### Step 3: Deploy on Render

1. Go to [render.com](https://render.com) and sign up (free, no credit card)
2. Click "New" → "Web Service"
3. Connect your GitHub account
4. Select your `research-assistant-backend` repository
5. Configure:
   - **Name:** `research-assistant-api` (or your choice)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Click "Advanced" → "Add Environment Variable"
   - Add all your API keys:
     - `OPENAI_API_KEY`
     - `LANGFUSE_PUBLIC_KEY`
     - `LANGFUSE_SECRET_KEY`
     - `LANGFUSE_HOST` = `https://cloud.langfuse.com`
7. Click "Create Web Service"
8. Wait 2-3 minutes for deployment
9. Copy your URL: `https://your-app.onrender.com`  _(`<placeholder — replace before use>`)_

### Step 4: Test Your Backend

```bash
# Replace your-app.onrender.com with your real Render URL — <placeholder — replace before use>
# Test health endpoint
curl https://your-app.onrender.com/health

# Test chat endpoint
curl -X POST https://your-app.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is LangGraph?"}'
```

---

## Part 2: Deploy Frontend to Streamlit Cloud

### Step 1: Prepare Your Frontend

1. Create a new directory: `frontend/`
2. Copy files from `week-4/frontend/`:
   - `app.py`
   - `requirements.txt`

### Step 2: Create GitHub Repository

```bash
cd frontend
git init
git add .
git commit -m "Initial commit: Research Assistant frontend"
git branch -M main
git remote add origin https://github.com/yourusername/research-assistant-frontend.git
git push -u origin main
```

### Step 3: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Configure:
   - **Repository:** Select `research-assistant-frontend`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click "Advanced settings"
6. Add secret:
   - **Key:** `API_URL`
   - **Value:** Your Render backend URL (e.g., `https://your-app.onrender.com` — `<placeholder — replace before use>`)
7. Click "Deploy"
8. Wait 1-2 minutes for deployment
9. Get your URL: `https://your-app.streamlit.app`  _(`<placeholder — replace before use>`)_

### Step 4: Test Your Frontend

1. Open your Streamlit app URL
2. Type a query in the chat
3. Verify it connects to your backend and returns responses

---

## Troubleshooting

### Backend Issues

**Problem:** Backend returns 500 errors
- **Solution:** Check Render logs, verify all environment variables are set

**Problem:** Backend times out
- **Solution:** Render free tier has cold starts. First request may take 30-60 seconds

**Problem:** CORS errors
- **Solution:** The backend already has CORS enabled. If issues persist, update `allow_origins` in `main.py`

### Frontend Issues

**Problem:** "Could not connect to API"
- **Solution:** Verify `API_URL` secret is set correctly in Streamlit Cloud

**Problem:** Requests timeout
- **Solution:** Increase timeout in `app.py` (currently 60 seconds)

---

## Next Steps

1. **Test your deployment** - Make sure everything works
2. **Share your app** - Send the Streamlit link to friends
3. **Monitor with Langfuse** - Check your traces and scores
4. **Post on LinkedIn** - Show off your production-ready AI system!

---

## Cost

**Total cost: $0**

- Render: Free tier (spins down after 15 min inactivity)
- Streamlit Cloud: Free tier (unlimited apps)
- Langfuse: Free tier (generous limits)

Perfect for learning and portfolio projects!


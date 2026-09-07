# Quick Start - Deploy Your Research Assistant

> **Note:** `https://your-app.onrender.com` and `https://your-app.streamlit.app`
> below are `<placeholder — replace before use>` — swap in the URLs Render and
> Streamlit Cloud give you.

## 🚀 Deploy in 10 Minutes

### Backend (Render)

1. **Create GitHub repo** for backend
2. **Copy files** from `week-4/backend/`:
   - `main.py`
   - `requirements.txt`
   - `.env.example` → rename to `.env` and add your keys
3. **Push to GitHub**
4. **Deploy on Render:**
   - Go to render.com → New Web Service
   - Connect repo
   - Build: `pip install -r requirements.txt`
   - Start: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add env vars (API keys)
   - Deploy → get URL: `https://your-app.onrender.com`  _(`<placeholder — replace before use>`)_

### Frontend (Streamlit Cloud)

1. **Create GitHub repo** for frontend
2. **Copy files** from `week-4/frontend/`:
   - `app.py`
   - `requirements.txt`
3. **Push to GitHub**
4. **Deploy on Streamlit Cloud:**
   - Go to share.streamlit.io → New app
   - Connect repo
   - Main file: `app.py`
   - Add secret: `API_URL = "https://your-app.onrender.com"`  _(`<placeholder — replace before use>`)_
   - Deploy → get URL: `https://your-app.streamlit.app`  _(`<placeholder — replace before use>`)_

## ✅ Done!

You now have a production-ready AI Research Assistant deployed for free!

**Test it:** Open your Streamlit URL and ask a question.

**Monitor it:** Check Langfuse dashboard for traces and scores.

**Share it:** Send the Streamlit link to anyone!


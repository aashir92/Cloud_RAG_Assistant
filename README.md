---
title: RAG Assistant
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: app.py
pinned: false
---

# Context-Aware RAG Chatbot

Production-style Retrieval-Augmented Generation chatbot for internal IT infrastructure and cloud deployment knowledge.

## Features

- Groq chat inference (`llama-3.3-70b-versatile` / `mixtral-8x7b-32768`)
- Local HuggingFace embeddings (`all-MiniLM-L6-v2`)
- FAISS semantic retrieval with top-k control
- History-aware retriever for coreference across chat turns
- Streamlit conversational UI with session memory
- File upload to ingest additional markdown/text docs

## Run locally

1. Install dependencies:
   `pip install -r requirements.txt`
2. Add API key in `.env`:
   `GROQ_API_KEY=your_key_here`
3. Generate starter corpus:
   `python data_generation.py`
4. Launch app:
   `streamlit run app.py`

## Deploy on Hugging Face Spaces

1. Create or use this Space repo: `https://huggingface.co/spaces/Aashir92/Cloud_RAG_Assistant`
2. Push this folder contents to that Space (see `deploy_to_remotes.ps1` below).
3. In Space Settings -> Secrets, add:
   - `GROQ_API_KEY`
4. Restart the Space.

### Local Streamlit secrets (optional)

If you want to use Streamlit secrets locally instead of `.env`, create:

- `.streamlit/secrets.toml`

From template:

`cp .streamlit/secrets.toml.example .streamlit/secrets.toml`

The app auto-loads docs from `data/` and builds (or reloads) a local FAISS index in `faiss_index/`.

## One-command push script

Use the PowerShell script in this repo to initialize git and push to both remotes:

`powershell -ExecutionPolicy Bypass -File .\deploy_to_remotes.ps1`

The script targets:

- Hugging Face Space: `https://huggingface.co/spaces/Aashir92/Cloud_RAG_Assistant`
- GitHub: `https://github.com/aashir92/Cloud_RAG_Assistant`

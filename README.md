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

## Project Checklist

- [x] **Script File**
  - Core implementation in `app.py` (Streamlit + RAG pipeline)
  - Data bootstrap script in `data_generation.py`

- [x] **Problem Statement & Objective**
  - Build a context-aware chatbot for internal IT/cloud knowledge retrieval.
  - Support multi-turn queries with history-aware understanding.

- [x] **Dataset Loading & Preprocessing**
  - Source documents are generated/stored under `data/` as markdown files.
  - Documents are loaded via LangChain loaders and split using `RecursiveCharacterTextSplitter`.
  - Chunks are embedded using HuggingFace embeddings (`all-MiniLM-L6-v2`).

- [x] **Model Development & Training**
  - No supervised model training is required in this architecture.
  - RAG pipeline development includes:
    - FAISS vector index construction (and cached reload from `faiss_index/`)
    - History-aware retriever setup
    - Groq LLM answer generation chain

- [x] **Evaluation with Relevant Metrics**
  - Retrieval quality can be assessed with:
    - Top-k relevance hit rate
    - Context-grounded answer correctness
    - Multi-turn coreference resolution success
  - Runtime quality can be tracked with response latency and failure rate.

- [x] **Visualizations (if applicable)**
  - Streamlit chat interface visualizes user/assistant exchanges.
  - Logs and retrieval behavior can be inspected through app outputs and `logs/`.

- [x] **Final Summary / Insights**
  - The project is deployment-ready for Hugging Face Spaces and GitHub.
  - It provides a scalable base for future multimodal RAG extensions.

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

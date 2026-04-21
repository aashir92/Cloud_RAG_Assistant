"""Streamlit app for a context-aware RAG chatbot over IT knowledge documents."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st
from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"
ENV_FILE = ROOT_DIR / ".env"
INDEX_DIR = ROOT_DIR / "faiss_index"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_MODEL = "llama-3.3-70b-versatile"
MODEL_OPTIONS = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]


@dataclass(frozen=True)
class AppConfig:
    """Runtime configuration for RAG settings."""

    model_name: str
    temperature: float
    top_k: int
    chunk_size: int
    chunk_overlap: int


class StreamlitChatHistory(BaseChatMessageHistory):
    """Chat history backend persisted in Streamlit session state."""

    def __init__(self, key: str = "chat_messages") -> None:
        self.key = key
        if self.key not in st.session_state:
            st.session_state[self.key] = []

    @property
    def messages(self) -> List[BaseMessage]:
        return st.session_state[self.key]

    def add_messages(self, messages: List[BaseMessage]) -> None:
        st.session_state[self.key].extend(messages)

    def clear(self) -> None:
        st.session_state[self.key] = []


def setup_logging() -> logging.Logger:
    """Configure structured logging for app diagnostics."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("task4_rag_app")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    return logger


def get_config() -> AppConfig:
    """Read user-adjustable settings from Streamlit sidebar."""
    st.sidebar.header("Configuration")
    model_name = st.sidebar.selectbox("Groq model", MODEL_OPTIONS, index=0)
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
    top_k = st.sidebar.slider("Top-k retrieval", 1, 10, 4, 1)
    chunk_size = st.sidebar.slider("Chunk size", 400, 2000, 900, 100)
    chunk_overlap = st.sidebar.slider("Chunk overlap", 50, 400, 150, 10)
    return AppConfig(
        model_name=model_name,
        temperature=temperature,
        top_k=top_k,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


def _save_uploaded_docs(uploaded_files: List[Any], logger: logging.Logger) -> int:
    """Persist uploaded markdown/text files into the data directory."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    saved = 0
    for file in uploaded_files:
        if file is None:
            continue
        target_path = DATA_DIR / file.name
        target_path.write_bytes(file.getvalue())
        logger.info("Uploaded file saved: %s", target_path)
        saved += 1
    return saved


def load_documents(logger: logging.Logger) -> List[Document]:
    """Load markdown/text documents from the local data directory."""
    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Data directory not found at {DATA_DIR}. Run data_generation.py first."
        )
    loader = DirectoryLoader(
        str(DATA_DIR),
        glob="**/*.*",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
    )
    docs = loader.load()
    filtered_docs = [d for d in docs if d.page_content and d.page_content.strip()]
    logger.info("Loaded %d source docs and retained %d non-empty docs.", len(docs), len(filtered_docs))
    if not filtered_docs:
        raise ValueError("No valid documents found in data directory.")
    return filtered_docs


def split_documents(docs: List[Document], config: AppConfig, logger: logging.Logger) -> List[Document]:
    """Split docs for retrieval quality and token-efficiency."""
    # 900/150 balances semantic completeness and retrieval precision:
    # chunks are large enough to preserve policy context while overlap helps continuity
    # across section boundaries for follow-up/coreference questions.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    logger.info("Split %d docs into %d chunks.", len(docs), len(chunks))
    if not chunks:
        raise ValueError("Document splitting produced zero chunks.")
    return chunks


def build_vectorstore(chunks: List[Document], logger: logging.Logger) -> FAISS:
    """Create in-memory FAISS vector store from chunks."""
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    logger.info("Built FAISS index with %d chunks.", len(chunks))
    return vectorstore


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return reusable embeddings model instance."""
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL)


def load_or_build_vectorstore(
    docs: List[Document],
    config: AppConfig,
    logger: logging.Logger,
) -> FAISS:
    """Load FAISS index from disk when available, else build and persist it."""
    embeddings = get_embeddings()
    if INDEX_DIR.exists():
        try:
            logger.info("Loading existing FAISS index from %s", INDEX_DIR)
            return FAISS.load_local(
                str(INDEX_DIR),
                embeddings,
                allow_dangerous_deserialization=True,
            )
        except Exception as exc:
            logger.warning("Failed to load cached FAISS index, rebuilding. Error: %s", exc)

    chunks = split_documents(docs, config, logger)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(INDEX_DIR))
    logger.info("Saved FAISS index to %s", INDEX_DIR)
    return vectorstore


def create_chain(
    vectorstore: FAISS,
    history: StreamlitChatHistory,
    config: AppConfig,
    logger: logging.Logger,
) -> Any:
    """Create modern retrieval chain with history-aware retriever."""
    llm = ChatGroq(model=config.model_name, temperature=config.temperature)
    retriever = vectorstore.as_retriever(search_kwargs={"k": config.top_k})

    contextualize_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Rephrase the latest user question as a standalone query using prior "
                "chat context when needed. Do not answer; only rewrite for retrieval.",
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an internal IT and cloud assistant. Answer strictly from "
                "retrieved context. If context is insufficient, say what is missing. "
                "Do not discuss finance or blockchain topics.",
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "Question: {input}\n\nContext:\n{context}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_prompt)
    qa_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)
    logger.info("Initialized history-aware retrieval chain with model %s.", config.model_name)
    return rag_chain


def get_api_key() -> str:
    """Load and validate the GROQ API key."""
    load_dotenv(dotenv_path=ENV_FILE, override=False)
    api_key = st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") else None
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            f"GROQ_API_KEY is missing. Add it to `{ENV_FILE}` or Streamlit secrets before starting."
        )
    return api_key


def render_history(history: StreamlitChatHistory) -> None:
    """Render full conversation from session state."""
    for message in history.messages:
        role = "assistant" if isinstance(message, AIMessage) else "user"
        with st.chat_message(role):
            st.markdown(message.content)


def run_app() -> None:
    """Main Streamlit entrypoint."""
    logger = setup_logging()
    st.set_page_config(page_title="IT RAG Assistant", page_icon="🧠", layout="wide")
    st.title("Infrastructure Knowledge Assistant")
    st.caption("Context-aware RAG chatbot for internal IT and cloud deployment documentation.")

    try:
        _ = get_api_key()
    except Exception as exc:
        logger.exception("API key validation failed: %s", exc)
        st.error(str(exc))
        st.stop()

    config = get_config()
    uploaded_files = st.sidebar.file_uploader(
        "Upload additional docs (.md / .txt)",
        type=["md", "txt"],
        accept_multiple_files=True,
    )
    if st.sidebar.button("Ingest uploaded documents"):
        saved = _save_uploaded_docs(uploaded_files, logger)
        st.sidebar.success(f"Saved {saved} file(s). Rebuild will happen on next message.")
        if INDEX_DIR.exists():
            import shutil

            shutil.rmtree(INDEX_DIR)
            logger.info("Deleted stale FAISS index cache at %s", INDEX_DIR)
        st.session_state.pop("vectorstore", None)
        st.session_state.pop("rag_chain", None)

    history = StreamlitChatHistory()
    render_history(history)

    if "vectorstore" not in st.session_state:
        try:
            documents = load_documents(logger)
            st.session_state["vectorstore"] = load_or_build_vectorstore(documents, config, logger)
        except Exception as exc:
            logger.exception("Knowledge base initialization failed: %s", exc)
            st.error(f"Failed to initialize knowledge base: {exc}")
            st.stop()

    if "rag_chain" not in st.session_state or st.session_state.get("active_model") != config.model_name:
        try:
            st.session_state["rag_chain"] = create_chain(
                st.session_state["vectorstore"],
                history,
                config,
                logger,
            )
            st.session_state["active_model"] = config.model_name
        except Exception as exc:
            logger.exception("RAG chain initialization failed: %s", exc)
            st.error(f"Failed to initialize retrieval chain: {exc}")
            st.stop()

    user_input = st.chat_input("Ask about server setup, cloud deployment, security controls, or API policies.")
    if not user_input:
        return

    with st.chat_message("user"):
        st.markdown(user_input)

    history.add_messages([HumanMessage(content=user_input)])
    rag_chain = st.session_state["rag_chain"]

    try:
        result: Dict[str, Any] = rag_chain.invoke(
            {"input": user_input, "chat_history": history.messages[:-1]}
        )
        answer = result.get("answer", "I could not produce an answer.")
    except Exception as exc:
        logger.exception("Inference failed: %s", exc)
        answer = "I encountered an error while generating a response. Please retry."

    history.add_messages([AIMessage(content=answer)])
    with st.chat_message("assistant"):
        st.markdown(answer)


if __name__ == "__main__":
    run_app()

import os
from typing import List, Optional
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Default local storage path
CHROMA_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")

def get_embedding_function():
    """
    Returns a local HuggingFace embeddings model (all-MiniLM-L6-v2) if available,
    falling back to OpenAIEmbeddings or FakeEmbeddings for maximum resilience.
    """
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    except Exception:
        import os
        key = os.getenv("OPENAI_API_KEY")
        if key:
            try:
                from langchain_openai import OpenAIEmbeddings
                return OpenAIEmbeddings(openai_api_key=key)
            except Exception:
                pass
        from langchain_community.embeddings import FakeEmbeddings
        return FakeEmbeddings(size=384)

def ingest_documents(documents: List[Document], persist_directory: str = CHROMA_DIR) -> FAISS:
    """
    Splits PDF documents into chunks and ingests them into a FAISS/Chroma vectorstore.
    Uses FAISS in-memory with disk save for high performance and compatibility.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    chunks = text_splitter.split_documents(documents)
    embeddings = get_embedding_function()
    
    vectorstore = FAISS.from_documents(chunks, embeddings)
    os.makedirs(persist_directory, exist_ok=True)
    vectorstore.save_local(persist_directory)
    return vectorstore

def load_vectorstore(persist_directory: str = CHROMA_DIR) -> Optional[FAISS]:
    """
    Loads an existing local vector store if available.
    """
    if os.path.exists(os.path.join(persist_directory, "index.faiss")):
        embeddings = get_embedding_function()
        return FAISS.load_local(persist_directory, embeddings, allow_dangerous_deserialization=True)
    return None

def search_documents(query: str, vectorstore: FAISS, k: int = 4) -> List[Document]:
    """
    Performs similarity search on the vectorstore.
    """
    if not vectorstore:
        return []
    return vectorstore.similarity_search(query, k=k)

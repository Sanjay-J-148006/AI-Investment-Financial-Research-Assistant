import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

def load_pdf_documents(file_path: str) -> List[Document]:
    """
    Loads a PDF file using PyPDFLoader and returns a list of Document objects.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents

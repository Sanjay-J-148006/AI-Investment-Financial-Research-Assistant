import os
from langchain_core.tools import tool
from vectorstore.chroma_store import load_vectorstore, search_documents

@tool
def rag_search_tool(query: str) -> str:
    """
    Search the indexed Annual Reports and Financial PDFs (RAG) for specific information, financial metrics, risks, or disclosures.
    """
    vectorstore = load_vectorstore()
    if not vectorstore:
        return "No uploaded PDF financial documents have been indexed yet. Please upload a PDF report in the sidebar and click 'Build Knowledge Base'."
    
    docs = search_documents(query, vectorstore, k=4)
    if not docs:
        return "No relevant sections found in the uploaded financial documents."
    
    results = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Uploaded Document")
        page = doc.metadata.get("page", 0) + 1
        results.append(f"--- Chunk {i} (Source: {os.path.basename(source)}, Page {page}) ---\n{doc.page_content}")
    
    return "\n\n".join(results)

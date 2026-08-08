from tools.rag_tool import rag_search_tool
from langchain_core.prompts import ChatPromptTemplate
from utils.llm_factory import get_llm

def get_pdf_agent_response(query: str, provider: str = "openai", api_key: str = None) -> str:
    """
    RAG Agent dedicated to querying uploaded annual reports and financial document PDFs.
    """
    rag_context = rag_search_tool.invoke(query)
    
    llm = get_llm(provider=provider, api_key=api_key)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a Forensic Accounting & PDF Analysis Specialist at AlphaVest Capital. "
            "Answer the user's question accurately using strictly the provided document context from uploaded annual reports/10-Ks. "
            "Cite relevant chunk pages and source numbers if available. If the context does not contain enough information, state clearly what is available and what is missing."
        )),
        ("user", "User Question: {query}\n\nDocument Context:\n{context}")
    ])
    
    chain = prompt | llm
    res = chain.invoke({"query": query, "context": rag_context})
    return res.content

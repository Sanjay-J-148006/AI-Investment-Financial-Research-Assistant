from langchain_core.prompts import ChatPromptTemplate
from utils.llm_factory import get_llm

def get_news_agent_response(query: str, provider: str = "openai", api_key: str = None) -> str:
    """
    Financial News Agent that retrieves live market developments, earnings reports, and news.
    """
    search_results = ""
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search_tool = DuckDuckGoSearchRun()
        search_query = f"{query} stock financial news earnings"
        search_results = search_tool.run(search_query)
    except Exception as e:
        search_results = f"Live Search Notice: Could not connect to external search engine. Providing analysis based on available context for {query}."

    llm = get_llm(provider=provider, api_key=api_key)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a Senior Financial News Analyst at AlphaVest Capital. "
            "Analyze the retrieved search results or query context and summarize key news, earnings reports, market sentiments, "
            "and stock performance. Highlight dates, numbers, revenue metrics, and ticker symbols where available. "
            "Structure your answer with clear bullet points."
        )),
        ("user", "User Request: {query}\n\nSearch Context:\n{results}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"query": query, "results": search_results})
    return response.content

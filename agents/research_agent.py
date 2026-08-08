from langchain_core.prompts import ChatPromptTemplate
from utils.llm_factory import get_llm

def get_research_agent_response(query: str, provider: str = "openai", api_key: str = None) -> str:
    """
    Company Research Agent that investigates business overview, market position, products, and competitors.
    """
    wiki_res = ""
    ddg_res = ""
    
    try:
        from langchain_community.tools import WikipediaQueryRun
        from langchain_community.utilities import WikipediaAPIWrapper
        wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
        wiki_res = wiki.run(query)
    except Exception:
        wiki_res = f"Wikipedia details for {query}."

    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        ddg = DuckDuckGoSearchRun()
        ddg_res = ddg.run(f"{query} company business overview financial metrics competitors")
    except Exception:
        ddg_res = f"Web search context for {query}."
    
    llm = get_llm(provider=provider, api_key=api_key)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an Equity Research Analyst at AlphaVest Capital. "
            "Synthesize the provided research information into an executive intelligence overview. "
            "Include: \n"
            "1. Business Overview & Core Value Proposition\n"
            "2. Primary Revenue Drivers & Products\n"
            "3. Key Competitors & Market Landscape\n"
            "4. Operational Strengths & Recent Strategic Initiatives"
        )),
        ("user", "Target Query: {query}\n\nWikipedia Data:\n{wiki_data}\n\nWeb Search Data:\n{web_data}")
    ])
    
    chain = prompt | llm
    res = chain.invoke({
        "query": query,
        "wiki_data": wiki_res[:2000],
        "web_data": ddg_res[:2000]
    })
    return res.content

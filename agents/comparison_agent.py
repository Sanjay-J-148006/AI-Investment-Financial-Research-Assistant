from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from utils.llm_factory import get_llm
from agents.research_agent import get_research_agent_response
import pandas as pd
import re

def get_comparison_agent_response(query: str, provider: str = "openai", api_key: str = None) -> str:
    """
    Executes parallel research across multiple companies using RunnableParallel
    and produces a Markdown comparison table and analyst breakdown.
    """
    # Extract company names from query
    llm = get_llm(provider=provider, api_key=api_key)
    
    extraction_prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract the list of company names to compare from the query. Return them comma-separated (e.g., 'Microsoft, Apple, Google')."),
        ("user", "{query}")
    ])
    
    companies_str = (extraction_prompt | llm).invoke({"query": query}).content
    companies = [c.strip() for c in companies_str.split(",") if c.strip()]
    
    if len(companies) < 2:
        companies = ["Microsoft", "Google"] # Fallback default
        
    # Build RunnableParallel mapping for each company
    parallel_dict = {}
    for comp in companies:
        # Wrap each research call in RunnableLambda
        parallel_dict[comp] = RunnableLambda(lambda x, c=comp: get_research_agent_response(c, provider=provider, api_key=api_key))
        
    parallel_runner = RunnableParallel(**parallel_dict)
    results = parallel_runner.invoke({"query": query})
    
    # Synthesize results into Markdown comparison
    combined_research = ""
    for comp, res in results.items():
        combined_research += f"### Company: {comp}\n{res}\n\n"
        
    synth_prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a Portfolio Manager at AlphaVest Capital. "
            "Given the research on multiple companies, generate a side-by-side comparison table in Markdown format "
            "comparing: Core Business, Strengths, Revenue Model, and Relative Investment Attractiveness. "
            "Follow the table with a strategic comparison summary."
        )),
        ("user", "Target Query: {query}\n\nIndividual Company Research:\n{research}")
    ])
    
    final_output = (synth_prompt | llm).invoke({"query": query, "research": combined_research}).content
    return final_output

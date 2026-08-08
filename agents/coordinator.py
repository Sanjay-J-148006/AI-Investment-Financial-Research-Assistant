import time
import re
from langchain_core.runnables import RunnableBranch, RunnableLambda
from agents.news_agent import get_news_agent_response
from agents.research_agent import get_research_agent_response
from agents.pdf_agent import get_pdf_agent_response
from agents.comparison_agent import get_comparison_agent_response
from agents.email_agent import get_email_agent_response
from tools.financial_calculator import calculate_cagr, calculate_roi, calculate_growth_rate
from tools.rag_tool import rag_search_tool
from chains.sequential_chain import run_sequential_workflow
from utils.guardrails import sanitize_input, append_guardrail_disclaimer, calculate_token_cost

def _is_email_query(inputs: dict) -> bool:
    q = inputs.get("query", "").lower()
    return any(k in q for k in ["email", "send report", "mail to", "dispatch"])

def _is_comparison_query(inputs: dict) -> bool:
    q = inputs.get("query", "").lower()
    return any(k in q for k in ["compare", "versus", "vs.", "comparison"])

def _is_calc_query(inputs: dict) -> bool:
    q = inputs.get("query", "").lower()
    return any(k in q for k in ["cagr", "roi", "calculate", "growth rate", "return on investment"])

def _is_pdf_query(inputs: dict) -> bool:
    q = inputs.get("query", "").lower()
    return any(k in q for k in ["pdf", "annual report", "10-k", "10q", "uploaded document", "file", "risk factors"])

def _is_news_query(inputs: dict) -> bool:
    q = inputs.get("query", "").lower()
    return any(k in q for k in ["news", "earnings", "quarterly results", "market update", "latest stock"])

def _is_report_query(inputs: dict) -> bool:
    q = inputs.get("query", "").lower()
    return any(k in q for k in ["report", "full analysis", "investment thesis"])

def _exec_email(inputs: dict) -> dict:
    query, provider, api_key = inputs["query"], inputs.get("provider", "groq"), inputs.get("api_key")
    output = get_email_agent_response(query, last_report_text=inputs.get("last_report_text", ""), provider=provider, api_key=api_key)
    return {"agent_name": "Email Agent", "output": output, "trace": {}}

def _exec_comparison(inputs: dict) -> dict:
    query, provider, api_key = inputs["query"], inputs.get("provider", "groq"), inputs.get("api_key")
    output = get_comparison_agent_response(query, provider=provider, api_key=api_key)
    return {"agent_name": "Multi-Company Parallel Comparison Agent", "output": output, "trace": {}}

def _exec_calc(inputs: dict) -> dict:
    query = inputs["query"]
    q_lower = query.lower()
    nums = [float(n) for n in re.findall(r"[-+]?\d*\.\d+|\d+", query)]
    
    if "cagr" in q_lower and len(nums) >= 3:
        calc_res = calculate_cagr.invoke({"initial_value": nums[0], "final_value": nums[1], "num_years": nums[2]})
    elif "roi" in q_lower and len(nums) >= 2:
        calc_res = calculate_roi.invoke({"initial_investment": nums[0], "final_value": nums[1]})
    elif "growth" in q_lower and len(nums) >= 2:
        calc_res = calculate_growth_rate.invoke({"old_value": nums[0], "new_value": nums[1]})
    else:
        calc_res = (
            "Financial Calculator Tool Triggered.\n"
            "Supported Examples:\n"
            "- 'Calculate CAGR from 100 to 250 over 5 years'\n"
            "- 'Calculate ROI for 1000 initial investment and 1650 final value'\n"
            "- 'Calculate growth rate from 50 to 85'"
        )
    return {
        "agent_name": "Financial Calculator Tool",
        "output": calc_res,
        "trace": {"financial_calculations": calc_res}
    }

def _exec_pdf(inputs: dict) -> dict:
    query, provider, api_key = inputs["query"], inputs.get("provider", "groq"), inputs.get("api_key")
    output = get_pdf_agent_response(query, provider=provider, api_key=api_key)
    retrieved_chunks = rag_search_tool.invoke(query)
    return {
        "agent_name": "PDF RAG Agent",
        "output": output,
        "trace": {"retrieved_pdf_chunks": retrieved_chunks}
    }

def _exec_news(inputs: dict) -> dict:
    query, provider, api_key = inputs["query"], inputs.get("provider", "groq"), inputs.get("api_key")
    output = get_news_agent_response(query, provider=provider, api_key=api_key)
    return {
        "agent_name": "Financial News Agent",
        "output": output,
        "trace": {"latest_news": output}
    }

def _exec_report(inputs: dict) -> dict:
    query, provider, api_key = inputs["query"], inputs.get("provider", "groq"), inputs.get("api_key")
    company = query.replace("report", "").replace("generate", "").replace("investment", "").strip() or "NVIDIA"
    res = run_sequential_workflow(company, provider=provider, api_key=api_key)
    report_obj = res["report"]
    
    formatted_md = f"""# 📊 Investment Research Report: {report_obj.company_name} ({report_obj.ticker})

### 🏢 Company Overview
{report_obj.company_overview}

- **Industry:** {report_obj.industry}
- **Business Model:** {report_obj.business_model}

---

### 📰 Latest Market News
{report_obj.latest_news}

---

### 💡 Strengths
{"".join([f"- {s}\n" for s in report_obj.strengths])}

### ⚠️ Weaknesses
{"".join([f"- {w}\n" for w in report_obj.weaknesses])}

---

### 📈 Financial Highlights
{report_obj.financial_highlights}

### 🚀 Growth Opportunities
{report_obj.growth_opportunities}

### 🛡️ Potential Risks
{report_obj.potential_risks}

---

### 🎯 Analyst Recommendation & Verdict
{report_obj.investment_summary}
"""
    return {
        "agent_name": "Sequential Investment Report Chain",
        "output": formatted_md,
        "structured_report": report_obj,
        "trace": {
            "latest_news": res.get("news"),
            "retrieved_pdf_chunks": res.get("pdf"),
            "final_recommendation": report_obj.investment_summary
        }
    }

def _exec_default_research(inputs: dict) -> dict:
    query, provider, api_key = inputs["query"], inputs.get("provider", "groq"), inputs.get("api_key")
    output = get_research_agent_response(query, provider=provider, api_key=api_key)
    return {"agent_name": "Company Research Agent", "output": output, "trace": {}}

# LangChain RunnableBranch Intent Router (Module 8)
intent_router_branch = RunnableBranch(
    (RunnableLambda(_is_email_query), RunnableLambda(_exec_email)),
    (RunnableLambda(_is_comparison_query), RunnableLambda(_exec_comparison)),
    (RunnableLambda(_is_calc_query), RunnableLambda(_exec_calc)),
    (RunnableLambda(_is_pdf_query), RunnableLambda(_exec_pdf)),
    (RunnableLambda(_is_news_query), RunnableLambda(_exec_news)),
    (RunnableLambda(_is_report_query), RunnableLambda(_exec_report)),
    RunnableLambda(_exec_default_research)
)

def route_and_execute(query: str, last_report_text: str = "", provider: str = "groq", api_key: str = None) -> dict:
    """
    Executes LCEL RunnableBranch router to classify query intent and run the optimal agent with Telemetry & Financial Guardrails.
    """
    start_time = time.time()
    clean_query, is_safe = sanitize_input(query)
    
    inputs = {
        "query": clean_query,
        "last_report_text": last_report_text,
        "provider": provider,
        "api_key": api_key
    }
    
    res = intent_router_branch.invoke(inputs)
    latency = round(time.time() - start_time, 3)
    
    # Financial Disclaimer Guardrail
    guarded_output = append_guardrail_disclaimer(res.get("output", ""))
    res["output"] = guarded_output
    
    # Telemetry metrics
    token_stats = calculate_token_cost(len(query), len(guarded_output), provider=provider)
    res["telemetry"] = {
        "execution_latency_sec": latency,
        "provider": provider.upper(),
        "input_length": len(query),
        "output_length": len(guarded_output),
        **token_stats
    }
    return res

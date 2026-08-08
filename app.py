import streamlit as st
import os
import tempfile
import pandas as pd
from dotenv import load_dotenv

from utils.pdf_loader import load_pdf_documents
from vectorstore.chroma_store import ingest_documents, load_vectorstore
from memory.long_term import (
    save_investor_profile,
    get_investor_profile,
    get_all_investor_profiles,
    delete_investor_profile,
    log_conversation_turn,
    get_recent_conversation_logs
)
from agents.coordinator import route_and_execute
from agents.news_agent import get_news_agent_response
from agents.research_agent import get_research_agent_response
from agents.pdf_agent import get_pdf_agent_response
from agents.comparison_agent import get_comparison_agent_response
from agents.email_agent import get_email_agent_response
from chains.sequential_chain import run_sequential_workflow
from tools.financial_calculator import calculate_cagr, calculate_roi, calculate_growth_rate, create_comparison_table
from utils.formatter import export_report_as_txt, export_report_as_pdf
from utils.charts import generate_stock_performance_chart, generate_revenue_breakdown_chart, generate_comparison_bar_chart

load_dotenv()

# --- PAGE SETUP ---
st.set_page_config(
    page_title="AlphaVest — AI Investment & Financial Research Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLES ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .workspace-header {
        font-size: 2.0rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
    }
    
    .workspace-sub {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 20px;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    .telemetry-card {
        background: #F1F5F9;
        border-left: 4px solid #3B82F6;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 0.85rem;
        color: #334155;
    }
    
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE DB & SAMPLE PROFILES ---
existing_profiles = get_all_investor_profiles()
if not existing_profiles:
    save_investor_profile("AlphaVest Default Client", "Moderate", "Technology, Healthcare", "3-5 Years", "Default client mandate.")
    save_investor_profile("John Doe (Tech Growth)", "Aggressive", "Semiconductors, Cloud, AI", "5-10+ Years", "High CAGR tech growth mandate.")
    save_investor_profile("Sarah Smith (Dividend Income)", "Conservative", "Utilities, Consumer Staples", "1-3 Years", "Low volatility income mandate.")
    existing_profiles = get_all_investor_profiles()

# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to AlphaVest Capital AI Financial Research Assistant! How can I assist with your investment research, PDF annual reports, or company analysis today?"}
    ]

if "last_report_text" not in st.session_state:
    st.session_state.last_report_text = ""

if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []

if "provider" not in st.session_state:
    st.session_state.provider = os.getenv("DEFAULT_LLM_PROVIDER", "groq").lower()

if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("GROQ_API_KEY", "")

if "gmail_user" not in st.session_state:
    st.session_state.gmail_user = os.getenv("GMAIL_USER", "")

if "gmail_password" not in st.session_state:
    st.session_state.gmail_password = os.getenv("GMAIL_APP_PASSWORD", "")

if "active_investor" not in st.session_state:
    st.session_state.active_investor = existing_profiles[0]["name"] if existing_profiles else "Default Client"

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.markdown("### 🖥️ **Intelligence Workspace**")
    
    workspace_selection = st.radio(
        label="Workspace Navigation",
        options=[
            "📊 Market Overview",
            "🤖 AI Research Agent",
            "📰 News Intelligence",
            "🏢 Company Analysis",
            "⚖️ Multi-Company Comparison",
            "📄 Document Intelligence",
            "🧮 Financial Calculations",
            "📋 Investment Reports",
            "👤 Investor Memory",
            "⚙️ Settings"
        ],
        index=1,
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.subheader("📄 Upload Financial Reports")
    annual_pdfs = st.file_uploader("Upload Annual Reports (10-K)", type=["pdf"], accept_multiple_files=True, key="ann_up")
    quarterly_pdfs = st.file_uploader("Upload Quarterly Reports (10-Q)", type=["pdf"], accept_multiple_files=True, key="qtr_up")
    
    if st.button("🔨 Build Knowledge Base", type="primary", use_container_width=True):
        files_to_process = (annual_pdfs or []) + (quarterly_pdfs or [])
        if files_to_process:
            with st.spinner("Ingesting & Indexing PDF Documents..."):
                all_docs = []
                new_fnames = []
                for uf in files_to_process:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uf.getvalue())
                        tmp_p = tmp.name
                    docs = load_pdf_documents(tmp_p)
                    for d in docs:
                        d.metadata["source"] = uf.name
                    all_docs.extend(docs)
                    new_fnames.append(uf.name)
                    os.remove(tmp_p)
                ingest_documents(all_docs)
                st.session_state.indexed_files.extend(new_fnames)
                st.success(f"Indexed {len(all_docs)} pages from {len(new_fnames)} PDFs!")
        else:
            st.warning("Please select at least one PDF file.")
            
    if st.session_state.indexed_files:
        st.caption("📂 **View Uploaded Reports:**")
        for fn in set(st.session_state.indexed_files):
            st.markdown(f"- `{fn}`")

    st.divider()
    
    st.subheader("👤 Active Investor & Conversations")
    profile_names = [p["name"] for p in get_all_investor_profiles()]
    if not profile_names:
        profile_names = ["Default Client"]
    selected_prof = st.selectbox(
        "Previous Conversations / Client Profile",
        options=profile_names,
        index=profile_names.index(st.session_state.active_investor) if st.session_state.active_investor in profile_names else 0
    )
    st.session_state.active_investor = selected_prof
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat history cleared. How can I assist with your research?"}
        ]
        st.rerun()

# --- WORKSPACE 1: MARKET OVERVIEW ---
if workspace_selection == "📊 Market Overview":
    st.markdown('<div class="workspace-header">📊 Market Overview & Live Benchmarks</div>', unsafe_allow_html=True)
    st.markdown('<div class="workspace-sub">Real-time market indicators, global indices, and key equity drivers</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-title">S&P 500</div><div class="metric-val">5,864.67</div><div class="metric-change">+0.42% ▲</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-title">NASDAQ 100</div><div class="metric-val">18,489.55</div><div class="metric-change">+0.85% ▲</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-title">DOW JONES</div><div class="metric-val">43,275.91</div><div class="metric-change">-0.12% ▼</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><div class="metric-title">MARKET SENTIMENT</div><div class="metric-val">BULLISH</div><div class="metric-change">Greed Index: 68</div></div>', unsafe_allow_html=True)
        
    st.divider()
    
    st.plotly_chart(generate_stock_performance_chart("S&P 500 Benchmark", "Global Equity Indices"), use_container_width=True)
    
    st.divider()
    st.subheader("⚡ Quick Stock Actions")
    qcol1, qcol2, qcol3, qcol4, qcol5, qcol6 = st.columns(6)
    quick_sel = None
    if qcol1.button("NVDA", use_container_width=True): quick_sel = "NVIDIA"
    if qcol2.button("AAPL", use_container_width=True): quick_sel = "Apple"
    if qcol3.button("MSFT", use_container_width=True): quick_sel = "Microsoft"
    if qcol4.button("AMZN", use_container_width=True): quick_sel = "Amazon"
    if qcol5.button("GOOGL", use_container_width=True): quick_sel = "Google"
    if qcol6.button("TSLA", use_container_width=True): quick_sel = "Tesla"
    
    if quick_sel:
        with st.spinner(f"Fetching Live Market News for {quick_sel}..."):
            res = get_news_agent_response(quick_sel, provider=st.session_state.provider, api_key=st.session_state.api_key)
            st.markdown(f"### Live News & Sentiment: {quick_sel}")
            st.markdown(res)

# --- WORKSPACE 2: AI RESEARCH AGENT ---
elif workspace_selection == "🤖 AI Research Agent":
    st.markdown('<div class="workspace-header">🤖 AI Research Agent</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="workspace-sub">Active Investor Profile: <b>{st.session_state.active_investor}</b> • LangChain Multi-Agent Router</div>', unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    if prompt := st.chat_input("Ask a question, e.g. 'Research NVIDIA', 'Compare Microsoft and Google', 'Calculate CAGR'..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Orchestrating agents & processing query..."):
                try:
                    res = route_and_execute(
                        query=prompt,
                        last_report_text=st.session_state.last_report_text,
                        provider=st.session_state.provider,
                        api_key=st.session_state.api_key
                    )
                    
                    agent_name = res.get("agent_name", "Coordinator Router")
                    output_text = res.get("output", "")
                    trace = res.get("trace", {})
                    telemetry = res.get("telemetry", {})
                    
                    st.caption(f"🤖 **Routed Agent:** `{agent_name}`")
                    st.markdown(output_text)
                    
                    if telemetry:
                        with st.expander("⚡ Agent Execution Telemetry & Latency Trace"):
                            st.markdown(f"""
                            <div class="telemetry-card">
                                ⏱️ <b>Latency:</b> {telemetry.get('execution_latency_sec')}s | 
                                ⚡ <b>Provider:</b> {telemetry.get('provider')} | 
                                🔤 <b>Est. Tokens:</b> {telemetry.get('total_tokens')} | 
                                💵 <b>Est. Cost:</b> ${telemetry.get('estimated_cost_usd')} USD
                            </div>
                            """, unsafe_allow_html=True)

                    if trace.get("latest_news"):
                        with st.expander("📰 Latest News"):
                            st.markdown(trace["latest_news"])
                    if trace.get("retrieved_pdf_chunks"):
                        with st.expander("📄 Retrieved PDF Chunks"):
                            st.markdown(trace["retrieved_pdf_chunks"])
                    if trace.get("financial_calculations"):
                        with st.expander("🔢 Financial Calculations"):
                            st.markdown(trace["financial_calculations"])
                    if trace.get("final_recommendation"):
                        with st.expander("🎯 Final Recommendation"):
                            st.markdown(trace["final_recommendation"])
                            
                    if "output" in res and ("Investment Research Report" in res["output"] or "Company Overview" in res["output"]):
                        st.session_state.last_report_text = res["output"]
                        
                    st.session_state.messages.append({"role": "assistant", "content": f"**[{agent_name}]**\n\n{output_text}"})
                    log_conversation_turn(st.session_state.active_investor, "user", prompt)
                    log_conversation_turn(st.session_state.active_investor, "assistant", output_text)
                except Exception as e:
                    st.error(f"⚠️ Execution error: {str(e)}")

# --- WORKSPACE 3: NEWS INTELLIGENCE ---
elif workspace_selection == "📰 News Intelligence":
    st.markdown('<div class="workspace-header">📰 News Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="workspace-sub">Retrieves live financial news, earnings announcements, and industry trends</div>', unsafe_allow_html=True)
    
    news_query = st.text_input("Enter Company or Financial Query", value="NVIDIA earnings Q3 AI announcements")
    if st.button("🔎 Search Live News", type="primary"):
        with st.spinner("Retrieving Live Financial News..."):
            n_out = get_news_agent_response(news_query, provider=st.session_state.provider, api_key=st.session_state.api_key)
            st.markdown(n_out)

# --- WORKSPACE 4: COMPANY ANALYSIS ---
elif workspace_selection == "🏢 Company Analysis":
    st.markdown('<div class="workspace-header">🏢 Company Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="workspace-sub">Combines web search & Wikipedia to analyze Business Overview, Products, Competitors & Revenue Sources</div>', unsafe_allow_html=True)
    
    comp_name = st.text_input("Company Name", value="Microsoft")
    if st.button("🔬 Perform Company Research", type="primary"):
        with st.spinner(f"Analyzing {comp_name}..."):
            r_out = get_research_agent_response(comp_name, provider=st.session_state.provider, api_key=st.session_state.api_key)
            st.markdown(r_out)
            st.divider()
            
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(generate_stock_performance_chart("MSFT", comp_name), use_container_width=True)
            with c2:
                st.plotly_chart(generate_revenue_breakdown_chart(comp_name), use_container_width=True)

# --- WORKSPACE 5: MULTI-COMPANY COMPARISON ---
elif workspace_selection == "⚖️ Multi-Company Comparison":
    st.markdown('<div class="workspace-header">⚖️ Multi-Company Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="workspace-sub">Executes parallel research across companies before merging into a unified comparison table</div>', unsafe_allow_html=True)
    
    comp_input = st.text_input("Companies to Compare (comma-separated)", value="Microsoft, Apple, Google, Meta")
    if st.button("⚡ Run Parallel Comparison", type="primary"):
        with st.spinner("Executing Parallel Research..."):
            c_out = get_comparison_agent_response(comp_input, provider=st.session_state.provider, api_key=st.session_state.api_key)
            st.markdown(c_out)
            st.divider()
            
            c_list = [c.strip() for c in comp_input.split(",") if c.strip()]
            st.plotly_chart(generate_comparison_bar_chart(c_list), use_container_width=True)

# --- WORKSPACE 6: DOCUMENT INTELLIGENCE (PDF RAG) ---
elif workspace_selection == "📄 Document Intelligence":
    st.markdown('<div class="workspace-header">📄 Document Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="workspace-sub">Upload 10-Ks, 10-Qs, Investor Presentations & answer questions using document chunks</div>', unsafe_allow_html=True)
    
    col_up, col_q = st.columns([1, 1])
    with col_up:
        st.subheader("1. Document Ingestion")
        up_files = st.file_uploader("Upload Reports (PDF)", type=["pdf"], accept_multiple_files=True, key="doc_intel_up")
        if st.button("🔨 Index Documents into Vector Store", type="primary", use_container_width=True):
            if up_files:
                with st.spinner("Indexing PDF Chunks..."):
                    all_docs = []
                    new_fns = []
                    for uf in up_files:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            tmp.write(uf.getvalue())
                            tmp_p = tmp.name
                        docs = load_pdf_documents(tmp_p)
                        for d in docs: d.metadata["source"] = uf.name
                        all_docs.extend(docs)
                        new_fns.append(uf.name)
                        os.remove(tmp_p)
                    ingest_documents(all_docs)
                    st.session_state.indexed_files.extend(new_fns)
                    st.success(f"Indexed {len(all_docs)} pages from {len(new_fns)} PDFs!")
            else:
                st.warning("Upload a PDF file first.")
                
        if st.session_state.indexed_files:
            st.caption("📂 **Indexed Store Files:**")
            for fn in set(st.session_state.indexed_files):
                st.markdown(f"- `{fn}`")
                
    with col_q:
        st.subheader("2. Forensic RAG Query")
        pdf_query = st.text_input("Question for uploaded documents", value="Summarize risk factors and revenue growth drivers")
        if st.button("🔍 Search Document RAG", use_container_width=True):
            with st.spinner("Searching Vector Store..."):
                p_out = get_pdf_agent_response(pdf_query, provider=st.session_state.provider, api_key=st.session_state.api_key)
                st.markdown(p_out)

# --- WORKSPACE 7: FINANCIAL CALCULATIONS ---
elif workspace_selection == "🧮 Financial Calculations":
    st.markdown('<div class="workspace-header">🧮 Financial Calculations</div>', unsafe_allow_html=True)
    st.markdown('<div class="workspace-sub">Calculates CAGR, ROI, Annual Growth Rates, and generates Markdown comparison tables</div>', unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs(["📈 CAGR Calculator", "💰 ROI Calculator", "📊 Annual Growth Rate", "📋 Comparison Table Generator"])
    
    with t1:
        st.subheader("CAGR Calculation")
        c1, c2, c3 = st.columns(3)
        iv = c1.number_input("Initial Value ($)", value=100.0)
        fv = c2.number_input("Final Value ($)", value=250.0)
        ny = c3.number_input("Years", value=5.0)
        if st.button("Calculate CAGR", type="primary"):
            st.success(calculate_cagr.invoke({"initial_value": iv, "final_value": fv, "num_years": ny}))
            
    with t2:
        st.subheader("ROI Calculation")
        r1, r2 = st.columns(2)
        ic = r1.number_input("Initial Investment ($)", value=1000.0)
        fv_r = r2.number_input("Final Value ($)", value=1650.0)
        if st.button("Calculate ROI", type="primary"):
            st.success(calculate_roi.invoke({"initial_investment": ic, "final_value": fv_r}))
            
    with t3:
        st.subheader("Annual Growth Rate Calculation")
        g1, g2 = st.columns(2)
        ov = g1.number_input("Previous Period Value", value=50.0)
        nv = g2.number_input("Current Period Value", value=85.0)
        if st.button("Calculate Growth Rate", type="primary"):
            st.success(calculate_growth_rate.invoke({"old_value": ov, "new_value": nv}))

    with t4:
        st.subheader("Comparison Table Generator")
        comp_str = st.text_input("Companies (comma-separated)", value="Microsoft, Google, Amazon, Meta")
        if st.button("Generate Comparison Table", type="primary"):
            tbl_md = create_comparison_table.invoke({"companies_data": comp_str})
            st.markdown(tbl_md)

# --- WORKSPACE 8: INVESTMENT REPORTS ---
elif workspace_selection == "📋 Investment Reports":
    st.markdown('<div class="workspace-header">📋 Investment Reports</div>', unsafe_allow_html=True)
    st.markdown('<div class="workspace-sub">Sequential Pipeline: Research → Read PDF → Merge Info → Analyze → Structured Pydantic Report → Email Dispatch</div>', unsafe_allow_html=True)
    
    rep_target = st.text_input("Target Company", value="NVIDIA")
    
    if st.button("📑 Run Sequential Report Pipeline", type="primary"):
        with st.spinner(f"Running Sequential Pipeline for {rep_target}..."):
            w_res = run_sequential_workflow(rep_target, provider=st.session_state.provider, api_key=st.session_state.api_key)
            rep_obj = w_res["report"]
            
            md_out = f"""# 📊 Investment Research Report: {rep_obj.company_name} ({rep_obj.ticker})

### 🏢 Company Overview
{rep_obj.company_overview}

- **Industry:** {rep_obj.industry}
- **Business Model:** {rep_obj.business_model}

---

### 📰 Latest Market News
{rep_obj.latest_news}

---

### 💡 Strengths
{"".join([f"- {s}\n" for s in rep_obj.strengths])}

### ⚠️ Weaknesses
{"".join([f"- {w}\n" for w in rep_obj.weaknesses])}

---

### 📈 Financial Highlights
{rep_obj.financial_highlights}

### 🚀 Growth Opportunities
{rep_obj.growth_opportunities}

### 🛡️ Potential Risks
{rep_obj.potential_risks}

---

### 🎯 Analyst Investment Verdict
{rep_obj.investment_summary}
"""
            st.session_state.last_report_text = md_out
            st.markdown(md_out)
            
    if st.session_state.last_report_text:
        st.divider()
        st.subheader("📥 Export & Email Dispatch Center")
        
        ex1, ex2 = st.columns(2)
        with ex1:
            txt_p = export_report_as_txt(st.session_state.last_report_text)
            with open(txt_p, "rb") as f:
                st.download_button("📄 Download TXT Report", data=f.read(), file_name="Investment_Report.txt", mime="text/plain", use_container_width=True)
        with ex2:
            pdf_p = export_report_as_pdf(st.session_state.last_report_text)
            with open(pdf_p, "rb") as f:
                st.download_button("📕 Download PDF Pitchbook", data=f.read(), file_name="Investment_Report.pdf", mime="application/pdf", use_container_width=True)
        
        st.divider()
        st.subheader("📧 Dispatch Email Report to Client")
        
        with st.expander("🔑 Sender Gmail & Credentials Setup (Click to Expand)", expanded=(not bool(st.session_state.gmail_user and st.session_state.gmail_password))):
            st.info("""
            **How to Send Real Emails via Gmail in 30 Seconds:**
            1. Enter your **Sender Gmail Address** (e.g. `yourname@gmail.com`).
            2. Enter a **16-Character Gmail App Password**.
               *Note: To create an App Password, go to your **Google Account -> Security -> 2-Step Verification -> App Passwords**, generate a password for 'Mail', and paste it here.*
            """)
            g_usr_in = st.text_input("Sender Gmail Address", value=st.session_state.gmail_user, placeholder="yourname@gmail.com")
            g_pwd_in = st.text_input("16-Character Gmail App Password", value=st.session_state.gmail_password, type="password", placeholder="abcd efgh ijkl mnop")
            if st.button("💾 Save Gmail Credentials"):
                st.session_state.gmail_user = g_usr_in.strip()
                st.session_state.gmail_password = g_pwd_in.strip()
                st.success("Gmail credentials saved for this session!")
                st.rerun()

        recip = st.text_input("Recipient Email Address", value="client@alphavest.com")
        attach_pdf = st.checkbox("Attach Styled PDF Report to Email", value=True)
        
        if st.button("🚀 Dispatch Email Report", type="primary", use_container_width=True):
            try:
                pdf_path_to_attach = export_report_as_pdf(st.session_state.last_report_text) if (attach_pdf and st.session_state.last_report_text) else ""
                with st.spinner("Composing & Dispatching Executive Email..."):
                    e_out = get_email_agent_response(
                        query=f"Send report to {recip}",
                        last_report_text=st.session_state.last_report_text,
                        provider=st.session_state.provider,
                        api_key=st.session_state.api_key,
                        gmail_user=st.session_state.gmail_user,
                        gmail_password=st.session_state.gmail_password,
                        attachment_path=pdf_path_to_attach
                    )
                    st.markdown(e_out)
            except Exception as ex:
                st.error(f"⚠️ Email Dispatch Error: {str(ex)}")

# --- WORKSPACE 9: INVESTOR MEMORY ---
elif workspace_selection == "👤 Investor Memory":
    st.markdown('<div class="workspace-header">👤 Investor Memory</div>', unsafe_allow_html=True)
    st.markdown('<div class="workspace-sub">SQLite persistent database storing investor risk profiles, target sectors, guidelines, and conversation history</div>', unsafe_allow_html=True)
    
    all_profs = get_all_investor_profiles()
    st.subheader(f"📋 Registered Client Profiles ({len(all_profs)})")
    if all_profs:
        df_p = pd.DataFrame(all_profs)
        st.dataframe(df_p.rename(columns={
            "name": "Client Name",
            "risk_profile": "Risk Profile",
            "preferred_industries": "Target Sectors",
            "investment_horizon": "Horizon",
            "notes": "Strategy Notes",
            "updated_at": "Last Updated"
        })[["Client Name", "Risk Profile", "Target Sectors", "Horizon", "Strategy Notes", "Last Updated"]], use_container_width=True)
        
    st.divider()
    col_ed, col_lg = st.columns([1, 1])
    
    with col_ed:
        st.subheader("➕ Create or Edit Profile")
        sel_name = st.selectbox("Select Profile", options=["-- Create New --"] + [p["name"] for p in all_profs])
        ex_d = get_investor_profile(sel_name) if sel_name != "-- Create New --" else {}
        
        c_name = st.text_input("Client Name", value=ex_d.get("name", ""))
        r_opts = ["Conservative", "Moderate", "Growth", "Aggressive"]
        c_r = ex_d.get("risk_profile", "Growth")
        r_t = st.selectbox("Risk Profile", r_opts, index=r_opts.index(c_r) if c_r in r_opts else 2)
        sectors = st.text_input("Target Sectors", value=ex_d.get("preferred_industries", "Technology, Cloud, AI"))
        h_opts = ["1-3 Years", "3-5 Years", "5-10+ Years"]
        c_h = ex_d.get("investment_horizon", "5-10+ Years")
        horizon = st.selectbox("Investment Horizon", h_opts, index=h_opts.index(c_h) if c_h in h_opts else 2)
        notes = st.text_area("Strategy Notes", value=ex_d.get("notes", ""))
        
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("💾 Save Profile to SQLite", type="primary", use_container_width=True):
                if c_name.strip():
                    save_investor_profile(c_name.strip(), r_t, sectors, horizon, notes)
                    st.session_state.active_investor = c_name.strip()
                    st.success("Profile saved!")
                    st.rerun()
                else: st.warning("Enter a name.")
        with bc2:
            if sel_name != "-- Create New --":
                if st.button("🗑️ Delete Profile", use_container_width=True):
                    delete_investor_profile(sel_name)
                    st.session_state.active_investor = "AlphaVest Default Client"
                    st.success("Profile deleted!")
                    st.rerun()

    with col_lg:
        st.subheader(f"📜 Persistent Conversation Logs ({st.session_state.active_investor})")
        logs = get_recent_conversation_logs(st.session_state.active_investor, limit=15)
        if logs:
            for l in logs:
                st.caption(f"**[{l['role'].upper()}]** ({l['timestamp']})")
                st.markdown(l['content'][:300] + ("..." if len(l['content']) > 300 else ""))
                st.divider()
        else:
            st.info("No conversation logs recorded for this client yet.")

# --- WORKSPACE 10: SETTINGS ---
elif workspace_selection == "⚙️ Settings":
    st.markdown('<div class="workspace-header">⚙️ System Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="workspace-sub">Configure LLM model providers, API keys, Gmail SMTP credentials, and diagnostics</div>', unsafe_allow_html=True)
    
    st.subheader("1. Active Model Provider")
    provider_choice = st.selectbox("Provider", ["Groq", "OpenAI", "Google Gemini"], index=0)
    st.session_state.provider = provider_choice.lower()
    if st.session_state.provider == "google gemini": st.session_state.provider = "google"
    
    st.subheader("2. Groq / OpenAI API Key String")
    k_in = st.text_input("API Key", value=st.session_state.api_key, type="password")
    
    st.subheader("3. Gmail SMTP Dispatch Credentials")
    st.caption("Required if you wish to dispatch emails to clients directly from the application.")
    gm_u = st.text_input("Sender Gmail Address", value=st.session_state.gmail_user, placeholder="yourname@gmail.com")
    gm_p = st.text_input("16-Character Gmail App Password", value=st.session_state.gmail_password, type="password", placeholder="abcd efgh ijkl mnop")
    
    if st.button("💾 Save All System Settings", type="primary"):
        st.session_state.api_key = k_in.strip()
        st.session_state.gmail_user = gm_u.strip()
        st.session_state.gmail_password = gm_p.strip()
        st.success("System & Gmail settings saved successfully!")
        
    st.divider()
    st.subheader("4. System Architecture Diagnostic")
    st.markdown("- **Router**: `RunnableBranch` in `agents/coordinator.py`")
    st.markdown("- **Parallel Agent**: `RunnableParallel` in `agents/comparison_agent.py`")
    st.markdown("- **Sequential Pipeline**: `RunnableLambda` chain in `chains/sequential_chain.py`")
    st.markdown("- **Structured Output**: Pydantic `InvestmentReport` schema")
    st.markdown("- **Vector Store**: ChromaDB / FAISS RAG under `./chroma_db`")
    st.markdown("- **Persistent Memory**: SQLite database (`memory/investor_memory.db`)")

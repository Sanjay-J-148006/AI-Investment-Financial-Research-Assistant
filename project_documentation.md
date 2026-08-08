# 📄 Capstone Project Documentation: AI Investment & Financial Research Assistant

**Program:** Agentic AI Engineering Program — Capstone Project 3  
**Organization:** AlphaVest Capital  
**Frameworks:** LangChain, Streamlit, Groq AI / OpenAI, ChromaDB / FAISS, SQLite, Pydantic  

---

## 🏛️ Case Study & Business Problem

AlphaVest Capital is a financial advisory firm assisting clients in making informed investment decisions. Financial analysts spend hours every day researching company fundamentals, market news, annual reports (10-Ks, 10-Qs), economic indicators, and industry trends before synthesizing formal investment reports.

**Objective:** Automate analyst workflows using an AI-powered Multi-Agent Financial Research Assistant deployed as an interactive Streamlit web application.

---

## 🏗️ System Architecture

```text
                  Investor / Financial Analyst
                               │
                               ▼
                         Streamlit UI
                               │
                               ▼
        Financial Research Coordinator (RunnableBranch Router)
         │                   │                 │              │
         ▼                   ▼                 ▼              ▼
    News Agent          PDF RAG Agent   Research Agent   Email Agent
         │                   │                 │              │
         └───────────────────┴─────────────────┴──────────────┘
                               │
                     Financial Memory Layer
                     ├── Short-Term Conversation Memory
                     └── Long-Term Persistent SQLite Memory
                               │
                        ChromaDB / FAISS Vector Store
```

---

## 🧩 Module-by-Module Technical Specs

| Module | Name | Technical Implementation |
|---|---|---|
| **Module 1** | AI Financial Assistant | Conversational Streamlit interface powered by LangChain multi-agent routing. |
| **Module 2** | Financial News Agent | Live financial news search via DuckDuckGo retrieving market developments & stock earnings updates (`agents/news_agent.py`). |
| **Module 3** | Company Research Agent | Deep equity research combining web search and Wikipedia API to analyze Business Overview, Products, Competitors, and Revenue Streams (`agents/research_agent.py`). |
| **Module 4** | Annual Report Analysis (RAG) | `PyPDFLoader` + text chunking + FAISS/ChromaDB similarity retriever (`vectorstore/chroma_store.py`, `agents/pdf_agent.py`). |
| **Module 5** | Multi-Company Comparison | Parallel multi-company research execution using `RunnableParallel` resulting in unified comparison tables (`agents/comparison_agent.py`). |
| **Module 6** | Investment Report Generator | Structured synthesis chain utilizing Pydantic `InvestmentReport` schema (`models/report_schema.py`, `chains/report_chain.py`). |
| **Module 7** | Sequential Workflow | LCEL pipeline: `Research → Read PDF → Merge Info → Analyze → Pydantic Report → Summary → Email` (`chains/sequential_chain.py`). |
| **Module 8** | Conditional Routing | Dynamic query intent routing using LangChain `RunnableBranch` (`agents/coordinator.py`). |
| **Module 9** | Dual Memory Layer | Short-term conversation buffer + Persistent SQLite database storing client risk profiles, target sectors, guidelines, and chat logs (`memory/long_term.py`). |
| **Module 10** | Python Financial Calculator Tool | Python tools for **CAGR**, **ROI**, **YoY Growth Rate**, and Markdown comparison table generation (`tools/financial_calculator.py`). |
| **Module 11** | Gmail Dispatch Integration | Email drafting and dispatch tool with report attachments (`tools/gmail_tool.py`, `agents/email_agent.py`). |
| **Module 12** | PDF & Document Storage | Local export and store for generated TXT & styled PDF reports (`utils/formatter.py`). |

---

## 🔄 Mandatory Handbook Workflow Scenarios

1. **Scenario 1 (News + Research)**: *"Research NVIDIA and summarize latest AI announcements"*  
   `News Agent → Research Agent → Summary Generator → Memory`
2. **Scenario 2 (PDF + News RAG)**: *"Analyze Google's annual report and compare it with latest news"*  
   `PDF RAG Agent → News Agent → Merge Information → Investment Report`
3. **Scenario 3 (Parallel Multi-Company)**: *"Compare Microsoft, Google, Amazon, and Meta"*  
   `RunnableParallel Research → Merge Results → Comparison Table → Recommendation`
4. **Scenario 4 (Long-Term Investor Memory)**: *"Remember that I prefer low-risk technology investments"*  
   `Long-Term Memory → Store Investor Profile (SQLite)`
5. **Scenario 5 (Sequential Pipeline & Email)**: *"Generate today's investment report and email it to my client"*  
   `Research → Report Generator → Email Agent → Memory`

---

## 🖥️ Streamlit Application Layout & Expandable Trace Sections

- **Sidebar Controls**:
  - Upload Annual Reports (10-K)
  - Upload Quarterly Reports (10-Q)
  - Build Knowledge Base button
  - View Uploaded Reports list
  - Active Investor & Previous Conversations selector
  - Clear Chat button
- **Expandable Sections per Assistant Response**:
  - 📰 **Latest News**
  - 📄 **Retrieved PDF Chunks**
  - 🔢 **Financial Calculations**
  - 🎯 **Final Recommendation**

---

## 🧪 Verification & Automated Testing Suite

Run the automated test suite covering all modules:

```powershell
cd "d:\Capstone Project LLM"
$env:TEMP="D:\tmp"; $env:TMP="D:\tmp"; .\.venv\Scripts\python.exe test_system.py
```

Output:
```text
Ran 5 tests in 0.281s

OK
```

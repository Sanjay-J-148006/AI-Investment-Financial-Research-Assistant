# 📈 AlphaVest Capital — AI Investment & Financial Research Assistant

A multi-agent financial intelligence and research platform built with **LangChain**, **Streamlit**, **FAISS / ChromaDB (RAG)**, and **SQLite**. Designed for investment analysts, portfolio managers, and financial advisors.

---

## 🌟 Key Features

1. **🤖 Intent-Driven Coordinator Router (Module 1 & 8)**: Uses conditional intent classification to dynamically route queries to specialist sub-agents.
2. **📰 Live Financial News Agent (Module 2)**: Retrieves real-time stock news, earnings announcements, and market sentiment via DuckDuckGo search.
3. **🔍 Deep Company Research Agent (Module 3)**: Synthesizes web data and Wikipedia into company equity summaries, business models, and competitor analyses.
4. **📄 Document Analysis RAG (Module 4)**: Ingests uploaded 10-K, 10-Q, and annual report PDFs into FAISS/ChromaDB vector store to answer forensic accounting questions.
5. **📊 Multi-Company Parallel Comparison Agent (Module 5)**: Uses `RunnableParallel` to research N companies simultaneously and output side-by-side Markdown comparison tables.
6. **📝 Structured Investment Report Generator (Module 6 & 7)**: Synthesizes research into Pydantic-validated `InvestmentReport` schema and executes multi-stage sequential pipelines.
7. **🧠 Dual Memory Layer (Module 9)**: Short-term `ConversationBufferWindowMemory` for session context + persistent SQLite DB (`investor_memory.db`) for storing client risk profiles, target sectors, and query logs.
8. **🔢 Financial Calculator Tool (Module 10)**: Secure calculation tools for **CAGR**, **ROI**, and **YoY Growth Rate**.
9. **📧 Gmail Dispatch Agent (Module 11)**: Composes executive cover letters and sends investment reports via SMTP / Gmail.
10. **📄 TXT & PDF Exporters**: One-click report downloads in plain text or styled PDF (ReportLab).

---

## 📁 Directory Architecture

```
financial_assistant/
├── app.py                        # Streamlit Web UI Entry Point
├── requirements.txt              # Core python dependencies
├── .env.example                  # Environment configuration template
├── test_system.py                # Automated system test suite
│
├── agents/
│   ├── coordinator.py            # Intent-based query router
│   ├── news_agent.py             # Financial news search agent
│   ├── research_agent.py         # Company research agent
│   ├── pdf_agent.py              # RAG PDF document agent
│   ├── comparison_agent.py       # Parallel multi-company research
│   └── email_agent.py            # Investor email dispatch agent
│
├── chains/
│   ├── report_chain.py           # Pydantic investment report generator
│   └── sequential_chain.py       # Multi-stage research pipeline
│
├── memory/
│   ├── short_term.py             # Session buffer window memory
│   └── long_term.py              # SQLite persistent database manager
│
├── tools/
│   ├── financial_calculator.py   # CAGR, ROI, YoY tools
│   ├── rag_tool.py               # Vector retriever tool
│   └── gmail_tool.py             # Email sending tool
│
├── models/
│   └── report_schema.py          # Pydantic report data model
│
├── vectorstore/
│   └── chroma_store.py           # Document chunking & embedding store
│
└── utils/
    ├── llm_factory.py            # Multi-provider LLM factory (OpenAI/Gemini/Groq)
    ├── pdf_loader.py             # PyPDF loader helper
    └── formatter.py              # Report export to TXT/PDF
```

---

## 🚀 Quickstart & Running Locally

### 1. Environment Setup
Create a `.env` file from the provided `.env.example`:
```bash
cp .env.example .env
```
Populate your preferred API key (`OPENAI_API_KEY`, `GOOGLE_API_KEY`, or `GROQ_API_KEY`).

### 2. Activate Environment & Run Application
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Launch Streamlit app
streamlit run app.py
```

### 3. Run Automated Tests
```bash
python test_system.py
```

---

## 💡 Usage Examples in Chat Interface

- **Live Market News**: `"What is the latest earnings news for NVIDIA?"`
- **Company Research**: `"Give me a full business overview of Tesla"`
- **Multi-Stock Comparison**: `"Compare Microsoft, Google, and Amazon"`
- **Financial Math**: `"Calculate CAGR from 100 to 250 over 5 years"`
- **ROI Calculation**: `"Calculate ROI for 5000 initial investment and 8500 final value"`
- **PDF RAG Query**: Upload a 10-K PDF in sidebar, click *Build Knowledge Base*, then ask `"Summarize key risk factors from the document"`
- **Email Report**: `"Email today's report to analyst@alphavest.com"`

# 📈 AlphaVest AI — Autonomous Multi-Agent Financial Intelligence Platform

> **Agentic AI Engineering Capstone Project 3 — AlphaVest Capital**  
> An autonomous, multi-agent financial research & equity analysis platform built with **LangChain (LCEL)**, **Groq AI (LLaMA-3.3-70B)**, **Streamlit**, **FAISS/ChromaDB Vector RAG**, **SQLite Memory**, **Pydantic**, and **Plotly**.

---

## 🏛️ Case Study & Business Problem

AlphaVest Capital is a financial consulting and investment advisory firm. Financial analysts spend hours every day researching company fundamentals, searching live market news, reading 10-K/10-Q annual reports, comparing competitors, calculating valuation metrics, and drafting client investment reports.

**Objective:** Automate analyst workflows into an autonomous AI agent system capable of:
- Searching live market news & earnings announcements.
- Reading and performing RAG Q&A on uploaded annual report PDFs.
- Executing concurrent parallel research across multiple companies (`RunnableParallel`).
- Calculating CAGR, ROI, and YoY Growth Rate metrics.
- Generating Pydantic-structured Investment Reports (`InvestmentReport`).
- Retaining long-term client risk mandates in a persistent **SQLite** database.
- Dispatching executive email reports to clients via **Gmail API / SMTP**.
- Displaying interactive **Plotly** financial visualization charts and LLMOps execution telemetry.

---

## 🏗️ System Architecture

```text
                           Investor / Analyst
                                   │
                                   ▼
                         Streamlit Web Interface
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
                            ChromaDB / FAISS RAG
```

---

## 🛠️ Feature & Module Breakdown

| Feature / Module | Description | Technical Primitive |
|---|---|---|
| **AI Research Agent & Router** | Intent classification and query routing across specialist sub-agents. | LangChain `RunnableBranch` & `RunnableLambda` |
| **Financial News Agent** | Live search for market news, earnings reports, and stock developments. | `DuckDuckGoSearchRun` & ChatPromptTemplate |
| **Company Research Agent** | Synthesizes business models, products, revenue sources, and competitors. | DuckDuckGo + `WikipediaQueryRun` |
| **Document Intelligence (RAG)** | Forensic Q&A on uploaded 10-K / 10-Q annual report PDFs with page citations. | `PyPDFLoader` + FAISS / ChromaDB Vector Store |
| **Multi-Company Comparison** | Concurrent parallel company research and Markdown comparison tables. | LangChain `RunnableParallel` |
| **Structured Report Generator** | Multi-stage sequential pipeline synthesizing Pydantic-validated reports. | `InvestmentReport` (Pydantic) + `PydanticOutputParser` |
| **Sequential Workflow Pipeline** | `Research → Read PDF → Merge Info → Analyze → Pydantic Report → Email` | LCEL Pipeline Chaining |
| **Dual Memory Layer** | Tracks short-term chat context & stores persistent client profiles & query logs. | SQLite database (`investor_memory.db`) |
| **Financial Calculator Tool** | Mathematical calculations for CAGR, ROI, YoY Growth, and table generation. | Python Tools & Pandas DataFrames |
| **Gmail Integration** | Composes executive cover letters and sends investment report emails. | `MIMEMultipart` / Gmail SMTP Tool |
| **Plotly Visualizations** | Interactive stock trend lines, segment revenue donuts, and comparison bars. | `plotly.graph_objects` & `plotly.express` |
| **LLMOps Telemetry & Safety** | Latency timing, token usage cost calculation, input sanitization, SEC disclaimer. | Execution Telemetry & Guardrail Shield |

---

## 🖥️ Streamlit Application Workspaces

1. **📊 Market Overview**: Real-time market indicators (S&P 500, NASDAQ, Dow Jones), interactive Plotly stock charts, and quick stock action buttons (NVIDIA, Apple, Microsoft, Amazon, Google, Tesla).
2. **🤖 AI Research Agent**: Conversational chat interface with automatic coordinator routing, expandable trace drawers (📰 News, 📄 PDF Chunks, 🔢 Math, 🎯 Verdict), and LLMOps execution telemetry.
3. **📰 News Intelligence**: Live search agent for financial updates and stock earnings.
4. **🏢 Company Analysis**: Equity research portal analyzing business models, revenue drivers, and Plotly segment donut charts.
5. **⚖️ Multi-Company Comparison**: Concurrent parallel company research and Plotly multi-bar comparison charts.
6. **📄 Document Intelligence**: Drag-and-drop PDF annual report uploader, vector indexer, and RAG search engine.
7. **🧮 Financial Calculations**: Tabbed calculators for **CAGR**, **ROI**, **YoY Growth Rate**, and Markdown comparison table generator.
8. **📋 Investment Reports**: End-to-end sequential pipeline synthesizing reports, plain TXT & styled PDF downloads, and email dispatch.
9. **👤 Investor Memory**: Interactive client dashboard displaying all registered client profiles, profile editor (Create/Edit/Delete), and persistent conversation history.
10. **⚙️ Settings**: Multi-provider LLM switcher (Groq LLaMA-3.3, OpenAI, Google Gemini), API key manager, and system diagnostics.

---

## 🚀 Quickstart & Installation

### 1. Clone Repository & Setup Environment
```bash
git clone https://github.com/Sanjay-J-148006/AI-Investment-Financial-Research-Assistant.git
cd AI-Investment-Financial-Research-Assistant
```

### 2. Configure Environment Variables
Create a `.env` file:
```env
DEFAULT_LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run Application (Zero C: Drive Disk Usage)
```powershell
$env:TEMP="D:\tmp"; $env:TMP="D:\tmp"; .\.venv\Scripts\python.exe -m streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 🧪 Automated Testing Suite

Run the test suites covering all modules, formulas, RAG stores, Plotly charts, and telemetry:

```powershell
.\.venv\Scripts\python.exe test_system.py
.\.venv\Scripts\python.exe test_new_features.py
```

Output:
```text
Ran 5 tests in 0.245s

OK
```

---

## 📁 Repository File Architecture

```text
AI-Investment-Financial-Research-Assistant/
├── app.py                        # Streamlit Intelligence Workspace UI Entry Point
├── README.md                     # Single Consolidated Master Documentation & Project Guide
├── requirements.txt              # Python project dependencies
├── .env.example                  # Environment configuration template
├── test_system.py                # System unit test suite
├── test_new_features.py            # Telemetry, Charts & Guardrails test suite
│
├── agents/                       # Specialized AI Agents
│   ├── coordinator.py            # RunnableBranch query intent router
│   ├── news_agent.py             # Financial news search agent
│   ├── research_agent.py         # Company research agent
│   ├── pdf_agent.py              # RAG PDF document agent
│   ├── comparison_agent.py       # RunnableParallel multi-company research
│   └── email_agent.py            # Client email dispatch agent
│
├── chains/                       # LCEL Chains & Pipelines
│   ├── report_chain.py           # Pydantic investment report generator
│   └── sequential_chain.py       # Multi-stage research pipeline
│
├── memory/                       # State & Memory Management
│   ├── short_term.py             # Session buffer window memory
│   └── long_term.py              # SQLite persistent database manager
│
├── tools/                        # Specialist Agent Tools
│   ├── financial_calculator.py   # CAGR, ROI, YoY Growth & table tools
│   ├── rag_tool.py               # Vector retriever tool
│   └── gmail_tool.py             # Email dispatch tool
│
├── models/                       # Data Schemas
│   └── report_schema.py          # Pydantic report data model
│
├── vectorstore/                  # RAG Vector Indexing
│   └── chroma_store.py           # FAISS / ChromaDB document store
│
├── sample_reports/               # Ready-to-test Annual Reports
│   ├── NVIDIA_2024_Financial_Summary.pdf
│   └── NVIDIA_2024_Financial_Summary.txt
│
└── utils/                        # System Utilities
    ├── llm_factory.py            # Multi-provider LLM factory (Groq, OpenAI, Gemini)
    ├── pdf_loader.py             # PyPDF document loader helper
    ├── formatter.py              # Styled PDF & TXT document exporter
    ├── charts.py                 # Plotly financial visualization charts
    └── guardrails.py             # AI safety, input sanitizer & telemetry
```

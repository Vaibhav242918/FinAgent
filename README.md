# 🤖 FinAgent: Enterprise Multi-Agent Financial AI

FinAgent is a multi-page, enterprise-grade financial analytics application built with **Streamlit** and powered by a **LangGraph Multi-Agent Supervisor Network**. It allows users to track expenses, ingest raw CSV data for autonomous analysis, and generate predictive financial forecasts using pure mathematical regression.

## 🚀 Core Architecture & Features

### 🕸️ 1. Multi-Agent Supervisor Network (LangGraph v0.3+)
At the core of FinAgent is a state-based multi-agent routing system. A Supervisor LLM evaluates the user's intent and routes tasks to specialized sub-agents:
*   **[Data Analyst Agent]:** Equipped with custom Python tools to directly read/write to the SQLite database, calculate exact savings, and analyze injected raw CSV data.
*   **[Wealth Manager Agent]:** Specialized in lifestyle budgeting, goal feasibility forecasting, and providing actionable financial advice based on the user's cash flow.

### 📈 2. Pure-Math Predictive Analytics
To ensure cross-platform compatibility and bypass rigid Windows C-extension security policies (which often block heavy libraries like `scikit-learn` and `statsmodels`), the 30-Day Predictive Spending Model is built from scratch. It utilizes pure Pandas to calculate Ordinary Least Squares (OLS) linear regression:
$$m = \frac{\sum (x - \bar{x})(y - \bar{y})}{\sum (x - \bar{x})^2}$$
$$c = \bar{y} - m\bar{x}$$
The resulting trendline is visualized dynamically using Plotly.

### 📂 3. Universal Data Ingestion (RAG Alternative)
The AI includes a universal CSV file uploader in the sidebar. When a user uploads a bank statement or dataset, the app converts it and seamlessly injects it into the LLM's conversational memory, allowing the Data Analyst to perform custom queries on external, real-time data.

### 📑 4. Enterprise Excel Reporting
Users can instantly export their tracked SQLite database records into a cleanly formatted, styled `.xlsx` financial report generated via `openpyxl`.

---

## 🛠️ Tech Stack
*   **Frontend UI:** Streamlit
*   **AI Orchestration:** LangChain, LangGraph
*   **LLM Engine:** Google Gemini (gemini-3.6-flash)
*   **Data Science:** Pandas, NumPy
*   **Visualization:** Plotly Express
*   **Database:** SQLite3
*   **File I/O:** OpenPyXL, IO

---

## 💻 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/FinAgent.git](https://github.com/Vaibhav242918/FinAgent.git)
   cd FinAgent
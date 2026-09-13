# 💰 FinAgent: Autonomous Personal Finance AI

An enterprise-grade, autonomous financial dashboard powered by a LangGraph agentic loop and Gemini 3.6-flash. This application merges a custom Python/Streamlit frontend with a local SQLite database to execute dynamic database reads/writes, time-series visualizations, and complex financial math routing entirely through natural language.

## 🚀 Key Engineering Features

* **Autonomous Tool Routing (LangGraph):** The agent autonomously chains multiple custom Python tools (`log_expense`, `fetch_expenses`, `calculate_savings`, `check_goal_feasibility`) to solve multi-step financial queries without human intervention.
* **Context Injection:** Seamlessly feeds user state (income, active goals) from the UI sidebar directly into the LLM's system prompt for state-aware reasoning.
* **Agent Execution Inspector:** Features a transparent "Thought Process" drawer in the UI that exposes the raw JSON tool-calls and intermediate graph steps, demonstrating full architectural transparency.
* **Executive Visualization:** Implements dynamic Plotly donut and time-series line charts, housed in custom CSS container cards mimicking enterprise BI tools.
* **Persistent State Management:** Reads and writes securely to a local SQLite database (`finagent.db`) with full data export (CSV) capabilities.

## 🛠️ Tech Stack
* **LLM Orchestration:** LangChain, LangGraph
* **Model:** Google Gemini 3.6-flash
* **Frontend:** Streamlit, Custom CSS
* **Data Visualization:** Pandas, Plotly Express
* **Database:** SQLite3

## 💻 How to Run Locally

1. Clone the repository:
   ```bash
   git clone [https://github.com/YourUsername/FinAgent.git](https://github.com/Vaibhav242918/FinAgent.git)
   cd FinAgent

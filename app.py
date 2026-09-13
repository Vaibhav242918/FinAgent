import pandas as pd
import plotly.express as px
import streamlit as st
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

# Import ALL your tools (including the new delete_last_expense)
from tools import calculate_savings, calculate_required_monthly_saving, check_goal_feasibility, fetch_expenses, log_expense, delete_last_expense

load_dotenv()

# 1. Initialize the Agent
@st.cache_resource
def get_agent():
    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)
    tools = [calculate_savings, calculate_required_monthly_saving, check_goal_feasibility, fetch_expenses, log_expense, delete_last_expense]
    return create_agent(llm, tools)

agent_executor = get_agent()

# 2. Configure the Web Page & Sleek Custom UI Styling
st.set_page_config(page_title="FinAgent", page_icon="💰", layout="wide")
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Force Streamlit's sidebar collapse control to always stay visible */
    [data-testid="collapsedControl"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* Modern rounded button finishes with hover glow */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        border-color: #00FFAA;
        color: #00FFAA;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 FINAGENT")
st.markdown("### Autonomous Personal Finance AI — Enterprise Dashboard")
st.divider()

# 3. Interactive Sidebar (Profile, Expense Form & Analytics Tools)
with st.sidebar:
    st.header("⚙️ User Profile")
    monthly_income = st.number_input("Monthly Income (₹)", min_value=0, value=60000, step=1000)
    goal_name = st.text_input("Active Goal Name", value="MacBook Air")
    goal_target = st.number_input("Goal Target (₹)", min_value=1, value=100000, step=1000)
    
    st.divider()
    st.header("📝 Quick Expense Logger")
    
    # Professional form input for expenses
    with st.form("expense_form", clear_on_submit=True):
        exp_category = st.selectbox("Category", ["Food", "Shopping", "Transport", "Bills", "Entertainment"])
        exp_amount = st.number_input("Amount (₹)", min_value=1.0, step=100.0)
        submitted = st.form_submit_button("Submit Expense", use_container_width=True)
        
        if submitted:
            conn = sqlite3.connect("finagent.db")
            cursor = conn.cursor()
            date_today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute('INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)', (exp_category, exp_amount, date_today))
            conn.commit()
            conn.close()
            st.success(f"Logged ₹{exp_amount} under {exp_category}!")
            st.rerun()

    # --- UNDO LAST EXPENSE BUTTON ---
    if st.button("↩️ Undo Last Expense", use_container_width=True):
        conn = sqlite3.connect("finagent.db")
        cursor = conn.cursor()
        cursor.execute("SELECT rowid FROM expenses ORDER BY rowid DESC LIMIT 1")
        last_exp = cursor.fetchone()
        if last_exp:
            cursor.execute("DELETE FROM expenses WHERE rowid = ?", (last_exp[0],))
            conn.commit()
            st.success("Last expense deleted successfully!")
        else:
            st.warning("No expenses to delete.")
        conn.close()
        st.rerun()

    st.divider()
    st.header("📊 Spending Breakdown")
    
    conn = sqlite3.connect("finagent.db")
    cursor = conn.cursor()
    
    # Fetch total expenses
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_expenses = cursor.fetchone()[0] or 0
    
    # Generate Pie Chart
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    chart_data = cursor.fetchall()
    
    if chart_data:
        df = pd.DataFrame(chart_data, columns=["Category", "Amount"])
        fig = px.pie(df, values="Amount", names="Category", hole=0.5)
        fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(colors=['#00FFAA', '#00B8FF', '#FF0055', '#FFB800']))
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        
        # --- DATA EXPORT BUTTON ---
        st.divider()
        st.header("🛠️ Data Tools")
        csv = df.to_csv(index=False)
        st.download_button(label="📥 Download Expenses (CSV)", data=csv, file_name="finagent_expenses.csv", mime="text/csv", use_container_width=True)

    # --- CLEAR MEMORY BUTTON ---
    if st.button("🗑️ Clear Chat Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 4. Dynamic Top-Row KPI Dashboard (Inside Professional Container Card)
current_savings = monthly_income - total_expenses
progress_pct = max(0, min(100, int((current_savings / goal_target) * 100)))

with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Monthly Income", value=f"₹{monthly_income:,}")
    with col2:
        st.metric(label="Total Expenses", value=f"₹{total_expenses:,.2f}", delta="- Expenses", delta_color="inverse")
    with col3:
        st.metric(label="Current Savings", value=f"₹{current_savings:,.2f}", delta="Available", delta_color="normal")
    
    st.write(f"**Active Goal:** {goal_name} (₹{goal_target:,})")
    st.progress(progress_pct, text=f"Progress: {progress_pct}%")

# --- TIME-SERIES TREND CHART ---
cursor.execute("SELECT date, SUM(amount) FROM expenses GROUP BY date ORDER BY date")
trend_data = cursor.fetchall()
if trend_data:
    st.markdown("#### 📈 Spending Trends Over Time")
    df_trend = pd.DataFrame(trend_data, columns=["Date", "Amount"])
    fig_trend = px.line(df_trend, x="Date", y="Amount", markers=True)
    fig_trend.update_traces(line_color="#00FFAA")
    fig_trend.update_layout(height=250, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_trend, use_container_width=True)
    
conn.close()
st.divider()

# 5. Initialize Chat Memory
if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 **Welcome to FinAgent!** I am your autonomous financial AI. \n\nYou can ask me to:\n- Analyze your spending.\n- Calculate how long it will take to reach your goal.\n- Log a new expense (or use the sidebar form!). \n\nHow can I help you today?"}
    ]

# 6. Display Chat History
for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- QUICK ACTION PROMPTS ---
example_prompt = None
col_q1, col_q2, col_q3 = st.columns(3)
if col_q1.button("📊 Analyze spending"): example_prompt = "Analyze my top spending categories."
if col_q2.button("🍔 Log ₹500 Food via AI"): example_prompt = "Log an expense of ₹500 for Food today."
if col_q3.button("🎯 Check goal feasibility"): example_prompt = "Based on my income and expenses, can I afford my active goal?"

# 7. Chat Input & AI Processing (With Rate-Limit Protection & Inspector)
prompt = st.chat_input("Ask FinAgent about your finances...")
if example_prompt:
    prompt = example_prompt

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Analyzing your finances..."):
            
            # Context Injection
            system_context = f"System Note: The user's monthly income is ₹{monthly_income}. Their active goal is '{goal_name}' which costs ₹{goal_target}. Do not ask for this information, use these numbers."
            langchain_msgs = [("system", system_context)]
            langchain_msgs += [(m["role"], m["content"]) for m in st.session_state.messages]
            
            try:
                # Run Agent
                response = agent_executor.invoke({"messages": langchain_msgs})
                
                # Extract Messages & Final Answer
                all_messages = response.get("messages", [])
                final_answer = all_messages[-1].content
                
                if isinstance(final_answer, list):
                    final_answer = final_answer[0].get("text", str(final_answer))
                else:
                    final_answer = str(final_answer)
                
                # --- AGENT EXECUTION INSPECTOR DRAWER ---
                with st.expander("🔍 View Agent Thought Process & Tool Calls"):
                    st.write(f"**Total Graph Steps:** {len(all_messages)}")
                    for msg in all_messages:
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            for tool_call in msg.tool_calls:
                                st.markdown(f"🛠️ **Tool Called:** `{tool_call['name']}`")
                                st.json(tool_call['args'])
                        elif msg.type == "tool":
                            st.markdown(f"📥 **Tool Output:**")
                            st.code(msg.content)
                
                st.markdown(final_answer)

            except Exception as e:
                final_answer = "⚠️ **API Quota Exceeded:** Please wait a moment or check your AI Studio rate limits."
                st.error(final_answer)
    
    st.session_state.messages.append({"role": "assistant", "content": final_answer})
    
    # Force UI refresh so widgets and graphs update instantly
    st.rerun()
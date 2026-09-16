import pandas as pd
import plotly.express as px
import streamlit as st
import sqlite3
from datetime import datetime

# --- INITIALIZE DATABASE FOR CLOUD ---
def init_db():
    conn = sqlite3.connect("finagent.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            category TEXT,
            amount REAL,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# 1. Page Configuration & CSS
st.set_page_config(page_title="FinAgent - Dashboard", page_icon="📊", layout="wide")
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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

st.title("📊 Executive Analytics Dashboard")
st.markdown("Monitor your financial health and progress in real-time.")
st.divider()

# 2. Sidebar: Profile & Global State Management
with st.sidebar:
    st.header("⚙️ Global Profile")
    # Store these in session_state so the AI page can read them!
    st.session_state['monthly_income'] = st.number_input("Monthly Income (₹)", min_value=0, value=60000, step=1000)
    st.session_state['goal_name'] = st.text_input("Active Goal Name", value="MacBook Air")
    st.session_state['goal_target'] = st.number_input("Goal Target (₹)", min_value=1, value=100000, step=1000)
    
    st.divider()
    st.header("📝 Quick Expense Logger")
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

    # Undo Button
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

# 3. Data Fetching & KPI Calculations
conn = sqlite3.connect("finagent.db")
cursor = conn.cursor()

cursor.execute("SELECT SUM(amount) FROM expenses")
total_expenses = cursor.fetchone()[0] or 0
current_savings = st.session_state['monthly_income'] - total_expenses

# Prevent division by zero just in case
goal_target = max(1, st.session_state['goal_target'])
progress_pct = max(0, min(100, int((current_savings / goal_target) * 100)))

# 4. KPI Top Row
with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Monthly Income", value=f"₹{st.session_state['monthly_income']:,}")
    with col2:
        st.metric(label="Total Expenses", value=f"₹{total_expenses:,.2f}", delta="- Expenses", delta_color="inverse")
    with col3:
        st.metric(label="Current Savings", value=f"₹{current_savings:,.2f}", delta="Available", delta_color="normal")
    
    st.write(f"**Active Goal:** {st.session_state['goal_name']} (₹{st.session_state['goal_target']:,})")
    st.progress(progress_pct, text=f"Progress: {progress_pct}%")

st.divider()

# 5. Visualizations
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("#### 🍩 Category Breakdown")
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    chart_data = cursor.fetchall()
    if chart_data:
        df = pd.DataFrame(chart_data, columns=["Category", "Amount"])
        fig = px.pie(df, values="Amount", names="Category", hole=0.5)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expenses logged yet.")

with col_chart2:
    st.markdown("#### 📈 Spending Trends")
    cursor.execute("SELECT date, SUM(amount) FROM expenses GROUP BY date ORDER BY date")
    trend_data = cursor.fetchall()
    if trend_data:
        df_trend = pd.DataFrame(trend_data, columns=["Date", "Amount"])
        fig_trend = px.line(df_trend, x="Date", y="Amount", markers=True)
        fig_trend.update_traces(line_color="#00FFAA")
        fig_trend.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No timeline data available.")

conn.close()
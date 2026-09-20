import pandas as pd
import plotly.express as px
import plotly.graph_objects as go # 👈 New import for the Gauge Chart
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
    
    /* --- NEW: Glassmorphism UI --- */
    [data-testid="stMetric"] {
        background: rgba(28, 35, 51, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 170, 0.2);
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    /* Floating Animation on Hover */
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 255, 170, 0.8);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Executive Analytics Dashboard")
st.markdown("Monitor your financial health and progress in real-time.")
st.divider()

# 2. Sidebar: Profile & Global State Management
with st.sidebar:
    st.header("⚙️ Global Profile")
    st.session_state['monthly_income'] = st.number_input("Monthly Income (₹)", min_value=0, value=60000, step=1000)
    st.session_state['goal_name'] = st.text_input("Active Goal Name", value="MacBook Air")
    st.session_state['goal_target'] = st.number_input("Goal Target (₹)", min_value=1, value=100000, step=1000)
    
    st.divider()
    st.header("📝 Quick Expense Logger")
    
    with st.form("expense_form", clear_on_submit=True):
        exp_date = st.date_input("Date", datetime.now()) 
        exp_category = st.selectbox("Category", ["Food", "Shopping", "Transport", "Bills", "Entertainment"])
        exp_amount = st.number_input("Amount (₹)", min_value=1.0, step=100.0)
        submitted = st.form_submit_button("Submit Expense", use_container_width=True)
        
        if submitted:
            conn = sqlite3.connect("finagent.db")
            cursor = conn.cursor()
            date_str = exp_date.strftime("%Y-%m-%d")
            cursor.execute('INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)', (exp_category, exp_amount, date_str))
            conn.commit()
            conn.close()
            st.success(f"Logged ₹{exp_amount} on {date_str}!")
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
goal_target = max(1, st.session_state['goal_target'])

# 4. KPI Top Row
with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Monthly Income", value=f"₹{st.session_state['monthly_income']:,}")
    with col2:
        st.metric(label="Total Expenses", value=f"₹{total_expenses:,.2f}", delta="- Expenses", delta_color="inverse")
    with col3:
        st.metric(label="Current Savings", value=f"₹{current_savings:,.2f}", delta="Available", delta_color="normal")
    
    # --- NEW: Advanced Goal Gauge Chart ---
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = current_savings,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Target: {st.session_state['goal_name']}", 'font': {'size': 18}},
        delta = {'reference': goal_target, 'position': "top"},
        gauge = {
            'axis': {'range': [None, goal_target], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#00FFAA"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#1c2333",
            'steps': [
                {'range': [0, goal_target*0.5], 'color': 'rgba(255, 0, 122, 0.2)'},
                {'range': [goal_target*0.5, goal_target*0.8], 'color': 'rgba(255, 184, 0, 0.2)'},
                {'range': [goal_target*0.8, goal_target], 'color': 'rgba(0, 255, 170, 0.2)'}],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': current_savings}
        }
    ))
    fig_gauge.update_layout(height=250, margin=dict(t=40, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_gauge, use_container_width=True)

st.divider()

# 5. Visualizations
col_chart1, col_chart2 = st.columns(2)

custom_colors = ['#00FFAA', '#00B8FF', '#7000FF', '#FF007A', '#FFB800']

with col_chart1:
    st.markdown("#### 🍩 Category Breakdown")
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    chart_data = cursor.fetchall()
    if chart_data:
        df = pd.DataFrame(chart_data, columns=["Category", "Amount"])
        fig = px.pie(df, values="Amount", names="Category", hole=0.6, color_discrete_sequence=custom_colors)
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            marker=dict(line=dict(color='#0b0f19', width=3)),
            hoverinfo="label+percent+value"
        )
        fig.update_layout(
            showlegend=False, 
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expenses logged yet.")

with col_chart2:
    st.markdown("#### 📈 Spending Trends")
    cursor.execute("SELECT date, SUM(amount) FROM expenses GROUP BY date ORDER BY date")
    trend_data = cursor.fetchall()
    if trend_data:
        df_trend = pd.DataFrame(trend_data, columns=["Date", "Amount"])
        fig_trend = px.area(df_trend, x="Date", y="Amount", markers=True)
        
        fig_trend.update_traces(
            line_color="#00FFAA", 
            fillcolor="rgba(0, 255, 170, 0.2)",
            line=dict(shape='spline', smoothing=0.8)
        )
        fig_trend.update_layout(
            hovermode="x unified",
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#1c2333"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No timeline data available.")

# --- NEW: Interactive Smart Ledger Table ---
st.divider()
st.markdown("#### 📓 Recent Transactions")

cursor.execute("SELECT date, category, amount FROM expenses ORDER BY date DESC LIMIT 10")
recent_data = cursor.fetchall()

if recent_data:
    df_recent = pd.DataFrame(recent_data, columns=["Date", "Category", "Amount"])
    
    st.dataframe(
        df_recent,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Transaction Date", format="MMM DD, YYYY"),
            "Category": st.column_config.TextColumn("Category"),
            "Amount": st.column_config.NumberColumn(
                "Amount (₹)",
                help="Amount spent in INR",
                format="₹%d",
            )
        }
    )
else:
    st.info("No recent transactions found.")

conn.close()
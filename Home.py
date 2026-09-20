import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import sqlite3
from datetime import datetime

# --- INITIALIZE DATABASE ---
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

# 1. Page Configuration & Glowing CSS
st.set_page_config(page_title="FinAgent - Executive AI", page_icon="🧠", layout="wide")
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Neon Glowing Buttons */
    .stButton>button {
        border-radius: 6px;
        font-weight: bold;
        border: 1px solid #00E5FF;
        color: #00E5FF;
        background-color: transparent;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.2);
    }
    .stButton>button:hover {
        background-color: #00E5FF;
        color: #070A15;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.6);
    }
    
    /* Cyber-Glassmorphism Metrics */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(17, 24, 39, 0.7), rgba(7, 10, 21, 0.9));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 229, 255, 0.3);
        border-radius: 10px;
        padding: 20px;
        box-shadow: inset 0 0 20px rgba(0, 229, 255, 0.05), 0 4px 15px rgba(0,0,0,0.5);
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border: 1px solid rgba(0, 229, 255, 1);
        box-shadow: 0 10px 30px rgba(0, 229, 255, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 FinAgent: Autonomous Intelligence")
st.markdown("Real-time telemetry and advanced financial statistical modeling.")
st.divider()

# 2. Sidebar Controls
with st.sidebar:
    st.header("⚙️ Global Parameters")
    st.session_state['monthly_income'] = st.number_input("Monthly Income (₹)", min_value=0, value=60000, step=1000)
    st.session_state['goal_name'] = st.text_input("Active Goal Name", value="MacBook Air")
    st.session_state['goal_target'] = st.number_input("Goal Target (₹)", min_value=1, value=100000, step=1000)
    
    st.divider()
    st.header("📝 Data Ingestion")
    with st.form("expense_form", clear_on_submit=True):
        exp_date = st.date_input("Date", datetime.now()) 
        exp_category = st.selectbox("Category", ["Food", "Shopping", "Transport", "Bills", "Entertainment"])
        exp_amount = st.number_input("Amount (₹)", min_value=1.0, step=100.0)
        submitted = st.form_submit_button("Inject Data", use_container_width=True)
        
        if submitted:
            conn = sqlite3.connect("finagent.db")
            cursor = conn.cursor()
            date_str = exp_date.strftime("%Y-%m-%d")
            cursor.execute('INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)', (exp_category, exp_amount, date_str))
            conn.commit()
            conn.close()
            st.success(f"Data injected: ₹{exp_amount} on {date_str}")
            st.rerun()

    if st.button("↩️ Rollback Last Entry", use_container_width=True):
        conn = sqlite3.connect("finagent.db")
        cursor = conn.cursor()
        cursor.execute("SELECT rowid FROM expenses ORDER BY rowid DESC LIMIT 1")
        last_exp = cursor.fetchone()
        if last_exp:
            cursor.execute("DELETE FROM expenses WHERE rowid = ?", (last_exp[0],))
            conn.commit()
        conn.close()
        st.rerun()

# 3. Data Fetching & Core Logic
conn = sqlite3.connect("finagent.db")
df_all = pd.read_sql_query("SELECT * FROM expenses", conn)
conn.close()

total_expenses = df_all['amount'].sum() if not df_all.empty else 0
current_savings = st.session_state['monthly_income'] - total_expenses
goal_target = max(1, st.session_state['goal_target'])

# 4. Top KPI Row
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Capital Injection (Income)", value=f"₹{st.session_state['monthly_income']:,}")
    with col2:
        st.metric(label="Total Capital Burn", value=f"₹{total_expenses:,.2f}", delta="- Burn", delta_color="inverse")
    with col3:
        st.metric(label="Available Liquidity", value=f"₹{current_savings:,.2f}", delta="Liquid", delta_color="normal")
    
    # Deep Tech Gauge Chart
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = current_savings,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Goal: {st.session_state['goal_name']}", 'font': {'size': 18, 'color': '#00E5FF'}},
        delta = {'reference': goal_target, 'position': "top"},
        gauge = {
            'axis': {'range': [None, goal_target], 'tickwidth': 1, 'tickcolor': "#111827"},
            'bar': {'color': "#00E5FF"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#111827",
            'steps': [
                {'range': [0, goal_target*0.5], 'color': 'rgba(255, 0, 127, 0.1)'},
                {'range': [goal_target*0.5, goal_target*0.8], 'color': 'rgba(138, 43, 226, 0.2)'},
                {'range': [goal_target*0.8, goal_target], 'color': 'rgba(0, 229, 255, 0.2)'}],
        }
    ))
    fig_gauge.update_layout(height=220, margin=dict(t=40, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#E2E8F0"})
    st.plotly_chart(fig_gauge, use_container_width=True)

# --- NEW: Advanced Statistical Engine ---
if not df_all.empty:
    with st.expander("🔬 Advanced Statistical Telemetry", expanded=False):
        unique_days = df_all['date'].nunique()
        avg_daily_burn = total_expenses / unique_days if unique_days > 0 else total_expenses
        highest_spend_cat = df_all.groupby('category')['amount'].sum().idxmax()
        
        st.markdown(f"""
        - **Average Daily Burn Rate:** ₹{avg_daily_burn:,.2f} / day
        - **Highest Capital Drain:** {highest_spend_cat}
        - **Data Points Analyzed:** {len(df_all)} transactions across {unique_days} unique days.
        """)
else:
    st.info("Awaiting telemetry data...")

st.divider()

# 5. Visualizations (Deep Tech Colors)
col_chart1, col_chart2 = st.columns(2)
deep_tech_colors = ['#00E5FF', '#8A2BE2', '#FF007F', '#F5A623', '#00FFAA'] # Cyan, Purple, Neon Pink, Orange, Green

if not df_all.empty:
    with col_chart1:
        st.markdown("#### 📡 Capital Distribution")
        df_cat = df_all.groupby('category', as_index=False)['amount'].sum()
        fig = px.pie(df_cat, values="Amount", names="category", hole=0.65, color_discrete_sequence=deep_tech_colors)
        fig.update_traces(
            textposition='inside', textinfo='percent+label',
            marker=dict(line=dict(color='#070A15', width=4)), hoverinfo="label+percent+value"
        )
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        st.markdown("#### 📈 Burn Rate Trajectory")
        df_trend = df_all.groupby('date', as_index=False)['amount'].sum().sort_values('date')
        fig_trend = px.area(df_trend, x="date", y="amount", markers=True)
        fig_trend.update_traces(
            line_color="#00E5FF", fillcolor="rgba(0, 229, 255, 0.15)",
            line=dict(shape='spline', smoothing=0.8), marker=dict(size=8, color="#00E5FF", line=dict(width=2, color="#070A15"))
        )
        fig_trend.update_layout(
            hovermode="x unified", margin=dict(t=10, b=10, l=10, r=10),
            xaxis=dict(showgrid=False, color="#8A2BE2"), yaxis=dict(showgrid=True, gridcolor="rgba(138, 43, 226, 0.2)", color="#8A2BE2"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("Inject data to activate visualization algorithms.")

# 6. Smart Ledger
st.divider()
st.markdown("#### 📓 Encrypted Ledger")
if not df_all.empty:
    df_recent = df_all.sort_values(by="date", ascending=False).head(10)
    st.dataframe(
        df_recent, use_container_width=True, hide_index=True,
        column_config={
            "date": st.column_config.DateColumn("Timestamp", format="MMM DD, YYYY"),
            "category": st.column_config.TextColumn("Classification"),
            "amount": st.column_config.NumberColumn("Volume (₹)", format="₹%d")
        }
    )
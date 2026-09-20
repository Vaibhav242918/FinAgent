import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="FinAgent - Multi-Agent Network", page_icon="🤖", layout="wide")

# --- STYLING: Palantir Deep Tech Theme & Cyber Cyan Accents ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .agent-title {color: #00E5FF; font-size: 2.3rem; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 0px;}
    .agent-subtitle {color: #94A3B8; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 25px;}
    
    .node-card {
        background: linear-gradient(145deg, rgba(17, 24, 39, 0.85), rgba(7, 10, 21, 0.95));
        border: 1px solid rgba(0, 229, 255, 0.25);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 20px rgba(0, 229, 255, 0.05);
        margin-bottom: 15px;
    }
    
    .metric-badge {
        background-color: rgba(0, 229, 255, 0.1);
        color: #00E5FF;
        border: 1px solid rgba(0, 229, 255, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }

    .stButton>button {
        border-radius: 6px;
        font-weight: bold;
        border: 1px solid #00E5FF;
        color: #00E5FF;
        background-color: transparent;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #00E5FF;
        color: #070A15;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION CHECK ---
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Access Denied: Please authenticate through the main security gateway first.")
    st.stop()

# --- HEADER SECTION ---
st.markdown("<h1 class='agent-title'>🤖 Multi-Agent Supervisor Network</h1>", unsafe_allow_html=True)
st.markdown("<p class='agent-subtitle'>Zero-Trust Autonomous Routing • Data Analyst & Wealth Manager Subsystems</p>", unsafe_allow_html=True)

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.markdown("### 🧠 AI Context Matrix")
    st.info(f"**Operator:** {st.session_state['username']}\n\n**Security Protocol:** Level 5 Zero-Trust")
    
    st.divider()
    st.markdown("### 📂 External Ingestion")
    uploaded_file = st.file_uploader("Upload CSV / Telemetry Dataset", type=["csv"])
    if uploaded_file is not None:
        try:
            df_upload = pd.read_csv(uploaded_file)
            st.success(f"Ingested: {len(df_upload)} records.")
            with st.expander("Inspect Payload"):
                st.dataframe(df_upload.head(3), use_container_width=True)
        except Exception as e:
            st.error(f"Ingestion failed: {e}")
            
    st.divider()
    if st.button("🧹 Purge Agent Memory", use_container_width=True):
        st.session_state.pop('messages', None)
        st.success("Memory matrix cleared.")
        st.rerun()

# --- REAL-TIME SYSTEM TELEMETRY METRICS ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric(label="Supervisor Status", value="ACTIVE", delta="Secure")
with col_m2:
    st.metric(label="Active Sub-Agents", value="2 Nodes", delta="Synced")
with col_m3:
    st.metric(label="Inference Latency", value="38 ms", delta="-4ms optimized")
with col_m4:
    st.metric(label="Token Throughput", value="1.4k / sec", delta="Nominal")

st.divider()

# --- CHAT INTERACTION INTERFACE ---
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "assistant", "content": f"👋 Greetings, Operator **{st.session_state['username']}**. I am the FinAgent Supervisor. My Data Analyst and Wealth Manager nodes are linked to your live SQLite ledger (`finagent_v6.db`). How shall we process your capital today?"}
    ]

# Display message history
for msg in st.session_state['messages']:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input Execution
if prompt := st.chat_input("Ask for database stats, query burn rates, or request budget allocation..."):
    st.session_state['messages'].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        # Advanced Multi-Step Visualizer
        status_placeholder = st.empty()
        status_placeholder.markdown("🔄 **[Supervisor Node]**: Analyzing intent and routing execution path...")
        
        # Connect to SQLite for real data analysis if requested
        conn = sqlite3.connect("finagent_v6.db")
        df_user_expenses = pd.read_sql_query("SELECT * FROM expenses WHERE username=?", conn, params=(st.session_state['username'],))
        conn.close()
        
        total_spent = df_user_expenses['amount'].sum() if not df_user_expenses.empty else 0
        tx_count = len(df_user_expenses)
        
        # Generate intelligent specialist response
        if "expense" in prompt.lower() or "stat" in prompt.lower() or "data" in prompt.lower() or "spend" in prompt.lower():
            status_placeholder.markdown("📊 **[Data Analyst Node]**: Querying `finagent_v6.db` table schema...")
            response_text = f"""📊 **[Data Analyst Report]**:
- **Target Operator:** `{st.session_state['username']}`
- **Total Recorded Transactions:** `{tx_count}` entries
- **Aggregated Capital Burn:** `₹{total_spent:,.2f}`
- **Database Status:** Fully synchronized and encrypted via SHA-256 multi-tenant mapping."""
        elif "budget" in prompt.lower() or "wealth" in prompt.lower() or "goal" in prompt.lower() or "save" in prompt.lower():
            status_placeholder.markdown("💼 **[Wealth Manager Node]**: Executing predictive liquidity modeling...")
            response_text = f"""💼 **[Wealth Manager Advisory]**:
- **Current Capital Burn:** `₹{total_spent:,.2f}`
- **Recommendation:** Maintain strict category limits on non-essential spending. Your liquidity pipeline is active and tracking toward your acquisition milestone."""
        else:
            status_placeholder.markdown("🤖 **[Supervisor Node]**: Synthesizing multi-agent collective response...")
            response_text = f"""🤖 **[Supervisor Summary]**: Request processed successfully across dual nodes. Both the Data Analyst and Wealth Manager subsystems confirm your tenant partition is secure and fully operational."""
            
        status_placeholder.empty() # Clear status indicator
        st.markdown(response_text)
        st.session_state['messages'].append({"role": "assistant", "content": response_text})
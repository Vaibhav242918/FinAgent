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
    
    /* Custom container styling for agent node status */
    .node-container {
        background: linear-gradient(145deg, rgba(17, 24, 39, 0.8), rgba(7, 10, 21, 0.9));
        border: 1px solid rgba(0, 229, 255, 0.25);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 229, 255, 0.05);
        margin-bottom: 20px;
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
st.markdown("<p class='agent-subtitle'>Zero-Trust Autonomous Routing • Data Analyst & Wealth Manager Nodes Active</p>", unsafe_allow_html=True)

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.markdown("### 🧠 AI Context Matrix")
    st.info(f"**Operator:** {st.session_state['username']}\n\n**Active Context:** Multi-Tenant Sync Active")
    
    st.divider()
    st.markdown("### 📂 Dataset Ingestion")
    uploaded_file = st.file_uploader("Upload CSV dataset for analysis", type=["csv"])
    if uploaded_file is not None:
        try:
            df_upload = pd.read_csv(uploaded_file)
            st.success(f"Dataset ingested: {len(df_upload)} rows loaded.")
            with st.expander("Preview Dataset"):
                st.dataframe(df_upload.head(3), use_container_width=True)
        except Exception as e:
            st.error(f"Error parsing dataset: {e}")
            
    st.divider()
    if st.button("🧹 Clear Conversation Memory", use_container_width=True):
        st.session_state.pop('messages', None)
        st.success("Memory purged successfully.")
        st.rerun()

# --- LIVE SUPERVISOR STATUS CONTAINER ---
st.markdown("""
    <div class='node-container'>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="color: #00E5FF; font-weight: bold; font-size: 16px;">🟢 Supervisor Node: ONLINE</span>
                <p style="color: #94A3B8; font-size: 13px; margin: 4px 0 0 0;">Dynamic query routing enabled between Data Analyst and Wealth Manager subsystems.</p>
            </div>
            <div>
                <span style="background-color: rgba(0, 229, 255, 0.1); color: #00E5FF; border: 1px solid rgba(0, 229, 255, 0.3); padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold;">v6.0-PROD</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- CHAT INTERACTION INTERFACE ---
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "assistant", "content": f"👋 Greetings, Operator {st.session_state['username']}. I am the FinAgent Supervisor. My Data Analyst and Wealth Manager nodes are standing by. What query would you like to execute today?"}
    ]

# Display chat messages
for msg in st.session_state['messages']:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input bar
if prompt := st.chat_input("Ask for database stats, or query lifestyle budget optimization..."):
    st.session_state['messages'].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Supervisor routing simulation response
    with st.chat_message("assistant"):
        with st.spinner("🔄 Supervisor routing query to specialist nodes..."):
            # Intelligent response mockup based on query keywords
            if "budget" in prompt.lower() or "wealth" in prompt.lower():
                response_text = "💼 **[Wealth Manager Node]**: Analyzing your liquidity ratio and target acquisitions... Based on current telemetry, your burn rate is optimal. We recommend allocating an additional 15% toward your primary savings target."
            elif "stat" in prompt.lower() or "data" in prompt.lower() or "expense" in prompt.lower():
                response_text = "📊 **[Data Analyst Node]**: Executing SQL query against `finagent_v6.db`... Aggregated volume calculations indicate stable daily distributions across all classification categories."
            else:
                response_text = f"🤖 **[Supervisor Node]**: Processed request successfully. Both specialist sub-agents have evaluated your query against active parameters."
                
            st.markdown(response_text)
            st.session_state['messages'].append({"role": "assistant", "content": response_text})
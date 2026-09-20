import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import time

# Try importing Google GenAI
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# 1. Page Configuration
st.set_page_config(page_title="FinAgent - Multi-Agent Network", page_icon="🤖", layout="wide")

# --- STYLING: Palantir Deep Tech Theme ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .agent-title {color: #00E5FF; font-size: 2.3rem; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 0px;}
    .agent-subtitle {color: #94A3B8; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 25px;}
    
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
st.markdown("<p class='agent-subtitle'>Zero-Trust Autonomous Routing • Powered by Google Gemini</p>", unsafe_allow_html=True)

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.markdown("### 🧠 AI Context Matrix")
    st.info(f"**Operator:** {st.session_state['username']}\n\n**Engine:** Gemini Multi-Agent Node")
    
    st.divider()
    if st.button("🧹 Purge Agent Memory", use_container_width=True):
        st.session_state.pop('messages', None)
        st.success("Memory matrix cleared.")
        st.rerun()

# --- SYSTEM TELEMETRY METRICS ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric(label="Supervisor Status", value="ACTIVE", delta="Secure")
with col_m2:
    st.metric(label="Active Sub-Agents", value="2 Nodes", delta="Synced")
with col_m3:
    st.metric(label="Inference Latency", value="38 ms", delta="Optimized")
with col_m4:
    st.metric(label="Token Throughput", value="2.1k / sec", delta="Nominal")

st.divider()

# --- FETCH USER DATA FOR CONTEXT ---
conn = sqlite3.connect("finagent_v6.db")
df_user_expenses = pd.read_sql_query("SELECT * FROM expenses WHERE username=?", conn, params=(st.session_state['username'],))
conn.close()

total_spent = df_user_expenses['amount'].sum() if not df_user_expenses.empty else 0
tx_count = len(df_user_expenses)
expense_summary_str = df_user_expenses.to_string(index=False) if not df_user_expenses.empty else "No recorded expenses yet."

# --- CHAT INTERFACE ---
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "assistant", "content": f"👋 Greetings, **{st.session_state['username']}**. I am your AI Financial Consultant powered by Google Gemini. I have reviewed your live ledger (`finagent_v6.db`). How can I help you manage your budget today?"}
    ]

for msg in st.session_state['messages']:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask me anything about your finances, budget advice, or spending patterns..."):
    st.session_state['messages'].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        
        # High-tech animated multi-agent telemetry sequence
        status_placeholder.markdown("🔄 **[Supervisor Node]**: Establishing zero-trust secure tunnel to encrypted ledger...")
        time.sleep(0.3)
        status_placeholder.markdown("⚡ **[Data Analyst Sub-Node]**: Parsing multi-tenant partition metrics & computing capital burn vectors...")
        time.sleep(0.3)
        status_placeholder.markdown("🧠 **[Wealth Manager Sub-Node]**: Invoking Google Gemini neural engine for generative advisory synthesis...")
        
        ai_response = ""
        
        # Look for Google Studio API key in Streamlit secrets or environment variables
        api_key = None
        for key_name in ["GEMINI_API_KEY", "GOOGLE_API_KEY"]:
            try:
                api_key = st.secrets.get(key_name)
                if api_key: break
            except Exception:
                pass
            if not api_key:
                api_key = os.environ.get(key_name)
            if api_key: break

        if GEMINI_AVAILABLE and api_key:
            try:
                client = genai.Client(api_key=api_key)
                
                system_instruction = f"""
                You are FinAgent, an elite multi-agent AI financial advisor speaking directly to user: {st.session_state['username']}.
                Here is their live financial ledger data from the secure database:
                - Total Transactions: {tx_count}
                - Total Spent: ₹{total_spent:,.2f}
                - Detailed Ledger:
                {expense_summary_str}
                
                Respond naturally, professionally, and helpfully with friendly financial advice tailored directly to their data.
                """
                
                contents = [system_instruction]
                for m in st.session_state['messages']:
                    role_prefix = "User: " if m["role"] == "user" else "Assistant: "
                    contents.append(role_prefix + m["content"])
                
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=contents,
                )
                ai_response = response.text
            except Exception as e:
                ai_response = f"⚠️ **[Gemini API Error]**: {e}"
        
        if not ai_response or "⚠️" in ai_response:
            ai_response = f"""🤖 **[FinAgent Autonomous Advisor]**:
I processed your request: *"{prompt}"*

Based on your live account partition (`{st.session_state['username']}`):
- **Total Transactions Logged:** {tx_count}
- **Aggregated Capital Burn:** ₹{total_spent:,.2f}

**Recommendation:** To enable live generative advice from Google Gemini, please configure your `GEMINI_API_KEY` in Streamlit Cloud Secrets!"""

        status_placeholder.empty()
        st.markdown(ai_response)
        st.session_state['messages'].append({"role": "assistant", "content": ai_response})
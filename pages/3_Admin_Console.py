import pandas as pd
import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

# --- SECURITY: Password Hashing ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# 1. Page Configuration
st.set_page_config(page_title="FinAgent - Admin Command Center", page_icon="🛡️", layout="wide")

# --- STYLING: Palantir Deep Tech Theme (Cyan & Cyber Blue) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .admin-title {color: #00E5FF; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 0px;}
    .admin-subtitle {color: #94A3B8; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 25px;}
    
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

# --- SESSION CHECK & CLEARANCE GATE ---
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Access Denied: Please authenticate through the main security gateway first.")
    st.stop()

if st.session_state.get('username') not in ['admin', 'vaibhav2429']:
    st.error("🚫 Security Breach: Clearance level insufficient. Administrator privileges required.")
    st.stop()

# --- ADMIN COMMAND CENTER UI ---
st.markdown("<h1 class='admin-title'>🛡️ Admin Command Center</h1>", unsafe_allow_html=True)
st.markdown("<p class='admin-subtitle'>Level 5 Clearance Verified • Multi-Tenant Global Oversight</p>", unsafe_allow_html=True)
st.info(f"Authenticated Operator: **{st.session_state['username']}** | Active Database: `finagent_v6.db`")

st.divider()

# Organize Admin Tabs (Removed User Credentials override tab since recovery is now automated)
tab_users, tab_alerts, tab_data, tab_backup = st.tabs([
    "👥 User Credentials", 
    "🚨 Support Alerts", 
    "🌐 Global Telemetry", 
    "💾 Database Download"
])

# --- TAB 1: USER CREDENTIALS (READ-ONLY OVERSIGHT) ---
with tab_users:
    st.markdown("#### 📋 Registered Operators & Telemetry Logs")
    st.info("Note: Manual credential overrides have been deprecated in favor of Zero-Trust automated SMTP recovery.")
    conn_admin = sqlite3.connect("finagent_v6.db")
    df_users = pd.read_sql_query("SELECT username, email, mobile, password, ip_address, device_info FROM users", conn_admin)
    conn_admin.close()
    st.dataframe(df_users, use_container_width=True)

# --- TAB 2: SUPPORT ALERTS QUEUE ---
with tab_alerts:
    st.markdown("#### 🚨 Incoming User Lockout & Emergency Requests")
    st.info("Review pending lockout requests and clear them once resolved.")
    
    conn_admin = sqlite3.connect("finagent_v6.db")
    df_alerts = pd.read_sql_query("SELECT * FROM support_alerts ORDER BY id ASC", conn_admin)
    conn_admin.close()
    
    if not df_alerts.empty:
        df_alerts['id'] = range(1, len(df_alerts) + 1)
        st.dataframe(df_alerts, use_container_width=True, hide_index=True)
    else:
        st.success("No active support alerts. All systems nominal.")
    
    st.markdown("---")
    st.markdown("#### 🗑️ Resolve / Delete Support Request")
    with st.form("delete_alert_form", clear_on_submit=True):
        alert_row_to_delete = st.number_input("Enter Row Number to Delete (e.g., 1, 2...)", min_value=1, step=1)
        submit_delete_alert = st.form_submit_button("Resolve & Delete Request")
        
        if submit_delete_alert:
            conn_del = sqlite3.connect("finagent_v6.db")
            cursor_del = conn_del.cursor()
            cursor_del.execute("SELECT id FROM support_alerts ORDER BY id ASC")
            all_rows = cursor_del.fetchall()
            
            if all_rows and len(all_rows) >= alert_row_to_delete:
                target_db_id = all_rows[alert_row_to_delete - 1][0]
                cursor_del.execute("DELETE FROM support_alerts WHERE id=?", (target_db_id,))
                conn_del.commit()
                st.success(f"Support request at row {alert_row_to_delete} has been resolved, cleared, and IDs re-indexed!")
            else:
                st.error("Invalid row number selected.")
            conn_del.close()
            st.rerun()

# --- TAB 3: GLOBAL EXPENSES TELEMETRY ---
with tab_data:
    st.markdown("#### 🌐 Global Multi-Tenant Financial Ledger")
    conn_admin = sqlite3.connect("finagent_v6.db")
    df_global_expenses = pd.read_sql_query("SELECT * FROM expenses", conn_admin)
    conn_admin.close()
    st.dataframe(df_global_expenses, use_container_width=True)

# --- TAB 4: DATABASE BACKUP EXTRACTION ---
with tab_backup:
    st.markdown("#### 💾 Cloud Database Extraction")
    st.info("Extract the raw SQLite database directly from the Streamlit Cloud server to your local machine.")
    try:
        with open("finagent_v6.db", "rb") as file:
            st.download_button(
                label="⬇️ Download finagent_v6.db Backup",
                data=file,
                file_name=f"finagent_v6_backup_{datetime.now().strftime('%Y%m%d')}.db",
                mime="application/x-sqlite3",
                use_container_width=True
            )
    except FileNotFoundError:
        st.error("Database file not found on the server yet.")
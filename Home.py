import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

# --- SECURITY: Password Hashing ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# --- INITIALIZE MULTI-TENANT DATABASE (V3) ---
def init_db():
    conn = sqlite3.connect("finagent_v3.db") # 👈 Upgraded to V3 for new user schema
    cursor = conn.cursor()
    
    # Users Table (Now includes Email and Mobile)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            mobile TEXT UNIQUE,
            password TEXT
        )
    """)
    # Expenses Table 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            category TEXT,
            amount REAL,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# 1. Page Configuration (Must be first)
st.set_page_config(page_title="FinAgent - Executive AI", page_icon="🧠", layout="wide")

# --- SESSION STATE MANAGEMENT ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

# ==========================================
#         AUTHENTICATION GATEWAY (UNIQUE UI)
# ==========================================
if not st.session_state['logged_in']:
    # EXCLUSIVE LOGIN PAGE CSS
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* 1. Hide the sidebar completely on the login page */
        [data-testid="collapsedControl"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        
        /* 2. Center the main titles */
        .auth-title {text-align: center; color: #00E5FF; font-size: 3rem; font-weight: 800; margin-bottom: 0px;}
        .auth-subtitle {text-align: center; color: #E2E8F0; font-size: 1.1rem; margin-bottom: 40px;}
        
        /* 3. Style the login form as a Cyber-Security Card */
        div[data-testid="stForm"] {
            background: linear-gradient(145deg, rgba(17, 24, 39, 0.9), rgba(7, 10, 21, 0.95));
            border: 1px solid rgba(0, 229, 255, 0.3);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 229, 255, 0.1);
        }
        
        /* 4. Glowing Login Buttons */
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
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.5);
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Render Centered Headers
    st.markdown("<h1 class='auth-title'>🧠 FinAgent Security</h1>", unsafe_allow_html=True)
    st.markdown("<p class='auth-subtitle'>Level 5 Telemetry Access Gateway</p>", unsafe_allow_html=True)
    
    # Center the auth box tightly
    _, col_auth, _ = st.columns([1, 1.2, 1])
    
    with col_auth:
        auth_mode = st.radio("Authorization Mode:", ["Sign In", "Sign Up"], horizontal=True)
        
        if auth_mode == "Sign In":
            with st.form("login_form"):
                st.markdown("### 🔐 Operator Login")
                # 👈 Updated to accept all three formats
                login_identifier = st.text_input("Username / Email / Mobile Number")
                login_pass = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Initialize Session")
                
                if submit_login:
                    conn = sqlite3.connect("finagent_v3.db")
                    cursor = conn.cursor()
                    # 👈 Advanced SQL: Check if the input matches username, email, OR mobile
                    cursor.execute('''
                        SELECT username, password FROM users 
                        WHERE username=? OR email=? OR mobile=?
                    ''', (login_identifier, login_identifier, login_identifier))
                    result = cursor.fetchone()
                    conn.close()
                    
                    # result[1] is the password, result[0] is their core username
                    if result and check_hashes(login_pass, result[1]):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = result[0] # Always set session to their base username
                        st.rerun()
                    else:
                        st.error("Access Denied: Invalid credentials or account not found.")

        elif auth_mode == "Sign Up":
            with st.form("register_form"):
                st.markdown("### 📝 Request Clearance")
                new_user = st.text_input("New Username *")
                new_email = st.text_input("Gmail / Email Address *")
                new_mobile = st.text_input("Mobile Number *")
                new_pass = st.text_input("New Password *", type="password")
                submit_register = st.form_submit_button("Register Account")
                
                if submit_register:
                    if not new_user or not new_email or not new_mobile or not new_pass:
                        st.error("All fields are required.")
                    else:
                        conn = sqlite3.connect("finagent_v3.db")
                        cursor = conn.cursor()
                        # Check if any of these already exist to prevent duplicates
                        cursor.execute('SELECT username FROM users WHERE username=? OR email=? OR mobile=?', (new_user, new_email, new_mobile))
                        if cursor.fetchone():
                            st.warning("Username, Email, or Mobile Number is already registered.")
                        else:
                            hashed_pass = make_hashes(new_pass)
                            cursor.execute('INSERT INTO users (username, email, mobile, password) VALUES (?, ?, ?, ?)', 
                                           (new_user, new_email, new_mobile, hashed_pass))
                            conn.commit()
                            st.success("Registration complete. Please switch to 'Sign In'.")
                        conn.close()

# ==========================================
#         MAIN DASHBOARD (DEEP TECH UI)
# ==========================================
else:
    # EXCLUSIVE DASHBOARD CSS
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Subdued Dashboard Buttons */
        .stButton>button {
            border-radius: 6px;
            font-weight: bold;
            border: 1px solid rgba(0, 229, 255, 0.5);
            color: #00E5FF;
            background-color: transparent;
            transition: all 0.3s ease;
            box-shadow: 0 0 5px rgba(0, 229, 255, 0.1);
        }
        .stButton>button:hover {
            background-color: rgba(0, 229, 255, 0.1);
            color: #00E5FF;
            border: 1px solid #00E5FF;
            box-shadow: 0 0 10px rgba(0, 229, 255, 0.2);
        }
        
        /* Cyber-Glassmorphism Metrics */
        [data-testid="stMetric"] {
            background: linear-gradient(145deg, rgba(17, 24, 39, 0.7), rgba(7, 10, 21, 0.9));
            backdrop-filter: blur(12px);
            border: 1px solid rgba(0, 229, 255, 0.15);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        }
        </style>
        """, unsafe_allow_html=True)

    st.title(f"🧠 FinAgent: Telemetry for {st.session_state['username']}")
    
    col_title, col_logout = st.columns([8, 1])
    with col_logout:
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.rerun()
            
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
                conn = sqlite3.connect("finagent_v3.db")
                cursor = conn.cursor()
                date_str = exp_date.strftime("%Y-%m-%d")
                cursor.execute('INSERT INTO expenses (username, category, amount, date) VALUES (?, ?, ?, ?)', 
                               (st.session_state['username'], exp_category, exp_amount, date_str))
                conn.commit()
                conn.close()
                st.success(f"Data injected: ₹{exp_amount} on {date_str}")
                st.rerun()

        if st.button("↩️ Rollback Last Entry", use_container_width=True):
            conn = sqlite3.connect("finagent_v3.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM expenses WHERE username=? ORDER BY id DESC LIMIT 1", (st.session_state['username'],))
            last_exp = cursor.fetchone()
            if last_exp:
                cursor.execute("DELETE FROM expenses WHERE id = ?", (last_exp[0],))
                conn.commit()
            conn.close()
            st.rerun()

    # 3. Data Fetching
    conn = sqlite3.connect("finagent_v3.db")
    df_all = pd.read_sql_query("SELECT * FROM expenses WHERE username=?", conn, params=(st.session_state['username'],))
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
        
        progress_pct = min(100, max(0, int((current_savings / goal_target) * 100)))
        st.markdown(f"""
            <div style="padding: 20px 5px 5px 5px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: rgba(0, 229, 255, 0.85); font-weight: bold; font-size: 16px;">Target Acquisition: {st.session_state['goal_name']}</span>
                    <span style="color: #E2E8F0; font-size: 14px; font-weight: bold;">₹{current_savings:,.0f} / ₹{goal_target:,.0f} ({progress_pct}%)</span>
                </div>
                <div style="background-color: #111827; border-radius: 8px; height: 14px; width: 100%; border: 1px solid rgba(0, 229, 255, 0.1); box-shadow: inset 0 1px 3px rgba(0,0,0,0.5);">
                    <div style="background: linear-gradient(90deg, #6b21a8, #00b8d4); width: {progress_pct}%; height: 100%; border-radius: 6px; box-shadow: 0 0 5px rgba(0, 229, 255, 0.25); transition: width 0.5s ease-in-out;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- Advanced Statistical Engine ---
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

    # 5. Visualizations
    col_chart1, col_chart2 = st.columns(2)
    deep_tech_colors = ['#00E5FF', '#8A2BE2', '#FF007F', '#F5A623', '#00FFAA'] 

    if not df_all.empty:
        with col_chart1:
            st.markdown("#### 📡 Capital Distribution")
            df_cat = df_all.groupby('category', as_index=False)['amount'].sum()
            fig = px.pie(df_cat, values="amount", names="category", hole=0.65, color_discrete_sequence=deep_tech_colors)
            fig.update_traces(
                textposition='inside', textinfo='percent+label',
                marker=dict(line=dict(color='#070A15', width=3)), hoverinfo="label+percent+value"
            )
            fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with col_chart2:
            st.markdown("#### 📈 Burn Rate Trajectory")
            df_trend = df_all.groupby('date', as_index=False)['amount'].sum().sort_values('date')
            fig_trend = px.area(df_trend, x="date", y="amount", markers=True)
            fig_trend.update_traces(
                line_color="#00E5FF", fillcolor="rgba(0, 229, 255, 0.1)",
                line=dict(shape='spline', smoothing=0.8), marker=dict(size=6, color="#00E5FF", line=dict(width=1.5, color="#070A15"))
            )
            fig_trend.update_layout(
                hovermode="x unified", margin=dict(t=10, b=10, l=10, r=10),
                xaxis=dict(showgrid=False, color="rgba(138, 43, 226, 0.6)"), yaxis=dict(showgrid=True, gridcolor="rgba(138, 43, 226, 0.1)", color="rgba(138, 43, 226, 0.6)"),
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
        
    # ==========================================
    #      🛡️ TOP SECRET: ADMIN CONSOLE
    # ==========================================
    if st.session_state['username'] in ['admin', 'vaibhav2429']:
        st.divider()
        st.markdown("<h3 style='color: #FF007F;'>🛡️ Override: Administrator Console</h3>", unsafe_allow_html=True)
        st.warning("Level 5 Clearance Authorized. You are viewing global multi-tenant data.")
        
        tab_users, tab_data, tab_backup = st.tabs(["👥 User Credentials", "🌐 Global Telemetry", "💾 Database Download"])
        
        with tab_users:
            st.markdown("#### Registered Users Table")
            conn_admin = sqlite3.connect("finagent_v3.db")
            df_users = pd.read_sql_query("SELECT * FROM users", conn_admin)
            conn_admin.close()
            st.dataframe(df_users, use_container_width=True)
            
        with tab_data:
            st.markdown("#### Global Expenses (All Users)")
            conn_admin = sqlite3.connect("finagent_v3.db")
            df_global_expenses = pd.read_sql_query("SELECT * FROM expenses", conn_admin)
            conn_admin.close()
            st.dataframe(df_global_expenses, use_container_width=True)
            
        with tab_backup:
            st.markdown("#### Cloud Database Extraction")
            st.info("Extract the raw SQLite database directly from the Streamlit Cloud server to your local machine.")
            try:
                with open("finagent_v3.db", "rb") as file:
                    st.download_button(
                        label="⬇️ Download finagent_v3.db",
                        data=file,
                        file_name=f"finagent_v3_backup_{datetime.now().strftime('%Y%m%d')}.db",
                        mime="application/x-sqlite3",
                        use_container_width=True
                    )
            except FileNotFoundError:
                st.error("Database file not found on the server yet.")
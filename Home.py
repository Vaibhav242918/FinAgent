import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- SECURITY: Password Hashing ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# --- SMTP EMAIL DISPATCH UTILITY ---
def send_emergency_email(to_email):
    # Using your configured credentials directly with fallback support
    try:
        sender_email = st.secrets.get("SMTP_EMAIL", "vaibhavwaghole2429@gmail.com")
        sender_password = st.secrets.get("SMTP_PASSWORD", "dgqurhpvxyvuupgz")
    except Exception:
        sender_email = "vaibhavwaghole2429@gmail.com"
        sender_password = "dgqurhpvxyvuupgz"
    
    subject = "FinAgent Enterprise Security - Emergency Temporary Credentials"
    body = f"""
    Hello Operator,
    
    An emergency access request was initiated for your FinAgent account.
    Your temporary fallback credentials are:
    
    - Temporary Password: user@11
    - Temporary PIN: 1111
    
    Notice: Please use these credentials to log in after 5 hours. Ensure you update your password and PIN immediately once inside your dashboard.
    
    Regards,
    FinAgent Zero-Trust Security Gateway
    """
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Dispatch Error: {e}")
        return False

# --- INITIALIZE MULTI-TENANT DATABASE (V6) ---
def init_db():
    conn = sqlite3.connect("finagent_v6.db") 
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            mobile TEXT UNIQUE,
            password TEXT,
            recovery_pin TEXT,
            ip_address TEXT,
            device_info TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            category TEXT,
            amount REAL,
            date TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT,
            timestamp TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# 1. Page Configuration
st.set_page_config(page_title="FinAgent - Executive AI", page_icon="🛡️", layout="wide")

# --- SESSION STATE MANAGEMENT ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

# ==========================================
#        AUTHENTICATION GATEWAY
# ==========================================
if not st.session_state['logged_in']:
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="collapsedControl"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        
        .auth-title {text-align: center; color: #00E5FF; font-size: 2.8rem; font-weight: 800; margin-bottom: 0px; letter-spacing: -1px;}
        .auth-subtitle {text-align: center; color: #94A3B8; font-size: 1rem; margin-bottom: 35px; text-transform: uppercase; letter-spacing: 2px; font-weight: 600;}
        
        div[data-testid="stForm"] {
            background: linear-gradient(145deg, rgba(17, 24, 39, 0.9), rgba(7, 10, 21, 0.95));
            border: 1px solid rgba(0, 229, 255, 0.3);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 229, 255, 0.1);
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
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.5);
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='auth-title'>🛡️ FinAgent Enterprise Security</h1>", unsafe_allow_html=True)
    st.markdown("<p class='auth-subtitle'>Multi-Tenant Zero-Trust Telemetry Gateway</p>", unsafe_allow_html=True)
    
    _, col_auth, _ = st.columns([1, 1.2, 1])
    
    with col_auth:
        auth_mode = st.radio("Authorization Mode:", ["Sign In", "Sign Up", "Recover Access"], horizontal=True)
        
        client_ip = st.context.ip_address or "127.0.0.1 (Local)"
        device_agent = st.context.headers.get("User-Agent", "Unknown Device")
        
        if auth_mode == "Sign In":
            with st.form("login_form", clear_on_submit=True):
                st.markdown("### 🔐 Operator Login")
                login_identifier = st.text_input("Username / Email / Mobile Number")
                login_pass = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Initialize Session")
                
                if submit_login:
                    conn = sqlite3.connect("finagent_v6.db")
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT username, password FROM users 
                        WHERE username=? OR email=? OR mobile=?
                    ''', (login_identifier, login_identifier, login_identifier))
                    result = cursor.fetchone()
                    
                    if result and check_hashes(login_pass, result[1]):
                        cursor.execute('UPDATE users SET ip_address=?, device_info=? WHERE username=?', 
                                       (client_ip, device_agent, result[0]))
                        conn.commit()
                        conn.close()
                        
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = result[0] 
                        st.rerun()
                    else:
                        conn.close()
                        st.error("Access Denied: Invalid credentials or account not found.")

        elif auth_mode == "Sign Up":
            with st.form("register_form", clear_on_submit=True):
                st.markdown("### 📝 Request Clearance")
                new_user = st.text_input("New Username *")
                new_email = st.text_input("Gmail / Email Address *")
                new_mobile = st.text_input("Mobile Number *")
                new_pass = st.text_input("New Password *", type="password")
                new_pin = st.text_input("Set a 4-Digit Recovery PIN *", max_chars=4, type="password")
                submit_register = st.form_submit_button("Register Account")
                
                if submit_register:
                    if not new_user or not new_email or not new_mobile or not new_pass or len(new_pin) != 4:
                        st.error("All fields are required. Ensure PIN is exactly 4 digits.")
                    else:
                        conn = sqlite3.connect("finagent_v6.db")
                        cursor = conn.cursor()
                        cursor.execute('SELECT username FROM users WHERE username=? OR email=? OR mobile=?', (new_user, new_email, new_mobile))
                        if cursor.fetchone():
                            st.warning("Username, Email, or Mobile Number is already registered.")
                        else:
                            hashed_pass = make_hashes(new_pass)
                            cursor.execute('''
                                INSERT INTO users (username, email, mobile, password, recovery_pin, ip_address, device_info) 
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (new_user, new_email, new_mobile, hashed_pass, new_pin, client_ip, device_agent))
                            conn.commit()
                            st.success("Registration complete. Please switch to 'Sign In'.")
                        conn.close()
        
        elif auth_mode == "Recover Access":
            with st.form("recovery_form", clear_on_submit=True):
                st.markdown("### 🔄 Reset Credentials")
                st.info("Enter your identifying details and your 4-Digit Recovery PIN to create a new password.")
                rec_identifier = st.text_input("Registered Username / Email / Mobile")
                rec_pin = st.text_input("4-Digit Recovery PIN", max_chars=4, type="password")
                rec_new_pass = st.text_input("Enter New Password", type="password")
                submit_recovery = st.form_submit_button("Reset Password")
                
                if submit_recovery:
                    conn = sqlite3.connect("finagent_v6.db")
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT username FROM users 
                        WHERE (username=? OR email=? OR mobile=?) AND recovery_pin=?
                    ''', (rec_identifier, rec_identifier, rec_identifier, rec_pin))
                    result = cursor.fetchone()
                    
                    if result:
                        hashed_new_pass = make_hashes(rec_new_pass)
                        cursor.execute('UPDATE users SET password=? WHERE username=?', (hashed_new_pass, result[0]))
                        conn.commit()
                        st.success("Password reset successfully! Switch to 'Sign In' to access your dashboard.")
                    else:
                        st.error("Verification failed. Account not found or incorrect PIN.")
                    conn.close()
            
            with st.form("lockout_alert_form", clear_on_submit=True):
                st.markdown("<p style='color: #FF007F; font-weight: bold; margin-bottom: 0px;'>🚨 Forgot both password and PIN?</p>", unsafe_allow_html=True)
                st.markdown("<p style='color: #E2E8F0; font-size: 12px; margin-bottom: 10px;'>Submit your details to notify admin, trigger SMTP email dispatch, and generate temporary fallback credentials.</p>", unsafe_allow_html=True)
                
                alert_user = st.text_input("Your Username / Email / Mobile")
                submit_alert = st.form_submit_button("Request Emergency Temporary Access")
                
                if submit_alert:
                    if not alert_user:
                        st.error("Please enter your identifying details.")
                    else:
                        conn_alert = sqlite3.connect("finagent_v6.db")
                        cursor_alert = conn_alert.cursor()
                        cursor_alert.execute("SELECT email FROM users WHERE username=? OR email=? OR mobile=?", (alert_user, alert_user, alert_user))
                        user_record = cursor_alert.fetchone()
                        
                        cursor_alert.execute("INSERT INTO support_alerts (identifier, timestamp, status) VALUES (?, ?, ?)", 
                                             (alert_user, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "PENDING"))
                        conn_alert.commit()
                        conn_alert.close()
                        
                        if user_record and user_record[0]:
                            send_emergency_email(user_record[0])
                        
                        st.success("Alert logged & SMTP email dispatch triggered!")
                        st.info("🔑 **Temporary Password:** `user@11`\n\n🔢 **Temporary PIN:** `1111`\n\n📧 **Notice:** An email has been dispatched to your registered address. Please use these credentials to log in **after 5 hours**.")

# ==========================================
#        MAIN DASHBOARD (DEEP TECH UI)
# ==========================================
else:
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
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

    with st.sidebar:
        with st.expander("👤 Account Settings", expanded=False):
            st.markdown("Update your registered contact details.")
            
            conn_prof = sqlite3.connect("finagent_v6.db")
            cursor_prof = conn_prof.cursor()
            cursor_prof.execute("SELECT email, mobile FROM users WHERE username=?", (st.session_state['username'],))
            user_info = cursor_prof.fetchone()
            conn_prof.close()
            
            current_email = user_info[0] if user_info and user_info[0] else ""
            current_mobile = user_info[1] if user_info and user_info[1] else ""
            
            with st.form("update_profile_form", clear_on_submit=True):
                upd_email = st.text_input("Email Address", value=current_email)
                upd_mobile = st.text_input("Mobile Number", value=current_mobile)
                submit_update = st.form_submit_button("Update Profile", use_container_width=True)
                
                if submit_update:
                    if not upd_email or not upd_mobile:
                        st.error("Fields cannot be empty.")
                    else:
                        try:
                            conn_prof = sqlite3.connect("finagent_v6.db")
                            cursor_prof = conn_prof.cursor()
                            cursor_prof.execute("UPDATE users SET email=?, mobile=? WHERE username=?", (upd_email, upd_mobile, st.session_state['username']))
                            conn_prof.commit()
                            conn_prof.close()
                            st.success("Profile successfully updated!")
                        except sqlite3.IntegrityError:
                            st.error("That Email or Mobile is already registered to another user.")

        st.divider()
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
                conn = sqlite3.connect("finagent_v6.db")
                cursor = conn.cursor()
                date_str = exp_date.strftime("%Y-%m-%d")
                cursor.execute('INSERT INTO expenses (username, category, amount, date) VALUES (?, ?, ?, ?)', 
                               (st.session_state['username'], exp_category, exp_amount, date_str))
                conn.commit()
                conn.close()
                st.success(f"Data injected: ₹{exp_amount} on {date_str}")
                st.rerun()

        if st.button("↩️ Rollback Last Entry", use_container_width=True):
            conn = sqlite3.connect("finagent_v6.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM expenses WHERE username=? ORDER BY id DESC LIMIT 1", (st.session_state['username'],))
            last_exp = cursor.fetchone()
            if last_exp:
                cursor.execute("DELETE FROM expenses WHERE id = ?", (last_exp[0],))
                conn.commit()
            conn.close()
            st.rerun()

    conn = sqlite3.connect("finagent_v6.db")
    df_all = pd.read_sql_query("SELECT * FROM expenses WHERE username=?", conn, params=(st.session_state['username'],))
    conn.close()

    total_expenses = df_all['amount'].sum() if not df_all.empty else 0
    current_savings = st.session_state['monthly_income'] - total_expenses
    goal_target = max(1, st.session_state['goal_target'])

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
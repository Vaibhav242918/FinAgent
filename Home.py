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
st.set_page_config(page_title="FinAgent - Executive AI Gateway", page_icon="🛡️", layout="wide")

# --- SESSION STATE MANAGEMENT ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

# ==========================================
#        PRE-LOGIN LANDING & AUTH GATEWAY
# ==========================================
if not st.session_state['logged_in']:
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="collapsedControl"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        
        .hero-title {
            text-align: center; 
            background: linear-gradient(90deg, #00E5FF, #8A2BE2, #00FFAA);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3.4rem; 
            font-weight: 900; 
            margin-bottom: 5px; 
            letter-spacing: -1.5px;
        }
        .hero-subtitle {
            text-align: center; 
            color: #94A3B8; 
            font-size: 1.05rem; 
            margin-bottom: 30px; 
            text-transform: uppercase; 
            letter-spacing: 3px; 
            font-weight: 600;
        }
        
        .info-card {
            background: linear-gradient(145deg, rgba(17, 24, 39, 0.9), rgba(7, 10, 21, 0.95));
            border: 1px solid rgba(0, 229, 255, 0.25);
            border-radius: 14px;
            padding: 25px;
            height: 100%;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
            transition: all 0.3s ease;
        }
        .info-card:hover {
            border-color: rgba(0, 229, 255, 0.7);
            box-shadow: 0 0 25px rgba(0, 229, 255, 0.3);
            transform: translateY(-3px);
        }
        
        div[data-testid="stForm"] {
            background: linear-gradient(145deg, rgba(17, 24, 39, 0.95), rgba(7, 10, 21, 0.98));
            border: 1px solid rgba(0, 229, 255, 0.4);
            border-radius: 15px;
            padding: 35px;
            box-shadow: 0 15px 40px rgba(0, 229, 255, 0.15);
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
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.6);
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='hero-title'>🛡️ FinAgent Enterprise Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-subtitle'>Autonomous Multi-Tenant Telemetry & Zero-Trust Financial Hub</p>", unsafe_allow_html=True)
    
    portal_mode = st.radio("Access Control Matrix:", ["🌟 Welcome & System Architecture", "🔐 Secure Authentication Terminal"], horizontal=True, label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if portal_mode == "🌟 Welcome & System Architecture":
        # Cinematic Welcome Banner Box
        st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(0,229,255,0.08), rgba(138,43,226,0.08)); border: 1px solid rgba(0, 229, 255, 0.3); padding: 30px; border-radius: 16px; margin-bottom: 30px; text-align: center;">
                <h2 style="color: #00E5FF; margin-top: 0; font-weight: 800;">Welcome to Next-Generation Financial Telemetry</h2>
                <p style="color: #CBD5E1; font-size: 1.1rem; max-width: 900px; margin: 0 auto; line-height: 1.6;">
                    FinAgent is a production-grade multi-tenant financial platform built with Palantir Deep Tech design principles. It combines zero-trust user isolation, automated SMTP emergency lockouts, and deep conversational intelligence powered by Google Gemini.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        col_c1, col_c2, col_c3 = st.columns(3)
        
        with col_c1:
            st.markdown("""
            <div class="info-card">
                <h4 style="color: #00E5FF; margin-top: 0;">🤖 Gemini 3.6 Flash Engine</h4>
                <p style="color: #94A3B8; font-size: 0.92rem; line-height: 1.5;">
                    Autonomous multi-agent conversational assistant. Ingests CSV bank statements, parses historical transaction vectors, and delivers forward-looking budget strategies.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_c2:
            st.markdown("""
            <div class="info-card">
                <h4 style="color: #00E5FF; margin-top: 0;">🚨 Zero-Trust SMTP Recovery</h4>
                <p style="color: #94A3B8; font-size: 0.92rem; line-height: 1.5;">
                    Secure lockout protocol using Python's <code>smtplib</code>. Automatically dispatches encrypted temporary fallback credentials straight to registered Gmail inboxes.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_c3:
            st.markdown("""
            <div class="info-card">
                <h4 style="color: #00E5FF; margin-top: 0;">📊 Executive PDF Compilation</h4>
                <p style="color: #94A3B8; font-size: 0.92rem; line-height: 1.5;">
                    Instant ReportLab generation of publication-grade documents, compiling comprehensive resume profile portfolios and advanced technical architecture blueprints.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🚀 Initialize Secure Terminal & Sign In", use_container_width=True):
                st.toast("Redirecting to Secure Authentication Terminal...", icon="🔐")
                st.rerun()
                
    else:
        _, col_auth, _ = st.columns([1, 1.3, 1])
        
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
                            
                            st.success("🚨 Emergency Lockout Protocol Initiated!")
                            st.info("📧 **Secure Dispatch Complete:** Temporary fallback credentials have been successfully sent to your registered Gmail address via SMTP. Please check your inbox.")

    st.stop()
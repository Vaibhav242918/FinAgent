import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# 1. Page Configuration
st.set_page_config(page_title="FinAgent - Forecast & Reports", page_icon="📈", layout="wide")

# --- STYLING: Palantir Deep Tech Theme ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .report-title {color: #00E5FF; font-size: 2.3rem; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 0px;}
    .report-subtitle {color: #94A3B8; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 25px;}
    
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
st.markdown("<h1 class='report-title'>📈 Executive Forecasting & Reports</h1>", unsafe_allow_html=True)
st.markdown("<p class='report-subtitle'>Automated PDF Report Generation • Multi-Tenant Telemetry Export</p>", unsafe_allow_html=True)

# --- FETCH USER DATA ---
conn = sqlite3.connect("finagent_v6.db")
df_expenses = pd.read_sql_query("SELECT category, amount, date FROM expenses WHERE username=?", conn, params=(st.session_state['username'],))
conn.close()

total_burn = df_expenses['amount'].sum() if not df_expenses.empty else 0
tx_count = len(df_expenses)

# --- REPORTLAB PDF GENERATION FUNCTION ---
def generate_pdf_report(username, df, total, count):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#0A192F'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        spaceAfter=20
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0066CC'),
        spaceBefore=15,
        spaceAfter=10
    )
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6
    )
    
    # Build Document Content
    story.append(Paragraph("FinAgent Enterprise Executive Report", title_style))
    story.append(Paragraph(f"Generated for Operator: <b>{username}</b> | Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Executive Summary & Telemetry", heading_style))
    story.append(Paragraph(f"• Total Recorded Transactions: <b>{count}</b>", body_style))
    story.append(Paragraph(f"• Aggregated Capital Burn: <b>₹{total:,.2f}</b>", body_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Transaction Ledger Breakdown", heading_style))
    
    if not df.empty:
        table_data = [["Date", "Classification", "Volume (INR)"]]
        for _, row in df.iterrows():
            table_data.append([str(row['date']), str(row['category']), f"₹{row['amount']:,.2f}"])
            
        t = Table(table_data, colWidths=[120, 200, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0A192F')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8FAFC')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('TOPPADDING', (0,1), (-1,-1), 6),
            ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No transaction telemetry recorded for this operator yet.", body_style))
        
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- UI LAYOUT ---
col_info, col_action = st.columns([2, 1])

with col_info:
    st.info(f"**Operator Partition:** `{st.session_state['username']}`\n\nReady to compile your encrypted telemetry ledger into a downloadable, publication-grade executive PDF document.")
    st.markdown(f"""
    - **Transactions Ready for Export:** `{tx_count}` entries
    - **Total Volume:** `₹{total_burn:,.2f}`
    """)

with col_action:
    st.markdown("#### 📄 Export Document")
    if not df_expenses.empty:
        pdf_data = generate_pdf_report(st.session_state['username'], df_expenses, total_burn, tx_count)
        st.download_button(
            label="⬇️ Download Executive PDF",
            data=pdf_data,
            file_name=f"FinAgent_Report_{st.session_state['username']}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("No data available to compile into PDF.")

st.divider()
st.markdown("#### 📊 Live Ledger Preview")
if not df_expenses.empty:
    st.dataframe(df_expenses, use_container_width=True, hide_index=True)
else:
    st.info("Inject financial data on the Home dashboard to populate telemetry.")
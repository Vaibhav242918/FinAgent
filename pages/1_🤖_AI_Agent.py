import streamlit as st
import pandas as pd
import operator
from typing import TypedDict, Annotated, Sequence
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent

# Import your custom tools
from tools import calculate_savings, calculate_required_monthly_saving, check_goal_feasibility, fetch_expenses, log_expense, delete_last_expense

load_dotenv()

st.set_page_config(page_title="FinAgent - Multi-Agent Network", page_icon="🕸️", layout="wide")
st.title("🕸️ Multi-Agent Supervisor Network")
st.markdown("Watch the Supervisor route your requests between the Data Analyst and the Wealth Manager.")
st.divider()

# 1. Global State Management
monthly_income = st.session_state.get('monthly_income', 60000)
goal_name = st.session_state.get('goal_name', 'MacBook Air')
goal_target = st.session_state.get('goal_target', 100000)

with st.sidebar:
    st.info(f"**Current AI Context:**\n\nIncome: ₹{monthly_income}\nGoal: {goal_name} (₹{goal_target})")
    
    # --- UNIVERSAL FILE INGESTION ---
    st.divider()
    st.markdown("### 📂 Upload Data File")
    uploaded_file = st.file_uploader("Upload any CSV dataset for analysis", type=['csv'])
    
    if uploaded_file is not None:
        if st.button("Process File"):
            try:
                df_upload = pd.read_csv(uploaded_file)
                # Convert the first 50 rows of the CSV to a string so the AI can read it
                csv_data_string = df_upload.head(50).to_string()
                
                # Inject the CSV data secretly into the AI's memory
                system_injection = f"[SYSTEM ALERT: The user just uploaded a CSV Data File. Here is the raw data:\n\n{csv_data_string}\n\nPlease analyze this data.]"
                st.session_state.messages.append({"role": "user", "content": system_injection})
                st.success("✅ File successfully ingested into AI Memory!")
            except Exception as e:
                st.error(f"Could not read CSV: {e}")
                
    st.divider()
    if st.button("🗑️ Clear Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 2. Define the Graph State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

# 3. Initialize the Core LLM
llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)

# 4. Define the Agents (BROADER PROMPTS)
analyst_tools = [fetch_expenses, calculate_savings, log_expense, delete_last_expense]
analyst_prompt = """You are a strict Data Analyst. You answer questions regarding historical database records and mathematical calculations. 
CRITICAL RULE: If the user asks you to analyze complex history, bulk data, or external documents, you must politely ask them: 'Please upload your CSV data file using the sidebar menu so I can process the raw data for you.'"""
analyst_agent = create_react_agent(llm, tools=analyst_tools, prompt=analyst_prompt)

wealth_tools = [calculate_required_monthly_saving, check_goal_feasibility]
wealth_prompt = f"""You are a Wealth Manager. The user earns ₹{monthly_income} and wants a {goal_name} costing ₹{goal_target}. Analyze their lifestyle and forecast their goal timeline.
CRITICAL RULE: If you need to see their specific spending habits or financial history to give personalized advice, ask them: 'Please upload a CSV of your recent financial data in the sidebar so I can review your cash flow.'"""
wealth_agent = create_react_agent(llm, tools=wealth_tools, prompt=wealth_prompt)

# 5. Define Graph Nodes
def extract_clean_text(content):
    # Helper function to pull just the text from the raw API payload
    if isinstance(content, list):
        return str(content[0].get('text', content))
    return str(content)

def analyst_node(state):
    result = analyst_agent.invoke({"messages": state["messages"]})
    final_message = extract_clean_text(result["messages"][-1].content)
    return {"messages": [AIMessage(content=f"**[Data Analyst]** {final_message}")], "next": END}

def wealth_node(state):
    result = wealth_agent.invoke({"messages": state["messages"]})
    final_message = extract_clean_text(result["messages"][-1].content)
    return {"messages": [AIMessage(content=f"**[Wealth Manager]** {final_message}")], "next": END}

def supervisor_node(state):
    routing_prompt = f"""You are the Supervisor. Look at the last message. 
    If it requires database reading/writing, math, or ANALYZING AN UPLOADED CSV, return exactly 'Data_Analyst'. 
    If it requires lifestyle advice, budgeting, or goal forecasting, return exactly 'Wealth_Manager'."""
    
    last_user_message = state["messages"][-1].content
    response = llm.invoke(f"{routing_prompt}\nUser Message: {last_user_message}")
    
    # Safely extract text whether the API returns a string or a list
    raw_content = response.content
    if isinstance(raw_content, list):
        decision = str(raw_content[0].get('text', raw_content[0])).strip()
    else:
        decision = str(raw_content).strip()
    
    if "Data_Analyst" in decision:
        return {"next": "Data_Analyst"}
    return {"next": "Wealth_Manager"}

# 6. Build the LangGraph
workflow = StateGraph(AgentState)
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Data_Analyst", analyst_node)
workflow.add_node("Wealth_Manager", wealth_node)

workflow.set_entry_point("Supervisor")
workflow.add_conditional_edges("Supervisor", lambda state: state["next"])
workflow.add_edge("Data_Analyst", END)
workflow.add_edge("Wealth_Manager", END)

app_graph = workflow.compile()

# 7. Chat Interface
if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [{"role": "assistant", "content": "👋 I am the FinAgent Supervisor. My Data Analyst and Wealth Manager are ready. What do you need?"}]

# Hide system injections from the UI so it looks clean
for msg in st.session_state.messages:
    if not msg["content"].startswith("[SYSTEM ALERT:"):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

prompt = st.chat_input("Ask for database stats, or ask for lifestyle budget advice...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Supervisor is routing your request..."):
            
            formatted_history = []
            for m in st.session_state.messages:
                if m["role"] == "user":
                    formatted_history.append(HumanMessage(content=m["content"]))
                elif m["role"] == "assistant":
                    formatted_history.append(AIMessage(content=m["content"]))
            
            try:
                final_state = app_graph.invoke({"messages": formatted_history})
                final_response = final_state["messages"][-1].content
                
                st.markdown(final_response)
                st.session_state.messages.append({"role": "assistant", "content": final_response})
                
            except Exception as e:
                st.error(f"Routing Error: {e}")
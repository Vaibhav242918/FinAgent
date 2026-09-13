import sqlite3
from datetime import datetime
from langchain_core.tools import tool

@tool
def calculate_savings(income: float, expenses: float) -> float:
    """Calculate monthly savings by subtracting expenses from income."""
    print(f"\n[TOOL] Calculating savings: {income} - {expenses}")
    return income - expenses

@tool
def calculate_required_monthly_saving(target_amount: float, months_remaining: int) -> float:
    """Calculate how much money needs to be saved per month to reach a target goal."""
    print(f"\n[TOOL] Calculating required savings for target: {target_amount} over {months_remaining} months")
    if months_remaining <= 0:
        return 0.0
    return target_amount / months_remaining

@tool
def check_goal_feasibility(monthly_savings_capacity: float, required_monthly_saving: float) -> str:
    """Check if a financial goal is realistic based on current savings capacity."""
    print(f"\n[TOOL] Checking feasibility: Capacity ({monthly_savings_capacity}) vs Required ({required_monthly_saving})")
    if monthly_savings_capacity >= required_monthly_saving:
        return "Goal is feasible! You are saving enough."
    else:
        shortfall = required_monthly_saving - monthly_savings_capacity
        return f"Goal is not feasible. You have a monthly shortfall of {shortfall}."

@tool
def fetch_expenses() -> str:
    """Fetch all recorded expenses from the database so you can analyze the user's spending."""
    print("\n[TOOL] Fetching expenses from SQLite database...")
    conn = sqlite3.connect("finagent.db")
    cursor = conn.cursor()
    cursor.execute("SELECT category, amount, date FROM expenses")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "No expenses found in the database."
    
    result = "User Expenses:\n"
    for row in rows:
        result += f"- {row[0]}: ₹{row[1]} on {row[2]}\n"
    return result

@tool
def log_expense(category: str, amount: float) -> str:
    """Log a new expense into the database. Use this when the user says they bought or paid for something."""
    print(f"\n[TOOL] Logging expense: {category} - ₹{amount}")
    
    conn = sqlite3.connect("finagent.db")
    cursor = conn.cursor()
    date_today = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)', (category, amount, date_today))
    conn.commit()
    conn.close()
    
    return f"Successfully logged ₹{amount} for {category} on {date_today}."

@tool
def delete_last_expense() -> str:
    """Deletes the most recently logged expense from the database. Use this when the user asks to undo, remove, or delete their last expense."""
    print("\n[TOOL] Deleting last expense...")
    conn = sqlite3.connect("finagent.db")
    cursor = conn.cursor()
    
    # Find the most recent expense
    cursor.execute("SELECT rowid, category, amount FROM expenses ORDER BY rowid DESC LIMIT 1")
    last_exp = cursor.fetchone()
    
    if last_exp:
        # Delete it using its hidden rowid
        cursor.execute("DELETE FROM expenses WHERE rowid = ?", (last_exp[0],))
        conn.commit()
        conn.close()
        return f"Successfully deleted the last expense: ₹{last_exp[2]} for {last_exp[1]}."
    else:
        conn.close()
        return "No expenses found to delete."
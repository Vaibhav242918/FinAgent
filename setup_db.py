import sqlite3

def init_db():
    # Connect to a local file (creates it if it doesn't exist)
    conn = sqlite3.connect("finagent.db")
    cursor = conn.cursor()

    # Create an Expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            amount REAL,
            date TEXT
        )
    ''')

    # Clear old data (for testing) and insert September 2026 sample data
    cursor.execute('DELETE FROM expenses')
    sample_expenses = [
        ("Food", 5000, "2026-09-01"),
        ("Shopping", 7000, "2026-09-05"),
        ("Transport", 3000, "2026-09-10"),
        ("Food", 1500, "2026-09-12")
    ]
    
    cursor.executemany('INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)', sample_expenses)
    
    conn.commit()
    conn.close()
    print("✅ Database 'finagent.db' initialized with sample expenses!")

if __name__ == "__main__":
    init_db()
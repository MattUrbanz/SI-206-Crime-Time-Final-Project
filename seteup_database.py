import sqlite3
import os

# Define the database name and path
DATABASE_NAME = "crime_time_database.db"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)

# Create the connection and cursor objects
conn = sqlite3.connect(DATABASE_PATH)
cur = conn.cursor()

# Optional: Create a test table (can be removed or modified later)
cur.execute('''
    CREATE TABLE IF NOT EXISTS test_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

print(f"Database '{DATABASE_NAME}' created successfully in the current directory.")

# Close the connection
conn.close()

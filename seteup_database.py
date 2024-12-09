import sqlite3
import os

# Define the database name and path
DATABASE_NAME = "crime_time_database.db"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)

# Create the connection and cursor objects
conn = sqlite3.connect(DATABASE_PATH)
cur = conn.cursor()


# Create integer key table if it doesn't exist
cur.execute('''
    CREATE TABLE IF NOT EXISTS SportKey (
        id INTEGER PRIMARY KEY,
        sport TEXT NOT NULL
    )
''')

# Insert records into the SportKey table
cur.execute('''
    SELECT 1 FROM SportKey WHERE id = ?
            ''', (1,))
if not cur.fetchone():
    cur.execute('''
        INSERT INTO SportKey (id, sport) VALUES (?, ?)
    ''', (1, 'Baseball'))

    cur.execute('''
        INSERT INTO SportKey (id, sport) VALUES (?, ?)
    ''', (2, 'Football'))
    conn.commit()

print(f"Database '{DATABASE_NAME}' created successfully in the current directory.")

# Close the connection
conn.close()

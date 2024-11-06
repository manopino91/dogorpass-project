import sqlite3

# Create a new database or connect to an existing one
connection = sqlite3.connect('ufc_analysis.db')
cursor = connection.cursor()

# Create a table (if it doesn't already exist)
cursor.execute("""
CREATE TABLE IF NOT EXISTS podcast_analysis (
    id INTEGER PRIMARY KEY,
    video_id TEXT,
    event_name TEXT,
    fighter_picks TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Commit changes and close the connection
connection.commit()
connection.close()

print("Database and table created successfully.")

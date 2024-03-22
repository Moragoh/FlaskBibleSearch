import json
import os
import sqlite3
import time

NT_FILE_PATH = './EN/NT'
OT_FILE_PATH = './EN/OT'

# Function to insert JSON data into the SQLite database
def insert_data(file_path):
    with open(file_path) as f:
        data = json.load(f)
        for chapter in data['chapters']:
            for verse in chapter['verses']:
                cursor.execute('''INSERT INTO verses (book, chapter, verse, content)
                                  VALUES (?, ?, ?, ?)''', (data['bookName'], int(chapter['chapter']), int(verse['verse']), verse['content']))


def create_bible_db():
    # Insert data from JSON files to the SQLite database
    # Insert New Testament
    for file_name in os.listdir(NT_FILE_PATH):
        if file_name.endswith('.json'):
            insert_data(os.path.join(NT_FILE_PATH, file_name))

    # Insert Old Testament
    for file_name in os.listdir(OT_FILE_PATH):
        if file_name.endswith('.json'):
            insert_data(os.path.join(OT_FILE_PATH, file_name))

# Search for a keyword in the SQLite database
def search_keywords(keyword):
    cursor.execute('''SELECT * FROM verses WHERE content LIKE ?''', ('%' + keyword.lower() + '%',))
    results = cursor.fetchall()
    return results

"""Database setup"""
# Connect to the SQLite database
conn = sqlite3.connect('bible.db')
cursor = conn.cursor()

# Create a table to store Bible verses
cursor.execute('''CREATE TABLE IF NOT EXISTS verses
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              book TEXT,
              chapter INTEGER,
              verse INTEGER,
              content TEXT)''')

# Commit changes and close the connection
conn.commit()


# Delete all rows from the verses table
# Temporary: Clearing the database so you don't get duplicates--actual deployment version will have a more efficient solutoon
cursor.execute('''DELETE FROM verses''')
create_bible_db()

# Example usage
keywords = 'Grace of God'

# Record the start time
start_time = time.time()

results = search_keywords(keywords)
print(results)

elapsed_time = time.time() - start_time
print(f"ELAPSED TIME: {elapsed_time} seconds")

# Commit changes and close the connection
conn.commit()
conn.close()

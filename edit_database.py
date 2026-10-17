import sqlite3
from werkzeug.security import generate_password_hash

connection = sqlite3.connect("sqlite.db", check_same_thread=False)
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE
);
''')

try:
    cursor.execute('ALTER TABLE post ADD author_id INTEGER;')
except sqlite3.OperationalError:
    pass

try:
    cursor.execute('ALTER TABLE user ADD COLUMN email TEXT UNIQUE;')
except sqlite3.OperationalError:
    pass

cursor.execute("UPDATE user SET email = 'example@example.com' WHERE id = 1;")

cursor.execute('SELECT * FROM user WHERE id = 1;')
user = cursor.fetchone()

if not user:
    cursor.execute('INSERT INTO user (username, password_hash, email) VALUES (?, ?, ?)',
                   ('Rocket', generate_password_hash('qwerty123'), 'example@example.com'))

cursor.execute('UPDATE post SET author_id = 1;')

connection.commit()
connection.close()
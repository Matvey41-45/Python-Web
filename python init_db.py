import sqlite3

connection = sqlite3.connect("sqlite.db")
cursor = connection.cursor()

# Создаем правильную таблицу пользователей
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE
);
''')

# Создаем правильную таблицу постов
cursor.execute('''
CREATE TABLE IF NOT EXISTS post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL
);
''')

# Создаем правильную таблицу лайков
cursor.execute('''
CREATE TABLE IF NOT EXISTS [like] (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL
);
''')

connection.commit()
connection.close()
print("База данных успешно создана с правильной структурой!")
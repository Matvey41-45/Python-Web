import sqlite3

# Этот код сам создаст чистый и правильный файл sqlite.db
connection = sqlite3.connect("sqlite.db")
cursor = connection.cursor()

# Таблица пользователей (с полем email)
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE
);
''')

# Таблица постов
cursor.execute('''
CREATE TABLE IF NOT EXISTS post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL
);
''')

# Таблица лайков
cursor.execute('''
CREATE TABLE IF NOT EXISTS [like] (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL
);
''')

connection.commit()
connection.close()
print("Новая база данных sqlite.db успешно создана!")
import sqlite3

# Создаем соединение с БД и курсор для работы с ней
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Создаем таблицу для тем
cursor.execute('''CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_name TEXT NOT NULL
)''')

# Создаем таблицу для содержимого тем
cursor.execute('''CREATE TABLE IF NOT EXISTS topic_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER,
    content TEXT,
    FOREIGN KEY (topic_id) REFERENCES topics(id)
)''')

#
cursor.execute('''CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    link TEXT,
    category TEXT
)''')

conn.commit()
conn.close()
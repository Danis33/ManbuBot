import sqlite3
from datetime import datetime, timedelta

# Создаем соединение с БД и курсор для работы с ней
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Создаем таблицу для сохранения задания пользователя
cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task_text TEXT,
    reminder_time TEXT
)''')

# Создаем таблицу для сохранения тем пользователя
cursor.execute('''CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_name TEXT NOT NULL
)''')

# Создаем таблицу для содержимого тем пользователя
cursor.execute('''CREATE TABLE IF NOT EXISTS topic_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER,
    content TEXT,
    FOREIGN KEY (topic_id) REFERENCES topics(id)
)''')

#  Создаем таблицу для учебного материала
cursor.execute('''CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    link TEXT,
    category TEXT
)''')

#  Создаем таблицу для цветных меток
cursor.execute('''CREATE TABLE IF NOT EXISTS task_labels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emoji TEXT NOT NULL,
    label TEXT NOT NULL,
    description TEXT,
    task_id INTEGER UNIQUE,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
)''')

conn.commit()
conn.close()

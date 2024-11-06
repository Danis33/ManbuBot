import sqlite3


# Функция для добавления задачи в базу данных
def add_task_to_db(user_id, task_text):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (user_id, task_text) VALUES (?, ?)', (user_id, task_text))
    conn.commit()
    conn.close()


# Функция для получения списка задач из базы данных
def get_tasks_from_db(user_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT id, task_text FROM tasks WHERE user_id = ?', (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks


# Функция для удаления задачи из базы данных по ID
def delete_task_from_db(task_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()


# Подключение к базе данных и получение списка ресурсов
def get_all_resources():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT name, description, link, category FROM resources")
    resources = cursor.fetchall()
    conn.close()
    return resources


# Получение ресурсов по категории
def get_resources_by_category(category):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT name, description, link FROM resources WHERE category=?", (category,))
    resources = cursor.fetchall()
    conn.close()
    return resources

import sqlite3


# Функция для добавления задачи в базу данных
def add_task_to_db(user_id, task_text, reminder_time):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (user_id, task_text, reminder_time) VALUES (?, ?, ?)',
                   (user_id, task_text, reminder_time))
    conn.commit()
    conn.close()


# Функция для отображения всех заданий с динамической нумерацией
def show_tasks():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT task_text FROM tasks ORDER BY id')
    tasks = cursor.fetchall()
    return [f"{index + 1}. {title[0]}" for index, title in enumerate(tasks)]


# Функция для получения списка задач из базы данных
def get_tasks_from_db(user_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT id, task_text FROM tasks WHERE user_id = ?', (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks


# Функция для удаления задания по его порядковому номеру
def delete_task(order_number):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM tasks ORDER BY id')
    tasks = cursor.fetchall()

    if 0 < order_number <= len(tasks):
        task_id = tasks[order_number - 1][0]
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        return True
    return False


# Подключение к базе данных и получение списка ресурсов
def get_resources():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM resources")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories


# Получение ресурсов по категории
def get_resources_by_category(category):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT name, description, link FROM resources WHERE category=?", (category,))
    resources = cursor.fetchall()
    conn.close()
    return resources


def save_label_to_db(task_id, label, emoji):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO task_labels (task_id, label, emoji) VALUES (?, ?, ?)
    ON CONFLICT(task_id) DO UPDATE SET label=excluded.label, emoji=excluded.emoji""",
                   (task_id, label, emoji))
    conn.commit()
    conn.close()

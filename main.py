import telebot
import os
import asyncio
import sqlite3

from telebot import types
from dotenv import load_dotenv
from list import (add_task_to_db,
                  get_tasks_from_db,
                  delete_task_from_db,
                  get_all_resources,
                  get_resources_by_category)

load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN'))

user_states = {}


# Функция для удаления задачи из базы данных по ID
@bot.message_handler(commands=['start'])
def get_start(message):
    bot.send_message(message.chat.id,
                     'Привет! Я помогу тебе с учебой.\n'
                     'Добавляй задания с помощью команды /add.\n'
                     'Добавляй свою тему для изучения с помощью команды /add_topic.\n'
                     'Введи /help для просмотра команд.')


@bot.message_handler(commands=['help'])
def to_help(message):
    bot.send_message(message.chat.id,
                     'Для создания задания введите команду /add.\n'
                     'Для просмотра списка введите команду /list.\n'
                     'Для удаления задания введите команду /delete.\n'
                     'Для добавления новой темы введите команду /add_topic.\n'
                     'Для добавления добавления информации для темы введите команду /add_info\n'
                     'Для просмотра добавленной информации в выбранной теме введите команду /view_info\n')


# Команда для добавления новой задачи
@bot.message_handler(commands=['add'])
def get_add_task(message):
    bot.send_message(message.chat.id, 'Напиши задачу, которую нужно добавить:')
    bot.register_next_step_handler(message, save_task)


def save_task(message):
    task_text = message.text  # Получаем текст задачи от пользователя
    user_id = message.from_user.id  # Идентификатор пользователя Telegram
    add_task_to_db(user_id, task_text)  # Сохраняем задачу в базе данных
    bot.send_message(message.chat.id, f"Задача '{task_text}' добавлена!")


@bot.message_handler(commands=['list'])
def list_tasks(message):
    user_id = message.from_user.id
    tasks = get_tasks_from_db(user_id)  # Получаем задачи пользователя из базы данных
    if tasks:
        task_list = "\n".join(f"{task[0]}. {task[1]}" for task in tasks)
        bot.send_message(message.chat.id, f"Текущие задачи:\n{task_list}")
    else:
        bot.send_message(message.chat.id, "Список задач пуст.")


@bot.message_handler(commands=['delete'])
def delete_task(message):
    user_id = message.from_user.id
    tasks = get_tasks_from_db(user_id)
    if tasks:
        task_list = "\n".join(f"{task[0]}. {task[1]}" for task in tasks)
        bot.send_message(message.chat.id, f"Выберите номер задачи для удаления:\n{task_list}")
        bot.register_next_step_handler(message, get_task_number)
    else:
        bot.send_message(message.chat.id, "Список задач пуст.")


def get_task_number(message):
    if message.text.isdigit():  # Проверяем, что введено число
        task_id = int(message.text)
        delete_task_from_db(task_id)
        bot.send_message(message.chat.id, f"Задача {task_id} удалена.")
    else:
        bot.send_message(delete_message.chat.id, "Некорректный ввод. Пожалуйста, введите номер задачи.")


@bot.message_handler(commands=['add_topic'])
def what_book(message):
    bot.send_message(message.chat.id, 'Введите название новой темы:')
    bot.register_next_step_handler(message, save_topic)


# Сохранение темы в базе данных
def save_topic(message):
    topic_name = message.text
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO topics (topic_name) VALUES (?)", (topic_name,))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"Тема '{topic_name}' успешно добавлена!")


# Команда для выбора темы и добавления информации к ней
@bot.message_handler(commands=['add_info'])
def topic_info(message):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topics")
    topics = cursor.fetchall()
    conn.close()

    # Проверяем, есть ли темы в БД
    if not topics:
        bot.send_message(message.chat.id, "Список тем пуст. Сначала добавьте новую тему с помощью команды /add_topic.")
        return

    # Формируем и отправляем список тем
    response = "Выберите тему для добавления информации:\n"
    for topic in topics:
        response += f"{topic[0]}. {topic[1]}\n"
    bot.send_message(message.chat.id, response)

    # Переходим к следующему шагу - обработка выбора темы
    bot.register_next_step_handler(message, get_topic_id)


# Обработка выбора темы и запрос на добавление информации
def get_topic_id(message):
    try:
        topic_id = int(message.text)
        user_states[message.chat.id] = topic_id  # Сохраняем ID темы для пользователя
        bot.send_message(message.chat.id, "Введите информацию, которую хотите добавить к теме:")
        bot.register_next_step_handler(message, save_content)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите номер темы.")
        bot.register_next_step_handler(message, get_topic_id)


# Сохранение информации по теме
def save_content(message):
    content = message.text
    topic_id = user_states.get(message.chat.id)

    # Сохранение информации в базе данных
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO topic_content (topic_id, content) VALUES (?, ?)", (topic_id, content))
    conn.commit()
    conn.close()

    bot.send_message(message.chat.id, "Информация успешно добавлена!")


@bot.message_handler(commands=['view_info'])
def view_info(message):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topics")
    topics = cursor.fetchall()
    conn.close()

    # Проверяем, есть ли темы в базе данных
    if not topics:
        bot.send_message(message.chat.id, "Список тем пуст. Сначала добавьте новую тему с помощью команды /add_topic.")
        return

    # Формируем и отправляем список тем пользователю
    response = "Выберите тему, чтобы просмотреть информацию по ней:\n"
    for topic in topics:
        response += f"{topic[0]}. {topic[1]}\n"
    bot.send_message(message.chat.id, response)

    # Переходим к следующему шагу, где пользователь выбирает тему
    bot.register_next_step_handler(message, show_topic_content)


# Обработка выбора темы для отображения связанной с ней информации
def show_topic_content(message):
    try:
        topic_id = int(message.text)  # Получаем ID выбранной темы
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()

        # Запрашиваем информацию по выбранной теме
        cursor.execute("SELECT content FROM topic_content WHERE topic_id = ?", (topic_id,))
        contents = cursor.fetchall()
        conn.close()

        # Проверяем, есть ли записи для выбранной темы
        if not contents:
            bot.send_message(message.chat.id, "Для этой темы пока нет сохранённой информации.")
        else:
            # Отправляем всю информацию, связанную с выбранной темой
            response = "Информация по выбранной теме:\n"
            for content in contents:
                response += f"- {content[0]}\n"
            bot.send_message(message.chat.id, response)

    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный номер темы.")
        bot.register_next_step_handler(message, show_topic_content)


@bot.message_handler(commands=['resources'])
def ask_category(message):
    bot.send_message(message.chat.id, "Введите категорию для поиска ресурсов:")


@bot.message_handler(func=lambda message: True)
def send_resources_by_category(message):
    category = message.text
    resources = get_resources_by_category(category)
    if resources:
        response = ""
        for res in resources:
            name, description, link = res
            response += f"🔹 {name}\n📖 {description}\n🔗 [Ссылка]({link})\n\n"
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, f"Ресурсы в категории '{category}' не найдены.")


# Для просмотра работы инфорации пользователя в телеграмме
@bot.message_handler(commands=['admin'])
def admins(message):
    bot.send_message(message.chat.id, message)


bot.polling(non_stop=True)

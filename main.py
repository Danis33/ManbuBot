import telebot
import os
import sqlite3

from telebot import types
from dotenv import load_dotenv
from list import *

load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN'))

user_states = {}


# Функция для взаимодеиствия с ботом
@bot.message_handler(commands=['start', 'Начать'])
def get_start(message):
    # Создаём клавиатуру с основными кнопками
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("Помощь"))
    markup.add(
        types.KeyboardButton("Создать задание"),
        types.KeyboardButton("Создать тему"),
        types.KeyboardButton("Посмотреть задания"),
        types.KeyboardButton("Посмотреть темы"),
        types.KeyboardButton("Удалить задание"),
        types.KeyboardButton("Добавить информацию к теме"),
    )
    markup.add(types.KeyboardButton("Учебные материалы"))

    bot.send_message(message.chat.id, "Добро пожаловать! Выберите нужный раздел:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Помощь")
def to_help(message):
    send_help_message(message.chat.id)


# Функция для отправки сообщения помощи
def send_help_message(chat_id):
    help_text = (
        "📚 *Навигация по боту - Помощь*\n\n"
        "🔹 *Задания* - позволяет создать новое задание или посмотреть сохранённые задания.\n"
        "    - Создать задание: введи задание, и оно будет сохранено.\n"
        "    - Посмотреть задания: просмотр всех твоих сохранённых заданий.\n"
        "    - Удалить задание: выбирите номер задания которое хотите удалить.\n\n"
        "🔹 *Темы* - добавляет и сохраняет учебные темы, к которым можно добавлять текстовую информацию.\n"
        "    - Создать тему: введи название темы, чтобы создать новую.\n"
        "    - Посмотреть темы: просмотр всех твоих тем и добавленных к ним материалов.\n"
        "    - Удалить тему: выбирите номер темы для ее удаления.\n\n"
        "🔹 *Учебные материалы* - быстрый доступ к списку полезных учебных ресурсов и ссылок из интернета.\n"
        "    - Выбери категорию материала (например, Математика, Языки и т.д.), чтобы получить ссылки.\n\n"
        "🔹 *Помощь* - информация о том, как работает бот и что делает каждая кнопка.\n"
    )
    bot.send_message(chat_id, help_text, parse_mode="Markdown")


# Команда для добавления новой задачи
@bot.message_handler(func=lambda message: message.text == "Создать задание")
def get_add_task(message):
    bot.send_message(message.chat.id, 'Напиши задачу, которую нужно добавить:')
    bot.register_next_step_handler(message, save_task)


def save_task(message):
    task_text = message.text  # Получаем текст задачи от пользователя
    user_id = message.from_user.id  # Идентификатор пользователя Telegram
    add_task_to_db(user_id, task_text)  # Сохраняем задачу в базе данных
    bot.send_message(message.chat.id, f"Задача '{task_text}' добавлена!")


@bot.message_handler(func=lambda message: message.text == "Посмотреть задания")
def list_tasks(message):
    tasks = show_tasks()
    if tasks:
        task_list = "\n".join(tasks)
        bot.send_message(message.chat.id, f"Ваши задания:\n{task_list}")
    else:
        bot.send_message(message.chat.id, "Список заданий пуст.")


@bot.message_handler(func=lambda message: message.text == "Удалить задание")
def delete(message):
    tasks = show_tasks()
    if tasks:
        task_list = "\n".join(tasks)
        msg = bot.send_message(message.chat.id, f"Выберите номер задания для удаления:\n{task_list}")
        bot.register_next_step_handler(msg, delete_task_handler)
    else:
        bot.send_message(message.chat.id, "Список заданий пуст.")


def delete_task_handler(message):
    try:
        order_number = int(message.text)  # Убедитесь, что это целое число
        if delete_task(order_number):
            bot.send_message(message.chat.id, f"Задание номер {order_number} удалено.")
        else:
            bot.send_message(message.chat.id, "Задание с таким номером не найдено.")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный номер задания.")


@bot.message_handler(func=lambda message: message.text == "Создать тему")
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
@bot.message_handler(func=lambda message: message.text == "Добавить информацию к теме")
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


@bot.message_handler(func=lambda message: message.text == "Посмотреть темы")
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


@bot.message_handler(func=lambda message: message.text == "Учебные материалы")
def send_category_buttons(message):
    # Получаем список категорий
    categories = get_resources()
    if not categories:
        bot.send_message(message.chat.id, "Категории не найдены.")
        return

    # Создаем клавиатуру с кнопками для каждой категории
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for category in categories:
        markup.add(types.KeyboardButton(category))

    markup.add(types.KeyboardButton("Назад в главное меню"))

    # Отправляем сообщение с кнопками
    bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=markup)


# Обработчик для кнопки "Назад в главное меню"
@bot.message_handler(func=lambda message: message.text == "Назад в главное меню")
def go_back_to_main_menu(message):
    get_start(message)


# Обработчик нажатия кнопок с категориями
@bot.message_handler(func=lambda message: message.text in get_resources())
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

        # Убираем клавиатуру после выбора
        bot.send_message(message.chat.id, "Вы выбрали категорию: " + category, reply_markup=types.ReplyKeyboardRemove())


# Для просмотра работы инфорации пользователя в телеграмме
@bot.message_handler(commands=['message'])
def admins(message):
    bot.send_message(message.chat.id, message)


bot.polling(non_stop=True)

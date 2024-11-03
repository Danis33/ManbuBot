import telebot
import os
import asyncio
import sqlite3

from dotenv import load_dotenv
from list import add_task_to_db, get_tasks_from_db, delete_task_from_db

load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN'))


# Функция для удаления задачи из базы данных по ID
@bot.message_handler(commands=['start'])
def get_start(message):
    bot.send_message(message.chat.id,
                     'Привет! Я помогу тебе с учебой. Добавляй задания с помощью команды /add.\n'
                     'Введи /help для просмотра команд.')


@bot.message_handler(commands=['help'])
def to_help(message):
    bot.send_message(message.chat.id,
                     'Для создания задания введите команду /add.\n'
                     'Для просмотра списка введите команду /list.\n'
                     'Для удаления задания введите команду /delete.\n')


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


bot.polling(non_stop=True)

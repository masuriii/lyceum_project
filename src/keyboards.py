import sqlite3
from typing import Optional

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, \
    InlineKeyboardButton, InlineKeyboardMarkup

lang_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Python🐍", callback_data="python")]
])


def show_courses(courses: list[sqlite3.Row]):
    buttons = []
    for course in courses:
        title = course["title"]
        id_ = course["id"]
        buttons.append(InlineKeyboardButton(title, callback_data=f"course:{id_}"))
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        *[[button] for button in buttons]
    ])
    return keyboard


course_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Назад", callback_data="back")]
])

admin_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton("Добавить курс")],
    [KeyboardButton("Удалить курс")]
])

cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton("Отмена")]
])
skip_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton("Пропустить")],
    [KeyboardButton("Отмена")],
])


def admin_show_courses(courses: list[sqlite3.Row]):
    buttons = []
    for course in courses:
        title = course["title"]
        id_ = course["id"]
        buttons.append(InlineKeyboardButton(title, callback_data=f"delete_course:{id_}"))
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        *[[button] for button in buttons]
    ])
    return keyboard

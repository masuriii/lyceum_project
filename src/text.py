import sqlite3

welcome_text = "Привет! Я бот-помощник в изучении программирования! Выбери язык и приступай к познанию гениального"

lang_chosen = "Отлично, вы выбрали язык <b>{}</b>!"

decs = {
    "python": """Python — это высокоуровневый, интерпретируемый язык программирования, созданный Гвидо ван Россумом в 1991 году. Он обладает простым и читаемым синтаксисом, что делает его популярным среди начинающих и опытных программистов. Python является мультипарадигмальным языком, поддерживающим объектно-ориентированное, структурное и функциональное программирование.

Python широко используется в различных областях, таких как веб-разработка, научные исследования, анализ данных, искусственный интеллект, автоматизация и многих других. Благодаря большому количеству сторонних библиотек и пакетов, Python стал одним из самых гибких и мощных языков программирования."""
}

bot_descs = {
    "python": [
        "Со мной ты сможешь с лёгкостью освоить основы языка, базовые структуры. Мне очень нравится помогать тебе!",
        "Сейчас я отправлю тебе базу всех моих знаний по этому языку!"]
}

show_courses = "Тыкай на любую тему, которая тебе нужна!"


def show_course(course: sqlite3.Row):
    title = course["title"]
    text_ = course["text"]
    examples = course["examples"] or None
    additional_link = course["additional_link"] or None
    if additional_link:
        additional_link = additional_link.split(",")
    nl_char = "\n"

    course_text = f"""<b>{title}</b>

{text_}{f"{nl_char}{nl_char}Примеры:{nl_char}<code>{examples}</code>" if examples else ""}{f"{nl_char}{nl_char}<b>Дополнительные ссылки:</b>{nl_char}{nl_char.join(additional_link)}" if additional_link else ""}"""
    return course_text


admin_welcome = "Здравствуйте, хозяин ^^"


class add_course:
    title = "Хорошо, давайте добавим новый курс. Как он будет называться?"
    text = "Введите текст для курса"
    photos = "Отправьте фотографии (или пропустите этот шаг)"
    examples = "Добавьте примеры (или пропустите этот шаг)"
    additional_links = "Добавьте дополнительные ссылки (или пропустите)"

    success = "Курс успешно добавлен!"


class delete_course:
    select = "Выберите курс, который хотите удалить"

    success = "Курс успешно удалён!"
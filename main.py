import asyncio
from typing import Union, Optional
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.handler import SkipHandler
from aiogram.types import ParseMode, ContentType
from aiogram.utils import executor

from src import text, keyboards
from src.db.engine import Database

db = Database("base.db")

ADMINS = [659661273]

TOKEN = "6203612258:AAEldZkVG0S5WtTV5-Zbgt0vMekzDH_040k"
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


# States
class LangForm(StatesGroup):
    set_lang = State()


class CourseAction(StatesGroup):
    action = State()


class AddCourseForm(StatesGroup):
    set_title = State()
    set_text = State()
    set_photos = State()
    set_examples = State()
    set_links = State()


# Filters
class IsAdmin(BoundFilter):
    key = "is_admin"

    def __init__(self, is_admin: bool):
        self.is_admin = is_admin

    async def check(self, call: Union[types.Message, types.CallbackQuery]):
        return (call.from_user.id in ADMINS) == self.is_admin


dp.bind_filter(IsAdmin)


@dp.message_handler(state="*")
async def handler(message: types.Message):
    db.add_user(message.from_user.id)
    raise SkipHandler()


@dp.message_handler(commands=["start"], state="*")
async def handler(message: types.Message, state: FSMContext):
    user = db.get_user_by_userid(message.from_user.id)
    if user["language"] is None:
        await message.reply(text.welcome_text, reply_markup=keyboards.lang_kb)
        await LangForm.set_lang.set()
    else:
        courses = db.get_courses()
        msg = await message.answer(text.show_courses, reply_markup=keyboards.show_courses(courses))
        await state.update_data(prev_msg=msg)


@dp.callback_query_handler(state=LangForm.set_lang)
async def handler(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    if data == "python":
        await bot.send_message(callback.from_user.id, text.lang_chosen.format("Python"))
        db.edit_user(callback.from_user.id, language="python")
        await callback.answer()
        await state.finish()
        await asyncio.sleep(2)
        await bot.send_message(callback.from_user.id, text.decs["python"])
        descs = text.bot_descs["python"]
        for desc in descs:
            await asyncio.sleep(4.5)
            await bot.send_message(callback.from_user.id, desc)
        await asyncio.sleep(1.5)
        courses = db.get_courses()
        msg = await bot.send_message(callback.from_user.id, text.show_courses,
                                     reply_markup=keyboards.show_courses(courses))
        await state.update_data(prev_msg=msg)


@dp.callback_query_handler(text_startswith="course:", state="*")
async def handler(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    course_id = int(data.split(":")[1])
    course = db.get_course_by_id(course_id)
    if course:
        data = await state.get_data()
        prev_msg: types.Message = data.get("prev_msg", callback.message)
        await prev_msg.delete()
        images_ids = course["images_ids"] or None
        if images_ids:
            await bot.send_photo(callback.from_user.id, images_ids, text.show_course(course),
                                 reply_markup=keyboards.course_kb)
            # await bot.send_message(callback.from_user.id, "Загружаю...", reply_markup=keyboards.course_kb)
            # images_ids = images_ids.split(",")
            # group = MediaGroup()
            # for i, image_id in enumerate(images_ids):
            #     image = InputMediaPhoto(image_id)
            #     if i == 0:
            #         image.caption = text.show_course(course)
            #     group.attach(image)
            # await bot.send_media_group(callback.from_user.id, group)
        else:
            await bot.send_message(callback.from_user.id, text.show_course(course),
                                   reply_markup=keyboards.course_kb)
        await CourseAction.action.set()


@dp.callback_query_handler(text="back", state=CourseAction.action)
async def handler(callback: types.CallbackQuery, state: FSMContext):
    # msg = await message.answer("Загружаю...", reply_markup=ReplyKeyboardRemove())
    # await msg.delete()
    await callback.answer()
    courses = db.get_courses()
    msg = await bot.send_message(callback.from_user.id, text.show_courses, reply_markup=keyboards.show_courses(courses))
    await state.finish()
    await state.update_data(prev_msg=msg)


@dp.message_handler(is_admin=True, commands=["admin"], state="*")
async def handler(message: types.Message):
    await message.answer(text.admin_welcome, reply_markup=keyboards.admin_kb)


@dp.message_handler(is_admin=True, text="Добавить курс", state="*")
async def handler(message: types.Message):
    await message.answer(text.add_course.title, reply_markup=keyboards.cancel_kb)
    await AddCourseForm.set_title.set()


@dp.message_handler(is_admin=True, text="Удалить курс", state="*")
async def handler(message: types.Message, state: FSMContext):
    courses = db.get_courses()
    msg = await message.answer(text.delete_course.select, reply_markup=keyboards.admin_show_courses(courses))
    await AddCourseForm.set_title.set()
    await state.update_data(menu_msg=msg)


@dp.callback_query_handler(is_admin=True, text_startswith="delete_course:", state="*")
async def handler(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    course_id = int(data.split(":")[1])
    db.delete_course(course_id)
    data = await state.get_data()
    menu_msg: Optional[types.Message] = data.get("menu_msg")
    if menu_msg:
        courses = db.get_courses()
        await menu_msg.edit_reply_markup(keyboards.show_courses(courses))
    await callback.answer(text.delete_course.success)
    # await bot.send_message(callback.from_user.id, text.delete_course.success)
    # await callback.answer()


@dp.message_handler(is_admin=True, text="Отмена", state="*")
async def handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer(text.admin_welcome, reply_markup=keyboards.admin_kb)


@dp.message_handler(is_admin=True, state=AddCourseForm.set_title)
async def handler(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(text.add_course.text)
    await AddCourseForm.set_text.set()


@dp.message_handler(is_admin=True, state=AddCourseForm.set_text)
async def handler(message: types.Message, state: FSMContext):
    await state.update_data(text=message.html_text)
    await message.answer(text.add_course.photos, reply_markup=keyboards.skip_kb)
    await AddCourseForm.set_photos.set()


@dp.message_handler(is_admin=True, state=AddCourseForm.set_photos, content_types=ContentType.ANY)
async def handler(message: types.Message, state: FSMContext):
    if message.text == "Пропустить":
        await message.answer(text.add_course.examples)
        await AddCourseForm.set_examples.set()
        return
    photo = message.photo
    if photo:
        photo = photo[0]
        await state.update_data(photo_ids=photo.file_id)
        await message.answer(text.add_course.examples)
        await AddCourseForm.set_examples.set()
    else:
        ...


@dp.message_handler(is_admin=True, state=AddCourseForm.set_examples)
async def handler(message: types.Message, state: FSMContext):
    if message.text == "Пропустить":
        await message.answer(text.add_course.additional_links)
        await AddCourseForm.set_links.set()
        return
    await state.update_data(examples=message.text)
    await message.answer(text.add_course.additional_links)
    await AddCourseForm.set_links.set()


@dp.message_handler(is_admin=True, state=AddCourseForm.set_links)
async def handler(message: types.Message, state: FSMContext):
    if message.text == "Пропустить":
        ...
    else:
        await state.update_data(links=message.text)
    data = await state.get_data()
    title = data["title"]
    text_ = data["text"]
    photo_ids = data.get("photo_ids")
    examples = data.get("examples")
    links = data.get("links")
    db.add_course(title, text_, photo_ids, examples, links)
    await message.answer(text.add_course.success)
    await state.reset_data()
    await state.finish()
    await message.answer(text.admin_welcome, reply_markup=keyboards.admin_kb)

if __name__ == '__main__':
    executor.start_polling(dp)

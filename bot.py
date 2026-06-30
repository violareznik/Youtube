import asyncio
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

BASE_DIR = Path(__file__).parent

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

IMG = {
    "start": "welcome_banner.png",
    "mentor": "mentor_card.png",
    "courses": "courses_banner.png",
    "course_start": "course_start.png",
    "course_money": "course_money.png",
    "course_mentor": "course_mentor.png",
    "learn": "learn_card.png",
    "program": "program_card.png",
    "system": "system_card.png",
    "final": "final_card.png",
    "price": "price_card.png",
    "free": "free_lesson.png",
    "apply": "apply_card.png",
    "contact": "contact_card.png",
    "success": "success_card.png",
}

PDF_FILE = "free_youtube_lesson.pdf"


def file(name: str) -> FSInputFile:
    return FSInputFile(BASE_DIR / IMG[name])


def pdf() -> FSInputFile:
    return FSInputFile(BASE_DIR / PDF_FILE)


def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="👨‍🏫 Обо мне", callback_data="about")
    kb.button(text="🎓 Курсы", callback_data="courses")
    kb.button(text="💰 Прайс", callback_data="price")
    kb.button(text="🎁 Бесплатный урок", callback_data="free")
    kb.button(text="📩 Оставить заявку", callback_data="apply")
    kb.button(text="📞 Контакты", callback_data="contacts")
    kb.adjust(2, 2, 1, 1)
    return kb.as_markup()


def back_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад в меню", callback_data="menu")
    return kb.as_markup()


def courses_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 YouTube с нуля", callback_data="course_start")
    kb.button(text="💸 Монетизация YouTube", callback_data="course_money")
    kb.button(text="👑 Наставничество", callback_data="course_mentor")
    kb.button(text="📚 Что входит в обучение", callback_data="program")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def course_actions(course_code: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Смотреть прайс", callback_data="price")
    kb.button(text="📩 Оставить заявку", callback_data=f"apply_{course_code}")
    kb.button(text="⬅️ Назад к курсам", callback_data="courses")
    kb.adjust(1)
    return kb.as_markup()


def price_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Выбрать Стандарт", callback_data="apply_standard")
    kb.button(text="🔥 Выбрать PRO", callback_data="apply_pro")
    kb.button(text="👑 Выбрать Наставничество", callback_data="apply_mentor")
    kb.button(text="⬅️ Назад в меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def contact_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="💬 Telegram", url="https://t.me/your_username")
    kb.button(text="📸 Instagram", url="https://instagram.com/your_instagram")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


class Application(StatesGroup):
    name = State()
    username = State()
    goal = State()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer_photo(
        photo=file("start"),
        caption="👋 <b>Добро пожаловать в YouTube Money Academy</b>\n\nВыберите раздел ниже:",
        reply_markup=main_menu()
    )


@dp.callback_query(F.data == "menu")
async def menu(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo=file("start"),
        caption="🏠 <b>Главное меню</b>\n\nВыберите нужный раздел:",
        reply_markup=main_menu()
    )
    await callback.answer()


@dp.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo=file("mentor"),
        caption="👨‍🏫 <b>О наставнике</b>\n\nАлександр Воронов помогает запускать YouTube-каналы, выбирать прибыльные ниши и выходить на доход.",
        reply_markup=back_menu()
    )
    await callback.answer()


@dp.callback_query(F.data == "courses")
async def courses(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo=file("courses"),
        caption="🎓 <b>Обучающие программы</b>\n\nВыберите направление:",
        reply_markup=courses_menu()
    )
    await callback.answer()


@dp.callback_query(F.data == "course_start")
async def course_start(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo=file("course_start"),
        caption="🚀 <b>YouTube с нуля</b>\n\nДля тех, кто хочет запустить канал с полного нуля.",
        reply_markup=course_actions("youtube_start")
    )
    await callback.answer()


@dp.callback_query(F.data == "course_money")
async def course_money(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo=file("course_money"),
        caption="💸 <b>Монетизация YouTube</b>\n\nРеклама, партнерки, спонсорство и дополнительные источники дохода.",
        reply_markup=course_actions("monetization")
    )
    await callback.answer()


@dp.callback_query(F.data == "course_mentor")
async def course_mentor(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo=file("course_mentor"),
        caption="👑 <b>Персональное наставничество</b>\n\nИндивидуальная стратегия, разбор канала и поддержка.",
        reply_markup=course_actions("mentoring")
    )
    await callback.answer()


@dp.callback_query(F.data == "program")
async def program(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo=file("program"),
        caption="📚 <b>Что входит в обучение</b>\n\nСоздание канала, контент, продвижение, аналитика и монетизация.",
        reply_markup=back_menu()
    )
    await callback.answer()


@dp.callback_query(F.data == "price")
async def price(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo=file("price"),
        caption="💰 <b>Прайс</b>\n\nВыберите тариф и оставьте заявку.",
        reply_markup=price_menu()
    )
    await callback.answer()


@dp.callback_query(F.data == "free")
async def free_lesson(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo=file("free"),
        caption="🎁 <b>Бесплатный урок</b>\n\nСтартовый материал по запуску YouTube-канала.",
        reply_markup=back_menu()
    )
    try:
        await callback.message.answer_document(
            document=pdf(),
            caption="📄 Бесплатный урок: <b>Первый шаг к доходу на YouTube</b>"
        )
    except Exception as e:
        logging.error(f"PDF error: {e}")
        await callback.message.answer("PDF временно недоступен.")
    await callback.answer()


@dp.callback_query(F.data == "contacts")
async def contacts(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo=file("contact"),
        caption="📞 <b>Контакты</b>\n\nСвяжитесь с нами удобным способом.",
        reply_markup=contact_menu()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("apply"))
async def apply_start(callback: CallbackQuery, state: FSMContext):
    selected = callback.data.replace("apply_", "")
    if selected == "apply":
        selected = "Не выбран"
    await state.update_data(course=selected)
    await callback.message.answer_photo(
        photo=file("apply"),
        caption="📩 <b>Оставить заявку</b>\n\nОтветьте на несколько вопросов."
    )
    await callback.message.answer("Как вас зовут?")
    await state.set_state(Application.name)
    await callback.answer()


@dp.message(Application.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Укажите ваш Telegram username или контакт для связи:")
    await state.set_state(Application.username)


@dp.message(Application.username)
async def get_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Какая у вас цель по YouTube?")
    await state.set_state(Application.goal)


@dp.message(Application.goal)
async def get_goal(message: Message, state: FSMContext):
    await state.update_data(goal=message.text)
    data = await state.get_data()

    course_names = {
        "youtube_start": "YouTube с нуля",
        "monetization": "Монетизация YouTube",
        "mentoring": "Персональное наставничество",
        "standard": "Тариф Стандарт",
        "pro": "Тариф PRO",
        "mentor": "Тариф Наставничество",
        "Не выбран": "Не выбран",
    }
    selected_course = course_names.get(data.get("course"), data.get("course", "Не выбран"))

    admin_text = (
        "📩 <b>Новая заявка</b>\n\n"
        f"👤 Имя: {data.get('name')}\n"
        f"📱 Контакт: {data.get('username')}\n"
        f"🎯 Цель: {data.get('goal')}\n"
        f"🎓 Курс/тариф: {selected_course}"
    )

    if ADMIN_ID:
        try:
            await bot.send_message(int(ADMIN_ID), admin_text)
        except Exception as e:
            logging.error(f"Admin error: {e}")

    await message.answer_photo(
        photo=file("success"),
        caption="✅ <b>Спасибо! Ваша заявка принята.</b>\n\nМенеджер свяжется с вами в ближайшее время.",
        reply_markup=main_menu()
    )
    await state.clear()


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

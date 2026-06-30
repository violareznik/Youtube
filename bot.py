import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
MEDIA_DIR = BASE_DIR / "media"
MATERIALS_DIR = BASE_DIR / "materials"

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Add BOT_TOKEN to GitHub Secrets or .env")

logging.basicConfig(level=logging.INFO)
router = Router()


@dataclass
class Course:
    title: str
    price: str
    old_price: str
    duration: str
    image: str
    short: str
    program: list[str]
    result: str


COURSES = {
    "start": Course(
        title="YouTube с нуля",
        price="$129",
        old_price="$199",
        duration="3 недели",
        image="course_start.png",
        short="Для тех, кто хочет запустить канал правильно: ниша, оформление, первые видео и контент-план.",
        program=[
            "Выбор прибыльной ниши",
            "Оформление и упаковка канала",
            "Идеи для первых видео",
            "Контент-план на 30 дней",
            "Базовая оптимизация видео",
        ],
        result="Готовый YouTube-канал, понятная ниша и план первых публикаций.",
    ),
    "money": Course(
        title="Монетизация YouTube",
        price="$199",
        old_price="$349",
        duration="4 недели",
        image="course_money.png",
        short="Для авторов, которые хотят превратить канал в источник дохода.",
        program=[
            "Партнерская программа YouTube",
            "Реклама, CPM и RPM",
            "Партнерские программы",
            "Спонсорство и бренды",
            "Дополнительные источники дохода",
        ],
        result="Понимание способов заработка и стратегия монетизации канала.",
    ),
    "mentor": Course(
        title="Персональное наставничество",
        price="$499",
        old_price="$999",
        duration="6 недель",
        image="course_mentor.png",
        short="Индивидуальная работа с наставником: разбор канала, стратегия и сопровождение.",
        program=[
            "Аудит канала или идеи",
            "Персональная стратегия роста",
            "Разбор контента и ошибок",
            "Еженедельные рекомендации",
            "План монетизации под вашу нишу",
        ],
        result="Личный маршрут запуска/роста канала и поддержка на каждом этапе.",
    ),
}


class LeadForm(StatesGroup):
    name = State()
    telegram = State()
    has_channel = State()
    goal = State()
    course = State()


def photo(name: str) -> FSInputFile:
    return FSInputFile(MEDIA_DIR / name)


def doc(name: str) -> FSInputFile:
    return FSInputFile(MATERIALS_DIR / name)


def kb_main():
    kb = InlineKeyboardBuilder()
    kb.button(text="👨‍🏫 О наставнике", callback_data="about")
    kb.button(text="🎓 Курсы", callback_data="courses")
    kb.button(text="💰 Прайс", callback_data="price")
    kb.button(text="🎁 Бесплатный урок", callback_data="free")
    kb.button(text="📚 Чему научитесь", callback_data="learn")
    kb.button(text="📩 Оставить заявку", callback_data="apply")
    kb.button(text="📞 Контакты", callback_data="contacts")
    kb.button(text="❓ FAQ", callback_data="faq")
    kb.adjust(2, 2, 2, 2)
    return kb.as_markup()


def kb_back():
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Главное меню", callback_data="menu")
    return kb.as_markup()


def kb_courses():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 YouTube с нуля", callback_data="course:start")
    kb.button(text="💰 Монетизация YouTube", callback_data="course:money")
    kb.button(text="👑 Персональное наставничество", callback_data="course:mentor")
    kb.button(text="💰 Смотреть прайс", callback_data="price")
    kb.button(text="📩 Оставить заявку", callback_data="apply")
    kb.button(text="⬅️ Главное меню", callback_data="menu")
    kb.adjust(1, 1, 1, 2, 1)
    return kb.as_markup()


def kb_after_course(code: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="📩 Заявка на этот курс", callback_data=f"lead_course:{code}")
    kb.button(text="💰 Прайс", callback_data="price")
    kb.button(text="⬅️ Все курсы", callback_data="courses")
    kb.button(text="🏠 Меню", callback_data="menu")
    kb.adjust(1, 2, 1)
    return kb.as_markup()


def kb_apply_courses():
    kb = InlineKeyboardBuilder()
    for code, course in COURSES.items():
        kb.button(text=f"{course.title} — {course.price}", callback_data=f"lead_course:{code}")
    kb.adjust(1)
    return kb.as_markup()


async def send_menu(target):
    text = (
        "<b>YouTube Money Academy</b>\n\n"
        "Демо-бот пакета <b>STANDARD</b> для эксперта, который продает обучение по YouTube.\n\n"
        "Здесь пользователь может посмотреть курсы, прайс, получить бесплатный PDF и оставить заявку."
    )
    if isinstance(target, CallbackQuery):
        await target.message.answer_photo(photo("welcome_banner.png"), caption=text, reply_markup=kb_main())
    else:
        await target.answer_photo(photo("welcome_banner.png"), caption=text, reply_markup=kb_main())


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await send_menu(message)


@router.callback_query(F.data == "menu")
async def menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await send_menu(call)
    await call.answer()


@router.callback_query(F.data == "about")
async def about(call: CallbackQuery):
    text = (
        "<b>О наставнике</b>\n\n"
        "Александр Воронов — YouTube-эксперт и наставник по запуску каналов, росту аудитории и монетизации.\n\n"
        "Фокус: каналы без лица, система контента, аналитика, партнерские программы, реклама и стабильный доход с YouTube."
    )
    await call.message.answer_photo(photo("mentor_card.png"), caption=text, reply_markup=kb_back())
    await call.answer()


@router.callback_query(F.data == "courses")
async def courses(call: CallbackQuery):
    text = (
        "<b>Обучающие программы</b>\n\n"
        "Выберите направление, которое хотите посмотреть подробнее."
    )
    await call.message.answer_photo(photo("courses_banner.png"), caption=text, reply_markup=kb_courses())
    await call.answer()


@router.callback_query(F.data.startswith("course:"))
async def course_detail(call: CallbackQuery):
    code = call.data.split(":", 1)[1]
    course = COURSES[code]
    program = "\n".join(f"• {item}" for item in course.program)
    text = (
        f"<b>{course.title}</b>\n\n"
        f"<b>Цена:</b> {course.price} <s>{course.old_price}</s>\n"
        f"<b>Длительность:</b> {course.duration}\n\n"
        f"<b>Кому подходит:</b>\n{course.short}\n\n"
        f"<b>В программе:</b>\n{program}\n\n"
        f"<b>Результат:</b>\n{course.result}"
    )
    await call.message.answer_photo(photo(course.image), caption=text, reply_markup=kb_after_course(code))
    await call.answer()


@router.callback_query(F.data == "price")
async def price(call: CallbackQuery):
    text = (
        "<b>Прайс курса</b>\n\n"
        "🚀 <b>YouTube с нуля</b> — $129\n"
        "Базовый запуск канала, ниша, оформление и первые видео.\n\n"
        "💰 <b>Монетизация YouTube</b> — $199\n"
        "Способы заработка: реклама, партнерки, спонсоры, продукты.\n\n"
        "👑 <b>Персональное наставничество</b> — $499\n"
        "Индивидуальная стратегия, разбор и сопровождение."
    )
    kb = InlineKeyboardBuilder()
    kb.button(text="📩 Выбрать тариф", callback_data="apply")
    kb.button(text="⬅️ Главное меню", callback_data="menu")
    kb.adjust(1)
    await call.message.answer_photo(photo("price_card.png"), caption=text, reply_markup=kb.as_markup())
    await call.answer()


@router.callback_query(F.data == "free")
async def free(call: CallbackQuery):
    text = (
        "<b>Бесплатный урок</b>\n\n"
        "PDF: <b>Первый шаг к доходу на YouTube</b>.\n\n"
        "Внутри: выбор ниши, оформление канала, первые видео и ошибки новичков."
    )
    await call.message.answer_photo(photo("free_lesson.png"), caption=text)
    await call.message.answer_document(
        doc("free_youtube_lesson.pdf"),
        caption="📎 Ваш бесплатный материал прикреплен.",
        reply_markup=kb_back(),
    )
    await call.answer()


@router.callback_query(F.data == "learn")
async def learn(call: CallbackQuery):
    text = (
        "<b>Чему вы научитесь</b>\n\n"
        "• создавать канал с нуля;\n"
        "• выбирать прибыльную нишу;\n"
        "• делать контент, который смотрят;\n"
        "• оптимизировать видео;\n"
        "• подключать разные источники дохода;\n"
        "• анализировать статистику и масштабироваться."
    )
    kb = InlineKeyboardBuilder()
    kb.button(text="📘 Что входит в обучение", callback_data="program")
    kb.button(text="📩 Оставить заявку", callback_data="apply")
    kb.button(text="⬅️ Главное меню", callback_data="menu")
    kb.adjust(1)
    await call.message.answer_photo(photo("learn_card.png"), caption=text, reply_markup=kb.as_markup())
    await call.answer()


@router.callback_query(F.data == "program")
async def program(call: CallbackQuery):
    text = (
        "<b>Система обучения</b>\n\n"
        "Курс построен как пошаговый путь: от выбора ниши и создания канала до монетизации, аналитики и масштабирования."
    )
    await call.message.answer_photo(photo("program_card.png"), caption=text, reply_markup=kb_back())
    await call.answer()


@router.callback_query(F.data == "contacts")
async def contacts(call: CallbackQuery):
    text = (
        "<b>Контакты</b>\n\n"
        "Telegram: @alex_ym_academy\n"
        "Instagram: @youtube_money_academy\n"
        "E-mail: info@ym-academy.com\n\n"
        "В демо-боте кнопки можно заменить на реальные ссылки клиента."
    )
    await call.message.answer_photo(photo("contact_card.png"), caption=text, reply_markup=kb_back())
    await call.answer()


@router.callback_query(F.data == "faq")
async def faq(call: CallbackQuery):
    text = (
        "<b>FAQ</b>\n\n"
        "<b>Нужен ли опыт?</b>\nНет, есть программа для полного старта с нуля.\n\n"
        "<b>Можно ли без лица?</b>\nДа, можно строить каналы без личного бренда.\n\n"
        "<b>Есть ли поддержка?</b>\nДа, в зависимости от тарифа: чат, обратная связь или личное наставничество.\n\n"
        "<b>Можно ли оплатить частями?</b>\nДля наставничества можно добавить рассрочку или оплату частями."
    )
    await call.message.answer(text, reply_markup=kb_back())
    await call.answer()


@router.callback_query(F.data == "apply")
async def apply(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(LeadForm.name)
    await call.message.answer_photo(
        photo("apply_card.png"),
        caption="<b>Оставить заявку</b>\n\nНапишите ваше имя, и бот пошагово соберет заявку.",
    )
    await call.message.answer("Как вас зовут?")
    await call.answer()


@router.callback_query(F.data.startswith("lead_course:"))
async def apply_course(call: CallbackQuery, state: FSMContext):
    code = call.data.split(":", 1)[1]
    await state.clear()
    await state.update_data(course=COURSES[code].title)
    await state.set_state(LeadForm.name)
    await call.message.answer_photo(
        photo("apply_card.png"),
        caption=f"Вы выбрали: <b>{COURSES[code].title}</b>\n\nКак вас зовут?",
    )
    await call.answer()


@router.message(LeadForm.name)
async def lead_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(LeadForm.telegram)
    await message.answer("Укажите ваш Telegram для связи. Например: @username")


@router.message(LeadForm.telegram)
async def lead_tg(message: Message, state: FSMContext):
    await state.update_data(telegram=message.text.strip())
    await state.set_state(LeadForm.has_channel)
    kb = InlineKeyboardBuilder()
    kb.button(text="Да, канал уже есть", callback_data="has_channel:yes")
    kb.button(text="Нет, начинаю с нуля", callback_data="has_channel:no")
    kb.adjust(1)
    await message.answer("У вас уже есть YouTube-канал?", reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith("has_channel:"))
async def lead_channel(call: CallbackQuery, state: FSMContext):
    value = "Да" if call.data.endswith("yes") else "Нет"
    await state.update_data(has_channel=value)
    await state.set_state(LeadForm.goal)
    await call.message.answer("Какая ваша цель? Например: запустить канал, подключить монетизацию, выйти на $1000/мес.")
    await call.answer()


@router.message(LeadForm.goal)
async def lead_goal(message: Message, state: FSMContext):
    await state.update_data(goal=message.text.strip())
    data = await state.get_data()
    if data.get("course"):
        await finish_lead(message, state)
    else:
        await state.set_state(LeadForm.course)
        await message.answer("Какой тариф/курс вам интересен?", reply_markup=kb_apply_courses())


@router.callback_query(LeadForm.course, F.data.startswith("lead_course:"))
async def lead_course_choice(call: CallbackQuery, state: FSMContext):
    code = call.data.split(":", 1)[1]
    await state.update_data(course=COURSES[code].title)
    await finish_lead(call.message, state)
    await call.answer()


async def finish_lead(message: Message, state: FSMContext):
    data = await state.get_data()
    admin_text = (
        "<b>📩 Новая заявка из YouTube Money Academy</b>\n\n"
        f"Имя: {data.get('name')}\n"
        f"Telegram: {data.get('telegram')}\n"
        f"Есть канал: {data.get('has_channel')}\n"
        f"Цель: {data.get('goal')}\n"
        f"Курс/тариф: {data.get('course', 'Не выбран')}"
    )
    if ADMIN_ID:
        try:
            await message.bot.send_message(int(ADMIN_ID), admin_text)
        except Exception as e:
            logging.warning("Admin notification failed: %s", e)

    await message.answer_photo(
        photo("success_card.png"),
        caption="✅ <b>Спасибо! Ваша заявка принята.</b>\n\nМенеджер свяжется с вами в ближайшее время.",
        reply_markup=kb_main(),
    )
    await state.clear()


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

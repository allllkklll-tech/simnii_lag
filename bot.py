import asyncio
from aiogram import Bot, Dispatcher, types ,F
from aiogram.filters import Command ,StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from dotenv import load_dotenv
import os
from datetime import datetime
load_dotenv()  # загружает переменные из .env
# ... после load_dotenv() ...

# === НОВОЕ: настройки счётчика ===
COUNTER_FILE = "counter.txt"
MAX_PARTICIPANTS = 20  # ← ЗАМЕНИ НА НУЖНОЕ КОЛИЧЕСТВО
ADMIN_CHAT_ID = 5795412174
# ===============================
def get_count_from_file():
    """Возвращает текущее количество участников из файла"""
    if not os.path.exists(COUNTER_FILE):
        return 0
    try:
        with open(COUNTER_FILE, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except:
        return 0

def save_count_to_file(count: int):
    """Сохраняет число участников в файл"""
    with open(COUNTER_FILE, "w", encoding="utf-8") as f:
        f.write(str(count))
# Путь к файлу (будет создан в папке проекта)
RESPONSES_FILE = "responses.txt"
PAYMENT_NUMBER = os.getenv("PAYMENT_NUMBER")

# Вставьте сюда ваш токен
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
class Questionnaire(StatesGroup):
    name = State()      # Спрашиваем имя
    age = State()       # Спрашиваем возраст
    payment_confirmed = State()


Inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Конечно!", callback_data="yes"), InlineKeyboardButton(text="К сожалению, нет..." ,callback_data="no")]
    ],
)

@dp.message(Command("start"))


async def send_welcome(message: types.Message ,state: FSMContext):
    await message.answer(
        "Очистка интерфейса...",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer \
        ("Приветсвую, друг! Мы крайне желаем видеть тебя на нашем новогоднем выезде, который пройдёт на базе христианского лагеря Родник, c 1 по 3 января. Итак, ждать ли тебя на этом выезде?"
        ,reply_markup=Inline_keyboard)
@dp.message(Questionnaire.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Questionnaire.age)


@dp.message(Questionnaire.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введи возраст цифрами.")
        return  # Остаёмся в том же состоянии
    await state.update_data(age=int(message.text))
    await message.answer(
        f"Замечательно, вот и познакомились. А теперь к делу - для нахождения в лагере требуется взнос в размере 1 миллиарда рублей. Да, я понимаю, что это много, но оно того стоит, поверь. Да и нужно ведь мне на что-то жить? можешь скидывать деньги по номеру {PAYMENT_NUMBER} (Озон)\n\n"
        "После перевода напиши сюда: «Оплатил» ")
    await state.set_state(Questionnaire.payment_confirmed)

    # Подтверждение оплаты


@dp.message(Questionnaire.payment_confirmed)
async def handle_payment(message: Message, state: FSMContext):
    current_count = get_count_from_file()

    if current_count >= MAX_PARTICIPANTS:
        await message.answer(
            "🚫 Извини, все места уже заняты!\n"
            "Следи за новостями — будут новые события! 🙌"
        )
        await state.clear()
        return

    if "оплатил" not in message.text.lower():
        await message.answer("Пожалуйста, напиши «Оплатил», когда переведёшь.")
        return

    try:
        data = await state.get_data()
        new_count = current_count + 1
        save_count_to_file(new_count)  # ← Сохраняем сразу!

        # Отправляем данные админу
        await save_response(data["name"], data["age"])

        # Отвечаем пользователю
        await message.answer(
            f"✅ Отлично! Ты №{new_count} из {MAX_PARTICIPANTS}!\n"
            "До встречи на новогоднем выезде! 🎄"
        )
    except Exception as e:
        print(f"Ошибка при обработке оплаты: {e}")
        await message.answer("Произошла ошибка. Попробуй позже.")
    finally:
        await state.clear()
@dp.callback_query(F.data == "no")
async def handle_no(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Очень жаль, тогда до новых встреч🙌")
    await state.clear()


@dp.callback_query(F.data == "yes")
async def handle_yes(callback: CallbackQuery, state: FSMContext):
    current_count = get_count_from_file()
    if current_count >= MAX_PARTICIPANTS:
        await callback.answer()
        await callback.message.answer(
            "🚫 Извини, все места на выезде уже заняты!\n"
            "Следи за нашими новостями — будут новые события! 🙌"
        )
        return

    await callback.answer()
    await callback.message.answer("Замечательно! Тогда ответь на ряд вопросов:\nКак тебя зовут? (Фамилия Имя)")
    await state.set_state(Questionnaire.name)

ADMIN_CHAT_ID = 5795412174  # твой ID в Telegram

async def save_response(name, age):
    report = f"✅ Новый участник:\nИмя: {name}\nВозраст: {age}"
    await bot.send_message(ADMIN_CHAT_ID, report)




async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())













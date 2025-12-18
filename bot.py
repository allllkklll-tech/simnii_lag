
import asyncio
from aiogram import Bot, Dispatcher, types,F
from aiogram.filters import Command,StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from dotenv import load_dotenv
import os
from datetime import datetime
load_dotenv()  # загружает переменные из .env
# Путь к файлу (будет создан в папке проекта)
RESPONSES_FILE = "responses.txt"


def save_response(name: str, age: int, pol: str):
    #"""Сохраняет ответ пользователя в файл"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] Имя: {name}, Возраст: {age}, Пол: {pol}\n"

    # 'a' = append (дозапись в конец)
    with open(RESPONSES_FILE, "a", encoding="utf-8") as f:
        f.write(line)
# Вставьте сюда ваш токен
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
class Questionnaire(StatesGroup):
    name = State()      # Спрашиваем имя
    age = State()       # Спрашиваем возраст
    pol = State()      # Спрашиваем город
    payment_confirmed = State()


Inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Конечно!", callback_data="yes"), InlineKeyboardButton(text="К сожалению, нет...",callback_data="no")]
    ],
)

@dp.message(Command("start"))


async def send_welcome(message: types.Message,state: FSMContext):
    await message.answer(
        "Очистка интерфейса...",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer("Приветсвую, друг! Мы крайне желаем видеть тебя на нашем новогоднем выезде, который пройдёт на базе христианского лагеря Родник, c 1 по 3 января. Итак, ждать ли тебя на этом выезде?",reply_markup=Inline_keyboard)
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
    await message.answer("Твой пол?")
    await state.set_state(Questionnaire.pol)

T = os.getenv("PAYMENT_NUMBER")
@dp.message(Questionnaire.pol)
async def process_pol(message: Message, state: FSMContext):
    await state.update_data(pol=message.text)
    await message.answer(
        f"Замечательно, вот и познакомились. А теперь к делу - для нахождения в лагере требуется взнос в размере 1 миллиарда рублей. Да, я понимаю, что это много, но оно того стоит, поверь. Да и нужно ведь мне на что-то жить? можешь скидывать деньги по номеру {T} (Озон)\n\n"
        "После перевода напиши сюда: «Оплатил» ")
    await state.set_state(Questionnaire.payment_confirmed)

    # Подтверждение оплаты


@dp.message(Questionnaire.payment_confirmed)
async def handle_payment(message: Message, state: FSMContext):
    if "оплатил" in message.text.lower():
        # Сохраняем данные в файл
        data = await state.get_data()
        save_response(data["name"], data["age"], data["pol"])

        await message.answer(
            "✅ Отлично! Я вижу твой платёж.\n"
            "До встречи на новогоднем выезде! 🎄\n"
            "Все детали пришлю ближе к дате."
        )
        await state.clear()
    else:
        await message.answer("Пожалуйста, напиши «Оплатил», когда переведёшь.")
@dp.callback_query(F.data == "no")
async def handle_no(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Очень жаль, тогда до новых встреч🙌")
    await state.clear()

@dp.callback_query(F.data == "yes")
async def handle_yes(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Замечательно! Тогда ответь на ряд вопросов:\nКак тебя зовут? (Фамилия Имя)")
    await state.set_state(Questionnaire.name)
    
ADMIN_CHAT_ID = SimonBratt  # твой ID в Telegram

async def save_response(name, age, pol):
    report = f"Новый участник:\nИмя: {name}\nВозраст: {age}\nПол: {pol}"
    await bot.send_message(ADMIN_CHAT_ID, report)




async def main():
    await dp.start_polling(bot)

if __name__ == ("__main__"):

    asyncio.run(main())


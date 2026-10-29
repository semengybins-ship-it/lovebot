import os
import json
import logging
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получаем токены из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")  # Ваш Telegram ID (число)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Ссылка на твое Mini App на GitHub Pages
WEB_APP_URL = "https://YOUR_GITHUB_USERNAME.github.io/YOUR_REPO_NAME/"


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Кнопка для открытия розовенького Mini App
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Пройти опрос 💖",
                web_app=WebAppInfo(url=WEB_APP_URL)
            )
        ]
    ])

    await message.answer(
        "Приветик ! ✨\n"
        "Помойся и пройди опрос.\n"
        "Нажми на кнопку ниже, чтобы открыть! 👇",
        reply_markup=keyboard
    )


# Обработка ответов, приходящих из Web App
@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        q_num = data.get("question_num")
        q_text = data.get("question_text")
        user_answer = data.get("answer")

        # Красивое уведомление админу (тебе)
        report_text = (
            f"💌 **Новый ответ!**\n\n"
            f"**Вопрос {q_num}:** {q_text}\n"
            f"**Ответ:** {user_answer}"
        )

        if ADMIN_ID:
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=report_text,
                parse_mode="Markdown"
            )

        # Ответ девушке в чате
        await message.answer(
            f"Окак! Ответ на вопрос №{q_num} отправлен ",
            parse_mode="Markdown"
        )

    except Exception as e:
        logging.error(f"Ошибка при обработке Web App data: {e}")


async def main():
    print("Бот успешно запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
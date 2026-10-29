import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

# 1. Загрузка переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Ссылка на твой Web App (укажи свою ссылку на GitHub Pages!)
WEB_APP_URL = "https://semengybins-ship-it.github.io/lovebot/"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 2. Заглушка веб-сервера для Render (убирает ошибку No open ports)
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    # Запускаем на порту 10000, который ожидает Render
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()

# 3. Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Пройти опрос 💖",
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ]
        ]
    )
    await message.answer(
        "Привет! Нажми на кнопку ниже, чтобы открыть пиксельный опросник ✨",
        reply_markup=keyboard
    )

# 4. Обработчик ответов из Web App
@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    try:
        # Данные из Mini App
        data = json.loads(message.web_app_data.data)
        q_num = data.get("question_num", "?")
        q_text = data.get("question_text", "")
        user_answer = data.get("answer", "")

        # Данные отправителя
        user_first_name = message.from_user.first_name or "Аноним"
        user_username = f"@{message.from_user.username}" if message.from_user.username else "без юзернейма"

        # Формируем красивое сообщение
        report_text = (
            f"💌 **Новый ответ на вопрос!**\n\n"
            f"👤 **От кого:** {user_first_name} ({user_username})\n"
            f"❓ **Вопрос {q_num}:** {q_text}\n"
            f"💬 **Ответ:** `{user_answer}`"
        )

        # Отправляем сообщение тебе (ADMIN_ID)
        if ADMIN_ID:
            await bot.send_message(
                chat_id=int(ADMIN_ID),
                text=report_text,
                parse_mode="Markdown"
            )

        # Подтверждение пользователю
        await message.answer("Спасибо! Твой ответ принят ✨")

    except Exception as e:
        print(f"Ошибка при обработке данных: {e}")

# 5. Главная функция
async def main():
    # Запускаем фоновый веб-сервер для Render
    await start_web_server()
    print("Бот и веб-сервер успешно запущены!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

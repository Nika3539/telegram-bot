import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

API_TOKEN = '7355204062:AAGxmhwKAAsO3kED8WcbprirmptgV51aOpE'
CHANNEL_USERNAME = '@film_now55'

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Коды фильмов
movie_codes = {
    '/001': '🎬 Игра престолов',
    '/002': '🎬 Во все тяжкие',
    '/003': '🎬 Иллюзия обмана',
}

# Проверка подписки
async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# Команда /start
@dp.message(F.text == '/start')
async def cmd_start(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text='🔍 Проверить подписку', callback_data='check_subscription')
    await message.answer(
        "👋 Привет!\n"
        "ХОЧЕШЬ УЗНАТЬ НАЗВАНИЕ ФИЛЬМА/СЕРИАЛА ПО КОДУ?\n\n"
        "🔹 Сначала подпишись на наш канал\n"
        "👉 https://t.me/+bzdNraniZOA3MjY6\n\n"
        "После этого нажми кнопку ниже 👇",
        reply_markup=kb.as_markup()
    )

# Проверка подписки по кнопке
@dp.callback_query(F.data == 'check_subscription')
async def check_subs(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await check_subscription(user_id):
        await callback.message.answer(
            "✅ Отлично! Теперь отправь мне код (например: /001), и я пришлю название фильма 🎬"
        )
    else:
        await callback.message.answer(
            "❗ Ты еще не подписан на канал!\n"
            "🔹 Подпишись 👉 https://t.me/+bzdNraniZOA3MjY6\n"
            "Затем нажми кнопку снова"
        )
    await callback.answer()

# Обработка кодов (с проверкой подписки)
@dp.message(F.text.startswith('/'))
async def handle_code(message: Message):
    user_id = message.from_user.id
    subscribed = await check_subscription(user_id)

    if not subscribed:
        await message.answer(
            "❗ Чтобы получить название фильма, сначала подпишись на канал!\n"
            "👉 https://t.me/+bzdNraniZOA3MjY6\n"
            "Затем нажми /start и проверь подписку."
        )
        return

    code = message.text.strip()
    if code in movie_codes:
        await message.answer(movie_codes[code])
    else:
        await message.answer("❌ Код не найден. Проверь правильность ввода.")

# HTTP-сервер для UptimeRobot
async def handle(request):
    return web.Response(text="Бот работает 👍")

def keep_alive():
    app = web.Application()
    app.add_routes([web.get("/", handle)])
    runner = web.AppRunner(app)

    async def start():
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8080)
        await site.start()

    asyncio.create_task(start())

# Запуск
async def main():
    keep_alive()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

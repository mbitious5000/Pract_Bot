import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# ==== НАСТРОЙКИ ====
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL", "")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN)
dp = Dispatcher()


# ==== ОБРАБОТЧИКИ ====
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот, работающий на Render 24/7.\n\n"
        "Напиши мне что-нибудь — я повторю (эхо)."
    )


@dp.message(F.text)
async def echo_handler(message: types.Message):
    await message.answer(f"🔁 Ты написал: {message.text}")


# ==== ЗАПУСК ====
async def on_startup(bot: Bot):
    webhook_host = os.getenv("RENDER_EXTERNAL_URL", "")

    if not webhook_host.startswith("https://"):
        logging.warning(f"⚠️ RENDER_EXTERNAL_URL ещё не готов: '{webhook_host}'. Ждём 10 секунд...")
        await asyncio.sleep(10)
        webhook_host = os.getenv("RENDER_EXTERNAL_URL", "")

    if not webhook_host.startswith("https://"):
        logging.error("❌ RENDER_EXTERNAL_URL так и не появился.")
        return

    webhook_url = f"{webhook_host}{WEBHOOK_PATH}"
    await bot.set_webhook(url=webhook_url)
    logging.info(f"✅ Webhook установлен: {webhook_url}")


async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    logging.info("❌ Webhook удален.")


# ВАЖНО: main() теперь НЕ async!
def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    port = int(os.getenv("PORT", 8080))
    logging.info(f"🚀 Запуск на порту {port}")
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()

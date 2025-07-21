#!/usr/bin/env python3
"""
PrometeyLabs Telegram Bot
Основний файл запуску бота з підтримкою webhook та polling
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Додаємо поточну директорію до PATH
sys.path.insert(0, str(Path(__file__).parent))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from handlers import user, admin, payments
from middleware.auth import AuthMiddleware
from db import init_db
from config import BOT_TOKEN, ADMIN_ID

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Ініціалізація бота та диспетчера
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Конфігурація для Render
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN.split(':')[0]}"
WEBHOOK_SECRET = "PrometeyLabs_webhook_secret_2025"
BASE_WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-app.onrender.com")

async def on_startup(bot: Bot) -> None:
    """Функція ініціалізації при запуску"""
    try:
        # Ініціалізація бази даних
        await init_db()
        logger.info("✅ База даних ініціалізована")
        
        # Реєстрація middleware
        dp.message.middleware(AuthMiddleware())
        dp.callback_query.middleware(AuthMiddleware())
        
        # Реєстрація роутерів (порядок важливий!)
        dp.include_router(admin.router)  # Адмін роутер першим
        dp.include_router(payments.router)  # Платежі другими  
        dp.include_router(user.router)  # Користувацький останнім
        
        # Налаштування webhook для деплою
        if os.getenv("ENVIRONMENT") == "production":
            webhook_url = f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}"
            await bot.set_webhook(
                url=webhook_url,
                secret_token=WEBHOOK_SECRET,
                drop_pending_updates=True
            )
            logger.info(f"✅ Webhook налаштований: {webhook_url}")
        else:
            # Локальний режим - видаляємо webhook
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("✅ Webhook видалений для локального режиму")
        
        logger.info(f"✅ Бот запущено для @PrometeyLabs (ADMIN_ID: {ADMIN_ID})")
        
    except Exception as e:
        logger.error(f"❌ Помилка при ініціалізації: {e}")
        raise

async def on_shutdown(bot: Bot) -> None:
    """Функція очищення при зупинці"""
    try:
        await bot.session.close()
        logger.info("✅ Бот зупинено")
    except Exception as e:
        logger.error(f"❌ Помилка при зупинці: {e}")

async def health_check(request: Request) -> Response:
    """Health check для Render"""
    return Response(
        text="PrometeyLabs Bot OK",
        status=200,
        headers={"Content-Type": "text/plain"}
    )

def create_app() -> web.Application:
    """Створення aiohttp додатку для webhook"""
    # Створюємо веб-додаток
    app = web.Application()
    
    # Додаємо health check endpoint
    app.router.add_get("/health", health_check)
    app.router.add_get("/", health_check)
    
    # Налаштовуємо webhook тільки для продакшн
    if os.getenv("ENVIRONMENT") == "production":
        # Створюємо обробник webhook
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=WEBHOOK_SECRET
        )
        
        # Реєструємо webhook маршрут
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        
        # Налаштовуємо додаток для aiogram
        setup_application(app, dp, bot=bot)
    
    return app

async def main():
    """Головна функція запуску бота"""
    try:
        # Ініціалізація
        await on_startup(bot)
        
        # Перевіряємо режим роботи
        if os.getenv("ENVIRONMENT") == "production":
            # Режим webhook для Render
            logger.info("🚀 Запуск в режимі webhook для Render")
            # Додаток буде запущено через Gunicorn/Uvicorn
            return create_app()
        else:
            # Режим polling для локальної розробки
            logger.info("🔄 Запуск в режимі polling для локальної розробки")
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except Exception as e:
        logger.error(f"❌ Помилка при запуску бота: {e}")
        raise
    finally:
        if os.getenv("ENVIRONMENT") != "production":
            await on_shutdown(bot)

# Створення додатку для ASGI серверів (Gunicorn/Uvicorn)
app = create_app()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот зупинено користувачем")
    except Exception as e:
        logger.error(f"💥 Критична помилка: {e}")
        sys.exit(1) 
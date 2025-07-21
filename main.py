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

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

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
bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Підключаємо middleware
dp.middleware.setup(LoggingMiddleware())

# Конфігурація для Render
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN.split(':')[0]}"
WEBHOOK_SECRET = "PrometeyLabs_webhook_secret_2025"
BASE_WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-app.onrender.com")

async def on_startup(dp):
    """Функція ініціалізації при запуску"""
    try:
        # Ініціалізація бази даних
        await init_db()
        logger.info("✅ База даних ініціалізована")
        
        # Імпортуємо хендлери (важливо робити після ініціалізації dp)
        from handlers import user, admin, payments
        
        # Налаштування webhook для деплою
        if os.getenv("ENVIRONMENT") == "production":
            webhook_url = f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}"
            await bot.set_webhook(
                url=webhook_url,
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

async def on_shutdown(dp):
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
        from aiogram.utils.executor import set_webhook
        
        # Налаштовуємо webhook через executor
        executor.set_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            web_app=app,
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            host="0.0.0.0",
            port=int(os.getenv("PORT", 8000))
        )
    
    return app

def main():
    """Головна функція запуску бота"""
    try:
        # Перевіряємо режим роботи
        if os.getenv("ENVIRONMENT") == "production":
            # Режим webhook для Render
            logger.info("🚀 Запуск в режимі webhook для Render")
            # Додаток буде запущено через create_app()
            return create_app()
        else:
            # Режим polling для локальної розробки
            logger.info("🔄 Запуск в режимі polling для локальної розробки")
            executor.start_polling(
                dp,
                skip_updates=True,
                on_startup=on_startup,
                on_shutdown=on_shutdown
            )
        
    except Exception as e:
        logger.error(f"❌ Помилка при запуску бота: {e}")
        raise

# Створення додатку для ASGI серверів (Gunicorn/Uvicorn)
app = create_app()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Бот зупинено користувачем")
    except Exception as e:
        logger.error(f"💥 Критична помилка: {e}")
        sys.exit(1) 
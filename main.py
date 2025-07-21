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

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web, web_app

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
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Конфігурація для Render
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN.split(':')[0]}"
BASE_WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-app.onrender.com")

async def health_check(request):
    """Health check endpoint для Render"""
    return web.Response(text="OK", status=200)

async def on_startup():
    """Функція ініціалізації при запуску"""
    try:
        # Ініціалізація бази даних
        await init_db()
        logger.info("✅ База даних ініціалізована")
        
        # Імпортуємо та підключаємо роутери з middleware
        from handlers import user, admin, payments
        from middleware.auth import AuthMiddleware
        
        # Підключаємо middleware авторизації
        dp.message.middleware(AuthMiddleware())
        dp.callback_query.middleware(AuthMiddleware())
        
        # Підключаємо роутери (порядок важливий!)
        dp.include_router(admin.router)  # Адмін роутер першим
        dp.include_router(payments.router)
        dp.include_router(user.router)   # Користувацький роутер останнім
        
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

async def on_shutdown():
    """Функція очищення при зупинці"""
    try:
        session = await bot.get_session()
        await session.close()
        logger.info("✅ Бот зупинено")
    except Exception as e:
        logger.error(f"❌ Помилка при зупинці: {e}")

async def main():
    """Головна функція запуску бота"""
    try:
        await on_startup()
        
        # Перевіряємо режим роботи
        if os.getenv("ENVIRONMENT") == "production":
            # Режим webhook для Render
            logger.info("🚀 Запуск в режимі webhook для Render")
            
            # Отримуємо порт з середовища
            port = int(os.getenv("PORT", 8000))
            
            # Створюємо веб додаток для health check
            app = web.Application()
            app.router.add_get('/health', health_check)
            
            # Налаштовуємо webhook
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", port)
            await site.start()
            
            logger.info(f"🌐 Сервер запущено на порту {port}")
            
            # Запускаємо polling для обробки webhook
            await dp.start_polling(bot, skip_updates=True)
            
        else:
            # Режим polling для локальної розробки
            logger.info("🔄 Запуск в режимі polling для локальної розробки")
            await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logger.error(f"❌ Помилка при запуску бота: {e}")
        raise
    finally:
        await on_shutdown()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот зупинено користувачем")
    except Exception as e:
        logger.error(f"💥 Критична помилка: {e}")
        sys.exit(1) 
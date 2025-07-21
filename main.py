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
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from db import init_db
from config import BOT_TOKEN, ADMIN_ID, ENVIRONMENT, WEBHOOK_URL, PORT

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

# Конфігурація webhook
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN.split(':')[0]}"

async def health_check(request):
    """Health check endpoint для Render"""
    return web.Response(text="Bot is running", status=200)

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
        
        logger.info(f"✅ Бот запущено для @PrometeyLabs (ADMIN_ID: {ADMIN_ID})")
        
    except Exception as e:
        logger.error(f"❌ Помилка при ініціалізації: {e}")
        raise

async def setup_webhook():
    """Налаштування webhook для production"""
    try:
        # Видаляємо старий webhook перед встановленням нового
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("🗑️ Старий webhook видалено")
        
        # Встановлюємо новий webhook
        webhook_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )
        logger.info(f"✅ Webhook налаштований: {webhook_url}")
        
    except Exception as e:
        logger.error(f"❌ Помилка налаштування webhook: {e}")
        raise

async def setup_polling():
    """Налаштування polling для development"""
    try:
        # Видаляємо webhook для локального режиму
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook видалений для локального режиму")
        
    except Exception as e:
        logger.error(f"❌ Помилка налаштування polling: {e}")
        raise

async def main_webhook():
    """Запуск в режимі webhook для Render"""
    logger.info("🚀 Запуск в режимі webhook для Render")
    
    # Ініціалізація
    await on_startup()
    await setup_webhook()
    
    # Створюємо веб додаток
    app = web.Application()
    
    # Health check endpoint
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)  # Для головної сторінки
    
    # Налаштовуємо webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    
    # Налаштовуємо додаток
    setup_application(app, dp, bot=bot)
    
    logger.info(f"🌐 Сервер запущено на порту {PORT}")
    logger.info(f"📡 Webhook endpoint: {WEBHOOK_PATH}")
    
    return app

async def main_polling():
    """Запуск в режимі polling для локальної розробки"""
    logger.info("🔄 Запуск в режимі polling для локальної розробки")
    
    # Ініціалізація
    await on_startup()
    await setup_polling()
    
    # Запускаємо polling
    await dp.start_polling(bot, skip_updates=True)

async def on_shutdown():
    """Функція очищення при зупинці"""
    try:
        session = await bot.get_session()
        if session:
            await session.close()
        logger.info("✅ Бот зупинено")
    except Exception as e:
        logger.error(f"❌ Помилка при зупинці: {e}")

async def main():
    """Головна функція запуску бота"""
    try:
        if ENVIRONMENT == "production":
            # Webhook режим для Render
            app = await main_webhook()
            # Запускаємо aiohttp сервер
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", PORT)
            await site.start()
            logger.info(f"🌐 HTTP сервер запущено на 0.0.0.0:{PORT}")
            
            # Тримаємо сервер активним
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                pass
        else:
            # Polling режим для локальної розробки
            await main_polling()
            
    except KeyboardInterrupt:
        logger.info("🛑 Бот зупинено користувачем")
    except Exception as e:
        logger.error(f"💥 Критична помилка: {e}")
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
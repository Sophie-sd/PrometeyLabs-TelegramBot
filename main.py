#!/usr/bin/env python3
"""
PrometeyLabs Telegram Bot
КАРДИНАЛЬНО ПЕРЕПИСАНА ВЕРСІЯ ДЛЯ УНИКНЕННЯ WEBHOOK/POLLING КОНФЛІКТІВ
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

# 🔍 ДІАГНОСТИКА ЗМІННИХ ОТОЧЕННЯ
logger.info("=" * 80)
logger.info("🔍 ДІАГНОСТИКА ЗАПУСКУ PROMETEYLABS BOT")
logger.info("=" * 80)
logger.info(f"📊 ENVIRONMENT: '{ENVIRONMENT}' (тип: {type(ENVIRONMENT)})")
logger.info(f"🌐 WEBHOOK_URL: '{WEBHOOK_URL}'")
logger.info(f"🔢 PORT: {PORT}")
logger.info(f"🤖 BOT_TOKEN: {BOT_TOKEN[:20]}...")
logger.info(f"👤 ADMIN_ID: {ADMIN_ID}")

# Додаткова перевірка через os.getenv
raw_env = os.getenv('ENVIRONMENT')
logger.info(f"🔎 RAW ENVIRONMENT з os.getenv: '{raw_env}' (тип: {type(raw_env)})")

# КРИТИЧНИЙ БЛОК ВИЗНАЧЕННЯ РЕЖИМУ
if ENVIRONMENT == "production" or raw_env == "production":
    FORCE_WEBHOOK_MODE = True
    logger.info("✅ РЕЖИМ: PRODUCTION - ПРИМУСОВИЙ WEBHOOK!")
else:
    FORCE_WEBHOOK_MODE = False
    logger.info("⚠️ РЕЖИМ: DEVELOPMENT - ДОЗВОЛЕНИЙ POLLING")
logger.info("=" * 80)

# Ініціалізація бота та диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Конфігурація webhook
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN.split(':')[0]}"

async def health_check(request):
    """Health check endpoint для Render"""
    return web.Response(text="PrometeyLabs Bot is running! 🚀", status=200)

async def setup_handlers():
    """Налаштування handlers та middleware"""
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
        
        logger.info(f"✅ Handlers налаштовані для @PrometeyLabs (ADMIN_ID: {ADMIN_ID})")
        
    except Exception as e:
        logger.error(f"❌ Помилка налаштування handlers: {e}")
        raise

async def force_webhook_mode():
    """ПРИМУСОВЕ налаштування webhook для production"""
    try:
        logger.info("🔧 ПРИМУСОВЕ налаштування webhook...")
        
        # Спочатку ОБОВ'ЯЗКОВО видаляємо будь-які webhook'и
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("🗑️ Всі старі webhook'и ВИДАЛЕНО")
        
        # Затримка для впевненості
        await asyncio.sleep(2)
        
        # Встановлюємо новий webhook
        webhook_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        result = await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )
        
        if result:
            logger.info(f"✅ WEBHOOK УСПІШНО ВСТАНОВЛЕНИЙ: {webhook_url}")
        else:
            logger.error("❌ ПОМИЛКА ВСТАНОВЛЕННЯ WEBHOOK!")
            raise Exception("Не вдалося встановити webhook")
        
        # Перевіряємо webhook
        webhook_info = await bot.get_webhook_info()
        logger.info(f"🔍 Webhook status: {webhook_info.url}")
        logger.info(f"🔍 Pending updates: {webhook_info.pending_update_count}")
        
    except Exception as e:
        logger.error(f"❌ КРИТИЧНА ПОМИЛКА WEBHOOK: {e}")
        raise

async def force_polling_mode():
    """Налаштування polling для development"""
    try:
        logger.info("🔄 Налаштування polling режиму...")
        
        # Видаляємо webhook для локального режиму
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook видалений для локального режиму")
        
    except Exception as e:
        logger.error(f"❌ Помилка налаштування polling: {e}")
        raise

async def create_webhook_app():
    """Створення веб додатку для webhook"""
    app = web.Application()
    
    # Health check endpoints
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    
    # Налаштовуємо webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    
    # Налаштовуємо додаток
    setup_application(app, dp, bot=bot)
    
    logger.info(f"🌐 Webhook додаток створено")
    logger.info(f"📡 Webhook endpoint: {WEBHOOK_PATH}")
    
    return app

async def start_webhook_server():
    """Запуск webhook сервера для Render"""
    logger.info("🚀 ЗАПУСК WEBHOOK СЕРВЕРА ДЛЯ RENDER")
    
    # Налаштування
    await setup_handlers()
    await force_webhook_mode()
    
    # Створюємо додаток
    app = await create_webhook_app()
    
    # Запускаємо HTTP сервер
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    
    logger.info(f"🌐 HTTP сервер запущено на 0.0.0.0:{PORT}")
    logger.info("🎯 WEBHOOK РЕЖИМ АКТИВНИЙ - POLLING ЗАБОРОНЕНИЙ!")
    
    # Тримаємо сервер активним БЕЗ POLLING!
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        logger.info("⏹️ Отримано сигнал зупинки сервера")
    finally:
        await runner.cleanup()

async def start_polling_server():
    """Запуск polling сервера для development"""
    logger.info("🔄 ЗАПУСК POLLING СЕРВЕРА ДЛЯ РОЗРОБКИ")
    
    # Налаштування
    await setup_handlers()
    await force_polling_mode()
    
    # Запускаємо polling
    logger.info("🎯 POLLING РЕЖИМ АКТИВНИЙ - WEBHOOK ВИДАЛЕНИЙ!")
    await dp.start_polling(bot, skip_updates=True)

async def shutdown():
    """Очищення ресурсів при зупинці"""
    try:
        session = await bot.get_session()
        if session:
            await session.close()
        logger.info("✅ Бот зупинено")
    except Exception as e:
        logger.error(f"❌ Помилка при зупинці: {e}")

async def main():
    """ГОЛОВНА ФУНКЦІЯ З ПРИМУСОВИМ РЕЖИМОМ"""
    try:
        logger.info("🚀 ЗАПУСК PROMETEYLABS BOT...")
        
        # КРИТИЧНЕ РІШЕННЯ: ПРИМУСОВИЙ WEBHOOK ДЛЯ PRODUCTION
        if FORCE_WEBHOOK_MODE:
            logger.info("🎯 ПРИМУСОВИЙ WEBHOOK РЕЖИМ")
            await start_webhook_server()
        else:
            logger.info("🎯 ДОЗВОЛЕНИЙ POLLING РЕЖИМ")
            await start_polling_server()
            
    except KeyboardInterrupt:
        logger.info("🛑 Бот зупинено користувачем")
    except Exception as e:
        logger.error(f"💥 КРИТИЧНА ПОМИЛКА: {e}")
        raise
    finally:
        await shutdown()

if __name__ == '__main__':
    try:
        # ЗАПУСК БЕЗ МОЖЛИВОСТІ КОНФЛІКТУ
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот зупинено користувачем")
    except Exception as e:
        logger.error(f"💥 КРИТИЧНА ПОМИЛКА: {e}")
        sys.exit(1) 
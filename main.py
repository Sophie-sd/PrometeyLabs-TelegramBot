#!/usr/bin/env python3
"""
PrometeyLabs Telegram Bot
Основний файл запуску бота
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

async def main():
    """Головна функція запуску бота"""
    try:
        # Ініціалізація бази даних
        await init_db()
        logger.info("База даних ініціалізована")
        
        # Реєстрація middleware
        dp.message.middleware(AuthMiddleware())
        dp.callback_query.middleware(AuthMiddleware())
        
        # Реєстрація роутерів (порядок важливий!)
        dp.include_router(admin.router)  # Адмін роутер першим
        dp.include_router(payments.router)  # Платежі другими  
        dp.include_router(user.router)  # Користувацький останнім (має catch-all обробник)
        
        # Пропускаємо накопичені оновлення
        await bot.delete_webhook(drop_pending_updates=True)
        
        logger.info("Бот запущено")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Помилка при запуску бота: {e}")
        raise
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот зупинено користувачем")
    except Exception as e:
        logger.error(f"Критична помилка: {e}")
        sys.exit(1) 
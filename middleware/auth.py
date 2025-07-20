"""
Middleware авторизації для PrometeyLabs Bot
Всі користувачі мають доступ до основного функціоналу
Тільки адмін має доступ до адмін панелі
"""

import logging
from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from config import ADMIN_ID
from db import get_user, add_user

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseMiddleware):
    """
    Middleware для логування активності користувачів
    Блокує тільки адмін функції для неадмінів
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        """
        Логує активність користувачів та перевіряє доступ до адмін функцій
        """
        user_id = None
        
        # Отримуємо user_id залежно від типу події
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if not user_id:
            logger.warning("Не вдалося отримати user_id з події")
            return
        
        # Перевіряємо чи це адмін команда/функція
        is_admin_action = await self.is_admin_action(event)
        
        if is_admin_action and user_id != ADMIN_ID:
            # Тільки адмін функції блокуємо для неадмінів
            await self.send_admin_only_message(event)
            logger.warning(f"Спроба доступу до адмін функцій від неадміна {user_id}")
            return
        
        # Логуємо активність користувача
        await self.log_user_activity(user_id, event)
        
        # Передаємо управління далі
        return await handler(event, data)
    
    async def is_admin_action(self, event: Union[Message, CallbackQuery]) -> bool:
        """
        Перевіряє чи це адмін дія
        """
        if isinstance(event, Message):
            if event.text:
                # Адмін команди
                admin_commands = ['/admin', '/broadcast', '/users', '/analytics', '/settings']
                return any(event.text.startswith(cmd) for cmd in admin_commands)
        
        elif isinstance(event, CallbackQuery):
            if event.data:
                # Адмін callback'и
                admin_callbacks = ['adm:', 'broadcast:', 'admin_', 'manage_']
                return any(event.data.startswith(prefix) for prefix in admin_callbacks)
        
        return False
    
    async def send_admin_only_message(self, event: Union[Message, CallbackQuery]):
        """
        Відправляє повідомлення про обмеження адмін функцій
        """
        try:
            admin_message = "🔒 Ця функція доступна тільки адміністратору."
            
            if isinstance(event, Message):
                await event.answer(admin_message)
            elif isinstance(event, CallbackQuery):
                await event.answer(admin_message, show_alert=True)
        except Exception as e:
            logger.error(f"Помилка відправки повідомлення про адмін обмеження: {e}")
    
    async def log_user_activity(self, user_id: int, event: Union[Message, CallbackQuery]):
        """
        Логує активність користувача
        """
        try:
            # Додаємо/оновлюємо користувача в БД
            if isinstance(event, Message):
                username = event.from_user.username
                await add_user(user_id, username)
                
                # Логуємо тип активності
                if event.text:
                    if event.text.startswith('/'):
                        logger.info(f"Користувач {user_id} виконав команду: {event.text}")
                    else:
                        logger.info(f"Користувач {user_id} надіслав повідомлення")
            
            elif isinstance(event, CallbackQuery):
                logger.info(f"Користувач {user_id} натиснув кнопку: {event.data}")
                
        except Exception as e:
            logger.error(f"Помилка логування активності користувача {user_id}: {e}")

# Функції для перевірки ролей
async def is_admin(user_id: int) -> bool:
    """
    Перевіряє чи є користувач адміном
    """
    return user_id == ADMIN_ID

async def is_user_authorized(user_id: int) -> bool:
    """
    Всі користувачі авторизовані для основного функціоналу
    """
    return True 
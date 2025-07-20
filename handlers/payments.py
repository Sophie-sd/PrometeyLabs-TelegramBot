"""
Обробники платежів для PrometeyLabs Bot
"""

import logging
from aiogram import Router
from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(lambda c: c.data and c.data.startswith("pay:"))
async def payment_handler(callback: CallbackQuery):
    """Обробник платежів"""
    await callback.answer("💳 Система платежів буде реалізована в наступних кроках", show_alert=True)

# TODO: Реалізувати інтеграцію з Monobank згідно ТЗ 
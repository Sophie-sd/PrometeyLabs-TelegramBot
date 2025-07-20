"""
Обробники для користувачів PrometeyLabs Bot
"""

import logging
from typing import Dict, Any, Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, SERVICES
from db import add_user, get_user, update_user_activity, get_courses, check_course_access, get_course
from keyboards import (
    main_menu, services_menu, website_service_keyboard, service_contact_keyboard,
    courses_menu, course_card_keyboard, online_resources_keyboard, about_company_keyboard,
    portfolio_keyboard, back_to_about_keyboard
)
from messages import (
    WELCOME_MESSAGE, SERVICES_MAIN_MESSAGE,
    WEBSITE_SERVICE_MESSAGE, TELEGRAM_BOT_SERVICE_MESSAGE, CRM_SERVICE_MESSAGE,
    SOCIAL_MEDIA_SERVICE_MESSAGE, COURSES_MAIN_MESSAGE, NO_COURSES_MESSAGE,
    course_card_message, ONLINE_RESOURCES_MESSAGE, ABOUT_COMPANY_MESSAGE,
    PORTFOLIO_MESSAGE, WHY_US_MESSAGE, PAYMENT_INFO_MESSAGE, ERROR_MESSAGE,
    COMMAND_NOT_FOUND_MESSAGE, COURSE_DEMO_MESSAGE
)

logger = logging.getLogger(__name__)
router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    """Обробник команди /start"""
    user_id = message.from_user.id
    username = message.from_user.username
    
    try:
        # Додаємо користувача в БД
        await add_user(user_id, username)
        await update_user_activity(user_id)
        
        # Перевіряємо чи це адмін
        if user_id == ADMIN_ID:
            # Для адміна показуємо адмін панель
            from keyboards import admin_main_menu
            from messages import ADMIN_WELCOME_MESSAGE
            
            await message.answer(
                ADMIN_WELCOME_MESSAGE,
                reply_markup=admin_main_menu()
            )
            logger.info(f"Адмін {user_id} (@{username}) запустив бота")
        else:
            # Для звичайних користувачів показуємо звичайне меню
            await message.answer(
                WELCOME_MESSAGE,
                reply_markup=main_menu(user_id)
            )
            logger.info(f"Користувач {user_id} (@{username}) запустив бота")
        
    except Exception as e:
        logger.error(f"Помилка в start_handler: {e}")
        await message.answer(ERROR_MESSAGE)

@router.message(Command('help'))
async def help_handler(message: Message):
    """Обробник команди /help"""
    user_id = message.from_user.id
    
    await update_user_activity(user_id)
    await message.answer(
        WELCOME_MESSAGE,
        reply_markup=main_menu(user_id)
    )

@router.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: CallbackQuery):
    """Повернення до головного меню"""
    user_id = callback.from_user.id
    await update_user_activity(user_id)
    
    await callback.message.edit_text(
        WELCOME_MESSAGE,
        reply_markup=main_menu(user_id)
    )
    await callback.answer()

# Обробники блоку "Послуги"
@router.callback_query(F.data.startswith("srv:"))
async def services_handler(callback: CallbackQuery):
    """Обробники послуг"""
    user_id = callback.from_user.id
    await update_user_activity(user_id)
    
    action = callback.data.split(":", 1)[1]
    
    try:
        if action == "main":
            await callback.message.edit_text(
                SERVICES_MAIN_MESSAGE,
                reply_markup=services_menu(user_id)
            )
        
        elif action == "website":
            await callback.message.edit_text(
                WEBSITE_SERVICE_MESSAGE,
                reply_markup=website_service_keyboard()
            )
        
        elif action == "telegram_bot":
            await callback.message.edit_text(
                TELEGRAM_BOT_SERVICE_MESSAGE,
                reply_markup=service_contact_keyboard("telegram_bot")
            )
        
        elif action == "crm":
            await callback.message.edit_text(
                CRM_SERVICE_MESSAGE,
                reply_markup=service_contact_keyboard("crm")
            )
        
        elif action == "social_media":
            await callback.message.edit_text(
                SOCIAL_MEDIA_SERVICE_MESSAGE,
                reply_markup=service_contact_keyboard("social_media")
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Помилка в services_handler для action '{action}': {e}")
        logger.error(f"Повна помилка: {str(e)}")
        await callback.answer("Сталася помилка", show_alert=True)

# Обробники блоку "Курси"
@router.callback_query(F.data.startswith("crs:"))
async def courses_handler(callback: CallbackQuery):
    """Обробники курсів"""
    user_id = callback.from_user.id
    await update_user_activity(user_id)
    
    action = callback.data.split(":", 1)[1]
    
    try:
        if action == "main":
            courses = await get_courses()
            
            if not courses:
                await callback.message.edit_text(
                    NO_COURSES_MESSAGE,
                    reply_markup=courses_menu(user_id)
                )
            else:
                # Формуємо список курсів
                keyboard = []
                for course in courses:
                    keyboard.append([{
                        'text': f"🎓 {course['title']} - {course['price_uah']} ₴",
                        'callback_data': f"crs:view_{course['id']}"
                    }])
                
                keyboard.append([{
                    'text': '⬅️ Головне меню',
                    'callback_data': 'main_menu'
                }])
                
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=btn['text'], callback_data=btn['callback_data'])]
                    for row in keyboard for btn in row
                ])
                
                await callback.message.edit_text(
                    COURSES_MAIN_MESSAGE,
                    reply_markup=markup
                )
        
        elif action == "load":
            # TODO: Реалізувати завантаження з ZenEdu API
            await callback.answer("Функція буде реалізована після налаштування ZenEdu API", show_alert=True)
            return
        
        elif action.startswith("view_"):
            course_id = int(action.split("_")[1])
            course = await get_course(course_id)
            
            if not course:
                await callback.answer("Курс не знайдено", show_alert=True)
                return
            
            # Перевіряємо доступ
            has_access = await check_course_access(user_id, course_id)
            
            message_text = course_card_message(
                title=course['title'],
                description=course['description'],
                price=course['price_uah']
            )
            
            await callback.message.edit_text(
                message_text,
                reply_markup=course_card_keyboard(
                    course_id=course_id,
                    has_access=has_access,
                    z_link=course['z_link'],
                    price=course['price_uah']
                )
            )
        
        elif action.startswith("demo_"):
            await callback.message.edit_text(
                COURSE_DEMO_MESSAGE,
                reply_markup=course_card_keyboard(
                    course_id=int(action.split("_")[1])
                )
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Помилка в courses_handler: {e}")
        await callback.answer("Сталася помилка", show_alert=True)

# Обробники блоку "Онлайн-ресурси"
@router.callback_query(F.data == "online_resources")
async def online_resources_handler(callback: CallbackQuery):
    """Онлайн ресурси"""
    user_id = callback.from_user.id
    await update_user_activity(user_id)
    
    await callback.message.edit_text(
        ONLINE_RESOURCES_MESSAGE,
        reply_markup=online_resources_keyboard(user_id)
    )
    await callback.answer()

# Обробники блоку "Про компанію"
@router.callback_query(F.data == "about_company")
async def about_company_handler(callback: CallbackQuery):
    """Про компанію"""
    user_id = callback.from_user.id
    await update_user_activity(user_id)
    
    await callback.message.edit_text(
        ABOUT_COMPANY_MESSAGE,
        reply_markup=about_company_keyboard(user_id)
    )
    await callback.answer()

@router.callback_query(F.data == "portfolio")
async def portfolio_handler(callback: CallbackQuery):
    """Портфоліо"""
    user_id = callback.from_user.id
    await update_user_activity(user_id)
    
    await callback.message.edit_text(
        PORTFOLIO_MESSAGE,
        reply_markup=portfolio_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "why_us")
async def why_us_handler(callback: CallbackQuery):
    """Чому ми"""
    user_id = callback.from_user.id
    await update_user_activity(user_id)
    
    await callback.message.edit_text(
        WHY_US_MESSAGE,
        reply_markup=back_to_about_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "payment_info")
async def payment_info_handler(callback: CallbackQuery):
    """Інформація про оплату"""
    user_id = callback.from_user.id
    await update_user_activity(user_id)
    
    await callback.message.edit_text(
        PAYMENT_INFO_MESSAGE,
        reply_markup=back_to_about_keyboard()
    )
    await callback.answer()

# Обробник невідомих команд
@router.message()
async def unknown_message_handler(message: Message):
    """Обробник невідомих повідомлень"""
    user_id = message.from_user.id
    
    await update_user_activity(user_id)
    
    # Якщо це адмін, перенаправляємо до адмін команд
    if user_id == ADMIN_ID and message.text and message.text.startswith('/'):
        return
    
    await message.answer(
        COMMAND_NOT_FOUND_MESSAGE,
        reply_markup=main_menu(user_id)
    )

# Обробник невідомих callback'ів
@router.callback_query()
async def unknown_callback_handler(callback: CallbackQuery):
    """Обробник невідомих callback'ів"""
    user_id = callback.from_user.id
    await update_user_activity(user_id)
    
    logger.warning(f"Невідомий callback від {user_id}: {callback.data}")
    await callback.answer("Функція тимчасово недоступна", show_alert=True) 
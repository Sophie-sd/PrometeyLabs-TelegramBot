"""
Обробники платежів для PrometeyLabs Bot
Інтеграція з ZenEdu для продажу курсів
"""

import logging
from typing import Optional
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import CALLBACK_PREFIXES
from db import get_course, add_purchase, grant_course_access, get_user
from services.zenedu_client import (
    grant_course_access_to_user, 
    get_course_access_link,
    zenedu_client
)
from middleware.auth import is_admin

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data.startswith(f"{CALLBACK_PREFIXES['payment']}"))
async def payment_handler(callback: CallbackQuery):
    """Обробник платежів через ZenEdu"""
    user_id = callback.from_user.id
    action = callback.data.split(":", 1)[1]
    
    try:
        if action.startswith("buy_"):
            # Покупка курсу
            course_id = int(action.split("_")[1])
            await handle_course_purchase(callback, course_id)
            
        elif action.startswith("access_"):
            # Отримання доступу до купленого курсу
            course_id = int(action.split("_")[1])
            await handle_course_access(callback, course_id)
            
        elif action == "methods":
            # Показати методи оплати
            await show_payment_methods(callback)
            
        else:
            await callback.answer("❌ Невідома дія платежу", show_alert=True)
            
    except Exception as e:
        logger.error(f"❌ Помилка в payment_handler: {str(e)}", exc_info=True)
        await callback.answer("❌ Сталася помилка. Спробуйте пізніше.", show_alert=True)

async def handle_course_purchase(callback: CallbackQuery, course_id: int):
    """Обробка покупки курсу"""
    user_id = callback.from_user.id
    username = callback.from_user.username
    
    try:
        # Отримуємо інформацію про курс
        course = await get_course(course_id)
        if not course:
            await callback.answer("❌ Курс не знайдено", show_alert=True)
            return
        
        # Перевіряємо чи користувач вже має доступ
        from db import check_course_access
        has_access = await check_course_access(user_id, course_id)
        if has_access:
            await callback.answer("✅ У вас вже є доступ до цього курсу!", show_alert=True)
            return
        
        # Для ZenEdu покупки відбуваються через їх платформу
        # Спочатку створюємо підписника в ZenEdu
        subscriber_created = await zenedu_client.create_subscriber(
            user_id=user_id,
            username=username,
            first_name=callback.from_user.first_name
        )
        
        if not subscriber_created:
            await callback.answer("❌ Помилка реєстрації в системі курсів", show_alert=True)
            return
        
        # Надаємо доступ через ZenEdu
        zenedu_id = course.get('zenedu_id') or str(course_id)
        access_granted = await grant_course_access_to_user(zenedu_id, user_id)
        
        if access_granted:
            # Записуємо покупку в локальну БД
            purchase_id = await add_purchase(
                user_id=user_id,
                course_id=course_id,
                amount=course['price_uah'],
                payment_method='zenedu',
                payment_status='completed'
            )
            
            # Отримуємо посилання доступу
            access_link = await get_course_access_link(zenedu_id, user_id)
            
            # Формуємо повідомлення про успішну покупку
            success_text = f"🎉 Вітаємо з покупкою!\n\n"
            success_text += f"📚 **{course['title']}**\n"
            success_text += f"💰 Сплачено: {course['price_uah']} ₴\n\n"
            
            keyboard = []
            
            if access_link:
                success_text += f"🎓 Ваш курс готовий до навчання!\n"
                success_text += f"Натисніть кнопку нижче щоб розпочати:"
                keyboard.append([
                    InlineKeyboardButton(
                        text="🚀 Розпочати навчання", 
                        url=access_link
                    )
                ])
            else:
                success_text += f"📧 Посилання для доступу буде надіслано найближчим часом."
                keyboard.append([
                    InlineKeyboardButton(
                        text="🎓 Отримати доступ", 
                        callback_data=f"{CALLBACK_PREFIXES['payment']}access_{course_id}"
                    )
                ])
            
            keyboard.append([
                InlineKeyboardButton(
                    text="⬅️ До курсів", 
                    callback_data=f"{CALLBACK_PREFIXES['course']}main"
                )
            ])
            
            await callback.message.edit_text(
                success_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
                parse_mode="Markdown"
            )
            
            logger.info(f"✅ Користувач {user_id} успішно купив курс {course_id} через ZenEdu")
            
        else:
            # Помилка надання доступу
            await callback.message.edit_text(
                f"❌ **Помилка обробки покупки**\n\n"
                f"Курс: {course['title']}\n"
                f"Сума: {course['price_uah']} ₴\n\n"
                f"Будь ласка, зверніться до підтримки @PrometeyLabs",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"crs:view_{course_id}")]
                ]),
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"❌ Помилка обробки покупки курсу {course_id}: {str(e)}", exc_info=True)
        await callback.answer("❌ Помилка обробки покупки. Зверніться до підтримки.", show_alert=True)

async def handle_course_access(callback: CallbackQuery, course_id: int):
    """Отримання доступу до купленого курсу"""
    user_id = callback.from_user.id
    
    try:
        # Перевіряємо чи є доступ у користувача
        from db import check_course_access
        has_access = await check_course_access(user_id, course_id)
        
        if not has_access:
            await callback.answer("❌ У вас немає доступу до цього курсу", show_alert=True)
            return
        
        # Отримуємо курс
        course = await get_course(course_id)
        if not course:
            await callback.answer("❌ Курс не знайдено", show_alert=True)
            return
        
        # Отримуємо посилання доступу через ZenEdu
        zenedu_id = course.get('zenedu_id') or str(course_id)
        access_link = await get_course_access_link(zenedu_id, user_id)
        
        if access_link:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Розпочати навчання", url=access_link)],
                [InlineKeyboardButton(text="⬅️ До курсів", callback_data=f"{CALLBACK_PREFIXES['course']}main")]
            ])
            
            await callback.message.edit_text(
                f"🎓 **{course['title']}**\n\n"
                f"✅ У вас є доступ до цього курсу!\n"
                f"Натисніть кнопку нижче щоб розпочати навчання:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            # Якщо є локальне посилання
            if course.get('z_link') and not course['z_link'].startswith('zenedu://'):
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🚀 Розпочати навчання", url=course['z_link'])],
                    [InlineKeyboardButton(text="⬅️ До курсів", callback_data=f"{CALLBACK_PREFIXES['course']}main")]
                ])
                
                await callback.message.edit_text(
                    f"🎓 **{course['title']}**\n\n"
                    f"✅ У вас є доступ до цього курсу!",
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            else:
                await callback.answer("⏳ Посилання для доступу готується. Спробуйте через кілька хвилин.", show_alert=True)
        
    except Exception as e:
        logger.error(f"❌ Помилка отримання доступу до курсу {course_id}: {str(e)}", exc_info=True)
        await callback.answer("❌ Помилка отримання доступу", show_alert=True)

async def show_payment_methods(callback: CallbackQuery):
    """Показати доступні методи оплати"""
    user_id = callback.from_user.id
    
    text = """💳 **Методи оплати**

🏪 **ZenEdu Platform**
• Банківські картки (Visa, MasterCard)
• Apple Pay / Google Pay
• Приват24, Монобанк
• Безпечні платежі через ZenEdu

💰 **Переваги:**
✅ Миттєвий доступ до курсів
✅ Захист покупця
✅ Електронні чеки
✅ Повернення коштів за потреби

📞 **Підтримка:** @PrometeyLabs"""

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

# Адмін функції для роботи з курсами ZenEdu
@router.callback_query(F.data.startswith("admin_grant_course:"))
async def admin_grant_course_handler(callback: CallbackQuery):
    """Адмін видача курсу користувачу"""
    admin_user_id = callback.from_user.id
    
    if not await is_admin(admin_user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        data_parts = callback.data.split(":")
        target_user_id = int(data_parts[1])
        course_id = int(data_parts[2])
        
        # Отримуємо курс
        course = await get_course(course_id)
        if not course:
            await callback.answer("❌ Курс не знайдено", show_alert=True)
            return
        
        # Надаємо доступ через ZenEdu
        zenedu_id = course.get('zenedu_id') or str(course_id)
        access_granted = await grant_course_access_to_user(zenedu_id, target_user_id)
        
        if access_granted:
            # Записуємо безкоштовну покупку
            await add_purchase(
                user_id=target_user_id,
                course_id=course_id,
                amount=0,
                payment_method='admin_grant',
                payment_status='completed'
            )
            
            await callback.answer(f"✅ Доступ до курсу '{course['title']}' надано користувачу {target_user_id}", show_alert=True)
            logger.info(f"🎁 Адмін {admin_user_id} надав безкоштовний доступ до курсу {course_id} користувачу {target_user_id}")
        else:
            await callback.answer("❌ Помилка надання доступу", show_alert=True)
            
    except Exception as e:
        logger.error(f"❌ Помилка в admin_grant_course_handler: {str(e)}", exc_info=True)
        await callback.answer("❌ Помилка виконання операції", show_alert=True) 
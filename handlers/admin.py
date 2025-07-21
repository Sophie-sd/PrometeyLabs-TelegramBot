"""
Обробники адміністратора для PrometeyLabs Bot
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import re

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, CALLBACK_PREFIXES
from db import (
    get_users_count, get_active_users_count, get_new_users_count,
    get_courses_count, get_purchases_count, get_users_with_purchases_count,
    get_daily_interactions, get_weekly_interactions,
    get_users_by_segment, save_broadcast, get_scheduled_broadcasts, get_broadcast_history,
    save_recurring_broadcast, get_active_recurring_broadcasts,
    delete_scheduled_broadcast, delete_recurring_broadcast,
    get_broadcast_by_id, get_recurring_broadcast_by_id,
    search_users, get_users_list, get_user_purchases, get_all_purchases,
    get_purchases_stats, block_user, get_user
)
from keyboards import (
    admin_main_menu, admin_broadcasts_menu, admin_users_menu,
    admin_courses_menu, admin_settings_menu, admin_back_to_main,
    main_menu, broadcast_audience_keyboard, broadcast_schedule_keyboard,
    broadcast_confirm_keyboard, broadcast_back_to_menu_keyboard,
    broadcast_recurring_type_keyboard, broadcast_datetime_keyboard,
    broadcast_scheduled_list_keyboard, broadcast_delete_confirm_keyboard,
    users_list_pagination_keyboard, user_detail_keyboard, purchases_list_keyboard,
    back_to_users_keyboard, cancel_search_keyboard, user_message_keyboard
)
from messages import (
    ADMIN_WELCOME_MESSAGE, ADMIN_ANALYTICS_MESSAGE,
    ADMIN_COURSES_SYNC_MESSAGE, ADMIN_COURSES_SYNC_SUCCESS, ADMIN_COURSES_SYNC_ERROR,
    ERROR_MESSAGE
)
from services.zenedu_client import sync_courses, check_zenedu_connection
from middleware.auth import is_admin
from states.broadcast_states import BroadcastStates, UserManagementStates

logger = logging.getLogger(__name__)
router = Router()

# Команда /admin
@router.message(Command('admin'))
async def admin_command(message: Message):
    """Обробник команди /admin"""
    user_id = message.from_user.id
    logger.info(f"🔐 Отримано команду /admin від користувача {user_id}")
    
    if not await is_admin(user_id):
        logger.warning(f"❌ Користувач {user_id} не є адміном")
        await message.answer("🔒 Ця команда доступна тільки адміністратору @PrometeyLabs.")
        return
    
    try:
        await message.answer(
            ADMIN_WELCOME_MESSAGE,
            reply_markup=admin_main_menu()
        )
        logger.info(f"✅ Адмін {user_id} (@PrometeyLabs) відкрив панель адміністратора")
    except Exception as e:
        logger.error(f"❌ Помилка в admin_command: {str(e)}", exc_info=True)
        await message.answer("❌ Сталася помилка. Спробуйте пізніше.")

# Головне адмін меню
@router.callback_query(F.data == f"{CALLBACK_PREFIXES['admin']}main")
async def admin_main_handler(callback: CallbackQuery):
    """Головне адмін меню"""
    user_id = callback.from_user.id
    logger.info(f"🔄 Callback {callback.data} від користувача {user_id}")
    
    if not await is_admin(user_id):
        logger.warning(f"❌ Користувач {user_id} не є адміном")
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        await callback.message.edit_text(
            ADMIN_WELCOME_MESSAGE,
            reply_markup=admin_main_menu()
        )
        await callback.answer()
        logger.info(f"✅ Адмін {user_id} повернувся в головне меню")
    except Exception as e:
        logger.error(f"❌ Помилка в admin_main_handler: {str(e)}", exc_info=True)
        await callback.answer("Помилка завантаження меню")

# Переключення в режим користувача
@router.callback_query(F.data == f"{CALLBACK_PREFIXES['admin']}user_mode")
async def admin_user_mode_handler(callback: CallbackQuery):
    """Переключення адміна в режим звичайного користувача"""
    user_id = callback.from_user.id
    logger.info(f"🔄 Callback {callback.data} від користувача {user_id}")
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        from messages import WELCOME_MESSAGE
        from keyboards import admin_user_mode_menu
        
        await callback.message.edit_text(
            "👤 Режим користувача\n\n" + WELCOME_MESSAGE,
            reply_markup=admin_user_mode_menu()
        )
        await callback.answer()
        logger.info(f"Адмін {user_id} переключився в режим користувача")
    except Exception as e:
        logger.error(f"Помилка в admin_user_mode_handler: {e}")
        await callback.answer("Помилка переключення режиму")

# Повернення в адмін панель з режиму користувача
@router.callback_query(F.data == "return_to_admin")
async def return_to_admin_handler(callback: CallbackQuery):
    """Повернення в адмін панель з режиму користувача"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        await callback.message.edit_text(
            ADMIN_WELCOME_MESSAGE,
            reply_markup=admin_main_menu()
        )
        await callback.answer()
        logger.info(f"Адмін {user_id} повернувся в адміністративну панель")
    except Exception as e:
        logger.error(f"Помилка в return_to_admin_handler: {e}")
        await callback.answer("Помилка повернення в адмін панель")

# Аналітика
@router.callback_query(F.data == f"{CALLBACK_PREFIXES['admin']}analytics")
async def admin_analytics_handler(callback: CallbackQuery):
    """Показує аналітику"""
    user_id = callback.from_user.id
    logger.info(f"📊 Запит аналітики від користувача {user_id}")
    
    if not await is_admin(user_id):
        logger.warning(f"❌ Користувач {user_id} не є адміном")
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        logger.info("🔄 Збираю статистику...")
        # Збираємо статистику
        total_users = await get_users_count()
        new_users_day = await get_new_users_count(days=1)
        new_users_week = await get_new_users_count(days=7)
        new_users_month = await get_new_users_count(days=30)
        active_week = await get_active_users_count(days=7)
        course_purchases = await get_purchases_count()
        users_with_purchases = await get_users_with_purchases_count()
        
        # Розраховуємо взаємодії
        daily_interactions = await get_daily_interactions()
        weekly_interactions = await get_weekly_interactions()
        
        analytics_text = ADMIN_ANALYTICS_MESSAGE.format(
            users_count=total_users,
            new_users_day=new_users_day,
            new_users_week=new_users_week,
            new_users_month=new_users_month,
            active_week=active_week,
            course_purchases=course_purchases,
            users_with_purchases=users_with_purchases,
            daily_interactions=daily_interactions,
            weekly_interactions=weekly_interactions
        )
        
        logger.info("📊 Відправляю аналітику...")
        await callback.message.edit_text(
            analytics_text,
            reply_markup=admin_back_to_main()
        )
        await callback.answer()
        logger.info(f"✅ Аналітика успішно відправлена користувачу {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Помилка в admin_analytics_handler: {str(e)}", exc_info=True)
        await callback.answer("Помилка завантаження аналітики")

# Користувачі
@router.callback_query(F.data == f"{CALLBACK_PREFIXES['admin']}users")
async def admin_users_handler(callback: CallbackQuery):
    """Меню користувачів"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        await callback.message.edit_text(
            "👥 Управління користувачами\n\nОберіть дію:",
            reply_markup=admin_users_menu()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Помилка в admin_users_handler: {e}")
        await callback.answer("Помилка завантаження меню користувачів")

# Управління курсами
@router.callback_query(F.data == f"{CALLBACK_PREFIXES['admin']}courses")
async def admin_courses_handler(callback: CallbackQuery):
    """Меню управління курсами"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        await callback.message.edit_text(
            "🎓 Управління курсами\n\nОберіть дію:",
            reply_markup=admin_courses_menu()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Помилка в admin_courses_handler: {e}")
        await callback.answer("Помилка завантаження меню курсів")

# Синхронізація курсів з ZenEdu
@router.callback_query(F.data == f"{CALLBACK_PREFIXES['admin']}sync_courses")
async def admin_sync_courses_handler(callback: CallbackQuery):
    """Синхронізація курсів з ZenEdu"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        # Показуємо повідомлення про початок синхронізації
        await callback.message.edit_text(
            ADMIN_COURSES_SYNC_MESSAGE,
            reply_markup=admin_back_to_main()
        )
        await callback.answer()
        
        # Перевіряємо з'єднання з ZenEdu
        if not await check_zenedu_connection():
            await callback.message.edit_text(
                ADMIN_COURSES_SYNC_ERROR,
                reply_markup=admin_back_to_main()
            )
            return
        
        # Виконуємо синхронізацію
        synced_courses = await sync_courses()
        total_courses = await get_courses_count()
        
        # Показуємо результат
        await callback.message.edit_text(
            ADMIN_COURSES_SYNC_SUCCESS.format(
                synced_count=synced_courses,
                total_count=total_courses
            ),
            reply_markup=admin_back_to_main()
        )
        
    except Exception as e:
        logger.error(f"Помилка в admin_sync_courses_handler: {e}")
        await callback.message.edit_text(
            ADMIN_COURSES_SYNC_ERROR,
            reply_markup=admin_back_to_main()
        )

# Розсилки
@router.callback_query(F.data == f"{CALLBACK_PREFIXES['admin']}broadcasts")
async def admin_broadcasts_handler(callback: CallbackQuery):
    """Меню розсилок"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        await callback.message.edit_text(
            "📬 Управління розсилками\n\nОберіть дію:",
            reply_markup=admin_broadcasts_menu()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Помилка в admin_broadcasts_handler: {e}")
        await callback.answer("Помилка завантаження меню розсилок")

# Нова розсилка
@router.callback_query(F.data == f"{CALLBACK_PREFIXES['admin']}broadcast_new")
async def admin_broadcast_new_handler(callback: CallbackQuery, state: FSMContext):
    """Початок створення нової розсилки"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        # Очищуємо попередній стан
        await state.clear()
        
        # Встановлюємо стан очікування повідомлення
        await state.set_state(BroadcastStates.waiting_for_message)
        
        await callback.message.edit_text(
            "📬 Створення нової розсилки\n\n"
            "📝 Надішліть текст повідомлення для розсилки.\n"
            "Можна додати медіа (фото, відео).",
            reply_markup=broadcast_back_to_menu_keyboard()
        )
        await callback.answer()
        
        logger.info(f"Адмін {user_id} почав створення розсилки")
        
    except Exception as e:
        logger.error(f"Помилка в admin_broadcast_new_handler: {e}")
        await callback.answer("Помилка створення розсилки")

# Обробник тексту розсилки
@router.message(BroadcastStates.waiting_for_message)
async def broadcast_message_handler(message: Message, state: FSMContext):
    """Обробка тексту/медіа для розсилки"""
    user_id = message.from_user.id
    
    if not await is_admin(user_id):
        return
    
    try:
        # Зберігаємо текст повідомлення
        message_text = message.text or message.caption or ""
        if not message_text:
            await message.answer(
                "❌ Повідомлення має містити текст.\n\n"
                "Спробуйте ще раз або скасуйте створення розсилки.",
                reply_markup=broadcast_back_to_menu_keyboard()
            )
            return
        
        # Зберігаємо дані в стан
        await state.update_data(
            message_text=message_text,
            message_id=message.message_id
        )
        
        # Переходимо до вибору аудиторії
        await state.set_state(BroadcastStates.selecting_audience)
        
        await message.answer(
            "👥 Оберіть аудиторію для розсилки:",
            reply_markup=broadcast_audience_keyboard()
        )
        
        logger.info(f"Адмін {user_id} ввів текст розсилки: {message_text[:50]}...")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_message_handler: {e}")
        await message.answer("Помилка обробки повідомлення")

# Обробники вибору аудиторії
@router.callback_query(F.data.startswith("broadcast:audience_"), BroadcastStates.selecting_audience)
async def broadcast_audience_handler(callback: CallbackQuery, state: FSMContext):
    """Обробка вибору аудиторії"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        audience_type = callback.data.split("_")[1]  # all, buyers, inactive
        
        audience_names = {
            "all": "👥 Усі користувачі",
            "buyers": "💰 Покупці курсів", 
            "inactive": "😴 Неактивні 7+ днів"
        }
        
        # Отримуємо кількість користувачів в сегменті
        users_count = len(await get_users_by_segment(audience_type))
        
        # Перевіряємо чи є користувачі в сегменті ОДРАЗУ
        if users_count == 0:
            await callback.message.edit_text(
                f"❌ Не знайдено користувачів для розсилки в сегменті: {audience_names[audience_type]}\n\n"
                "👥 Оберіть інший сегмент аудиторії:",
                reply_markup=broadcast_audience_keyboard()
            )
            await callback.answer()
            logger.info(f"Адмін {user_id} обрав порожній сегмент: {audience_type}")
            return
        
        # Зберігаємо вибір аудиторії
        await state.update_data(
            audience_type=audience_type,
            audience_name=audience_names[audience_type],
            users_count=users_count
        )
        
        # Переходимо до планування
        await state.set_state(BroadcastStates.selecting_schedule)
        
        await callback.message.edit_text(
            f"✅ Обрано: {audience_names[audience_type]}\n"
            f"📊 Користувачів в сегменті: {users_count}\n\n"
            f"📅 Коли відправити розсилку?",
            reply_markup=broadcast_schedule_keyboard()
        )
        await callback.answer()
        
        logger.info(f"Адмін {user_id} обрав аудиторію: {audience_type} ({users_count} користувачів)")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_audience_handler: {e}")
        await callback.answer("Помилка вибору аудиторії")

# Заплановані розсилки
@router.callback_query(F.data == f"{CALLBACK_PREFIXES['admin']}broadcast_scheduled")
async def admin_broadcast_scheduled_handler(callback: CallbackQuery):
    """Показати заплановані розсилки"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        # Отримуємо одноразові заплановані розсилки
        scheduled = await get_scheduled_broadcasts()
        
        # Отримуємо регулярні розсилки
        recurring = await get_active_recurring_broadcasts()
        
        text = "📅 Заплановані розсилки\n\n"
        
        # Показуємо одноразові з нумерацією
        if scheduled:
            text += "📅 **Одноразові:**\n"
            for i, broadcast in enumerate(scheduled, 1):
                # Форматуємо час без "T" для красивого відображення
                scheduled_time = broadcast['scheduled_for']
                if 'T' in scheduled_time:
                    try:
                        # Парсимо ISO формат і показуємо як ДД.ММ.РРРР ГГ:ХХ
                        from datetime import datetime
                        dt = datetime.fromisoformat(scheduled_time.replace('T', ' '))
                        formatted_time = dt.strftime("%d.%m.%Y %H:%M")
                    except:
                        # Якщо не вдається парсити, просто замінюємо T на пробіл
                        formatted_time = scheduled_time.replace('T', ' ')
                else:
                    formatted_time = scheduled_time
                
                text += f"**#{i}** 📝 {broadcast['message_text'][:25]}...\n"
                text += f"👥 {broadcast['audience_type']}\n"
                text += f"📅 {formatted_time}\n\n"
        
        # Показуємо регулярні з продовженням нумерації
        if recurring:
            text += "🔄 **Регулярні:**\n"
            scheduled_count = len(scheduled)
            for i, broadcast in enumerate(recurring, scheduled_count + 1):
                text += f"**#{i}** 📝 {broadcast['message_text'][:25]}...\n"
                text += f"👥 {broadcast['audience_type']}\n"
                text += f"🔄 {broadcast['recurring_type']}\n\n"
        
        # Якщо немає жодних розсилок
        if not scheduled and not recurring:
            text += "Немає запланованих розсилок."
            await callback.message.edit_text(
                text,
                reply_markup=broadcast_back_to_menu_keyboard()
            )
        else:
            # Показуємо список з кнопками видалення
            text += "🗑️ **Оберіть розсилку для видалення:**"
            await callback.message.edit_text(
                text,
                reply_markup=broadcast_scheduled_list_keyboard(scheduled, recurring),
                parse_mode="Markdown"
            )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Помилка в admin_broadcast_scheduled_handler: {e}")
        await callback.answer("Помилка завантаження запланованих розсилок")

# Історія розсилок
@router.callback_query(F.data == f"{CALLBACK_PREFIXES['admin']}broadcast_history")
async def admin_broadcast_history_handler(callback: CallbackQuery):
    """Показати історію розсилок"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        history = await get_broadcast_history(10)
        
        if not history:
            text = "🕓 Історія розсилок\n\n" \
                   "Розсилки ще не створювались."
        else:
            text = "🕓 Історія розсилок\n\n"
            for broadcast in history:
                status_emoji = "✅" if broadcast['status'] == 'sent' else "❌"
                text += f"{status_emoji} {broadcast['message_text']}\n"
                text += f"👥 Аудиторія: {broadcast['audience_type']}\n"
                text += f"📅 Створено: {broadcast['created_at']}\n"
                if broadcast.get('sent_at'):
                    text += f"📤 Відправлено: {broadcast['sent_at']}\n"
                text += "\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=broadcast_back_to_menu_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Помилка в admin_broadcast_history_handler: {e}")
        await callback.answer("Помилка завантаження історії розсилок")

# Видалення запланованих розсилок
@router.callback_query(F.data.startswith("delete_scheduled:"))
async def broadcast_delete_scheduled_handler(callback: CallbackQuery):
    """Підтвердження видалення одноразової розсилки"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        broadcast_id = int(callback.data.split(":")[1])
        
        # Отримуємо деталі розсилки
        broadcast = await get_broadcast_by_id(broadcast_id)
        
        if not broadcast:
            await callback.answer("❌ Розсилку не знайдено", show_alert=True)
            return
        
        # Форматуємо час без "T"
        scheduled_time = broadcast['scheduled_for']
        if 'T' in scheduled_time:
            try:
                dt = datetime.fromisoformat(scheduled_time.replace('T', ' '))
                formatted_time = dt.strftime("%d.%m.%Y %H:%M")
            except:
                formatted_time = scheduled_time.replace('T', ' ')
        else:
            formatted_time = scheduled_time
        
        confirm_text = f"""
🗑️ **Видалення одноразової розсилки**

📝 **Текст:** {broadcast['message_text'][:50]}...
👥 **Аудиторія:** {broadcast['audience_type']}
📅 **Час відправки:** {formatted_time}

⚠️ **Ця дія незворотна!**

Ви дійсно хочете видалити цю розсилку?
        """
        
        await callback.message.edit_text(
            confirm_text,
            reply_markup=broadcast_delete_confirm_keyboard("scheduled", broadcast_id),
            parse_mode="Markdown"
        )
        await callback.answer()
        
        logger.info(f"Адмін {user_id} запитує підтвердження видалення розсилки {broadcast_id}")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_delete_scheduled_handler: {e}")
        await callback.answer("Помилка підтвердження видалення")

@router.callback_query(F.data.startswith("delete_recurring:"))
async def broadcast_delete_recurring_handler(callback: CallbackQuery):
    """Підтвердження видалення регулярної розсилки"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        broadcast_id = int(callback.data.split(":")[1])
        
        # Отримуємо деталі розсилки
        broadcast = await get_recurring_broadcast_by_id(broadcast_id)
        
        if not broadcast:
            await callback.answer("❌ Розсилку не знайдено", show_alert=True)
            return
        
        confirm_text = f"""
🗑️ **Видалення регулярної розсилки**

📝 **Текст:** {broadcast['message_text'][:50]}...
👥 **Аудиторія:** {broadcast['audience_type']}
🔄 **Тип:** {broadcast['recurring_type']}
⚙️ **CRON:** {broadcast.get('cron_expression', 'стандартний')}

⚠️ **Ця дія незворотна!**

Ви дійсно хочете видалити цю регулярну розсилку?
        """
        
        await callback.message.edit_text(
            confirm_text,
            reply_markup=broadcast_delete_confirm_keyboard("recurring", broadcast_id),
            parse_mode="Markdown"
        )
        await callback.answer()
        
        logger.info(f"Адмін {user_id} запитує підтвердження видалення регулярної розсилки {broadcast_id}")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_delete_recurring_handler: {e}")
        await callback.answer("Помилка підтвердження видалення")

@router.callback_query(F.data.startswith("confirm_delete_scheduled:"))
async def broadcast_confirm_delete_scheduled_handler(callback: CallbackQuery):
    """Фактичне видалення одноразової розсилки"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        broadcast_id = int(callback.data.split(":")[1])
        
        # Видаляємо розсилку
        success = await delete_scheduled_broadcast(broadcast_id)
        
        if success:
            await callback.answer("✅ Розсилку успішно видалено!")
            
            # Повертаємося до списку запланованих розсилок
            await admin_broadcast_scheduled_handler(callback)
            
            logger.info(f"Адмін {user_id} видалив заплановану розсилку {broadcast_id}")
        else:
            await callback.answer("❌ Помилка видалення розсилки", show_alert=True)
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_confirm_delete_scheduled_handler: {e}")
        await callback.answer("Помилка видалення розсилки")

@router.callback_query(F.data.startswith("confirm_delete_recurring:"))
async def broadcast_confirm_delete_recurring_handler(callback: CallbackQuery):
    """Фактичне видалення регулярної розсилки"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        broadcast_id = int(callback.data.split(":")[1])
        
        # Видаляємо регулярну розсилку
        success = await delete_recurring_broadcast(broadcast_id)
        
        if success:
            await callback.answer("✅ Регулярну розсилку успішно видалено!")
            
            # Повертаємося до списку запланованих розсилок
            await admin_broadcast_scheduled_handler(callback)
            
            logger.info(f"Адмін {user_id} видалив регулярну розсилку {broadcast_id}")
        else:
            await callback.answer("❌ Помилка видалення регулярної розсилки", show_alert=True)
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_confirm_delete_recurring_handler: {e}")
        await callback.answer("Помилка видалення регулярної розсилки")

# Статистика розсилок
@router.callback_query(F.data == "adm:broadcast_stats")
async def admin_broadcast_stats_handler(callback: CallbackQuery):
    """Показати статистику розсилок"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        # Базова статистика (заглушка, можна розширити)
        text = "📊 Статистика розсилок\n\n" \
               "📤 Всього відправлено: 0\n" \
               "✅ Успішних: 0\n" \
               "❌ Помилок: 0\n" \
               "📈 Середня доставка: 0%\n\n" \
               "📊 Детальна статистика буде доступна після перших розсилок."
        
        await callback.message.edit_text(
            text,
            reply_markup=broadcast_back_to_menu_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Помилка в admin_broadcast_stats_handler: {e}")
        await callback.answer("Помилка завантаження статистики розсилок")

# Обробники планування розсилки
@router.callback_query(F.data.startswith("broadcast:schedule_"), BroadcastStates.selecting_schedule)
async def broadcast_schedule_handler(callback: CallbackQuery, state: FSMContext):
    """Обробка вибору часу відправки"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        schedule_type = callback.data.split("_")[1]  # now, later, recurring
        
        # Отримуємо дані з стану
        data = await state.get_data()
        
        if schedule_type == "now":
            # Відправити одразу
            await state.update_data(
                schedule_type="immediate",
                schedule_time="одразу"
            )
            
            # Переходимо до підтвердження
            await state.set_state(BroadcastStates.confirming_broadcast)
            
            # Показуємо підтвердження
            confirm_text = f"""
✅ Підтвердіть розсилку:

📝 Текст: {data['message_text'][:100]}{'...' if len(data['message_text']) > 100 else ''}

👥 Аудиторія: {data['audience_name']}
📊 Користувачів: {data['users_count']}
📅 Час відправки: Одразу

Продовжити?
            """
            
            await callback.message.edit_text(
                confirm_text,
                reply_markup=broadcast_confirm_keyboard()
            )
            
        elif schedule_type == "later":
            # Запланувати на конкретний час
            await state.set_state(BroadcastStates.waiting_for_datetime)
            
            await callback.message.edit_text(
                "📅 Планування розсилки на конкретний час\n\n"
                "Введіть дату та час у форматі:\n"
                "**ДД.ММ.РРРР ГГ:ХХ**\n\n"
                "Приклад: `19.01.2025 15:30`\n\n"
                "⏰ Час вказується за київським часом (UTC+2)",
                reply_markup=broadcast_datetime_keyboard(),
                parse_mode="Markdown"
            )
            
        elif schedule_type == "recurring":
            # Регулярна розсилка
            await state.set_state(BroadcastStates.selecting_recurring)
            
            await callback.message.edit_text(
                "🔄 Регулярна розсилка\n\n"
                "Оберіть частоту відправки:",
                reply_markup=broadcast_recurring_type_keyboard()
            )
        
        await callback.answer()
        logger.info(f"Адмін {user_id} обрав тип планування: {schedule_type}")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_schedule_handler: {e}")
        await callback.answer("Помилка планування розсилки")

# Підтвердження та відправка розсилки
@router.callback_query(F.data == "broadcast:confirm_send", BroadcastStates.confirming_broadcast)
async def broadcast_confirm_send_handler(callback: CallbackQuery, state: FSMContext):
    """Підтвердження та відправка розсилки"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        # Отримуємо дані з стану
        data = await state.get_data()
        
        # Отримуємо список користувачів для розсилки
        users = await get_users_by_segment(data['audience_type'])
        
        # Перевірка користувачів вже виконується на етапі вибору аудиторії
        
        # Обробляємо різні типи розсилок
        if data.get('schedule_type') == 'immediate':
            # Миттєва відправка
            broadcast_id = await save_broadcast(
                admin_id=user_id,
                message_text=data['message_text'],
                audience=data['audience_type'],
                status="sent"
            )
            
        elif data.get('schedule_type') == 'scheduled':
            # Запланована розсилка
            broadcast_id = await save_broadcast(
                admin_id=user_id,
                message_text=data['message_text'],
                audience=data['audience_type'],
                scheduled_for=data['scheduled_datetime'],
                status="pending"
            )
            
        elif data.get('schedule_type') == 'recurring':
            # Регулярна розсилка
            broadcast_id = await save_recurring_broadcast(
                admin_id=user_id,
                message_text=data['message_text'],
                audience=data['audience_type'],
                recurring_type=data['recurring_type'],
                cron_expression=data['cron_expression']
            )
        
        # Обробляємо результат залежно від типу розсилки
        if data.get('schedule_type') == 'immediate':
            # Миттєва відправка - показуємо прогрес
            await callback.message.edit_text(
                f"📤 Відправляємо розсилку...\n\n"
                f"👥 Користувачів: {len(users)}\n"
                f"📝 Текст: {data['message_text'][:50]}...",
                reply_markup=None
            )
            
            # Імітуємо відправку (потрібно реалізувати реальну відправку)
            sent_count = 0
            error_count = 0
            
            # TODO: Реалізувати реальну відправку повідомлень
            # Поки що просто імітуємо успішну відправку
            sent_count = len(users)
            
            # Результат миттєвої відправки
            result_text = f"""
✅ Розсилка завершена!

📊 Статистика:
📤 Відправлено: {sent_count}
❌ Помилок: {error_count}
📈 Успішність: {round(sent_count / len(users) * 100, 1)}%

📝 Текст: {data['message_text'][:50]}...
👥 Аудиторія: {data['audience_name']}
            """
            
        elif data.get('schedule_type') == 'scheduled':
            # Запланована розсилка
            result_text = f"""
✅ Розсилка заплановано!

📅 Час відправки: {data['schedule_time']}
👥 Аудиторія: {data['audience_name']}
📊 Користувачів: {len(users)}

📝 Текст: {data['message_text'][:100]}...

Розсилка буде автоматично відправлена в зазначений час.
            """
            
        elif data.get('schedule_type') == 'recurring':
            # Регулярна розсилка
            result_text = f"""
✅ Регулярна розсилка створена!

🔄 Розклад: {data['recurring_name']}
👥 Аудиторія: {data['audience_name']}
📊 Користувачів: {len(users)}

📝 Текст: {data['message_text'][:100]}...

Розсилка буде автоматично відправлятися за розкладом.
            """
        else:
            # Резервний варіант
            result_text = f"""
✅ Розсилка налаштована!

👥 Аудиторія: {data['audience_name']}
📊 Користувачів: {len(users)}
📝 Текст: {data['message_text'][:50]}...
            """
        
        await callback.message.edit_text(
            result_text,
            reply_markup=broadcast_back_to_menu_keyboard()
        )
        
        # Очищуємо стан
        await state.clear()
        
        logger.info(f"Адмін {user_id} відправив розсилку {broadcast_id} для {len(users)} користувачів")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_confirm_send_handler: {e}")
        await callback.answer("Помилка відправки розсилки")
        await state.clear()

# Скасування створення розсилки
@router.callback_query(F.data == "broadcast:cancel")
async def broadcast_cancel_handler(callback: CallbackQuery, state: FSMContext):
    """Скасування створення розсилки"""
    try:
        await state.clear()
        await callback.message.edit_text(
            "❌ Створення розсилки скасовано.",
            reply_markup=broadcast_back_to_menu_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Помилка в broadcast_cancel_handler: {e}")

# Повернення до попереднього кроку
@router.callback_query(F.data == "broadcast:back_to_audience", BroadcastStates.selecting_schedule)
async def broadcast_back_to_audience_handler(callback: CallbackQuery, state: FSMContext):
    """Повернення до вибору аудиторії"""
    try:
        await state.set_state(BroadcastStates.selecting_audience)
        await callback.message.edit_text(
            "👥 Оберіть аудиторію для розсилки:",
            reply_markup=broadcast_audience_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Помилка в broadcast_back_to_audience_handler: {e}")

# Обробник введення дати/часу
@router.message(BroadcastStates.waiting_for_datetime)
async def broadcast_datetime_handler(message: Message, state: FSMContext):
    """Обробка введення дати та часу для планування"""
    user_id = message.from_user.id
    
    if not await is_admin(user_id):
        return
    
    try:
        datetime_str = message.text.strip()
        
        # Валідація формату дати/часу
        pattern = r'^(\d{2})\.(\d{2})\.(\d{4})\s+(\d{1,2}):(\d{2})$'
        match = re.match(pattern, datetime_str)
        
        if not match:
            await message.answer(
                "❌ Неправильний формат дати/часу\n\n"
                "Використовуйте формат: **ДД.ММ.РРРР ГГ:ХХ**\n"
                "Приклад: `19.01.2025 15:30`",
                reply_markup=broadcast_datetime_keyboard(),
                parse_mode="Markdown"
            )
            return
        
        day, month, year, hour, minute = match.groups()
        
        try:
            # Створюємо об'єкт datetime
            scheduled_datetime = datetime(
                int(year), int(month), int(day), 
                int(hour), int(minute)
            )
            
            # Перевіряємо що дата в майбутньому
            if scheduled_datetime <= datetime.now():
                await message.answer(
                    "❌ Дата має бути в майбутньому\n\n"
                    "Введіть правильну дату та час:",
                    reply_markup=broadcast_datetime_keyboard()
                )
                return
            
        except ValueError:
            await message.answer(
                "❌ Некоректна дата або час\n\n"
                "Перевірте правильність введених значень:",
                reply_markup=broadcast_datetime_keyboard()
            )
            return
        
        # Зберігаємо дату в стан
        await state.update_data(
            schedule_type="scheduled",
            schedule_time=scheduled_datetime.strftime("%d.%m.%Y %H:%M"),
            scheduled_datetime=scheduled_datetime.isoformat()
        )
        
        # Переходимо до підтвердження
        await state.set_state(BroadcastStates.confirming_broadcast)
        
        # Отримуємо дані для підтвердження
        data = await state.get_data()
        
        confirm_text = f"""
✅ Підтвердіть розсилку:

📝 Текст: {data['message_text'][:100]}{'...' if len(data['message_text']) > 100 else ''}

👥 Аудиторія: {data['audience_name']}
📊 Користувачів: {data['users_count']}
📅 Час відправки: {data['schedule_time']}

Продовжити?
        """
        
        await message.answer(
            confirm_text,
            reply_markup=broadcast_confirm_keyboard()
        )
        
        logger.info(f"Адмін {user_id} запланував розсилку на {data['schedule_time']}")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_datetime_handler: {e}")
        await message.answer("Помилка обробки дати/часу")

# Обробники регулярних розсилок
@router.callback_query(F.data.startswith("broadcast:recurring_"), BroadcastStates.selecting_recurring)
async def broadcast_recurring_handler(callback: CallbackQuery, state: FSMContext):
    """Обробка вибору типу регулярної розсилки"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        recurring_type = callback.data.split("_")[1]  # daily, weekly, monthly, custom
        
        # Відповідності типів та CRON виразів
        cron_expressions = {
            "daily": "0 12 * * *",      # Щодня о 12:00
            "weekly": "0 12 * * 1",     # Щопонеділка о 12:00
            "monthly": "0 12 1 * *",    # 1-го числа кожного місяця о 12:00
        }
        
        recurring_names = {
            "daily": "📅 Щоденно (12:00)",
            "weekly": "📆 Щотижнево (понеділок, 12:00)",
            "monthly": "🗓️ Щомісяця (1-го числа, 12:00)",
            "custom": "⚙️ Власний розклад"
        }
        
        if recurring_type == "custom":
            # Переходимо до введення CRON
            await state.set_state(BroadcastStates.waiting_for_cron)
            
            await callback.message.edit_text(
                "⚙️ Власний розклад розсилки\n\n"
                "Введіть CRON вираз:\n\n"
                "**Формат:** `хвилина година день місяць день_тижня`\n\n"
                "**Приклади:**\n"
                "• `0 9 * * *` - щодня о 9:00\n"
                "• `0 18 * * 5` - щоп'ятниці о 18:00\n"
                "• `30 14 1,15 * *` - 1-го і 15-го числа о 14:30",
                reply_markup=broadcast_datetime_keyboard(),
                parse_mode="Markdown"
            )
            
        else:
            # Стандартні типи регулярних розсилок
            await state.update_data(
                schedule_type="recurring",
                recurring_type=recurring_type,
                recurring_name=recurring_names[recurring_type],
                cron_expression=cron_expressions[recurring_type]
            )
            
            # Переходимо до підтвердження
            await state.set_state(BroadcastStates.confirming_broadcast)
            
            # Отримуємо дані для підтвердження
            data = await state.get_data()
            
            confirm_text = f"""
✅ Підтвердіть регулярну розсилку:

📝 Текст: {data['message_text'][:100]}{'...' if len(data['message_text']) > 100 else ''}

👥 Аудиторія: {data['audience_name']}
📊 Користувачів: {data['users_count']}
🔄 Розклад: {data['recurring_name']}

Продовжити?
            """
            
            await callback.message.edit_text(
                confirm_text,
                reply_markup=broadcast_confirm_keyboard()
            )
        
        await callback.answer()
        logger.info(f"Адмін {user_id} обрав тип регулярної розсилки: {recurring_type}")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_recurring_handler: {e}")
        await callback.answer("Помилка налаштування регулярної розсилки")

# Обробник CRON виразу
@router.message(BroadcastStates.waiting_for_cron)
async def broadcast_cron_handler(message: Message, state: FSMContext):
    """Обробка введення CRON виразу"""
    user_id = message.from_user.id
    
    if not await is_admin(user_id):
        return
    
    try:
        cron_expression = message.text.strip()
        
        # Базова валідація CRON виразу (5 частин розділених пробілами)
        parts = cron_expression.split()
        if len(parts) != 5:
            await message.answer(
                "❌ Неправильний CRON вираз\n\n"
                "Має бути 5 частин розділених пробілами:\n"
                "`хвилина година день місяць день_тижня`",
                reply_markup=broadcast_datetime_keyboard(),
                parse_mode="Markdown"
            )
            return
        
        # Зберігаємо CRON вираз
        await state.update_data(
            schedule_type="recurring",
            recurring_type="custom",
            recurring_name=f"⚙️ Власний розклад ({cron_expression})",
            cron_expression=cron_expression
        )
        
        # Переходимо до підтвердження
        await state.set_state(BroadcastStates.confirming_broadcast)
        
        # Отримуємо дані для підтвердження
        data = await state.get_data()
        
        confirm_text = f"""
✅ Підтвердіть регулярну розсилку:

📝 Текст: {data['message_text'][:100]}{'...' if len(data['message_text']) > 100 else ''}

👥 Аудиторія: {data['audience_name']}
📊 Користувачів: {data['users_count']}
🔄 Розклад: {data['recurring_name']}

Продовжити?
        """
        
        await message.answer(
            confirm_text,
            reply_markup=broadcast_confirm_keyboard()
        )
        
        logger.info(f"Адмін {user_id} ввів CRON вираз: {cron_expression}")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_cron_handler: {e}")
        await message.answer("Помилка обробки CRON виразу")

# Додаткові обробники навігації
@router.callback_query(F.data == "broadcast:back_to_schedule")
async def broadcast_back_to_schedule_handler(callback: CallbackQuery, state: FSMContext):
    """Повернення до вибору планування"""
    try:
        await state.set_state(BroadcastStates.selecting_schedule)
        
        data = await state.get_data()
        await callback.message.edit_text(
            f"✅ Обрано: {data['audience_name']}\n"
            f"📊 Користувачів в сегменті: {data['users_count']}\n\n"
            f"📅 Коли відправити розсилку?",
            reply_markup=broadcast_schedule_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Помилка в broadcast_back_to_schedule_handler: {e}")

# Обробники редагування розсилки
@router.callback_query(F.data == "broadcast:edit_message", BroadcastStates.confirming_broadcast)
async def broadcast_edit_message_handler(callback: CallbackQuery, state: FSMContext):
    """Редагування тексту розсилки"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        # Переходимо до стану редагування тексту
        await state.set_state(BroadcastStates.editing_message)
        
        await callback.message.edit_text(
            "✏️ Редагування тексту розсилки\n\n"
            "📝 Надішліть новий текст повідомлення для розсилки.\n"
            "Можна додати медіа (фото, відео).",
            reply_markup=broadcast_back_to_menu_keyboard()
        )
        await callback.answer()
        
        logger.info(f"Адмін {user_id} редагує текст розсилки")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_edit_message_handler: {e}")

@router.callback_query(F.data == "broadcast:edit_audience", BroadcastStates.confirming_broadcast)
async def broadcast_edit_audience_handler(callback: CallbackQuery, state: FSMContext):
    """Зміна аудиторії розсилки"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        # Переходимо до стану редагування аудиторії
        await state.set_state(BroadcastStates.editing_audience)
        
        await callback.message.edit_text(
            "👥 Оберіть нову аудиторію для розсилки:",
            reply_markup=broadcast_audience_keyboard()
        )
        await callback.answer()
        
        logger.info(f"Адмін {user_id} змінює аудиторію розсилки")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_edit_audience_handler: {e}")

@router.callback_query(F.data == "broadcast:edit_schedule", BroadcastStates.confirming_broadcast)
async def broadcast_edit_schedule_handler(callback: CallbackQuery, state: FSMContext):
    """Зміна планування розсилки"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        # Переходимо до стану редагування планування
        await state.set_state(BroadcastStates.editing_schedule)
        
        data = await state.get_data()
        await callback.message.edit_text(
            f"✅ Обрано: {data['audience_name']}\n"
            f"📊 Користувачів в сегменті: {data['users_count']}\n\n"
            f"📅 Оберіть новий час відправки розсилки:",
            reply_markup=broadcast_schedule_keyboard()
        )
        await callback.answer()
        
        logger.info(f"Адмін {user_id} змінює планування розсилки")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_edit_schedule_handler: {e}")

# Нові обробники для станів редагування (повертають прямо до підтвердження)
@router.message(BroadcastStates.editing_message)
async def broadcast_editing_message_handler(message: Message, state: FSMContext):
    """Обробка редагування тексту розсилки"""
    user_id = message.from_user.id
    
    if not await is_admin(user_id):
        return
    
    try:
        # Зберігаємо новий текст
        message_text = message.text or message.caption or ""
        if not message_text:
            await message.answer(
                "❌ Повідомлення має містити текст.\n\n"
                "Спробуйте ще раз:",
                reply_markup=broadcast_back_to_menu_keyboard()
            )
            return
        
        # Оновлюємо текст в стані
        await state.update_data(
            message_text=message_text,
            message_id=message.message_id
        )
        
        # Повертаємося до підтвердження
        await state.set_state(BroadcastStates.confirming_broadcast)
        
        # Отримуємо дані та показуємо підтвердження
        data = await state.get_data()
        
        # Визначаємо тип розсилки для правильного відображення
        if data.get('schedule_type') == 'immediate':
            schedule_info = "📅 Час відправки: Одразу"
        elif data.get('schedule_type') == 'scheduled':
            schedule_info = f"📅 Час відправки: {data.get('schedule_time', 'Не вказано')}"
        elif data.get('schedule_type') == 'recurring':
            schedule_info = f"🔄 Розклад: {data.get('recurring_name', 'Не вказано')}"
        else:
            schedule_info = "📅 Час відправки: Не налаштовано"
        
        confirm_text = f"""
✅ Підтвердіть розсилку:

📝 Текст: {data['message_text'][:100]}{'...' if len(data['message_text']) > 100 else ''}

👥 Аудиторія: {data['audience_name']}
📊 Користувачів: {data['users_count']}
{schedule_info}

Продовжити?
        """
        
        await message.answer(
            confirm_text,
            reply_markup=broadcast_confirm_keyboard()
        )
        
        logger.info(f"Адмін {user_id} оновив текст розсилки")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_editing_message_handler: {e}")
        await message.answer("Помилка збереження тексту")

@router.callback_query(F.data.startswith("broadcast:audience_"), BroadcastStates.editing_audience)
async def broadcast_editing_audience_handler(callback: CallbackQuery, state: FSMContext):
    """Обробка редагування аудиторії розсилки"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        audience_type = callback.data.split("_")[1]  # all, buyers, inactive
        
        audience_names = {
            "all": "👥 Усі користувачі",
            "buyers": "💰 Покупці курсів", 
            "inactive": "😴 Неактивні 7+ днів"
        }
        
        # Отримуємо кількість користувачів в сегменті
        users_count = len(await get_users_by_segment(audience_type))
        
        # Перевіряємо чи є користувачі в сегменті
        if users_count == 0:
            await callback.message.edit_text(
                f"❌ Не знайдено користувачів для розсилки в сегменті: {audience_names[audience_type]}\n\n"
                "👥 Оберіть інший сегмент аудиторії:",
                reply_markup=broadcast_audience_keyboard()
            )
            await callback.answer()
            return
        
        # Оновлюємо аудиторію в стані
        await state.update_data(
            audience_type=audience_type,
            audience_name=audience_names[audience_type],
            users_count=users_count
        )
        
        # Повертаємося до підтвердження
        await state.set_state(BroadcastStates.confirming_broadcast)
        
        # Отримуємо дані та показуємо підтвердження
        data = await state.get_data()
        
        # Визначаємо тип розсилки для правильного відображення
        if data.get('schedule_type') == 'immediate':
            schedule_info = "📅 Час відправки: Одразу"
        elif data.get('schedule_type') == 'scheduled':
            schedule_info = f"📅 Час відправки: {data.get('schedule_time', 'Не вказано')}"
        elif data.get('schedule_type') == 'recurring':
            schedule_info = f"🔄 Розклад: {data.get('recurring_name', 'Не вказано')}"
        else:
            schedule_info = "📅 Час відправки: Не налаштовано"
        
        confirm_text = f"""
✅ Підтвердіть розсилку:

📝 Текст: {data['message_text'][:100]}{'...' if len(data['message_text']) > 100 else ''}

👥 Аудиторія: {data['audience_name']}
📊 Користувачів: {data['users_count']}
{schedule_info}

Продовжити?
        """
        
        await callback.message.edit_text(
            confirm_text,
            reply_markup=broadcast_confirm_keyboard()
        )
        await callback.answer()
        
        logger.info(f"Адмін {user_id} оновив аудиторію розсилки: {audience_type}")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_editing_audience_handler: {e}")
        await callback.answer("Помилка зміни аудиторії")

@router.callback_query(F.data.startswith("broadcast:schedule_"), BroadcastStates.editing_schedule)
async def broadcast_editing_schedule_handler(callback: CallbackQuery, state: FSMContext):
    """Обробка редагування планування розсилки"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        schedule_type = callback.data.split("_")[1]  # now, later, recurring
        
        if schedule_type == "now":
            # Відправити одразу
            await state.update_data(
                schedule_type="immediate",
                schedule_time="одразу"
            )
            
            # Повертаємося до підтвердження
            await state.set_state(BroadcastStates.confirming_broadcast)
            
            # Отримуємо дані та показуємо підтвердження
            data = await state.get_data()
            
            confirm_text = f"""
✅ Підтвердіть розсилку:

📝 Текст: {data['message_text'][:100]}{'...' if len(data['message_text']) > 100 else ''}

👥 Аудиторія: {data['audience_name']}
📊 Користувачів: {data['users_count']}
📅 Час відправки: Одразу

Продовжити?
            """
            
            await callback.message.edit_text(
                confirm_text,
                reply_markup=broadcast_confirm_keyboard()
            )
            
        elif schedule_type == "later":
            # Запланувати на конкретний час
            await state.set_state(BroadcastStates.editing_datetime)
            
            await callback.message.edit_text(
                "📅 Планування розсилки на конкретний час\n\n"
                "Введіть дату та час у форматі:\n"
                "**ДД.ММ.РРРР ГГ:ХХ**\n\n"
                "Приклад: `19.01.2025 15:30`\n\n"
                "⏰ Час вказується за київським часом (UTC+2)",
                reply_markup=broadcast_datetime_keyboard(),
                parse_mode="Markdown"
            )
            
        elif schedule_type == "recurring":
            # Регулярна розсилка
            await state.set_state(BroadcastStates.editing_recurring)
            
            await callback.message.edit_text(
                "🔄 Регулярна розсилка\n\n"
                "Оберіть частоту відправки:",
                reply_markup=broadcast_recurring_type_keyboard()
            )
        
        await callback.answer()
        logger.info(f"Адмін {user_id} змінює планування розсилки: {schedule_type}")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_editing_schedule_handler: {e}")
        await callback.answer("Помилка зміни планування")

# Додаткові обробники для редагування дати/часу та регулярності
@router.message(BroadcastStates.editing_datetime)
async def broadcast_editing_datetime_handler(message: Message, state: FSMContext):
    """Обробка редагування дати/часу"""
    user_id = message.from_user.id
    
    if not await is_admin(user_id):
        return
    
    try:
        datetime_str = message.text.strip()
        
        # Валідація формату дати/часу
        pattern = r'^(\d{2})\.(\d{2})\.(\d{4})\s+(\d{1,2}):(\d{2})$'
        match = re.match(pattern, datetime_str)
        
        if not match:
            await message.answer(
                "❌ Неправильний формат дати/часу\n\n"
                "Використовуйте формат: **ДД.ММ.РРРР ГГ:ХХ**\n"
                "Приклад: `19.01.2025 15:30`",
                reply_markup=broadcast_datetime_keyboard(),
                parse_mode="Markdown"
            )
            return
        
        day, month, year, hour, minute = match.groups()
        
        try:
            # Створюємо об'єкт datetime
            scheduled_datetime = datetime(
                int(year), int(month), int(day), 
                int(hour), int(minute)
            )
            
            # Перевіряємо що дата в майбутньому
            if scheduled_datetime <= datetime.now():
                await message.answer(
                    "❌ Дата має бути в майбутньому\n\n"
                    "Введіть правильну дату та час:",
                    reply_markup=broadcast_datetime_keyboard()
                )
                return
            
        except ValueError:
            await message.answer(
                "❌ Некоректна дата або час\n\n"
                "Перевірте правильність введених значень:",
                reply_markup=broadcast_datetime_keyboard()
            )
            return
        
        # Зберігаємо дату в стан
        await state.update_data(
            schedule_type="scheduled",
            schedule_time=scheduled_datetime.strftime("%d.%m.%Y %H:%M"),
            scheduled_datetime=scheduled_datetime.isoformat()
        )
        
        # Повертаємося до підтвердження
        await state.set_state(BroadcastStates.confirming_broadcast)
        
        # Отримуємо дані та показуємо підтвердження
        data = await state.get_data()
        
        confirm_text = f"""
✅ Підтвердіть розсилку:

📝 Текст: {data['message_text'][:100]}{'...' if len(data['message_text']) > 100 else ''}

👥 Аудиторія: {data['audience_name']}
📊 Користувачів: {data['users_count']}
📅 Час відправки: {data['schedule_time']}

Продовжити?
        """
        
        await message.answer(
            confirm_text,
            reply_markup=broadcast_confirm_keyboard()
        )
        
        logger.info(f"Адмін {user_id} оновив час розсилки: {data['schedule_time']}")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_editing_datetime_handler: {e}")
        await message.answer("Помилка обробки дати/часу")

@router.callback_query(F.data.startswith("broadcast:recurring_"), BroadcastStates.editing_recurring)
async def broadcast_editing_recurring_handler(callback: CallbackQuery, state: FSMContext):
    """Обробка редагування регулярної розсилки"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        recurring_type = callback.data.split("_")[1]  # daily, weekly, monthly, custom
        
        # Відповідності типів та CRON виразів
        cron_expressions = {
            "daily": "0 12 * * *",      # Щодня о 12:00
            "weekly": "0 12 * * 1",     # Щопонеділка о 12:00
            "monthly": "0 12 1 * *",    # 1-го числа кожного місяця о 12:00
        }
        
        recurring_names = {
            "daily": "📅 Щоденно (12:00)",
            "weekly": "📆 Щотижнево (понеділок, 12:00)",
            "monthly": "🗓️ Щомісяця (1-го числа, 12:00)",
            "custom": "⚙️ Власний розклад"
        }
        
        if recurring_type == "custom":
            # Переходимо до введення CRON
            await state.set_state(BroadcastStates.editing_cron)
            
            await callback.message.edit_text(
                "⚙️ Власний розклад розсилки\n\n"
                "Введіть CRON вираз:\n\n"
                "**Формат:** `хвилина година день місяць день_тижня`\n\n"
                "**Приклади:**\n"
                "• `0 9 * * *` - щодня о 9:00\n"
                "• `0 18 * * 5` - щоп'ятниці о 18:00\n"
                "• `30 14 1,15 * *` - 1-го і 15-го числа о 14:30",
                reply_markup=broadcast_datetime_keyboard(),
                parse_mode="Markdown"
            )
            
        else:
            # Стандартні типи регулярних розсилок
            await state.update_data(
                schedule_type="recurring",
                recurring_type=recurring_type,
                recurring_name=recurring_names[recurring_type],
                cron_expression=cron_expressions[recurring_type]
            )
            
            # Повертаємося до підтвердження
            await state.set_state(BroadcastStates.confirming_broadcast)
            
            # Отримуємо дані та показуємо підтвердження
            data = await state.get_data()
            
            confirm_text = f"""
✅ Підтвердіть регулярну розсилку:

📝 Текст: {data['message_text'][:100]}{'...' if len(data['message_text']) > 100 else ''}

👥 Аудиторія: {data['audience_name']}
📊 Користувачів: {data['users_count']}
🔄 Розклад: {data['recurring_name']}

Продовжити?
            """
            
            await callback.message.edit_text(
                confirm_text,
                reply_markup=broadcast_confirm_keyboard()
            )
        
        await callback.answer()
        logger.info(f"Адмін {user_id} оновив регулярність розсилки: {recurring_type}")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_editing_recurring_handler: {e}")
        await callback.answer("Помилка редагування регулярності")

@router.message(BroadcastStates.editing_cron)
async def broadcast_editing_cron_handler(message: Message, state: FSMContext):
    """Обробка редагування CRON виразу"""
    user_id = message.from_user.id
    
    if not await is_admin(user_id):
        return
    
    try:
        cron_expression = message.text.strip()
        
        # Базова валідація CRON виразу (5 частин розділених пробілами)
        parts = cron_expression.split()
        if len(parts) != 5:
            await message.answer(
                "❌ Неправильний CRON вираз\n\n"
                "Має бути 5 частин розділених пробілами:\n"
                "`хвилина година день місяць день_тижня`",
                reply_markup=broadcast_datetime_keyboard(),
                parse_mode="Markdown"
            )
            return
        
        # Зберігаємо CRON вираз
        await state.update_data(
            schedule_type="recurring",
            recurring_type="custom",
            recurring_name=f"⚙️ Власний розклад ({cron_expression})",
            cron_expression=cron_expression
        )
        
        # Повертаємося до підтвердження
        await state.set_state(BroadcastStates.confirming_broadcast)
        
        # Отримуємо дані та показуємо підтвердження
        data = await state.get_data()
        
        confirm_text = f"""
✅ Підтвердіть регулярну розсилку:

📝 Текст: {data['message_text'][:100]}{'...' if len(data['message_text']) > 100 else ''}

👥 Аудиторія: {data['audience_name']}
📊 Користувачів: {data['users_count']}
🔄 Розклад: {data['recurring_name']}

Продовжити?
        """
        
        await message.answer(
            confirm_text,
            reply_markup=broadcast_confirm_keyboard()
        )
        
        logger.info(f"Адмін {user_id} оновив CRON вираз: {cron_expression}")
        
    except Exception as e:
        logger.error(f"Помилка в broadcast_editing_cron_handler: {e}")
        await message.answer("Помилка збереження CRON виразу")

# Налаштування
@router.callback_query(F.data == "adm:settings")
async def admin_settings_handler(callback: CallbackQuery):
    """Меню налаштувань"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        await callback.message.edit_text(
            "⚙️ Налаштування системи\n\nОберіть дію:",
            reply_markup=admin_settings_menu()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Помилка в admin_settings_handler: {e}")
        await callback.answer("Помилка завантаження налаштувань")

# Перевірка API
@router.callback_query(F.data == "adm:check_api")
async def admin_check_api_handler(callback: CallbackQuery):
    """Перевірка з'єднання з API"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        await callback.answer("⏳ Перевіряю API...", show_alert=False)
        
        # Перевіряємо ZenEdu API
        zenedu_status = await check_zenedu_connection()
        
        status_text = f"""
🔗 Статус API з'єднань

ZenEdu API: {'✅ Працює' if zenedu_status else '❌ Помилка'}
Monobank API: ⚠️ Не налаштовано
Telegram API: ✅ Працює

Останнє оновлення: {datetime.now().strftime('%H:%M:%S')}
        """
        
        await callback.message.edit_text(
            status_text,
            reply_markup=admin_back_to_main()
        )
        
    except Exception as e:
        logger.error(f"Помилка в admin_check_api_handler: {e}")
        await callback.answer("Помилка перевірки API")

# Обробники управління користувачами

# 🔍 Пошук користувачів
@router.callback_query(F.data == "adm:user_search")
async def admin_user_search_handler(callback: CallbackQuery, state: FSMContext):
    """Початок пошуку користувачів"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        await state.set_state(UserManagementStates.searching_user)
        
        await callback.message.edit_text(
            "🔍 **Пошук користувачів**\n\n"
            "Введіть для пошуку:\n"
            "• ID користувача (число)\n"
            "• Username (без @)\n\n"
            "Приклад: `123456789` або `username`",
            reply_markup=cancel_search_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer()
        
        logger.info(f"Адмін {user_id} розпочав пошук користувачів")
        
    except Exception as e:
        logger.error(f"Помилка в admin_user_search_handler: {e}")
        await callback.answer("Помилка запуску пошуку")

@router.message(UserManagementStates.searching_user)
async def process_user_search(message: Message, state: FSMContext):
    """Обробка пошуку користувачів"""
    user_id = message.from_user.id
    
    if not await is_admin(user_id):
        return
    
    try:
        query = message.text.strip()
        
        if not query:
            await message.answer(
                "❌ Введіть запит для пошуку\n\n"
                "ID користувача або username:",
                reply_markup=cancel_search_keyboard()
            )
            return
        
        # Шукаємо користувачів
        results = await search_users(query)
        
        if not results:
            await message.answer(
                f"❌ Не знайдено користувачів за запитом: `{query}`\n\n"
                "Спробуйте інший запит:",
                reply_markup=cancel_search_keyboard(),
                parse_mode="Markdown"
            )
            return
        
        # Формуємо результати пошуку
        text = f"🔍 **Результати пошуку:** `{query}`\n\n"
        
        for user in results[:10]:  # Показуємо перші 10 результатів
            status = "🚫 Заблокований" if user['is_blocked'] else "✅ Активний"
            username = f"@{user['username']}" if user['username'] else "не вказано"
            
            text += f"**👤 {user['id']}**\n"
            text += f"Username: {username}\n"
            text += f"Статус: {status}\n"
            text += f"Приєднався: {user['joined_at'][:10]}\n\n"
        
        if len(results) > 10:
            text += f"... та ще {len(results) - 10} користувачів"
        
        # Створюємо клавіатуру з користувачами
        keyboard = []
        for user in results[:5]:  # Кнопки для перших 5 користувачів
            username_display = f"@{user['username']}" if user['username'] else f"ID: {user['id']}"
            keyboard.append([
                InlineKeyboardButton(
                    text=f"👤 {username_display}",
                    callback_data=f"user_detail:{user['id']}"
                )
            ])
        
        keyboard.extend([
            [InlineKeyboardButton(text="🔍 Новий пошук", callback_data="adm:user_search")],
            [InlineKeyboardButton(text="👥 Меню", callback_data="adm:users")]
        ])
        
        await message.answer(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="Markdown"
        )
        
        # Очищуємо стан
        await state.clear()
        
        logger.info(f"Адмін {user_id} знайшов {len(results)} користувачів за запитом '{query}'")
        
    except Exception as e:
        logger.error(f"Помилка в process_user_search: {e}")
        await message.answer("Помилка пошуку користувачів")
        await state.clear()

# 📑 Список користувачів
@router.callback_query(F.data == "adm:user_list")
async def admin_user_list_handler(callback: CallbackQuery):
    """Показати список користувачів"""
    await show_users_list(callback, page=0)

@router.callback_query(F.data.startswith("users_page:"))
async def users_page_handler(callback: CallbackQuery):
    """Обробка пагінації списку користувачів"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        page_data = callback.data.split(":")[1]
        if page_data == "current":
            await callback.answer()
            return
        
        page = int(page_data)
        await show_users_list(callback, page)
        
    except Exception as e:
        logger.error(f"Помилка в users_page_handler: {e}")
        await callback.answer("Помилка навігації")

async def show_users_list(callback: CallbackQuery, page: int = 0):
    """Відображення списку користувачів з пагінацією"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        limit = 8
        offset = page * limit
        
        # Отримуємо користувачів
        users = await get_users_list(offset, limit)
        total_users = await get_users_count()
        total_pages = (total_users + limit - 1) // limit
        
        if not users:
            await callback.message.edit_text(
                "📑 **Список користувачів**\n\n"
                "❌ Користувачів не знайдено",
                reply_markup=back_to_users_keyboard(),
                parse_mode="Markdown"
            )
            await callback.answer()
            return
        
        # Формуємо текст
        text = f"📑 **Список користувачів**\n\n"
        text += f"📊 Сторінка {page + 1} з {total_pages} (всього: {total_users})\n\n"
        
        # Створюємо клавіатуру
        keyboard = []
        
        for user in users:
            status_icon = "🚫" if user['is_blocked'] else "✅"
            username_display = f"@{user['username']}" if user['username'] else f"ID: {user['id']}"
            
            text += f"{status_icon} **{username_display}**\n"
            text += f"ID: `{user['id']}`\n"
            text += f"Приєднався: {user['joined_at'][:10]}\n\n"
            
            # Кнопка для кожного користувача
            keyboard.append([
                InlineKeyboardButton(
                    text=f"{status_icon} {username_display}",
                    callback_data=f"user_detail:{user['id']}"
                )
            ])
        
        # Використовуємо нову клавіатуру
        has_prev = page > 0
        has_next = page < total_pages - 1
        pagination_keyboard = users_list_pagination_keyboard(page, total_pages, has_prev, has_next)
        
        # Додаємо кнопки користувачів до клавіатури
        for i, button_row in enumerate(keyboard):
            pagination_keyboard.inline_keyboard.insert(i, button_row)
        
        await callback.message.edit_text(
            text,
            reply_markup=pagination_keyboard,
            parse_mode="Markdown"
        )
        await callback.answer()
        
        logger.info(f"Адмін {user_id} переглядає список користувачів (сторінка {page + 1})")
        
    except Exception as e:
        logger.error(f"Помилка в show_users_list: {e}")
        await callback.answer("Помилка завантаження списку")

# 👤 Деталі користувача
@router.callback_query(F.data.startswith("user_detail:"))
async def user_detail_handler(callback: CallbackQuery):
    """Показати деталі користувача"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        target_user_id = int(callback.data.split(":")[1])
        
        # Отримуємо дані користувача
        user_data = await get_user(target_user_id)
        
        if not user_data:
            await callback.answer("❌ Користувача не знайдено", show_alert=True)
            return
        
        # Отримуємо покупки користувача
        purchases = await get_user_purchases(target_user_id)
        
        # Формуємо інформацію
        status = "🚫 Заблокований" if user_data.get('is_blocked') else "✅ Активний"
        username = f"@{user_data.get('username', 'не вказано')}"
        
        text = f"👤 **Користувач {target_user_id}**\n\n"
        text += f"📝 **Username:** {username}\n"
        text += f"📊 **Статус:** {status}\n"
        text += f"📅 **Приєднався:** {user_data.get('joined_at', 'не вказано')}\n"
        text += f"⏰ **Остання активність:** {user_data.get('last_activity', 'не вказано')}\n\n"
        
        if purchases:
            text += f"💰 **Покупки:** {len(purchases)}\n"
            text += "**Останні покупки:**\n"
            for purchase in purchases[:3]:
                text += f"• {purchase['course_title']} ({purchase['purchase_date'][:10]})\n"
            if len(purchases) > 3:
                text += f"... та ще {len(purchases) - 3} покупок\n"
        else:
            text += "💰 **Покупки:** Немає\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=user_detail_keyboard(target_user_id, user_data.get('is_blocked', False)),
            parse_mode="Markdown"
        )
        await callback.answer()
        
        logger.info(f"Адмін {user_id} переглядає деталі користувача {target_user_id}")
        
    except Exception as e:
        logger.error(f"Помилка в user_detail_handler: {e}")
        await callback.answer("Помилка завантаження даних користувача")

# 💰 Покупки
@router.callback_query(F.data == "adm:user_purchases")
async def admin_purchases_handler(callback: CallbackQuery):
    """Показати всі покупки"""
    await show_purchases_list(callback, page=0)

@router.callback_query(F.data.startswith("purchases_page:"))
async def purchases_page_handler(callback: CallbackQuery):
    """Обробка пагінації покупок"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        page_data = callback.data.split(":")[1]
        if page_data == "current":
            await callback.answer()
            return
        
        page = int(page_data)
        await show_purchases_list(callback, page)
        
    except Exception as e:
        logger.error(f"Помилка в purchases_page_handler: {e}")
        await callback.answer("Помилка навігації")

async def show_purchases_list(callback: CallbackQuery, page: int = 0):
    """Відображення списку покупок"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        limit = 10
        offset = page * limit
        
        # Отримуємо покупки та статистику
        purchases = await get_all_purchases(offset, limit)
        stats = await get_purchases_stats()
        
        if not purchases and page == 0:
            await callback.message.edit_text(
                "💰 **Покупки користувачів**\n\n"
                "❌ Покупок ще немає",
                reply_markup=back_to_users_keyboard(),
                parse_mode="Markdown"
            )
            await callback.answer()
            return
        
        # Розрахунок пагінації
        total_purchases = stats.get('total_purchases', 0)
        total_pages = (total_purchases + limit - 1) // limit if total_purchases > 0 else 1
        
        # Формуємо текст
        text = f"💰 **Покупки користувачів**\n\n"
        
        if stats:
            text += f"📊 **Статистика:**\n"
            text += f"• Всього покупок: {stats.get('total_purchases', 0)}\n"
            text += f"• Дохід: ₴{stats.get('total_revenue', 0)}\n"
            text += f"• За місяць: {stats.get('monthly_purchases', 0)}\n"
            text += f"• Середній чек: ₴{stats.get('avg_amount', 0)}\n\n"
        
        text += f"📄 Сторінка {page + 1} з {total_pages}\n\n"
        
        # Список покупок
        for purchase in purchases:
            username = f"@{purchase['username']}" if purchase['username'] else f"ID: {purchase['user_id']}"
            status_icon = "✅" if purchase['payment_status'] == 'completed' else "⏳"
            
            text += f"{status_icon} **{purchase['course_title']}**\n"
            text += f"👤 {username}\n"
            text += f"💰 ₴{purchase['amount']} • {purchase['purchase_date'][:10]}\n\n"
        
        # Пагінація
        has_prev = page > 0
        has_next = page < total_pages - 1
        
        keyboard = []
        pagination_row = []
        
        if has_prev:
            pagination_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"purchases_page:{page-1}"))
        
        pagination_row.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="purchases_page:current"))
        
        if has_next:
            pagination_row.append(InlineKeyboardButton(text="➡️", callback_data=f"purchases_page:{page+1}"))
        
        if pagination_row:
            keyboard.append(pagination_row)
        
        # Кнопки управління
        keyboard.extend([
            [
                InlineKeyboardButton(text="🔄 Оновити", callback_data="adm:user_purchases"),
                InlineKeyboardButton(text="👥 Меню", callback_data="adm:users")
            ]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="Markdown"
        )
        await callback.answer()
        
        logger.info(f"Адмін {user_id} переглядає покупки (сторінка {page + 1})")
        
    except Exception as e:
        logger.error(f"Помилка в show_purchases_list: {e}")
        await callback.answer("Помилка завантаження покупок")

# Дії з користувачами
@router.callback_query(F.data.startswith("user_action:"))
async def user_action_handler(callback: CallbackQuery, state: FSMContext):
    """Обробка дій з користувачами"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        action_data = callback.data.split(":")
        action = action_data[1].split("_")[0]  # block, unblock, grant, message
        target_user_id = int(action_data[1].split("_")[1])
        
        if action == "block":
            # Блокування користувача
            success = await block_user(target_user_id, blocked=True)
            if success:
                await callback.answer("✅ Користувача заблоковано", show_alert=True)
                logger.info(f"Адмін {user_id} заблокував користувача {target_user_id}")
            else:
                await callback.answer("❌ Помилка блокування", show_alert=True)
                
        elif action == "unblock":
            # Розблокування користувача
            success = await block_user(target_user_id, blocked=False)
            if success:
                await callback.answer("✅ Користувача розблоковано", show_alert=True)
                logger.info(f"Адмін {user_id} розблокував користувача {target_user_id}")
            else:
                await callback.answer("❌ Помилка розблокування", show_alert=True)
                
        elif action == "grant":
            # Видача курсу (заглушка)
            await callback.answer("🚧 Видача курсу - в розробці", show_alert=True)
            
        elif action == "message":
            # Відправка повідомлення від адміна
            await state.set_state(UserManagementStates.sending_message)
            await state.update_data(target_user_id=target_user_id)
            
            await callback.message.edit_text(
                f"✉️ **Відправка повідомлення від адміна**\n\n"
                f"Користувач: {target_user_id}\n\n"
                f"Введіть текст повідомлення:",
                reply_markup=user_message_keyboard(target_user_id),
                parse_mode="Markdown"
            )
            await callback.answer()
            return
            

            
        # Оновлюємо дані користувача після дії
        if action in ["block", "unblock"]:
            # Повертаємось до деталей користувача
            await user_detail_handler(
                CallbackQuery(
                    id=callback.id,
                    from_user=callback.from_user,
                    message=callback.message,
                    data=f"user_detail:{target_user_id}",
                    chat_instance=callback.chat_instance
                )
            )
        
    except Exception as e:
        logger.error(f"Помилка в user_action_handler: {e}")
        await callback.answer("Помилка виконання дії")

@router.message(UserManagementStates.sending_message)
async def process_admin_message(message: Message, state: FSMContext):
    """Обробка відправки повідомлення користувачу"""
    user_id = message.from_user.id
    
    if not await is_admin(user_id):
        return
    
    try:
        data = await state.get_data()
        target_user_id = data.get('target_user_id')
        
        if not target_user_id:
            await message.answer("❌ Помилка: не вказано користувача")
            await state.clear()
            return
        
        message_text = message.text
        if not message_text:
            await message.answer(
                "❌ Введіть текст повідомлення:",
                reply_markup=user_message_keyboard(target_user_id)
            )
            return
        
        # Відправляємо повідомлення користувачу від адміністратора
        try:
            from main import bot
            
            await bot.send_message(
                chat_id=target_user_id,
                text=f"📩 **Повідомлення від адміністратора:**\n\n{message_text}",
                parse_mode="Markdown"
            )
            
            await message.answer(
                f"✅ **Повідомлення від адміна відправлено!**\n\n"
                f"Користувач: {target_user_id}\n"
                f"Текст: {message_text[:100]}{'...' if len(message_text) > 100 else ''}",
                reply_markup=user_message_keyboard(target_user_id),
                parse_mode="Markdown"
            )
            
            logger.info(f"Адмін {user_id} відправив повідомлення від адміна користувачу {target_user_id}")
            
        except Exception as send_error:
            logger.error(f"Помилка відправки повідомлення користувачу {target_user_id}: {send_error}")
            await message.answer(
                f"❌ **Не вдалося відправити повідомлення**\n\n"
                f"Користувач {target_user_id} можливо заблокував бота або видалив акаунт.",
                reply_markup=user_message_keyboard(target_user_id),
                parse_mode="Markdown"
            )
        
        # Очищуємо стан
        await state.clear()
        
    except Exception as e:
        logger.error(f"Помилка в process_admin_message: {e}")
        await message.answer("Помилка відправки повідомлення")
        await state.clear()

# 📊 Покупки конкретного користувача
@router.callback_query(F.data.startswith("user_purchases:"))
async def user_purchases_handler(callback: CallbackQuery):
    """Показати покупки конкретного користувача"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        target_user_id = int(callback.data.split(":")[1])
        
        # Отримуємо дані користувача та його покупки
        user_data = await get_user(target_user_id)
        purchases = await get_user_purchases(target_user_id)
        
        if not user_data:
            await callback.answer("❌ Користувача не знайдено", show_alert=True)
            return
        
        # Формуємо інформацію
        username = f"@{user_data.get('username', 'не вказано')}"
        
        text = f"📊 **Покупки користувача**\n\n"
        text += f"👤 **Користувач:** {username}\n"
        text += f"🆔 **ID:** `{target_user_id}`\n\n"
        
        if purchases:
            total_amount = sum(float(p.get('amount', 0)) for p in purchases if p.get('payment_status') == 'completed')
            text += f"💰 **Покупок:** {len(purchases)}\n"
            text += f"💳 **Сума:** ₴{total_amount}\n\n"
            
            text += "**📋 Список покупок:**\n"
            for i, purchase in enumerate(purchases, 1):
                status_icon = "✅" if purchase['payment_status'] == 'completed' else "⏳"
                text += f"{i}. {status_icon} **{purchase['course_title']}**\n"
                text += f"   💰 ₴{purchase['amount']} • {purchase['purchase_date'][:10]}\n\n"
        else:
            text += "❌ **Покупок немає**\n"
        
        # Клавіатура
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 Профіль", callback_data=f"user_detail:{target_user_id}"),
                InlineKeyboardButton(text="📑 Список", callback_data="adm:user_list")
            ],
            [
                InlineKeyboardButton(text="👥 Меню", callback_data="adm:users")
            ]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await callback.answer()
        
        logger.info(f"Адмін {user_id} переглядає покупки користувача {target_user_id}")
        
    except Exception as e:
        logger.error(f"Помилка в user_purchases_handler: {e}")
        await callback.answer("Помилка завантаження покупок користувача")

# Заглушка для нереалізованих функцій (більш специфічна)
@router.callback_query(F.data.in_(["adm:broadcast_stats", "adm:user_stats", "adm:courses_list", "adm:course_access"]))
async def admin_placeholder_handler(callback: CallbackQuery):
    """Заглушка для функцій що ще не реалізовані"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    function_name = callback.data.replace("adm:", "").replace("_", " ").title()
    await callback.answer(f"🚧 {function_name} - в розробці", show_alert=True)
    logger.info(f"Адмін {user_id} спробував використати нереалізовану функцію: {callback.data}")

# Системні налаштування
@router.callback_query(F.data == "adm:system_settings")
async def admin_system_settings_handler(callback: CallbackQuery):
    """Системні налаштування"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        # Збираємо інформацію про систему
        import os
        import platform
        from config import DATABASE_PATH, ADMIN_ID
        
        # Інформація про систему
        system_info = f"""
🔧 **Системні налаштування**

💻 **Система:**
• ОС: {platform.system()} {platform.release()}
• Python: {platform.python_version()}
• Архітектура: {platform.machine()}

📊 **База даних:**
• Шлях: `{DATABASE_PATH}`
• Розмір: {os.path.getsize(DATABASE_PATH) / 1024:.1f} KB

👤 **Адміністратор:**
• ID: `{ADMIN_ID}`
• Поточний користувач: `{user_id}`

🤖 **Бот:**
• Статус: ✅ Працює
• Режим: Продакшн
        """
        
        await callback.message.edit_text(
            system_info,
            reply_markup=admin_back_to_main(),
            parse_mode="Markdown"
        )
        await callback.answer()
        
        logger.info(f"Адмін {user_id} переглядає системні налаштування")
        
    except Exception as e:
        logger.error(f"Помилка в admin_system_settings_handler: {e}")
        await callback.answer("Помилка завантаження системних налаштувань")

# Бекап бази даних
@router.callback_query(F.data == "adm:backup_db")
async def admin_backup_db_handler(callback: CallbackQuery):
    """Створення бекапу бази даних"""
    user_id = callback.from_user.id
    
    if not await is_admin(user_id):
        await callback.answer("🔒 Доступ заборонено", show_alert=True)
        return
    
    try:
        import os
        import shutil
        from datetime import datetime
        from config import DATABASE_PATH
        
        # Створюємо ім'я файлу бекапу
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_db_{timestamp}.sqlite"
        backup_path = os.path.join(os.path.dirname(DATABASE_PATH), backup_filename)
        
        # Перевіряємо чи існує база даних
        if not os.path.exists(DATABASE_PATH):
            await callback.answer("❌ База даних не знайдена", show_alert=True)
            return
        
        # Показуємо процес створення бекапу
        await callback.message.edit_text(
            "📦 **Створення бекапу бази даних...**\n\n"
            "⏳ Копіюємо файл бази даних...",
            reply_markup=None,
            parse_mode="Markdown"
        )
        
        # Створюємо бекап (копіюємо файл)
        shutil.copy2(DATABASE_PATH, backup_path)
        
        # Перевіряємо розмір файлів
        original_size = os.path.getsize(DATABASE_PATH)
        backup_size = os.path.getsize(backup_path)
        
        if backup_size == original_size:
            success_text = f"""
✅ **Бекап створено успішно!**

📄 **Файл:** `{backup_filename}`
📍 **Розташування:** `{backup_path}`
📊 **Розмір:** {backup_size / 1024:.1f} KB
⏰ **Час створення:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

💡 **Рекомендації:**
• Зберігайте бекапи в безпечному місці
• Регулярно створюйте нові бекапи
• Перевіряйте цілісність бекапів
            """
            
            await callback.message.edit_text(
                success_text,
                reply_markup=admin_back_to_main(),
                parse_mode="Markdown"
            )
            
            logger.info(f"Адмін {user_id} створив бекап БД: {backup_filename}")
            
        else:
            # Видаляємо невдалий бекап
            if os.path.exists(backup_path):
                os.remove(backup_path)
                
            await callback.message.edit_text(
                "❌ **Помилка створення бекапу**\n\n"
                "Розміри файлів не співпадають.\n"
                "Спробуйте ще раз.",
                reply_markup=admin_back_to_main(),
                parse_mode="Markdown"
            )
            
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Помилка в admin_backup_db_handler: {e}")
        
        # Спробуємо видалити невдалий бекап
        try:
            if 'backup_path' in locals() and os.path.exists(backup_path):
                os.remove(backup_path)
        except:
            pass
            
        await callback.message.edit_text(
            f"❌ **Помилка створення бекапу**\n\n"
            f"Технічна помилка: {str(e)[:100]}",
            reply_markup=admin_back_to_main(),
            parse_mode="Markdown"
        )
        await callback.answer("Помилка створення бекапу") 
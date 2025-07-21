"""
Клавіатури для PrometeyLabs Bot
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from typing import List, Dict, Any
from config import COMPANY_LINKS, CALLBACK_PREFIXES, SERVICES, ADMIN_ID

def add_admin_return_button(keyboard: List[List[InlineKeyboardButton]], user_id: int = None) -> List[List[InlineKeyboardButton]]:
    """Додає кнопку повернення в адмін панель якщо користувач є адміном"""
    if user_id and user_id == ADMIN_ID:
        keyboard.append([
            InlineKeyboardButton(
                text="🔧 Повернутися в адмін панель",
                callback_data="return_to_admin"
            )
        ])
    return keyboard

def main_menu(user_id: int = None) -> InlineKeyboardMarkup:
    """Головне меню"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="🛠 Послуги", 
                callback_data=f"{CALLBACK_PREFIXES['service']}main"
            ),
            InlineKeyboardButton(
                text="🎓 Курси", 
                callback_data=f"{CALLBACK_PREFIXES['course']}main"
            )
        ],
        [
            InlineKeyboardButton(
                text="📲 Онлайн-ресурси", 
                callback_data="online_resources"
            ),
            InlineKeyboardButton(
                text="👨‍💻 Про компанію", 
                callback_data="about_company"
            )
        ]
    ]
    
    # Додаємо кнопку повернення в адмін панель для адміна
    keyboard = add_admin_return_button(keyboard, user_id)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def services_menu(user_id: int = None) -> InlineKeyboardMarkup:
    """Меню послуг"""
    keyboard = [
        [InlineKeyboardButton(
            text=SERVICES['website']['title'],
            callback_data=f"{CALLBACK_PREFIXES['service']}website"
        )],
        [InlineKeyboardButton(
            text=SERVICES['telegram_bot']['title'],
            callback_data=f"{CALLBACK_PREFIXES['service']}telegram_bot"
        )],
        [InlineKeyboardButton(
            text=SERVICES['crm']['title'],
            callback_data=f"{CALLBACK_PREFIXES['service']}crm"
        )],
        [InlineKeyboardButton(
            text=SERVICES['social_media']['title'],
            callback_data=f"{CALLBACK_PREFIXES['service']}social_media"
        )],
        [InlineKeyboardButton(
            text="📞 Безкоштовна консультація",
            url=COMPANY_LINKS['telegram_manager']
        )]
    ]
    
    # Додаємо кнопку повернення в адмін панель для адміна
    keyboard = add_admin_return_button(keyboard, user_id)
    
    keyboard.append([InlineKeyboardButton(
        text="⬅️ Головне меню",
        callback_data="main_menu"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def website_service_keyboard() -> InlineKeyboardMarkup:
    """Клавіатура для послуги створення сайту"""
    keyboard = [
        [InlineKeyboardButton(
            text="💬 Написати в Telegram",
            url=COMPANY_LINKS['telegram_manager']
        )],
        [InlineKeyboardButton(
            text="🌐 Перейти на сайт",
            url=f"https://{COMPANY_LINKS['website']}"
        )],
        [InlineKeyboardButton(
            text="⬅️ Послуги",
            callback_data=f"{CALLBACK_PREFIXES['service']}main"
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def service_contact_keyboard(service_type: str) -> InlineKeyboardMarkup:
    """Універсальна клавіатура для контакту по послузі"""
    keyboard = [
        [InlineKeyboardButton(
            text="💬 Написати в Telegram",
            url=COMPANY_LINKS['telegram_manager']
        )],
        [InlineKeyboardButton(
            text="🌐 Перейти на сайт",
            url=f"https://{COMPANY_LINKS['website']}"
        )],
        [InlineKeyboardButton(
            text="⬅️ Послуги",
            callback_data=f"{CALLBACK_PREFIXES['service']}main"
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def courses_menu(user_id: int = None) -> InlineKeyboardMarkup:
    """Меню курсів - синхронізація з ZenEdu API"""
    keyboard = [
        [InlineKeyboardButton(
            text="🔄 Завантажити курси з ZenEdu",
            callback_data=f"{CALLBACK_PREFIXES['course']}sync"
        )]
    ]
    
    # Додаємо кнопку повернення в адмін панель для адміна
    keyboard = add_admin_return_button(keyboard, user_id)
    
    keyboard.append([InlineKeyboardButton(
        text="⬅️ Головне меню",
        callback_data="main_menu"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def course_card_keyboard(course_id: int, has_access: bool = False, 
                        z_link: str = None, price: int = None) -> InlineKeyboardMarkup:
    """Клавіатура для картки курсу з підтримкою ZenEdu"""
    keyboard = []
    
    if has_access:
        # Користувач має доступ до курсу
        if z_link and not z_link.startswith('zenedu://'):
            # Пряме посилання
            keyboard.append([InlineKeyboardButton(
                text="🎓 Перейти до курсу",
                url=z_link
            )])
        else:
            # Отримання доступу через ZenEdu
            keyboard.append([InlineKeyboardButton(
                text="🚀 Розпочати навчання",
                callback_data=f"{CALLBACK_PREFIXES['payment']}access_{course_id}"
            )])
    elif price and not has_access:
        # Користувач не має доступу, показуємо опції покупки
        keyboard.extend([
            [InlineKeyboardButton(
                text="🔍 Демо-урок",
                callback_data=f"{CALLBACK_PREFIXES['course']}demo_{course_id}"
            )],
            [InlineKeyboardButton(
                text=f"💳 Купити за {price} ₴",
                callback_data=f"{CALLBACK_PREFIXES['payment']}buy_{course_id}"
            )],
            [InlineKeyboardButton(
                text="💰 Методи оплати",
                callback_data=f"{CALLBACK_PREFIXES['payment']}methods"
            )]
        ])
    
    keyboard.append([InlineKeyboardButton(
        text="⬅️ До курсів",
        callback_data=f"{CALLBACK_PREFIXES['course']}main"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def online_resources_keyboard(user_id: int = None) -> InlineKeyboardMarkup:
    """Онлайн ресурси"""
    keyboard = [
        [InlineKeyboardButton(
            text="✈️ Telegram-канал",
            url=f"https://{COMPANY_LINKS['telegram_channel']}"
        )],
        [InlineKeyboardButton(
            text="📸 Instagram",
            url=f"https://www.instagram.com/{COMPANY_LINKS['instagram'][1:]}"
        )],
        [InlineKeyboardButton(
            text="🌐 Сайт",
            url=f"https://{COMPANY_LINKS['website']}"
        )]
    ]
    
    # Додаємо кнопку повернення в адмін панель для адміна
    keyboard = add_admin_return_button(keyboard, user_id)
    
    keyboard.append([InlineKeyboardButton(
        text="⬅️ Головне меню",
        callback_data="main_menu"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def about_company_keyboard(user_id: int = None) -> InlineKeyboardMarkup:
    """Про компанію"""
    keyboard = [
        [InlineKeyboardButton(
            text="📦 Портфоліо",
            callback_data="portfolio"
        )],
        [InlineKeyboardButton(
            text="🧠 Чому ми",
            callback_data="why_us"
        )],
        [InlineKeyboardButton(
            text="💳 Як відбувається оплата",
            callback_data="payment_info"
        )],
        [InlineKeyboardButton(
            text="🎓 Усі курси",
            callback_data=f"{CALLBACK_PREFIXES['course']}main"
        )]
    ]
    
    # Додаємо кнопку повернення в адмін панель для адміна
    keyboard = add_admin_return_button(keyboard, user_id)
    
    keyboard.append([InlineKeyboardButton(
        text="⬅️ Головне меню",
        callback_data="main_menu"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def portfolio_keyboard() -> InlineKeyboardMarkup:
    """Портфоліо клавіатура"""
    keyboard = [
        [InlineKeyboardButton(
            text="📸 Instagram (кейси в історіях)",
            url=f"https://www.instagram.com/{COMPANY_LINKS['instagram'][1:]}"
        )],
        [InlineKeyboardButton(
            text="🌐 Кейси на сайті",
            url=f"https://{COMPANY_LINKS['website']}"
        )],
        [InlineKeyboardButton(
            text="⬅️ Про компанію",
            callback_data="about_company"
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def back_to_about_keyboard() -> InlineKeyboardMarkup:
    """Повернутись до про компанію"""
    keyboard = [
        [InlineKeyboardButton(
            text="⬅️ Про компанію",
            callback_data="about_company"
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Адмін клавіатури
def admin_main_menu():
    """Головне адмін меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📬 Розсилки", callback_data="adm:broadcasts"),
            InlineKeyboardButton(text="👥 Користувачі", callback_data="adm:users")
        ],
        [
            InlineKeyboardButton(text="📊 Аналітика", callback_data="adm:analytics"),
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="adm:settings")
        ],
        [
            InlineKeyboardButton(text="🎓 Управління курсами", callback_data="adm:courses")
        ],
        [
            InlineKeyboardButton(text="👤 Режим користувача", callback_data="adm:user_mode")
        ]
    ])
    return keyboard

def admin_broadcasts_menu():
    """Меню розсилок"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Нова розсилка", callback_data="adm:broadcast_new"),
            InlineKeyboardButton(text="📅 Заплановані", callback_data="adm:broadcast_scheduled")
        ],
        [
            InlineKeyboardButton(text="🕓 Історія", callback_data="adm:broadcast_history"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="adm:broadcast_stats")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="adm:main")
        ]
    ])
    return keyboard

def admin_users_menu():
    """Меню користувачів"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Пошук", callback_data="adm:user_search"),
            InlineKeyboardButton(text="📑 Список", callback_data="adm:user_list")
        ],
        [
            InlineKeyboardButton(text="💲 Покупки", callback_data="adm:user_purchases")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="adm:main")
        ]
    ])
    return keyboard

def admin_courses_menu():
    """Меню управління курсами"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Синхронізувати з ZenEdu", callback_data="adm:sync_courses")
        ],
        [
            InlineKeyboardButton(text="📋 Список курсів", callback_data="adm:courses_list"),
            InlineKeyboardButton(text="👥 Доступи", callback_data="adm:course_access")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="adm:main")
        ]
    ])
    return keyboard

def admin_settings_menu():
    """Меню налаштувань"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔧 Системні налаштування", callback_data="adm:system_settings")
        ],
        [
            InlineKeyboardButton(text="🔗 Перевірити API", callback_data="adm:check_api"),
            InlineKeyboardButton(text="📦 Бекап БД", callback_data="adm:backup_db")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="adm:main")
        ]
    ])
    return keyboard

def admin_back_to_main():
    """Кнопка повернення до головного адмін меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Головне адмін меню", callback_data="adm:main")]
    ])
    return keyboard

def admin_user_mode_menu() -> InlineKeyboardMarkup:
    """Меню користувача для адміна з кнопкою повернення в адмін панель"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="🛠 Послуги", 
                callback_data=f"{CALLBACK_PREFIXES['service']}main"
            ),
            InlineKeyboardButton(
                text="🎓 Курси", 
                callback_data=f"{CALLBACK_PREFIXES['course']}main"
            )
        ],
        [
            InlineKeyboardButton(
                text="📲 Онлайн-ресурси", 
                callback_data="online_resources"
            ),
            InlineKeyboardButton(
                text="👨‍💻 Про компанію", 
                callback_data="about_company"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔧 Повернутися в адмін панель",
                callback_data="return_to_admin"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def user_actions_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Дії з користувачем"""
    keyboard = [
        [InlineKeyboardButton(
            text="⛔️ Блок",
            callback_data=f"{CALLBACK_PREFIXES['admin']}block_{user_id}"
        )],
        [InlineKeyboardButton(
            text="💲 Видати курс",
            callback_data=f"{CALLBACK_PREFIXES['admin']}grant_{user_id}"
        )],
        [InlineKeyboardButton(
            text="✉️ Написати",
            callback_data=f"{CALLBACK_PREFIXES['admin']}message_{user_id}"
        )],
        [InlineKeyboardButton(
            text="⬅️ Користувачі",
            callback_data=f"{CALLBACK_PREFIXES['admin']}users"
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def confirm_keyboard(action: str, item_id: str = "") -> InlineKeyboardMarkup:
    """Клавіатура підтвердження"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="✅ Підтвердити",
                callback_data=f"{CALLBACK_PREFIXES['admin']}confirm_{action}_{item_id}"
            ),
            InlineKeyboardButton(
                text="❌ Скасувати",
                callback_data=f"{CALLBACK_PREFIXES['admin']}cancel_{action}"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавіатури для управління користувачами
def users_list_pagination_keyboard(page: int = 0, total_pages: int = 1, has_prev: bool = False, has_next: bool = False):
    """Клавіатура для пагінації списку користувачів"""
    keyboard = []
    
    # Кнопки користувачів (додаються динамічно в обробнику)
    
    # Пагінація (без показу поточної сторінки)
    pagination_row = []
    if has_prev:
        pagination_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"users_page:{page-1}"))
    
    if has_next:
        pagination_row.append(InlineKeyboardButton(text="➡️", callback_data=f"users_page:{page+1}"))
    
    if pagination_row:
        keyboard.append(pagination_row)
    
    # Кнопки управління
    keyboard.append([
        InlineKeyboardButton(text="🔄 Оновити", callback_data="adm:user_list"),
        InlineKeyboardButton(text="🔍 Пошук", callback_data="adm:user_search")
    ])
    keyboard.append([
        InlineKeyboardButton(text="👥 Повернутися до меню користувачів", callback_data="adm:users")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def user_detail_keyboard(user_id: int, is_blocked: bool = False):
    """Клавіатура для деталей користувача"""
    keyboard = []
    
    # Показуємо тільки одну кнопку блокування залежно від статусу
    if is_blocked:
        keyboard.append([
            InlineKeyboardButton(text="✅ Розблокувати", callback_data=f"user_action:unblock_{user_id}")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton(text="⛔️ Блокувати", callback_data=f"user_action:block_{user_id}")
        ])
    
    keyboard.extend([
        [
            InlineKeyboardButton(text="💲 Видати курс", callback_data=f"user_action:grant_{user_id}"),
            InlineKeyboardButton(text="✉️ Написати від адміна", callback_data=f"user_action:message_{user_id}")
        ],
        [
            InlineKeyboardButton(text="💬 Написати в особисті", url=f"tg://user?id={user_id}"),
            InlineKeyboardButton(text="📊 Покупки", callback_data=f"user_purchases:{user_id}")
        ],
        [
            InlineKeyboardButton(text="📑 Повернутися до списку користувачів", callback_data="adm:user_list")
        ],
        [
            InlineKeyboardButton(text="👥 Повернутися до меню користувачів", callback_data="adm:users")
        ]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def purchases_list_keyboard(page: int = 0, total_pages: int = 1, has_prev: bool = False, has_next: bool = False):
    """Клавіатура для списку покупок"""
    keyboard = []
    
    # Пагінація
    pagination_row = []
    if has_prev:
        pagination_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"purchases_page:{page-1}"))
    
    pagination_row.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="purchases_page:current"))
    
    if has_next:
        pagination_row.append(InlineKeyboardButton(text="➡️", callback_data=f"purchases_page:{page+1}"))
    
    if pagination_row:
        keyboard.append(pagination_row)
    
    # Кнопки управління
    keyboard.append([
        InlineKeyboardButton(text="🔄 Оновити", callback_data="adm:user_purchases"),
        InlineKeyboardButton(text="👥 Меню", callback_data="adm:users")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def back_to_users_keyboard():
    """Кнопка повернення до меню користувачів"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Меню користувачів", callback_data="adm:users")]
    ])
    return keyboard

def cancel_search_keyboard():
    """Кнопка скасування пошуку"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати пошук", callback_data="adm:users")]
    ])
    return keyboard

def user_message_keyboard(user_id: int):
    """Клавіатура для меню відправки повідомлення користувачу"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 Повернутися до профілю користувача", callback_data=f"user_detail:{user_id}")
        ],
        [
            InlineKeyboardButton(text="📑 Повернутися до списку користувачів", callback_data="adm:user_list")
        ],
        [
            InlineKeyboardButton(text="👥 Повернутися до меню користувачів", callback_data="adm:users")
        ]
    ])
    return keyboard

# Клавіатури для розсилок
def broadcast_audience_keyboard():
    """Вибір аудиторії для розсилки"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Усі користувачі", callback_data="broadcast:audience_all")
        ],
        [
            InlineKeyboardButton(text="💰 Покупці курсів", callback_data="broadcast:audience_buyers")
        ],
        [
            InlineKeyboardButton(text="😴 Неактивні 7+ днів", callback_data="broadcast:audience_inactive")
        ],
        [
            InlineKeyboardButton(text="❌ Скасувати", callback_data="broadcast:cancel")
        ]
    ])
    return keyboard

def broadcast_schedule_keyboard():
    """Вибір часу відправки розсилки"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📤 Відправити одразу", callback_data="broadcast:schedule_now")
        ],
        [
            InlineKeyboardButton(text="📅 Запланувати на час", callback_data="broadcast:schedule_later")
        ],
        [
            InlineKeyboardButton(text="🔄 Регулярна розсилка", callback_data="broadcast:schedule_recurring")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="broadcast:back_to_audience"),
            InlineKeyboardButton(text="❌ Скасувати", callback_data="broadcast:cancel")
        ]
    ])
    return keyboard

def broadcast_confirm_keyboard():
    """Підтвердження розсилки"""  
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Підтвердити відправку", callback_data="broadcast:confirm_send")
        ],
        [
            InlineKeyboardButton(text="📝 Редагувати текст", callback_data="broadcast:edit_message"),
            InlineKeyboardButton(text="👥 Змінити аудиторію", callback_data="broadcast:edit_audience")
        ],
        [
            InlineKeyboardButton(text="📅 Змінити час", callback_data="broadcast:edit_schedule"),
            InlineKeyboardButton(text="❌ Скасувати", callback_data="broadcast:cancel")
        ]
    ])
    return keyboard

def broadcast_back_to_menu_keyboard():
    """Повернення до меню розсилок"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📬 Меню розсилок", callback_data="adm:broadcasts")
        ],
        [
            InlineKeyboardButton(text="🔧 Головна адмін панель", callback_data="adm:main")
        ]
    ])
    return keyboard

def broadcast_scheduled_list_keyboard(scheduled_broadcasts, recurring_broadcasts):
    """Клавіатура зі списком запланованих розсилок для видалення"""
    keyboard = []
    
    # Додаємо кнопки видалення для одноразових розсилок
    for i, broadcast in enumerate(scheduled_broadcasts, 1):
        keyboard.append([
            InlineKeyboardButton(
                text=f"🗑️ Видалити #{i} (одноразова)", 
                callback_data=f"delete_scheduled:{broadcast['id']}"
            )
        ])
    
    # Додаємо кнопки видалення для регулярних розсилок  
    scheduled_count = len(scheduled_broadcasts)
    for i, broadcast in enumerate(recurring_broadcasts, scheduled_count + 1):
        keyboard.append([
            InlineKeyboardButton(
                text=f"🗑️ Видалити #{i} (регулярна)",
                callback_data=f"delete_recurring:{broadcast['id']}"
            )
        ])
    
    # Кнопки навігації
    keyboard.append([
        InlineKeyboardButton(text="🔄 Оновити список", callback_data="adm:broadcast_scheduled")
    ])
    keyboard.append([
        InlineKeyboardButton(text="📬 Меню розсилок", callback_data="adm:broadcasts")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def broadcast_delete_confirm_keyboard(broadcast_type: str, broadcast_id: int):
    """Підтвердження видалення розсилки"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Так, видалити", 
                callback_data=f"confirm_delete_{broadcast_type}:{broadcast_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Скасувати", 
                callback_data="adm:broadcast_scheduled"
            )
        ]
    ])
    return keyboard

def broadcast_recurring_type_keyboard():
    """Вибір типу регулярної розсилки"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 Щоденно", callback_data="broadcast:recurring_daily")
        ],
        [
            InlineKeyboardButton(text="📆 Щотижнево", callback_data="broadcast:recurring_weekly")
        ],
        [
            InlineKeyboardButton(text="🗓️ Щомісяця", callback_data="broadcast:recurring_monthly")
        ],
        [
            InlineKeyboardButton(text="⚙️ Власний CRON", callback_data="broadcast:recurring_custom")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="broadcast:back_to_schedule"),
            InlineKeyboardButton(text="❌ Скасувати", callback_data="broadcast:cancel")
        ]
    ])
    return keyboard

def broadcast_datetime_keyboard():
    """Кнопки для введення дати/часу"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="broadcast:back_to_schedule"),
            InlineKeyboardButton(text="❌ Скасувати", callback_data="broadcast:cancel")
        ]
    ])
    return keyboard 
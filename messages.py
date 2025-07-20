"""
Тексти повідомлень для PrometeyLabs Bot
"""

from config import SERVICES, COMPANY_LINKS

# Привітання та головне меню
WELCOME_MESSAGE = """
🚀 Привіт! 

Я бот компанії PrometeyLabs — твій особистий гід у світі IT.

Оберіть, що саме вас цікавить? 👇"""

# Блок "Послуги"
SERVICES_MAIN_MESSAGE = """🛠 Інноваційні IT-рішення від PrometeyLabs

Швидко проєктуємо, розробляємо й запускаємо. Оберіть напрямок:"""

WEBSITE_SERVICE_MESSAGE = f"""⚡️ Сайт до ${SERVICES['website']['price']} і до {SERVICES['website']['delivery_days']} днів

{chr(10).join('• ' + feature for feature in SERVICES['website']['features'])}

📩 Напишіть повідомлення нижче — прорахуємо бюджет і строки."""

TELEGRAM_BOT_SERVICE_MESSAGE = f"""{SERVICES['telegram_bot']['title']}

{SERVICES['telegram_bot']['description']}

📩 Напишіть повідомлення для обговорення деталей проєкту."""

CRM_SERVICE_MESSAGE = f"""{SERVICES['crm']['title']}

{SERVICES['crm']['description']}

📩 Зв'яжіться з нами для обговорення вашого проєкту."""

SOCIAL_MEDIA_SERVICE_MESSAGE = f"""{SERVICES['social_media']['title']}

{SERVICES['social_media']['description']}

📩 Напишіть нам для розробки стратегії просування."""

# Блок "Курси"
COURSES_MAIN_MESSAGE = """🎓 Освітні програми

Оберіть курс або завантажте актуальний список з ZenEdu:"""

COURSES_LOADING_MESSAGE = """🔄 Завантажую курси з ZenEdu...

Це може зайняти кілька секунд."""

COURSES_LOADED_MESSAGE = """✅ Курси успішно завантажені!

Оберіть курс для перегляду:"""

COURSES_ERROR_MESSAGE = """❌ Помилка завантаження курсів з ZenEdu.

Спробуйте пізніше або зв'яжіться з підтримкою."""

NO_COURSES_MESSAGE = """📚 Курси ще не додані.

Слідкуйте за оновленнями в наших соцмережах!"""

def course_card_message(title: str, description: str, price: int, 
                       modules_count: int = None, duration: str = None) -> str:
    """Формує повідомлення картки курсу"""
    message = f"🎓 {title}\n\n"
    
    if description:
        message += f"{description}\n\n"
    
    if modules_count:
        message += f"• {modules_count} модулів\n"
    if duration:
        message += f"• Тривалість: {duration}\n"
    
    message += f"• Доступ назавжди\n\n💲 Ціна: {price} ₴"
    
    return message

COURSE_ACCESS_GRANTED_MESSAGE = """✅ Доступ до курсу надано!

Тепер ви можете перейти до навчання."""

COURSE_DEMO_MESSAGE = """🔍 Демо-урок буде доданий найближчим часом.

А поки що можете ознайомитись з повним описом курсу на нашому сайті."""

# Блок "Онлайн-ресурси"
ONLINE_RESOURCES_MESSAGE = """📲 Долучайтесь до нас 👇

Актуальні новини, кейси та корисні матеріали:"""

# Блок "Про компанію"
ABOUT_COMPANY_MESSAGE = """👨‍💻 PrometeyLabs — команда розробників, дизайнерів і AI-фахівців.

Ми запускаємо цифрові продукти й навчаємо тих, хто робить перші кроки в ІТ.

Що показати?"""

PORTFOLIO_MESSAGE = """📦 Наше портфоліо

Кейси та проєкти, які ми реалізували:"""

WHY_US_MESSAGE = """🧠 Чому обирають PrometeyLabs?

✅ Якість — працюємо за міжнародними стандартами
⚡ Швидкість — від ідеї до реалізації за тиждень
🎯 Результат — фокусуємось на ваших цілях
💬 Підтримка — супроводжуємо проєкт 24/7
🚀 Інновації — використовуємо найсучасніші технології"""

PAYMENT_INFO_MESSAGE = """💳 Як проходить оплата

✅ Ви отримуєте персональне посилання на оплату, де прописані:
— етапи та обсяг робіт
— точна сума й спосіб оплати  
— умови розстрочки (за потреби)

💵 Сплатити можна зручно:
— Apple Pay / Google Pay
— будь-якою карткою
— або прямим переказом за реквізитами

📆 За бажанням ділимо платіж на частини (наприклад 50% / 50%) — усе фіксуємо в договорі.

🔒 Розрахунки офіційні: інвойс і квитанція надсилаються одразу після оплати."""

# Адмін повідомлення
ADMIN_WELCOME_MESSAGE = """
🔧 Адмін панель PrometeyLabs Bot

Вітаю, адміністраторе! 

Оберіть розділ для управління:"""

ADMIN_ANALYTICS_MESSAGE = """
📊 Аналітика за 30 днів

👥 Користувачі:
• Всього: {users_count}
• Нових за день: {new_users_day}
• Нових за тиждень: {new_users_week}
• Нових за місяць: {new_users_month}
• Активних за тиждень: {active_week}

💰 Продажі:
• Покупок курсів: {course_purchases}
• Користувачів з покупками: {users_with_purchases}

📈 Взаємодії з ботом:
• За день: {daily_interactions}
• За тиждень: {weekly_interactions}"""

ADMIN_COURSES_SYNC_MESSAGE = """
🔄 Синхронізація з ZenEdu

⏳ Отримую список курсів...
"""

ADMIN_COURSES_SYNC_SUCCESS = """
✅ Синхронізація завершена!

📚 Знайдено курсів: {total_courses}
🆕 Нових курсів: {new_courses}
🔄 Оновлених курсів: {updated_courses}

Всі курси успішно синхронізовані з базою даних."""

ADMIN_COURSES_SYNC_ERROR = """
❌ Помилка синхронізації

Не вдалося підключитися до ZenEdu API.
Перевірте налаштування API ключа.

Деталі помилки записані в логи."""

ADMIN_BROADCAST_START_MESSAGE = """📬 Створення нової розсилки

Надішліть текст повідомлення (можна з медіа):"""

ADMIN_BROADCAST_AUDIENCE_MESSAGE = """👥 Оберіть аудиторію для розсилки:

• Усі користувачі
• Покупці курсів  
• Неактивні 7+ днів"""

ADMIN_BROADCAST_SCHEDULE_MESSAGE = """📅 Коли відправити?

• Одразу
• Запланувати на певний час"""

ADMIN_BROADCAST_CONFIRM_MESSAGE = """✅ Підтвердіть розсилку:

📝 Текст: {message_preview}
👥 Аудиторія: {audience}
📅 Час: {schedule_time}

Продовжити?"""

ADMIN_BROADCAST_SENT_MESSAGE = """✅ Розсилка відправлена!

📊 Надіслано: {sent_count}
❌ Помилок: {error_count}"""

ADMIN_USER_SEARCH_MESSAGE = """🔍 Пошук користувача

Надішліть ID, username або номер телефону:"""

ADMIN_USER_NOT_FOUND_MESSAGE = """❌ Користувача не знайдено.

Перевірте правильність введених даних."""

def admin_user_info_message(user_data: dict) -> str:
    """Формує інформацію про користувача для адміна"""
    message = f"""👤 Користувач {user_data['id']}

📝 Username: @{user_data.get('username', 'не вказано')}
📅 Приєднався: {user_data['joined_at']}
⏰ Остання активність: {user_data['last_activity']}
🚫 Заблокований: {'Так' if user_data.get('is_blocked') else 'Ні'}

Що зробити?"""
    return message

# Повідомлення про помилки та статуси
ERROR_MESSAGE = """
⚠️ Виникла помилка. Спробуйте пізніше або зверніться до підтримки.
"""

COMMAND_NOT_FOUND_MESSAGE = """
❓ Команда не розпізнана.

Скористайтесь меню нижче або відправте /start
"""

# Повідомлення оплати
PAYMENT_CREATED_MESSAGE = """💳 Створено рахунок для оплати

Сума: {amount} ₴
Курс: {course_title}

Посилання для оплати: {payment_url}

⏰ Рахунок дійсний 1 годину."""

PAYMENT_SUCCESS_MESSAGE = """✅ Оплата успішна!

Курс: {course_title}
Сума: {amount} ₴

Доступ до курсу надано. Перейдіть до навчання!"""

PAYMENT_FAILED_MESSAGE = """❌ Оплата не пройшла

Спробуйте ще раз або зв'яжіться з підтримкою."""

# Повідомлення ZenEdu інтеграції
ZENEDU_CONNECTION_ERROR = """⚠️ Проблема з підключенням до ZenEdu

Курси тимчасово недоступні. Спробуйте пізніше."""

ZENEDU_COURSE_ACCESS_ERROR = """❌ Помилка надання доступу до курсу в ZenEdu

Зв'яжіться з підтримкою."""

# Сповіщення про новий курс
def new_course_notification(title: str, price: int, description: str = "") -> str:
    """Повідомлення про новий курс"""
    message = f"""🎓 Новий курс від PrometeyLabs!

{title}

💲 Ціна: {price} ₴
"""
    if description:
        message += f"\n{description}\n"
    
    message += "\n🔗 Дізнатися більше та придбати можна в боті!"
    
    return message 
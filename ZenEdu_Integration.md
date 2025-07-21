# 🚀 Інтеграція PrometeyLabs Bot з ZenEdu

## 📋 Огляд

PrometeyLabs Telegram Bot тепер інтегрований з платформою [ZenEdu](https://www.zenedu.io/) для продажу та управління онлайн курсами безпосередньо в Telegram.

## 🔧 Налаштування

### API Токен
```
API Key: aKKYBIMaR92RXBxfR2Wp12G9CtFIB6k8E9EJabAM883db9a6
API URL: https://api.zenedu.io/v1
```

### Конфігурація (.env)
```bash
# ZenEdu API для продажу курсів
ZENEDU_API_URL=https://api.zenedu.io/v1
ZENEDU_API_KEY=aKKYBIMaR92RXBxfR2Wp12G9CtFIB6k8E9EJabAM883db9a6
ZENEDU_WEBHOOK_SECRET=your_webhook_secret_here
```

## 📚 Демо-курси

Система працює з наступними демо-курсами:

### 1. Основи Python програмування
- **Ціна:** 1500 ₴
- **ID:** course_1
- **Опис:** Повний курс Python з нуля до професіонала
- **Посилання:** https://zenedu.io/course/python-basics

### 2. Telegram Bot розробка  
- **Ціна:** 2500 ₴
- **ID:** course_2
- **Опис:** Створюємо професійних Telegram ботів
- **Посилання:** https://zenedu.io/course/telegram-bots

### 3. Веб-дизайн з Figma
- **Ціна:** 1200 ₴
- **ID:** course_3
- **Опис:** Сучасний веб-дизайн, макети в Figma
- **Посилання:** https://zenedu.io/course/web-design

## 🛠 Функціонал

### Для користувачів:
- 🛒 Перегляд каталогу курсів
- 💳 Покупка курсів через ZenEdu
- 🚀 Миттєвий доступ після оплати
- 🔗 Персональні посилання на курси
- 💰 Різні методи оплати

### Для адміністратора (@PrometeyLabs):
- 🔄 Синхронізація курсів з ZenEdu
- 🎁 Безкоштовна видача курсів
- 📊 Статистика продажів
- 👥 Управління доступами
- 📈 Аналітика курсів

## 🎮 Команди та кнопки

### Основні команди:
- `/start` - Запуск бота
- `/admin` - Адмін панель (тільки для @PrometeyLabs)

### Callback кнопки:
- `crs:main` - Головне меню курсів
- `crs:view_{id}` - Перегляд курсу
- `pay:buy_{id}` - Покупка курсу
- `pay:access_{id}` - Доступ до курсу
- `pay:methods` - Методи оплати

## 📁 Структура файлів

```
services/
├── zenedu_client.py        # ZenEdu API клієнт
└── __init__.py

handlers/
├── payments.py             # Обробники платежів
├── user.py                 # Користувацькі обробники
└── admin.py                # Адмін функції

config.py                   # Конфігурація з ZenEdu
keyboards.py                # Клавіатури з кнопками покупки
```

## 🔄 API Методи

### ZenEduClient основні методи:

```python
# Тестування з'єднання
await zenedu_client.test_connection()

# Отримання продуктів
products = await zenedu_client.get_products()

# Створення підписника
await zenedu_client.create_subscriber(user_id, username)

# Надання доступу
await zenedu_client.grant_product_access(product_id, user_id)

# Отримання посилання
link = await zenedu_client.get_product_access_link(product_id, user_id)

# Синхронізація з БД
count = await zenedu_client.sync_products_to_db()
```

### Хелпер функції:

```python
# Синхронізація курсів
from services.zenedu_client import sync_courses
synced_count = await sync_courses()

# Надання доступу з БД
from services.zenedu_client import grant_course_access_to_user
success = await grant_course_access_to_user(course_id, user_id)

# Перевірка з'єднання
from services.zenedu_client import check_zenedu_connection
is_connected = await check_zenedu_connection()
```

## 🔐 Безпека

- ✅ Тільки @PrometeyLabs (ID: 7603163573) має адмін доступ
- ✅ API ключ зберігається в змінних оточення
- ✅ Логування всіх операцій з курсами
- ✅ Перевірка доступу перед надання посилань
- ✅ Валідація всіх callback даних

## 📊 Логування

Система логує всі дії:

```
📚 Демо: отримано 3 продуктів
👤 Демо: створено підписника 7603163573 (PrometeyLabs)
🎓 Демо: надано доступ користувачу 7603163573 до продукту course_1
🔗 Демо: створено посилання для користувача 7603163573
✅ Користувач 7603163573 успішно купив курс course_1 через ZenEdu
```

## 🚀 Запуск

1. **Клонування репозиторію:**
```bash
git clone https://github.com/Sophie-sd/PrometeyLabs-TelegramBot.git
cd PrometeyLabs-TelegramBot
```

2. **Встановлення залежностей:**
```bash
pip install -r requirements.txt
```

3. **Налаштування .env:**
```bash
cp env.example .env
# Відредагуйте .env файл з правильними токенами
```

4. **Запуск бота:**
```bash
python3 main.py
```

## 🔧 Тестування

```bash
# Тест ZenEdu інтеграції
python3 -c "
import asyncio
from services.zenedu_client import sync_courses, check_zenedu_connection

async def test():
    connection = await check_zenedu_connection()
    if connection:
        synced = await sync_courses()
        print(f'Синхронізовано курсів: {synced}')

asyncio.run(test())
"
```

## 📞 Підтримка

**Розробник:** @PrometeyLabs  
**Telegram:** https://t.me/PrometeyLabs  
**Сайт:** https://prometeylabs.com

---

*Документація оновлена: 21.01.2025*  
*Версія бота: 2.0 з ZenEdu інтеграцією* 
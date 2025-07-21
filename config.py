"""
Конфігурація для PrometeyLabs Bot
"""

import os
from typing import List
from dotenv import load_dotenv

# Створюємо .env файл якщо він не існує
if not os.path.exists('.env'):
    env_content = """# PrometeyLabs Telegram Bot Configuration

# Токен бота (отримати у @BotFather)
BOT_TOKEN=8112513772:AAFIsM2RNDEQt5tyYCYAuZgpUsGmZUvP31M

# ID адміністратора (користувач з повним доступом)
# @PrometeyLabs ID: 7603163573
ADMIN_ID=7603163573

# Monobank API (опціонально)
MONOBANK_JAR_ID=your_monobank_jar_id_here

# ZenEdu API для продажу курсів
ZENEDU_API_URL=https://api.zenedu.io/v1
ZENEDU_API_KEY=aKKYBIMaR92RXBxfR2Wp12G9CtFIB6k8E9EJabAM883db9a6
ZENEDU_WEBHOOK_SECRET=your_webhook_secret_here
"""
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Створено .env файл з правильним токеном та ZenEdu API")
    except Exception as e:
        print(f"⚠️ Не вдалося створити .env файл: {e}")

# Завантажуємо змінні з .env файлу
load_dotenv(override=True)

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '8112513772:AAFIsM2RNDEQt5tyYCYAuZgpUsGmZUvP31M')
if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
    BOT_TOKEN = '8112513772:AAFIsM2RNDEQt5tyYCYAuZgpUsGmZUvP31M'
    print("✅ Використовується новий токен бота")

# Admin configuration  
ADMIN_ID = os.getenv('ADMIN_ID', '7603163573')
if not ADMIN_ID:
    ADMIN_ID = '7603163573'
    print("✅ Встановлено ADMIN_ID за замовчуванням")

try:
    ADMIN_ID = int(ADMIN_ID)
    # Додаткова перевірка на правильність ADMIN_ID
    if ADMIN_ID != 7603163573:
        print("⚠️ УВАГА: Знайдено неправильний ADMIN_ID!")
        print("🔄 Автоматично виправляю на правильний ID: 7603163573 (@PrometeyLabs)")
        os.environ['ADMIN_ID'] = '7603163573'
        ADMIN_ID = 7603163573
    print(f"✅ ADMIN_ID успішно встановлений: {ADMIN_ID} (@PrometeyLabs)")
except ValueError:
    print("❌ ADMIN_ID має бути числом, встановлюю за замовчуванням")
    ADMIN_ID = 7603163573

# Monobank configuration (опціонально)
MONOBANK_JAR_ID = os.getenv('MONOBANK_JAR_ID')

# ZenEdu configuration
ZENEDU_API_URL = os.getenv('ZENEDU_API_URL', 'https://api.zenedu.io/v1')
ZENEDU_API_KEY = os.getenv('ZENEDU_API_KEY', 'aKKYBIMaR92RXBxfR2Wp12G9CtFIB6k8E9EJabAM883db9a6')
ZENEDU_WEBHOOK_SECRET = os.getenv('ZENEDU_WEBHOOK_SECRET')

# Якщо API ключ не встановлений в .env, використовуємо за замовчуванням
if not ZENEDU_API_KEY or ZENEDU_API_KEY == 'your_zenedu_api_key_here':
    ZENEDU_API_KEY = 'aKKYBIMaR92RXBxfR2Wp12G9CtFIB6k8E9EJabAM883db9a6'
    print("✅ Встановлено ZenEdu API ключ для продажу курсів")

# Database configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'bot_database.db')

# Broadcast settings
BROADCAST_DELAY = 0.034  # 30 msg/sec максимум
MAX_RETRIES = 3

# Company links
COMPANY_LINKS = {
    'telegram_channel': 't.me/prometeylabs_channel',
    'telegram_manager': 'https://t.me/PrometeyLabs',
    'instagram': '@prometeylabs',
    'website': 'prometeylabs.com'
}

# Service pricing (приклади з ТЗ)
SERVICES = {
    'website': {
        'title': '💻 Створення сайту будь-якої складності',
        'price': 700,
        'delivery_days': 7,
        'features': [
            'Мобільна адаптивність',
            'Завантаження до 2 сек',
            'UI та копірайт під ваш бренд'
        ]
    },
    'telegram_bot': {
        'title': '🤖 Telegram-бот',
        'description': 'автоматизуємо бізнес-процеси'
    },
    'crm': {
        'title': '⚙️ CRM та інтеграції',
        'description': 'налаштовуємо, мігруємо дані'
    },
    'social_media': {
        'title': '📈 Соцмережі + AI-аватари',
        'description': 'рілси, автопости, нейромоделі'
    }
}

# Callback data prefixes (до 64 символів)
CALLBACK_PREFIXES = {
    'service': 'srv:',
    'course': 'crs:',
    'admin': 'adm:',
    'payment': 'pay:'
}

# Максимальні розміри
MAX_CALLBACK_DATA_LENGTH = 64
MAX_MESSAGE_LENGTH = 4096

# Часові інтервали
SESSION_TIMEOUT = 3600  # 1 година
CACHE_TTL = 1800  # 30 хвилин

# Environment configuration для Render
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # production або development
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://prometeylabs-telegram-bot-90mo.onrender.com')
PORT = int(os.getenv('PORT', 8000)) 
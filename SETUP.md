# Налаштування PrometeyLabs Telegram Bot

## 🚀 Швидкий старт

### 1. Клонування репозиторію
```bash
git clone https://github.com/your-username/prometeylabs-telegram-bot.git
cd prometeylabs-telegram-bot
```

### 2. Встановлення залежностей
```bash
pip install -r requirements.txt
```

### 3. Налаштування оточення

Створіть файл `.env` в корені проекту:
```bash
# Telegram Bot
BOT_TOKEN=your_bot_token_here

# Адміністратор
ADMIN_ID=your_admin_user_id_here

# База даних
DATABASE_PATH=bot_database.db

# ZenEdu API (опціонально)
ZENEDU_API_URL=https://api.zenedu.com
ZENEDU_API_KEY=your_zenedu_api_key

# Monobank API (опціонально)
MONOBANK_TOKEN=your_monobank_token
```

### 4. Запуск бота
```bash
python3 main.py
```

## 📋 Вимоги

- Python 3.8+
- aiogram 3.x
- aiosqlite
- python-dotenv

## 🔧 Налаштування адміністратора

1. Створіть бота через [@BotFather](https://t.me/BotFather)
2. Отримайте токен бота
3. Дізнайтеся свій Telegram ID (можна через [@userinfobot](https://t.me/userinfobot))
4. Вкажіть дані в `.env` файлі

## 📁 Структура проекту

```
prometeylabs_telegram_bot/
├── handlers/          # Обробники команд та callback'ів
│   ├── admin.py      # Адміністративна панель
│   ├── user.py       # Користувацькі команди
│   └── payments.py   # Обробка платежів
├── middleware/        # Middleware для авторизації
├── services/         # Інтеграції з зовнішніми сервісами
├── states/           # FSM стани для діалогів
├── keyboards.py      # Inline клавіатури
├── messages.py       # Тексти повідомлень
├── config.py         # Конфігурація
├── db.py            # Робота з базою даних
└── main.py          # Точка входу
```

## 🛠️ Функціонал

### Для користувачів:
- 🛠 Послуги компанії
- 🎓 Каталог курсів
- 📲 Онлайн-ресурси
- 👨‍💻 Інформація про компанію

### Для адміністратора:
- 📊 Аналітика користувачів
- 📬 Система розсилок
- 👥 Управління користувачами
- 🎓 Управління курсами
- ⚙️ Системні налаштування
- 📦 Бекап бази даних

## 🚨 Безпека

- Токен бота та інші чутливі дані зберігаються в `.env`
- Адмін доступ контролюється через ADMIN_ID
- База даних та логи виключені з Git репозиторію

## 📝 Деплой

### На VPS:
1. Клонуйте репозиторій
2. Налаштуйте `.env`
3. Встановіть systemd service для автозапуску
4. Налаштуйте nginx для webhook (опціонально)

### На Heroku:
1. Створіть Heroku додаток
2. Додайте Config Vars з `.env`
3. Підключіть GitHub репозиторій
4. Деплой

## 🐛 Траблшутинг

### Бот не запускається:
- Перевірте BOT_TOKEN в `.env`
- Переконайтеся що бот активований в BotFather

### Немає доступу до адмін панелі:
- Перевірте ADMIN_ID в `.env`
- Переконайтеся що ID вказано правильно

### Помилки бази даних:
- Перевірте права доступу до файлу БД
- Переконайтеся що папка існує

## 📞 Підтримка

Для питань та пропозицій:
- Telegram: [@PrometeyLabs](https://t.me/PrometeyLabs)
- Email: contact@prometeylabs.com 
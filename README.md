# PrometeyLabs Telegram Bot

Професійний Telegram-бот для компанії PrometeyLabs з інтеграцією курсів ZenEdu.

## 🚀 Особливості

- 🛠 **Послуги** - презентація IT-послуг компанії
- 🎓 **Курси** - інтеграція з платформою ZenEdu для продажу курсів
- 📊 **Адмін-панель** - управління користувачами, розсилками та курсами
- 🔒 **Безпека** - захищений доступ та авторизація
- ⚡ **Деплой** - готовий до роботи на Render

## 📋 Технології

- **Python 3.9+** - основна мова
- **aiogram 3.4** - фреймворк для Telegram Bot API
- **SQLite** - база даних
- **ZenEdu API** - платформа курсів
- **aiohttp** - веб-сервер для webhook
- **Render** - хмарна платформа

## 🎯 Функціонал

### Для користувачів:
- Перегляд послуг та курсів
- Покупка курсів через ZenEdu
- Онлайн-ресурси компанії
- Інформація про PrometeyLabs

### Для адміністратора (@PrometeyLabs):
- Повна аналітика користувачів
- Управління розсилками
- Синхронізація курсів з ZenEdu
- Видача безкоштовного доступу
- Системний моніторинг

## ⚙️ Деплой

Проект готовий до деплою на **Render**:

1. Підключіть GitHub репозиторій до Render
2. Налаштуйте Environment Variables:
   - `ENVIRONMENT=production`
   - `BOT_TOKEN=8112513772:AAFIsM2RNDEQt5tyYCYAuZgpUsGmZUvP31M`
   - `ADMIN_ID=7603163573`
   - `WEBHOOK_URL=https://your-app.onrender.com`
   - `ZENEDU_API_KEY=aKKYBIMaR92RXBxfR2Wp12G9CtFIB6k8E9EJabAM883db9a6`
3. Деплойте сервіс
4. Тестуйте через [@prometeylabs_bot](https://t.me/prometeylabs_bot)

Детальна інструкція: [`DEPLOY_RENDER.md`](./DEPLOY_RENDER.md)

## 📊 Структура

```
├── main.py              # Точка входу (webhook/polling)
├── config.py            # Конфігурація
├── db.py               # База даних SQLite
├── keyboards.py        # Клавіатури бота
├── messages.py         # Тексти повідомлень
├── handlers/           # Обробники подій
│   ├── admin.py       # Адмін функції
│   ├── user.py        # Користувацькі функції
│   └── payments.py    # Платежі ZenEdu
├── middleware/        # Проміжний шар
│   └── auth.py        # Авторизація
├── services/          # Зовнішні API
│   └── zenedu_client.py # ZenEdu інтеграція
├── states/            # FSM стани
│   └── broadcast_states.py
├── render.yaml        # Конфігурація Render
└── requirements.txt   # Python залежності
```

## 🔒 Безпека

- **Єдиний адмін:** @PrometeyLabs (ID: 7603163573)
- **Middleware авторизації** для всіх адмін функцій
- **Захищені токени** через environment variables
- **Логування** всіх дій для аудиту

## 📞 Контакти

- **Telegram:** [@PrometeyLabs](https://t.me/PrometeyLabs)
- **Сайт:** [prometeylabs.com](https://prometeylabs.com)
- **Бот:** [@prometeylabs_bot](https://t.me/prometeylabs_bot)

---

**PrometeyLabs** - ваш надійний партнер у світі IT-рішень 🚀 
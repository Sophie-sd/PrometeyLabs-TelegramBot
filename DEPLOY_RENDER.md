# 🚀 Деплой PrometeyLabs Bot на Render

## 📋 Передумови

✅ **Підтверджені налаштування:**
- Єдиний адмін: @PrometeyLabs (ID: 7603163573)
- Токен бота: 8112513772:AAFIsM2RNDEQt5tyYCYAuZgpUsGmZUvP31M
- ZenEdu API інтеграція налаштована
- Всі функції адмін панелі протестовані

## 🔧 Крок 1: Підготовка проекту

### Перевірка безпеки
```bash
python3 security_check.py
```

Ця команда перевірить:
- 🔐 Правильність ADMIN_ID (7603163573)
- 🤖 Токен бота
- 🌍 Змінні середовища
- 📁 Права доступу до файлів

## 🌐 Крок 2: Створення сервісу на Render

### 2.1 Підключення репозиторію
1. Відкрийте [Render Dashboard](https://dashboard.render.com/)
2. Натисніть **"New +"** → **"Web Service"**
3. Підключіть GitHub репозиторій: `PrometeyLabs-TelegramBot`
4. Оберіть **"Connect"**

### 2.2 Налаштування сервісу

**Basic Settings:**
- **Name:** `prometeylabs-telegram-bot`
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1`

**Advanced Settings:**
- **Health Check Path:** `/health`
- **Auto-Deploy:** `Yes`

## 🔑 Крок 3: Налаштування змінних середовища

**Environment Variables:**

| Назва | Значення | Опис |
|-------|----------|------|
| `ENVIRONMENT` | `production` | Режим роботи |
| `BOT_TOKEN` | `8112513772:AAFIsM2RNDEQt5tyYCYAuZgpUsGmZUvP31M` | Токен Telegram бота |
| `ADMIN_ID` | `7603163573` | ID єдиного адміна @PrometeyLabs |
| `WEBHOOK_URL` | `https://your-app-name.onrender.com` | URL вашого деплою |
| `ZENEDU_API_URL` | `https://api.zenedu.io/v1` | ZenEdu API URL |
| `ZENEDU_API_KEY` | `aKKYBIMaR92RXBxfR2Wp12G9CtFIB6k8E9EJabAM883db9a6` | ZenEdu API ключ |
| `DATABASE_PATH` | `bot_database.db` | Шлях до файлу БД |

### ⚠️ Важливо: WEBHOOK_URL
Після створення сервісу скопіюйте URL (наприклад: `https://prometeylabs-bot.onrender.com`) та встановіть його як `WEBHOOK_URL`.

## 🚀 Крок 4: Деплой

1. **Натисніть "Create Web Service"**
2. **Дочекайтеся завершення білду** (5-10 хвилин)
3. **Перевірте логи деплою:**
   ```
   ✅ База даних ініціалізована
   ✅ Webhook налаштований: https://your-app.onrender.com/webhook/8112513772
   ✅ Бот запущено для @PrometeyLabs (ADMIN_ID: 7603163573)
   ```

## ✅ Крок 5: Перевірка після деплою

### 5.1 Health Check
Відкрийте в браузері: `https://your-app-name.onrender.com/health`
Очікуваний результат: `PrometeyLabs Bot OK`

### 5.2 Тест бота
1. **Відкрийте бот:** [@prometeylabs_bot](https://t.me/prometeylabs_bot)
2. **Відправте:** `/start`
3. **Перевірте головне меню**
4. **Для адміна (@PrometeyLabs):** `/admin`

### 5.3 Тест адмін панелі
**Обов'язково протестуйте:**
- ✅ `/admin` - відкриття панелі
- ✅ 📊 Аналітика
- ✅ 📬 Розсилки
- ✅ 👥 Користувачі
- ✅ 🎓 Курси та синхронізація ZenEdu
- ✅ ⚙️ Налаштування

## 🔍 Моніторинг та логи

### Перегляд логів
В Render Dashboard → Services → prometeylabs-telegram-bot → Logs

**Важливі логи для пошуку:**
```
✅ Підтверджено адмін доступ для @PrometeyLabs
✅ Webhook налаштований
🔄 Callback від користувача
❌ Спроба доступу з неправильним ADMIN_ID
```

### Метрики
Render показує:
- CPU та Memory використання
- Час відповіді
- Кількість запитів
- Аптайм

## 🚨 Траблшутинг

### Проблема: Бот не відповідає
**Рішення:**
1. Перевірте логи на помилки
2. Переконайтеся що `WEBHOOK_URL` правильний
3. Перевірте що токен бота активний

### Проблема: Адмін панель не працює
**Рішення:**
1. Перевірте `ADMIN_ID=7603163573`
2. Перевірте логи на відхилення доступу
3. Переконайтеся що користувач @PrometeyLabs

### Проблема: ZenEdu синхронізація
**Рішення:**
1. Перевірте `ZENEDU_API_KEY`
2. Перевірте логи ZenEdu клієнта
3. Перевірте мережеві підключення

## 🔄 Оновлення

### Автоматичне оновлення
- При push в main branch Render автоматично деплоїть
- Час деплою: 3-5 хвилин
- Zero downtime deployment

### Ручне оновлення
1. Render Dashboard → Services → prometeylabs-telegram-bot
2. Натисніть **"Manual Deploy"**
3. Оберіть **"Deploy latest commit"**

## 📊 Продакшн чеклист

- [ ] ✅ ADMIN_ID перевірений (7603163573)
- [ ] ✅ BOT_TOKEN активний
- [ ] ✅ WEBHOOK_URL налаштований
- [ ] ✅ Health check відповідає
- [ ] ✅ Адмін панель працює
- [ ] ✅ ZenEdu інтеграція активна
- [ ] ✅ База даних ініціалізована
- [ ] ✅ Логи без помилок
- [ ] ✅ Автодеплой налаштований

---

## 🎯 Результат

**Після успішного деплою:**
- 🤖 Бот працює 24/7 на Render
- 🔒 Тільки @PrometeyLabs має адмін доступ
- 📊 Всі функції адмін панелі працюють
- 💰 ZenEdu інтеграція для продажу курсів
- 📈 Автоматичні оновлення з GitHub
- 🔍 Моніторинг та логування

**PrometeyLabs Bot готовий до роботи! 🚀** 
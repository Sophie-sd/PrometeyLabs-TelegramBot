# 🚀 Гід для деплою PrometeyLabs Telegram Bot на Render

## 📋 Що було виправлено

### ✅ Проблеми, які призводили до помилок:

1. **aiohttp==3.8.1 → 3.9.5** - виправлена несумісність з Python 3.13
2. **Procfile** - замінено gunicorn на python main.py для телеграм бота  
3. **render.yaml** - видалено --only-binary=all, додано health check
4. **Додано .python-version** - для чіткого контролю версії Python
5. **Health check endpoint** - для моніторингу статусу сервісу Render

## 🛠 Кроки для успішного деплою

### 1. Підготовка проекту
```bash
# Всі необхідні файли вже оновлені:
# ✅ requirements.txt - оновлені залежності
# ✅ Procfile - правильна команда запуску  
# ✅ render.yaml - оптимізована конфігурація
# ✅ .python-version - Python 3.11.7
# ✅ main.py - додано health check endpoint
```

### 2. Налаштування змінних середовища в Render
Обов'язково встановіть ці змінні в Render Dashboard:

```
BOT_TOKEN=8112513772:AAFIsM2RNDEQt5tyYCYAuZgpUsGmZUvP31M
ADMIN_ID=7603163573
WEBHOOK_URL=https://your-app-name.onrender.com
ZENEDU_API_URL=https://api.zenedu.io/v1
ZENEDU_API_KEY=aKKYBIMaR92RXBxfR2Wp12G9CtFIB6k8E9EJabAM883db9a6
DATABASE_PATH=bot_database.db
ENVIRONMENT=production
PORT=10000
```

### 3. Створення сервісу в Render

1. **Зайдіть на render.com** і створіть новий Web Service
2. **Підключіть GitHub репозиторій** 
3. **Налаштування сервісу:**
   - Name: `prometeylabs-telegram-bot`
   - Runtime: `Python 3.11.7`
   - Build Command: `pip install --upgrade pip && pip install -r requirements.txt`
   - Start Command: `python main.py`
   - Health Check Path: `/health`

### 4. Встановіть змінні середовища
Додайте всі змінні з пункту 2 в розділі Environment Variables

### 5. Деплой
Натисніть "Deploy" і дочекайтесь успішного деплою

## 📍 Важливі моменти

### Webhook URL
Після деплою оновіть змінну `WEBHOOK_URL` в Render:
```
WEBHOOK_URL=https://ваше-ім'я-додатка.onrender.com
```

### Health Check  
Бот тепер відповідає на GET `/health` запити статусом 200 OK

### Database
SQLite база створюється автоматично в файлі `bot_database.db`

## 🔧 Тестування після деплою

1. **Перевірте логи** в Render Dashboard
2. **Тестуйте бота** - відправте `/start` в Telegram
3. **Health check** - перейдіть на `https://ваш-додаток.onrender.com/health`

## 🚨 Якщо виникають помилки

### Проблеми з залежностями
```bash
# Локально перевірте requirements.txt:
pip install -r requirements.txt
```

### Проблеми з webhook
```bash
# Перевірте змінні середовища:
echo $WEBHOOK_URL
echo $BOT_TOKEN
```

### Проблеми з базою даних
```bash  
# База SQLite створюється автоматично
# Перевірте права доступу до файлової системи
```

## 📞 Підтримка

У разі проблем зверніться до команди Render Support або перевірте:
- [Render Documentation](https://render.com/docs)
- [Python on Render Guide](https://render.com/docs/python-version)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---
**✅ Проект готовий до продакшену!** 🎉 
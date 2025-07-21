# 🚀 Деплойment PrometeyLabs Bot на Render

## Основні зміни для webhook режиму

### 1. Архітектура
- **Локально**: Polling (getUpdates)
- **На Render**: Webhook (HTTP endpoint)

### 2. Змінні оточення в Render

Обов'язково встановіть такі змінні:

```bash
ENVIRONMENT=production
BOT_TOKEN=8112513772:AAFIsM2RNDEQt5tyYCYAuZgpUsGmZUvP31M
ADMIN_ID=7603163573
WEBHOOK_URL=https://prometeylabs-telegram-bot.onrender.com
PORT=8000
ZENEDU_API_URL=https://api.zenedu.io/v1
ZENEDU_API_KEY=aKKYBIMaR92RXBxfR2Wp12G9CtFIB6k8E9EJabAM883db9a6
DATABASE_PATH=bot_database.db
```

### 3. Ключові endpoint'и

- **Health Check**: `GET /health` - перевірка роботи бота
- **Webhook**: `POST /webhook/8112513772` - прийом оновлень від Telegram

### 4. Логіка роботи

#### Production режим (Render):
1. Видаляє старий webhook
2. Встановлює новий webhook на Render URL
3. Запускає aiohttp сервер на порту з PORT
4. Обробляє оновлення через webhook

#### Development режим (локально):
1. Видаляє webhook
2. Запускає polling режим
3. Обробляє оновлення через getUpdates

### 5. Файли конфігурації

#### render.yaml
```yaml
services:
  - type: web
    name: prometeylabs-telegram-bot
    runtime: python
    pythonVersion: "3.11"
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: python main.py
    healthCheckPath: /health
    envVars:
      - key: ENVIRONMENT
        value: production
      # ... інші змінні
```

#### Procfile
```
web: python main.py
```

### 6. Тестування

Для локального тестування webhook'а:
```bash
python test_webhook.py
```

### 7. Логи Render

Типові повідомлення при успішному запуску:
```
✅ База даних ініціалізована
🗑️ Старий webhook видалено
✅ Webhook налаштований: https://prometeylabs-telegram-bot.onrender.com/webhook/8112513772
🌐 HTTP сервер запущено на 0.0.0.0:8000
📡 Webhook endpoint: /webhook/8112513772
```

### 8. Вирішення проблем

#### Помилка "Conflict: can't use getUpdates method while webhook is active"
- **Причина**: Одночасне використання polling та webhook
- **Рішення**: Код тепер автоматично вибирає режим по ENVIRONMENT

#### Timeout на Render
- **Причина**: Блокування основного потоку
- **Рішення**: Асинхронне очікування з `asyncio.Event().wait()`

#### Webhook не працює
1. Перевірте WEBHOOK_URL в змінних оточення
2. Переконайтеся що порт правильний (PORT=8000)
3. Запустіть `test_webhook.py` для діагностики

### 9. Автоматичний деплой

При push в main гілку:
1. Render автоматично build'ить додаток
2. Встановлює залежності з requirements.txt  
3. Запускає main.py з production змінними
4. Бот автоматично налаштовує webhook

### 10. Моніторинг

- **Health check**: https://prometeylabs-telegram-bot.onrender.com/health
- **Логи**: Render Dashboard > Service > Logs
- **Webhook статус**: `/test_webhook.py` локально

### 11. Переваги нового підходу

✅ Автоматичний вибір режиму (production/development)  
✅ Правильне управління webhook'ом  
✅ Health check для Render  
✅ Асинхронна архітектура  
✅ Відсутність конфліктів polling/webhook  
✅ Автоматичне очищення старих webhook'ів 
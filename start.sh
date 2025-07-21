#!/bin/bash

# PrometeyLabs Telegram Bot Starter Script
echo "🚀 Запускаємо PrometeyLabs Telegram Bot..."

# Активація віртуального середовища
source venv/bin/activate

# Перевірка чи існує .env файл
if [ ! -f .env ]; then
    echo "⚠️ Файл .env не знайдено. Створюю з config.py..."
fi

# Запуск бота
echo "✅ Віртуальне середовище активоване"
echo "🤖 Запускаю бота..."
python main.py 
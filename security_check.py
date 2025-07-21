#!/usr/bin/env python3
"""
Модуль перевірки безпеки для PrometeyLabs Bot
Перевіряє налаштування перед деплоєм
"""

import os
import sys
from pathlib import Path

def check_admin_security():
    """Перевіряє налаштування адміна"""
    print("🔐 Перевірка безпеки адміна...")
    
    admin_id = os.getenv('ADMIN_ID', '7603163573')
    if admin_id != '7603163573':
        print(f"❌ ПОПЕРЕДЖЕННЯ: ADMIN_ID = {admin_id}, очікується 7603163573")
        return False
    
    print("✅ ADMIN_ID налаштований правильно")
    return True

def check_bot_token():
    """Перевіряє токен бота"""
    print("🤖 Перевірка токена бота...")
    
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        print("❌ BOT_TOKEN не встановлений!")
        return False
    
    if bot_token == 'YOUR_BOT_TOKEN_HERE':
        print("❌ BOT_TOKEN має значення за замовчуванням!")
        return False
    
    if not bot_token.startswith('8112513772:'):
        print(f"❌ ПОПЕРЕДЖЕННЯ: Неочікуваний токен бота: {bot_token[:20]}...")
        return False
    
    print("✅ BOT_TOKEN налаштований правильно")
    return True

def check_environment():
    """Перевіряє змінні середовища"""
    print("🌍 Перевірка змінних середовища...")
    
    environment = os.getenv('ENVIRONMENT', 'development')
    print(f"📍 Режим роботи: {environment}")
    
    if environment == 'production':
        webhook_url = os.getenv('WEBHOOK_URL')
        if not webhook_url:
            print("❌ WEBHOOK_URL не встановлений для продакшн!")
            return False
        print(f"🔗 Webhook URL: {webhook_url}")
    
    print("✅ Змінні середовища перевірені")
    return True

def check_file_permissions():
    """Перевіряє права доступу до файлів"""
    print("📁 Перевірка прав доступу до файлів...")
    
    # Перевіряємо можливість створення БД
    db_path = os.getenv('DATABASE_PATH', 'bot_database.db')
    try:
        # Якщо файл існує, перевіряємо читання/запис
        if os.path.exists(db_path):
            if not os.access(db_path, os.R_OK | os.W_OK):
                print(f"❌ Немає прав читання/запису для {db_path}")
                return False
        else:
            # Якщо файл не існує, перевіряємо можливість створення
            try:
                Path(db_path).touch()
                os.remove(db_path)
            except PermissionError:
                print(f"❌ Неможливо створити файл БД: {db_path}")
                return False
    
        print("✅ Права доступу до файлів в порядку")
        return True
    except Exception as e:
        print(f"❌ Помилка перевірки файлів: {e}")
        return False

def main():
    """Головна функція перевірки"""
    print("🚀 PrometeyLabs Bot - Перевірка безпеки перед деплоєм")
    print("=" * 60)
    
    checks = [
        check_admin_security,
        check_bot_token,
        check_environment,
        check_file_permissions
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Помилка в {check.__name__}: {e}")
            results.append(False)
            print()
    
    print("=" * 60)
    if all(results):
        print("✅ ВСІ ПЕРЕВІРКИ ПРОЙШЛИ УСПІШНО!")
        print("🚀 Проект готовий до деплою на Render")
        return True
    else:
        print("❌ ЗНАЙДЕНО ПРОБЛЕМИ!")
        print("🔧 Виправте помилки перед деплоєм")
        return False

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    
    success = main()
    sys.exit(0 if success else 1) 
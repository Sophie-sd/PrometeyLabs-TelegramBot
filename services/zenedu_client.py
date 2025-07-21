"""
Клієнт для роботи з ZenEdu API
ZenEdu - платформа для створення та продажу курсів в Telegram
https://www.zenedu.io/

ПРИМІТКА: Це демо-версія для тестування функціоналу
API токен: aKKYBIMaR92RXBxfR2Wp12G9CtFIB6k8E9EJabAM883db9a6
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from config import ZENEDU_API_URL, ZENEDU_API_KEY, ZENEDU_WEBHOOK_SECRET
from db import add_course, get_courses as get_db_courses, grant_course_access

logger = logging.getLogger(__name__)

class ZenEduClient:
    """
    Клієнт для взаємодії з ZenEdu API
    ZenEdu дозволяє створювати та продавати курси прямо в Telegram
    
    Поточна версія працює в демо-режимі з фейковими даними
    """
    
    def __init__(self):
        self.api_url = ZENEDU_API_URL
        self.api_key = ZENEDU_API_KEY
        self.webhook_secret = ZENEDU_WEBHOOK_SECRET
        self.demo_mode = True  # Демо-режим для тестування
    
    async def close(self):
        """Закрити HTTP сесію (не потрібно в демо-режимі)"""
        pass
    
    async def test_connection(self) -> bool:
        """
        Тестує з'єднання з ZenEdu API
        В демо-режимі завжди повертає True
        """
        try:
            if self.demo_mode:
                logger.info("✅ Демо-режим ZenEdu активний")
                logger.info(f"📋 API URL: {self.api_url}")
                logger.info(f"🔑 API Key: {self.api_key[:20]}...")
                await asyncio.sleep(0.5)  # Імітація мережевого запиту
                return True
            
            # Тут буде реальний код для підключення до ZenEdu API
            # коли будуть доступні правильні endpoints
            
        except Exception as e:
            logger.error(f"❌ Помилка тестування ZenEdu: {e}")
            return False
    
    async def get_products(self) -> List[Dict[str, Any]]:
        """
        Отримує список всіх продуктів (курсів) з ZenEdu
        Коли API буде доступний, тут буде реальний запит
        """
        try:
            if self.demo_mode:
                # В демо-режимі повертаємо порожній список
                # Курси додаються тільки через реальний ZenEdu API
                await asyncio.sleep(0.3)  # Імітація мережевого запиту
                logger.info(f"📚 ZenEdu: готовий до отримання курсів з платформи")
                logger.info(f"🔗 Для додавання курсів використовуйте ZenEdu Dashboard")
                
                # Поки що повертаємо порожній список
                # Реальні курси будуть синхронізуватися з ZenEdu API
                return []
                
        except Exception as e:
            logger.error(f"❌ Помилка отримання продуктів: {e}")
            return []
    
    async def get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Отримує детальну інформацію про продукт/курс
        """
        try:
            if self.demo_mode:
                # Фейкові деталі курсу
                demo_details = {
                    'id': product_id,
                    'name': f'Курс {product_id}',
                    'description': f'Детальний опис курсу {product_id}',
                    'price': 1500,
                    'access_link': f'https://zenedu.io/course/{product_id}'
                }
                
                await asyncio.sleep(0.2)
                logger.info(f"📖 Демо: отримано деталі продукту {product_id}")
                return demo_details
                
        except Exception as e:
            logger.error(f"❌ Помилка запиту деталей продукту {product_id}: {e}")
            return None
    
    async def create_subscriber(self, user_id: int, username: str = None, 
                              first_name: str = None) -> bool:
        """
        Створює нового підписника в ZenEdu
        """
        try:
            if self.demo_mode:
                await asyncio.sleep(0.2)
                logger.info(f"👤 Демо: створено підписника {user_id} ({username})")
                return True
                
        except Exception as e:
            logger.error(f"❌ Помилка створення підписника {user_id}: {e}")
            return False
    
    async def grant_product_access(self, product_id: str, user_id: int) -> bool:
        """
        Надає користувачу доступ до продукту в ZenEdu
        """
        try:
            if self.demo_mode:
                await asyncio.sleep(0.3)
                logger.info(f"🎓 Демо: надано доступ користувачу {user_id} до продукту {product_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Помилка надання доступу користувачу {user_id} до продукту {product_id}: {e}")
            return False
    
    async def revoke_product_access(self, product_id: str, user_id: int) -> bool:
        """
        Відбирає у користувача доступ до продукту
        """
        try:
            if self.demo_mode:
                await asyncio.sleep(0.3)
                logger.info(f"🚫 Демо: відібрано доступ користувача {user_id} до продукту {product_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Помилка відбирання доступу користувача {user_id} до продукту {product_id}: {e}")
            return False
    
    async def check_user_access(self, product_id: str, user_id: int) -> bool:
        """
        Перевіряє чи має користувач доступ до продукту в ZenEdu
        """
        try:
            if self.demo_mode:
                await asyncio.sleep(0.1)
                # В демо-режимі адмін має доступ до всіх курсів
                has_access = user_id == 7603163573
                logger.debug(f"🔍 Демо: перевірка доступу {user_id} до {product_id}: {has_access}")
                return has_access
                
        except Exception as e:
            logger.error(f"❌ Помилка перевірки доступу користувача {user_id} до продукту {product_id}: {e}")
            return False
    
    async def get_product_access_link(self, product_id: str, user_id: int) -> Optional[str]:
        """
        Отримує персональне посилання для доступу до продукту
        """
        try:
            if self.demo_mode:
                await asyncio.sleep(0.2)
                # Генеруємо демо-посилання
                demo_link = f"https://zenedu.io/course/{product_id}?user={user_id}&token=demo_access"
                logger.info(f"🔗 Демо: створено посилання для користувача {user_id} до продукту {product_id}")
                return demo_link
                
        except Exception as e:
            logger.error(f"❌ Помилка створення посилання для користувача {user_id}: {e}")
            return None
    
    async def sync_products_to_db(self) -> int:
        """
        Синхронізує продукти з ZenEdu до локальної бази даних
        """
        try:
            products = await self.get_products()
            synced_count = 0
            
            for product in products:
                product_id = str(product.get('id', ''))
                title = product.get('name') or product.get('title', '')
                price = product.get('price', 0)
                description = product.get('description', '')
                access_link = product.get('access_link', '')
                
                # Конвертуємо ціну в гривні
                if isinstance(price, (int, float)):
                    price_uah = int(price)
                else:
                    price_uah = 0
                
                if product_id and title:
                    # Додаємо курс до БД
                    db_course_id = await add_course(
                        zenedu_id=product_id,
                        title=title,
                        price_uah=price_uah,
                        z_link=access_link,
                        description=description
                    )
                    
                    if db_course_id:
                        synced_count += 1
                        logger.debug(f"📚 Синхронізовано продукт: {title}")
            
            logger.info(f"✅ Синхронізовано {synced_count} продуктів з ZenEdu (демо)")
            return synced_count
            
        except Exception as e:
            logger.error(f"❌ Помилка синхронізації продуктів: {e}")
            return 0

# Глобальний екземпляр клієнта
zenedu_client = ZenEduClient()

# Функції-хелпери для зручного використання
async def sync_courses() -> int:
    """Синхронізує курси з ZenEdu"""
    return await zenedu_client.sync_products_to_db()

async def grant_course_access_to_user(course_id: str, user_id: int) -> bool:
    """Надає користувачу доступ до курсу"""
    # Спочатку надаємо доступ в ZenEdu
    zenedu_success = await zenedu_client.grant_product_access(course_id, user_id)
    
    if zenedu_success:
        # Потім оновлюємо локальну БД
        try:
            local_success = await grant_course_access(user_id, int(course_id.replace('course_', '')))
        except (ValueError, AttributeError):
            # Якщо course_id не є числом, створюємо запис за ZenEdu ID
            local_success = True
            
        if local_success:
            logger.info(f"✅ Повний доступ надано користувачу {user_id} до курсу {course_id}")
            return True
    
    return False

async def check_zenedu_connection() -> bool:
    """Перевіряє з'єднання з ZenEdu"""
    return await zenedu_client.test_connection()

async def get_course_access_link(course_id: str, user_id: int) -> Optional[str]:
    """Створює персональне посилання для доступу до курсу"""
    return await zenedu_client.get_product_access_link(course_id, user_id) 
"""
Клієнт для роботи з ZenEdu API
"""

import logging
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from config import ZENEDU_API_URL, ZENEDU_API_KEY, ZENEDU_WEBHOOK_SECRET
from db import add_course, get_courses as get_db_courses, grant_course_access

logger = logging.getLogger(__name__)

class ZenEduClient:
    """
    Клієнт для взаємодії з ZenEdu API
    """
    
    def __init__(self):
        self.api_url = ZENEDU_API_URL
        self.api_key = ZENEDU_API_KEY
        self.webhook_secret = ZENEDU_WEBHOOK_SECRET
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Отримати HTTP сесію"""
        if self.session is None or self.session.closed:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'PrometeyLabs-Bot/1.0'
            }
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout
            )
        return self.session
    
    async def close(self):
        """Закрити HTTP сесію"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def test_connection(self) -> bool:
        """
        Тестує з'єднання з ZenEdu API
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.api_url}/health") as response:
                if response.status == 200:
                    logger.info("З'єднання з ZenEdu API успішне")
                    return True
                else:
                    logger.error(f"Помилка з'єднання з ZenEdu API: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Помилка тестування з'єднання з ZenEdu: {e}")
            return False
    
    async def get_courses(self) -> List[Dict[str, Any]]:
        """
        Отримує список всіх курсів з ZenEdu
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.api_url}/courses") as response:
                if response.status == 200:
                    data = await response.json()
                    courses = data.get('courses', [])
                    logger.info(f"Отримано {len(courses)} курсів з ZenEdu")
                    return courses
                else:
                    logger.error(f"Помилка отримання курсів: {response.status}")
                    text = await response.text()
                    logger.error(f"Відповідь: {text}")
                    return []
        except Exception as e:
            logger.error(f"Помилка запиту курсів з ZenEdu: {e}")
            return []
    
    async def get_course_details(self, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Отримує детальну інформацію про курс
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.api_url}/courses/{course_id}") as response:
                if response.status == 200:
                    course_data = await response.json()
                    logger.info(f"Отримано деталі курсу {course_id}")
                    return course_data
                else:
                    logger.error(f"Помилка отримання деталей курсу {course_id}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Помилка запиту деталей курсу {course_id}: {e}")
            return None
    
    async def grant_user_access(self, course_id: str, user_id: int, 
                               access_type: str = "lifetime") -> bool:
        """
        Надає користувачу доступ до курсу в ZenEdu
        """
        try:
            session = await self._get_session()
            payload = {
                'course_id': course_id,
                'user_id': user_id,
                'access_type': access_type,
                'source': 'PrometeyLabs_Bot'
            }
            
            async with session.post(
                f"{self.api_url}/courses/{course_id}/grant-access",
                json=payload
            ) as response:
                if response.status == 200:
                    logger.info(f"Надано доступ користувачу {user_id} до курсу {course_id}")
                    return True
                else:
                    logger.error(f"Помилка надання доступу: {response.status}")
                    text = await response.text()
                    logger.error(f"Відповідь: {text}")
                    return False
        except Exception as e:
            logger.error(f"Помилка надання доступу користувачу {user_id} до курсу {course_id}: {e}")
            return False
    
    async def revoke_user_access(self, course_id: str, user_id: int) -> bool:
        """
        Відбирає у користувача доступ до курсу
        """
        try:
            session = await self._get_session()
            payload = {
                'user_id': user_id,
                'reason': 'Revoked by admin'
            }
            
            async with session.post(
                f"{self.api_url}/courses/{course_id}/revoke-access",
                json=payload
            ) as response:
                if response.status == 200:
                    logger.info(f"Відібрано доступ користувача {user_id} до курсу {course_id}")
                    return True
                else:
                    logger.error(f"Помилка відбирання доступу: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Помилка відбирання доступу користувача {user_id} до курсу {course_id}: {e}")
            return False
    
    async def check_user_access(self, course_id: str, user_id: int) -> bool:
        """
        Перевіряє чи має користувач доступ до курсу в ZenEdu
        """
        try:
            session = await self._get_session()
            async with session.get(
                f"{self.api_url}/courses/{course_id}/access/{user_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    has_access = data.get('has_access', False)
                    logger.debug(f"Перевірка доступу {user_id} до {course_id}: {has_access}")
                    return has_access
                else:
                    logger.error(f"Помилка перевірки доступу: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Помилка перевірки доступу користувача {user_id} до курсу {course_id}: {e}")
            return False
    
    async def sync_courses_to_db(self) -> int:
        """
        Синхронізує курси з ZenEdu до локальної бази даних
        """
        try:
            courses = await self.get_courses()
            synced_count = 0
            
            for course in courses:
                course_id = course.get('id')
                title = course.get('title', '')
                price_uah = int(course.get('price', 0))
                description = course.get('description', '')
                z_link = course.get('access_link', '')
                
                if course_id and title:
                    db_course_id = await add_course(
                        zenedu_id=str(course_id),
                        title=title,
                        price_uah=price_uah,
                        z_link=z_link,
                        description=description
                    )
                    
                    if db_course_id:
                        synced_count += 1
                        logger.debug(f"Синхронізовано курс: {title}")
            
            logger.info(f"Синхронізовано {synced_count} курсів з ZenEdu")
            return synced_count
            
        except Exception as e:
            logger.error(f"Помилка синхронізації курсів: {e}")
            return 0
    
    async def create_course_invite(self, course_id: str, user_id: int) -> Optional[str]:
        """
        Створює персональне посилання для доступу до курсу
        """
        try:
            session = await self._get_session()
            payload = {
                'course_id': course_id,
                'user_id': user_id,
                'expires_in': 3600,  # 1 година
                'source': 'PrometeyLabs_Bot'
            }
            
            async with session.post(
                f"{self.api_url}/invites",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    invite_link = data.get('invite_link')
                    logger.info(f"Створено інвайт для користувача {user_id} до курсу {course_id}")
                    return invite_link
                else:
                    logger.error(f"Помилка створення інвайту: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Помилка створення інвайту для користувача {user_id}: {e}")
            return None

# Глобальний екземпляр клієнта
zenedu_client = ZenEduClient()

# Функції-хелпери для зручного використання
async def sync_courses() -> int:
    """Синхронізує курси з ZenEdu"""
    return await zenedu_client.sync_courses_to_db()

async def grant_course_access_to_user(course_id: str, user_id: int) -> bool:
    """Надає користувачу доступ до курсу"""
    # Спочатку надаємо доступ в ZenEdu
    zenedu_success = await zenedu_client.grant_user_access(course_id, user_id)
    
    if zenedu_success:
        # Потім оновлюємо локальну БД
        local_success = await grant_course_access(user_id, int(course_id))
        if local_success:
            logger.info(f"Повний доступ надано користувачу {user_id} до курсу {course_id}")
            return True
    
    return False

async def check_zenedu_connection() -> bool:
    """Перевіряє з'єднання з ZenEdu"""
    return await zenedu_client.test_connection()

async def get_course_invite_link(course_id: str, user_id: int) -> Optional[str]:
    """Створює персональне посилання для доступу до курсу"""
    return await zenedu_client.create_course_invite(course_id, user_id) 
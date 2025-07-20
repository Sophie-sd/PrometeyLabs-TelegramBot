"""
Модуль для роботи з базою даних SQLite
"""

import aiosqlite
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

# SQL створення таблиць згідно ТЗ
CREATE_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_blocked BOOLEAN DEFAULT FALSE,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zenedu_id TEXT UNIQUE,
        title TEXT NOT NULL,
        price_uah INTEGER NOT NULL,
        z_link TEXT,
        description TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        course_id INTEGER,
        ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        payment_status TEXT DEFAULT 'pending',
        monobank_payment_id TEXT,
        amount INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (course_id) REFERENCES courses (id)
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS broadcasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        media_file_id TEXT,
        target_segment TEXT DEFAULT 'all',
        scheduled_time TIMESTAMP,
        status TEXT DEFAULT 'draft',
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        sent_at TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users (id)
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS broadcast_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        broadcast_id INTEGER,
        user_id INTEGER,
        status TEXT,
        error_message TEXT,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (broadcast_id) REFERENCES broadcasts (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS user_course_access (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        course_id INTEGER,
        access_granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        access_expires_at TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (course_id) REFERENCES courses (id),
        UNIQUE(user_id, course_id)
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS recurring_broadcasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER,
        message_text TEXT NOT NULL,
        audience_type TEXT DEFAULT 'all',
        recurring_type TEXT NOT NULL,
        cron_expression TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_run TIMESTAMP,
        next_run TIMESTAMP,
        FOREIGN KEY (admin_id) REFERENCES users (id)
    )
    """
]

# Індекси для оптимізації
CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
    "CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_purchases_course_id ON purchases(course_id)",
    "CREATE INDEX IF NOT EXISTS idx_broadcast_log_broadcast_id ON broadcast_log(broadcast_id)",
    "CREATE INDEX IF NOT EXISTS idx_user_course_access_user_id ON user_course_access(user_id)"
]

async def init_db():
    """Ініціалізація бази даних"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Створюємо таблиці
            for sql in CREATE_TABLES_SQL:
                await db.execute(sql)
            
            # Створюємо індекси
            for sql in CREATE_INDEXES_SQL:
                await db.execute(sql)
            
            await db.commit()
            logger.info("База даних успішно ініціалізована")
    except Exception as e:
        logger.error(f"Помилка ініціалізації БД: {e}")
        raise

# Функції для роботи з користувачами
async def add_user(user_id: int, username: str = None) -> bool:
    """Додати користувача"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)",
                (user_id, username)
            )
            await db.commit()
            return True
    except Exception as e:
        logger.error(f"Помилка додавання користувача {user_id}: {e}")
        return False

async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Отримати користувача"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'username': row[1], 
                        'joined_at': row[2],
                        'is_blocked': bool(row[3]),
                        'last_activity': row[4]
                    }
                return None
    except Exception as e:
        logger.error(f"Помилка отримання користувача {user_id}: {e}")
        return None

async def update_user_activity(user_id: int):
    """Оновити час останньої активності користувача"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE id = ?",
                (user_id,)
            )
            await db.commit()
    except Exception as e:
        logger.error(f"Помилка оновлення активності користувача {user_id}: {e}")

async def block_user(user_id: int, blocked: bool = True):
    """Заблокувати/розблокувати користувача"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "UPDATE users SET is_blocked = ? WHERE id = ?",
                (blocked, user_id)
            )
            await db.commit()
            return True
    except Exception as e:
        logger.error(f"Помилка блокування користувача {user_id}: {e}")
        return False

# Функції для роботи з курсами
async def add_course(zenedu_id: str, title: str, price_uah: int, 
                    z_link: str = None, description: str = None) -> Optional[int]:
    """Додати курс"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                """INSERT INTO courses (zenedu_id, title, price_uah, z_link, description) 
                   VALUES (?, ?, ?, ?, ?)""",
                (zenedu_id, title, price_uah, z_link, description)
            )
            await db.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Помилка додавання курсу: {e}")
        return None

async def get_courses() -> List[Dict[str, Any]]:
    """Отримати всі активні курси"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute(
                "SELECT * FROM courses WHERE is_active = TRUE ORDER BY created_at DESC"
            ) as cursor:
                rows = await cursor.fetchall()
                return [{
                    'id': row[0],
                    'zenedu_id': row[1],
                    'title': row[2],
                    'price_uah': row[3],
                    'z_link': row[4],
                    'description': row[5],
                    'is_active': bool(row[6]),
                    'created_at': row[7]
                } for row in rows]
    except Exception as e:
        logger.error(f"Помилка отримання курсів: {e}")
        return []

async def get_course(course_id: int) -> Optional[Dict[str, Any]]:
    """Отримати курс за ID"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute(
                "SELECT * FROM courses WHERE id = ?", (course_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'zenedu_id': row[1],
                        'title': row[2],
                        'price_uah': row[3],
                        'z_link': row[4],
                        'description': row[5],
                        'is_active': bool(row[6]),
                        'created_at': row[7]
                    }
                return None
    except Exception as e:
        logger.error(f"Помилка отримання курсу {course_id}: {e}")
        return None

# Функції для роботи з покупками
async def create_purchase(user_id: int, course_id: int, amount: int, 
                         monobank_payment_id: str = None) -> Optional[int]:
    """Створити запис про покупку"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                """INSERT INTO purchases (user_id, course_id, amount, monobank_payment_id) 
                   VALUES (?, ?, ?, ?)""",
                (user_id, course_id, amount, monobank_payment_id)
            )
            await db.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Помилка створення покупки: {e}")
        return None

async def update_purchase_status(purchase_id: int, status: str):
    """Оновити статус покупки"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "UPDATE purchases SET payment_status = ? WHERE id = ?",
                (status, purchase_id)
            )
            await db.commit()
            return True
    except Exception as e:
        logger.error(f"Помилка оновлення статусу покупки {purchase_id}: {e}")
        return False

# Функції для роботи з доступами до курсів
async def grant_course_access(user_id: int, course_id: int, 
                             expires_at: datetime = None) -> bool:
    """Надати доступ до курсу"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                """INSERT OR REPLACE INTO user_course_access 
                   (user_id, course_id, access_expires_at) VALUES (?, ?, ?)""",
                (user_id, course_id, expires_at)
            )
            await db.commit()
            return True
    except Exception as e:
        logger.error(f"Помилка надання доступу до курсу: {e}")
        return False

async def check_course_access(user_id: int, course_id: int) -> bool:
    """Перевірити доступ до курсу"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute(
                """SELECT is_active FROM user_course_access 
                   WHERE user_id = ? AND course_id = ? AND 
                   (access_expires_at IS NULL OR access_expires_at > CURRENT_TIMESTAMP)""",
                (user_id, course_id)
            ) as cursor:
                row = await cursor.fetchone()
                return bool(row and row[0])
    except Exception as e:
        logger.error(f"Помилка перевірки доступу до курсу: {e}")
        return False

# Функції для статистики
async def get_user_stats() -> Dict[str, Any]:
    """Отримати статистику користувачів"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Загальна кількість
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                total_users = (await cursor.fetchone())[0]
            
            # Активні за останні 30 днів
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE last_activity > datetime('now', '-30 days')"
            ) as cursor:
                active_users = (await cursor.fetchone())[0]
            
            # Нові за останні 30 днів
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE joined_at > datetime('now', '-30 days')"
            ) as cursor:
                new_users = (await cursor.fetchone())[0]
            
            return {
                'total_users': total_users,
                'active_users_30d': active_users,
                'new_users_30d': new_users
            }
    except Exception as e:
        logger.error(f"Помилка отримання статистики: {e}")
        return {}

async def get_all_users() -> List[int]:
    """Отримати всіх користувачів (для розсилок)"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute(
                "SELECT id FROM users WHERE is_blocked = FALSE"
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
    except Exception as e:
        logger.error(f"Помилка отримання списку користувачів: {e}")
        return [] 

# Статистичні функції для адмін панелі
async def get_users_count() -> int:
    """Отримує загальну кількість користувачів"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            result = await cursor.fetchone()
            return result[0] if result else 0
    except Exception as e:
        logger.error(f"Помилка отримання кількості користувачів: {e}")
        return 0

async def get_new_users_count(days: int = 30) -> int:
    """Отримує кількість нових користувачів за останні N днів"""
    try:
        date_threshold = datetime.now() - timedelta(days=days)
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM users WHERE joined_at >= ?",
                (date_threshold,)
            )
            result = await cursor.fetchone()
            return result[0] if result else 0
    except Exception as e:
        logger.error(f"Помилка отримання кількості нових користувачів: {e}")
        return 0

async def get_active_users_count(days: int = 7) -> int:
    """Отримує кількість активних користувачів за останні N днів"""
    try:
        date_threshold = datetime.now() - timedelta(days=days)
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM users WHERE last_activity >= ?",
                (date_threshold,)
            )
            result = await cursor.fetchone()
            return result[0] if result else 0
    except Exception as e:
        logger.error(f"Помилка отримання кількості активних користувачів: {e}")
        return 0

async def get_courses_count() -> int:
    """Отримує загальну кількість курсів"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM courses")
            result = await cursor.fetchone()
            return result[0] if result else 0
    except Exception as e:
        logger.error(f"Помилка отримання кількості курсів: {e}")
        return 0

async def get_purchases_count() -> int:
    """Отримує загальну кількість покупок"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM purchases")
            result = await cursor.fetchone()
            return result[0] if result else 0
    except Exception as e:
        logger.error(f"Помилка отримання кількості покупок: {e}")
        return 0

async def get_users_with_purchases_count() -> int:
    """Отримує кількість користувачів які зробили покупки"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                "SELECT COUNT(DISTINCT user_id) FROM purchases"
            )
            result = await cursor.fetchone()
            return result[0] if result else 0
    except Exception as e:
        logger.error(f"Помилка отримання кількості користувачів з покупками: {e}")
        return 0

async def get_daily_interactions() -> int:
    """Розраховує приблизну кількість взаємодій за день"""
    try:
        # Отримуємо активних користувачів за день
        active_today = await get_active_users_count(days=1)
        
        # Припускаємо в середньому 3-5 взаємодій на активного користувача за день
        avg_interactions_per_user = 4
        
        return active_today * avg_interactions_per_user
    except Exception as e:
        logger.error(f"Помилка розрахунку денних взаємодій: {e}")
        return 0

async def get_weekly_interactions() -> int:
    """Розраховує приблизну кількість взаємодій за тиждень"""
    try:
        # Отримуємо активних користувачів за тиждень
        active_week = await get_active_users_count(days=7)
        
        # Припускаємо в середньому 15-20 взаємодій на активного користувача за тиждень
        avg_interactions_per_user = 18
        
        return active_week * avg_interactions_per_user
    except Exception as e:
        logger.error(f"Помилка розрахунку тижневих взаємодій: {e}")
        return 0

async def get_recent_purchases(limit: int = 10):
    """Отримує останні покупки"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT p.*, u.username, c.title 
                FROM purchases p
                LEFT JOIN users u ON p.user_id = u.id
                LEFT JOIN courses c ON p.course_id = c.id
                ORDER BY p.purchased_at DESC
                LIMIT ?
            """, (limit,))
            return await cursor.fetchall()
    except Exception as e:
        logger.error(f"Помилка отримання останніх покупок: {e}")
        return []

async def get_course_statistics():
    """Отримує статистику по курсах"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT 
                    c.title,
                    c.price_uah,
                    COUNT(p.id) as purchases_count,
                    SUM(c.price_uah) as total_revenue
                FROM courses c
                LEFT JOIN purchases p ON c.id = p.course_id
                GROUP BY c.id, c.title, c.price_uah
                ORDER BY purchases_count DESC
            """)
            return await cursor.fetchall()
    except Exception as e:
        logger.error(f"Помилка отримання статистики курсів: {e}")
        return []

# Функції для управління користувачами (адмін панель)
async def search_users(query: str) -> List[dict]:
    """Пошук користувачів за ID або username"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Якщо запит - число, шукаємо за ID
            if query.isdigit():
                user_id = int(query)
                async with db.execute(
                    "SELECT id, username, joined_at, is_blocked, last_activity FROM users WHERE id = ?",
                    (user_id,)
                ) as cursor:
                    rows = await cursor.fetchall()
            else:
                # Інакше шукаємо за username (частковий збіг)
                username_pattern = f"%{query}%"
                async with db.execute(
                    "SELECT id, username, joined_at, is_blocked, last_activity FROM users WHERE username LIKE ?",
                    (username_pattern,)
                ) as cursor:
                    rows = await cursor.fetchall()
            
            return [
                {
                    "id": row[0],
                    "username": row[1],
                    "joined_at": row[2],
                    "is_blocked": bool(row[3]),
                    "last_activity": row[4]
                }
                for row in rows
            ]
    except Exception as e:
        logger.error(f"Помилка пошуку користувачів за запитом '{query}': {e}")
        return []

async def get_users_list(offset: int = 0, limit: int = 10) -> List[dict]:
    """Отримати список користувачів з пагінацією"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute(
                """
                SELECT id, username, joined_at, is_blocked, last_activity 
                FROM users 
                ORDER BY joined_at DESC 
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            ) as cursor:
                rows = await cursor.fetchall()
                
            return [
                {
                    "id": row[0],
                    "username": row[1],
                    "joined_at": row[2],
                    "is_blocked": bool(row[3]),
                    "last_activity": row[4]
                }
                for row in rows
            ]
    except Exception as e:
        logger.error(f"Помилка отримання списку користувачів: {e}")
        return []

async def get_user_purchases(user_id: int) -> List[dict]:
    """Отримати покупки конкретного користувача"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute(
                """
                SELECT p.id, c.title, p.ts, p.payment_status, p.amount
                FROM purchases p
                JOIN courses c ON p.course_id = c.id
                WHERE p.user_id = ?
                ORDER BY p.ts DESC
                """,
                (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                
            return [
                {
                    "purchase_id": row[0],
                    "course_title": row[1],
                    "purchase_date": row[2],
                    "payment_status": row[3],
                    "amount": row[4]
                }
                for row in rows
            ]
    except Exception as e:
        logger.error(f"Помилка отримання покупок користувача {user_id}: {e}")
        return []

async def get_all_purchases(offset: int = 0, limit: int = 20) -> List[dict]:
    """Отримати всі покупки з інформацією про користувачів"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute(
                """
                SELECT p.id, u.id, u.username, c.title, p.ts, p.payment_status, p.amount
                FROM purchases p
                JOIN users u ON p.user_id = u.id
                JOIN courses c ON p.course_id = c.id
                ORDER BY p.ts DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            ) as cursor:
                rows = await cursor.fetchall()
                
            return [
                {
                    "purchase_id": row[0],
                    "user_id": row[1], 
                    "username": row[2],
                    "course_title": row[3],
                    "purchase_date": row[4],
                    "payment_status": row[5],
                    "amount": row[6]
                }
                for row in rows
            ]
    except Exception as e:
        logger.error(f"Помилка отримання всіх покупок: {e}")
        return []

async def get_purchases_stats() -> dict:
    """Отримати статистику покупок"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Загальна кількість покупок
            async with db.execute("SELECT COUNT(*) FROM purchases") as cursor:
                total_purchases = (await cursor.fetchone())[0]
            
            # Сума всіх покупок
            async with db.execute("SELECT SUM(amount) FROM purchases WHERE payment_status = 'completed'") as cursor:
                total_revenue = (await cursor.fetchone())[0] or 0
            
            # Покупки за останній місяць
            async with db.execute(
                "SELECT COUNT(*) FROM purchases WHERE ts > datetime('now', '-30 days')"
            ) as cursor:
                monthly_purchases = (await cursor.fetchone())[0]
            
            # Середній чек
            async with db.execute("SELECT AVG(amount) FROM purchases WHERE payment_status = 'completed'") as cursor:
                avg_amount = (await cursor.fetchone())[0] or 0
            
            return {
                "total_purchases": total_purchases,
                "total_revenue": total_revenue,
                "monthly_purchases": monthly_purchases,
                "avg_amount": round(avg_amount, 2)
            }
    except Exception as e:
        logger.error(f"Помилка отримання статистики покупок: {e}")
        return {}

# Функції для роботи з розсилками
async def get_users_by_segment(segment: str) -> List[int]:
    """Отримати користувачів за сегментом"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            if segment == "all":
                # Всі активні користувачі
                query = "SELECT id FROM users WHERE is_blocked = FALSE"
            elif segment == "buyers":
                # Користувачі з покупками
                query = """
                    SELECT DISTINCT u.id FROM users u
                    INNER JOIN purchases p ON u.id = p.user_id
                    WHERE u.is_blocked = FALSE
                """
            elif segment == "inactive":
                # Неактивні 7+ днів
                query = """
                    SELECT id FROM users 
                    WHERE is_blocked = FALSE 
                    AND (last_activity IS NULL OR last_activity < datetime('now', '-7 days'))
                """
            else:
                return []
            
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
    except Exception as e:
        logger.error(f"Помилка отримання користувачів сегменту {segment}: {e}")
        return []

async def save_broadcast(admin_id: int, message_text: str, audience: str, 
                        scheduled_for: str = None, status: str = "pending") -> int:
    """Зберегти розсилку в БД"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                """
                INSERT INTO broadcasts (title, message, target_segment, 
                                      scheduled_time, status, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (f"Розсилка від {datetime.now().strftime('%d.%m.%Y %H:%M')}", 
                 message_text, audience, scheduled_for, status, admin_id)
            )
            await db.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Помилка збереження розсилки: {e}")
        return 0

async def get_scheduled_broadcasts() -> List[dict]:
    """Отримати заплановані розсилки"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute(
                """
                SELECT id, message, target_segment, scheduled_time, created_at
                FROM broadcasts 
                WHERE status = 'pending' AND scheduled_time IS NOT NULL
                ORDER BY scheduled_time ASC
                """
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "id": row[0],
                        "message_text": row[1],
                        "audience_type": row[2], 
                        "scheduled_for": row[3],
                        "created_at": row[4]
                    }
                    for row in rows
                ]
    except Exception as e:
        logger.error(f"Помилка отримання запланованих розсилок: {e}")
        return []

async def get_broadcast_history(limit: int = 20) -> List[dict]:
    """Отримати історію розсилок"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute(
                """
                SELECT b.id, b.message, b.target_segment, b.status,
                       b.created_at, b.sent_at
                FROM broadcasts b
                WHERE b.status IN ('sent', 'failed')
                ORDER BY b.created_at DESC
                LIMIT ?
                """,
                (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "id": row[0],
                        "message_text": row[1][:50] + "..." if len(row[1]) > 50 else row[1],
                        "audience_type": row[2],
                        "status": row[3],
                        "created_at": row[4],
                        "sent_at": row[5]
                    }
                    for row in rows
                ]
    except Exception as e:
        logger.error(f"Помилка отримання історії розсилок: {e}")
        return []

async def save_recurring_broadcast(admin_id: int, message_text: str, audience: str, 
                                 recurring_type: str, cron_expression: str = None) -> int:
    """Зберегти регулярну розсилку"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                """
                INSERT INTO recurring_broadcasts (admin_id, message_text, audience_type, 
                                                 recurring_type, cron_expression, status)
                VALUES (?, ?, ?, ?, ?, 'active')
                """,
                (admin_id, message_text, audience, recurring_type, cron_expression)
            )
            await db.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Помилка збереження регулярної розсилки: {e}")
        return 0

async def get_active_recurring_broadcasts() -> List[dict]:
    """Отримати активні регулярні розсилки"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute(
                """
                SELECT id, message_text, audience_type, recurring_type, 
                       cron_expression, created_at
                FROM recurring_broadcasts 
                WHERE status = 'active'
                ORDER BY created_at DESC
                """
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "id": row[0],
                        "message_text": row[1],
                        "audience_type": row[2], 
                        "recurring_type": row[3],
                        "cron_expression": row[4],
                        "created_at": row[5]
                    }
                    for row in rows
                ]
    except Exception as e:
        logger.error(f"Помилка отримання регулярних розсилок: {e}")
        return []

async def delete_scheduled_broadcast(broadcast_id: int) -> bool:
    """Видалити заплановану розсилку"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "DELETE FROM broadcasts WHERE id = ? AND status = 'pending'",
                (broadcast_id,)
            )
            await db.commit()
            return True
    except Exception as e:
        logger.error(f"Помилка видалення запланованої розсилки {broadcast_id}: {e}")
        return False

async def delete_recurring_broadcast(broadcast_id: int) -> bool:
    """Видалити регулярну розсилку"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "UPDATE recurring_broadcasts SET status = 'deleted' WHERE id = ?",
                (broadcast_id,)
            )
            await db.commit()
            return True
    except Exception as e:
        logger.error(f"Помилка видалення регулярної розсилки {broadcast_id}: {e}")
        return False

async def get_broadcast_by_id(broadcast_id: int) -> dict:
    """Отримати розсилку за ID"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute(
                """
                SELECT id, message, target_segment, scheduled_time, status, created_at
                FROM broadcasts WHERE id = ?
                """,
                (broadcast_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "message_text": row[1],
                        "audience_type": row[2],
                        "scheduled_for": row[3],
                        "status": row[4],
                        "created_at": row[5]
                    }
                return {}
    except Exception as e:
        logger.error(f"Помилка отримання розсилки {broadcast_id}: {e}")
        return {}

async def get_recurring_broadcast_by_id(broadcast_id: int) -> dict:
    """Отримати регулярну розсилку за ID"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute(
                """
                SELECT id, message_text, audience_type, recurring_type, 
                       cron_expression, status, created_at
                FROM recurring_broadcasts WHERE id = ?
                """,
                (broadcast_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "message_text": row[1],
                        "audience_type": row[2],
                        "recurring_type": row[3],
                        "cron_expression": row[4],
                        "status": row[5],
                        "created_at": row[6]
                    }
                return {}
    except Exception as e:
        logger.error(f"Помилка отримання регулярної розсилки {broadcast_id}: {e}")
        return {} 
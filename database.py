import aiosqlite
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

class Database:
    def __init__(self, db_name='bot.db'):
        self.db_name = db_name

    async def init(self):
        try:
            async with aiosqlite.connect(self.db_name) as db:
                logging.info("Initializing database...")
            # Создаем основную таблицу пользователей
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    selected_epoch TEXT,
                    difficulty_level TEXT,
                    start_year INTEGER,
                    current_year INTEGER,
                    last_fact_date TEXT,
                    subscription_active BOOLEAN DEFAULT 1,
                    facts_viewed INTEGER DEFAULT 0,
                    correct_answers INTEGER DEFAULT 0,
                    wrong_answers INTEGER DEFAULT 0,
                    setup_completed BOOLEAN DEFAULT 0
                )
            ''')
            
            # Создаем таблицу выбранных тем
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_themes (
                    user_id INTEGER,
                    theme TEXT,
                    PRIMARY KEY (user_id, theme),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Создаем таблицу для отслеживания просмотренных фактов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS viewed_facts (
                    user_id INTEGER,
                    epoch TEXT,
                    year INTEGER,
                    view_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            await db.commit()
            
    async def get_user_progress(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить прогресс пользователя."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                logging.debug(f"Getting progress for user {user_id}")
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    'SELECT * FROM users WHERE user_id = ?', 
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            logging.error(f"Error getting user progress: {e}")
            return None 
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
            if row:
                # Преобразуем sqlite3.Row в обычный словарь
                return dict(row)
            return None
                
    async def update_current_year(self, user_id: int, new_year: int):
        """Обновить текущий год изучения."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'UPDATE users SET current_year = ? WHERE user_id = ?',
                (new_year, user_id)
            )
            await db.commit()

    async def add_user(self, user_id: int):
        """Добавить нового пользователя."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'INSERT OR IGNORE INTO users (user_id, facts_viewed, correct_answers, wrong_answers) VALUES (?, 0, 0, 0)',
                (user_id,)
            )
            await db.commit()

    async def update_user_preferences(self, user_id: int, epoch: str, level: str, start_year: int):
        """Обновить предпочтения пользователя."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                UPDATE users 
                SET selected_epoch = ?, difficulty_level = ?, start_year = ?, current_year = ?
                WHERE user_id = ?
            ''', (epoch, level, start_year, start_year, user_id))
            await db.commit()

    async def update_difficulty(self, user_id: int, difficulty: str):
        """Обновить уровень сложности для пользователя."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'UPDATE users SET difficulty_level = ? WHERE user_id = ?',
                (difficulty, user_id)
            )
            await db.commit()

    async def update_epoch(self, user_id: int, epoch: str, start_year: int):
        """Обновить только эпоху и сбросить текущий год."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'UPDATE users SET selected_epoch = ?, start_year = ?, current_year = ? WHERE user_id = ?',
                (epoch, start_year, start_year, user_id)
            )
            await db.commit()

    async def get_active_users(self):
        """Получить всех активных пользователей."""
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM users WHERE subscription_active = 1'
            ) as cursor:
                return await cursor.fetchall()

    async def increment_fact_counter(self, user_id: int):
        """Увеличить счетчик просмотренных фактов."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'UPDATE users SET facts_viewed = facts_viewed + 1 WHERE user_id = ?',
                (user_id,)
            )
            await db.commit()

    async def increment_correct_answers(self, user_id: int):
        """Увеличить счетчик правильных ответов."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'UPDATE users SET correct_answers = correct_answers + 1 WHERE user_id = ?',
                (user_id,)
            )
            await db.commit()

    async def increment_wrong_answers(self, user_id: int):
        """Увеличить счетчик неправильных ответов."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'UPDATE users SET wrong_answers = wrong_answers + 1 WHERE user_id = ?',
                (user_id,)
            )
            await db.commit()

    async def update_subscription(self, user_id: int, subscription_active: bool):
        """Обновить статус подписки пользователя."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'UPDATE users SET subscription_active = ? WHERE user_id = ?',
                (subscription_active, user_id)
            )
            await db.commit()

    async def mark_setup_completed(self, user_id: int):
        """Отметить завершение первоначальной настройки."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'UPDATE users SET setup_completed = 1 WHERE user_id = ?',
                (user_id,)
            )
            await db.commit()

    async def toggle_theme(self, user_id: int, theme: str):
        """Добавить или удалить тему пользователя."""
        async with aiosqlite.connect(self.db_name) as db:
            # Проверяем, существует ли уже такая тема для пользователя
            async with db.execute(
                'SELECT * FROM user_themes WHERE user_id = ? AND theme = ?', 
                (user_id, theme)
            ) as cursor:
                existing = await cursor.fetchone()
                
            if existing:
                # Если тема существует, удаляем её
                await db.execute(
                    'DELETE FROM user_themes WHERE user_id = ? AND theme = ?',
                    (user_id, theme)
                )
            else:
                # Если темы нет, добавляем её
                await db.execute(
                    'INSERT INTO user_themes (user_id, theme) VALUES (?, ?)',
                    (user_id, theme)
                )
            
            await db.commit()

    async def get_user_themes(self, user_id: int) -> List[str]:
        """Получить список тем пользователя."""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute(
                'SELECT theme FROM user_themes WHERE user_id = ?', 
                (user_id,)
            ) as cursor:
                themes = await cursor.fetchall()
                return [theme[0] for theme in themes]
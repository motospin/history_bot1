import aiosqlite
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

class Database:
    def __init__(self, db_name='bot.db'):
        self.db_name = db_name

    async def init(self):
        async with aiosqlite.connect(self.db_name) as db:
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
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM users WHERE user_id = ?', 
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

    # Сразу после метода update_user_preferences
async def update_user_preferences(self, user_id: int, epoch: str, level: str, start_year: int):
    """Обновить предпочтения пользователя."""
    async with aiosqlite.connect(self.db_name) as db:
        await db.execute('''
            UPDATE users 
            SET selected_epoch = ?, difficulty_level = ?, start_year = ?, current_year = ?
            WHERE user_id = ?
        ''', (epoch, level, start_year, start_year, user_id))
        await db.commit()

# Здесь добавьте новый метод
async def update_difficulty(self, user_id: int, difficulty: str):
    """Обновить уровень сложности для пользователя."""
    async with aiosqlite.connect(self.db_name) as db:
        await db.execute(
            'UPDATE users SET difficulty_level = ? WHERE user_id = ?',
            (difficulty, user_id)
        )
        await db.commit()

# Далее может следовать метод update_epoch или get_active_users

    async def get_active_users(self):
        """Получить всех активных пользователей."""
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM users WHERE subscription_active = 1'
            ) as cursor:
                return await cursor.fetchall()
    
async def update_epoch(self, user_id: int, epoch: str, start_year: int):
    """Обновить только эпоху и сбросить текущий год."""
    async with aiosqlite.connect(self.db_name) as db:
        await db.execute(
            'UPDATE users SET selected_epoch = ?, start_year = ?, current_year = ? WHERE user_id = ?',
            (epoch, start_year, start_year, user_id)
        )
        await db.commit()

import aiosqlite
import logging
from datetime import datetime

class Database:
    def __init__(self, db_name='bot.db'):
        self.db_name = db_name

    async def init(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    selected_epoch TEXT,
                    difficulty_level TEXT,
                    start_year INTEGER,
                    current_year INTEGER,
                    subscription_active BOOLEAN DEFAULT 1
                )
            ''')
            await db.commit()

    async def add_user(self, user_id: int):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'INSERT OR IGNORE INTO users (user_id) VALUES (?)',
                (user_id,)
            )
            await db.commit()

    async def update_user_preferences(self, user_id: int, epoch: str, level: str, start_year: int):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                UPDATE users 
                SET selected_epoch = ?, difficulty_level = ?, start_year = ?, current_year = ?
                WHERE user_id = ?
            ''', (epoch, level, start_year, start_year, user_id))
            await db.commit()

    async def get_active_users(self):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute(
                'SELECT * FROM users WHERE subscription_active = 1'
            ) as cursor:
                return await cursor.fetchall()

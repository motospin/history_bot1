import os
import aiohttp
import random
from typing import Optional

class YandexGPT:
    def __init__(self):
        self.facts_db = {
            "ri": {  # Российская Империя
                1721: "Пётр I принял титул императора, Россия официально стала империей.",
                1812: "Бородинское сражение - крупнейшая битва Отечественной войны.",
                1861: "Император Александр II отменил крепостное право в России.",
            },
            "ussr": {  # СССР
                1922: "Образован Союз Советских Социалистических Республик.",
                1941: "Начало Великой Отечественной войны.",
                1961: "Юрий Гагарин совершил первый полёт человека в космос.",
            },
            "rf": {  # Российская Федерация
                1991: "Распад СССР и образование Российской Федерации.",
                1993: "Принята действующая Конституция РФ.",
                2000: "Владимир Путин впервые избран президентом России.",
            }
        }

    async def generate_history_fact(self, epoch: str, year: Optional[int], difficulty: str) -> str:
        if epoch not in self.facts_db:
            return "Извините, для данной эпохи факты отсутствуют."

        if year and year in self.facts_db[epoch]:
            return self.facts_db[epoch][year]

        # Если год не указан или для него нет факта, возвращаем случайный факт из эпохи
        available_facts = list(self.facts_db[epoch].values())
        return random.choice(available_facts)

    def _create_prompt(self, epoch: str, year: Optional[int], difficulty: str) -> str:
        pass  # Этот метод больше не используется
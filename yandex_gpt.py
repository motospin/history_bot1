
import os
import aiohttp
from typing import Optional

class YandexGPT:
    def __init__(self):
        self.api_key = os.getenv('YANDEX_API_KEY')
        self.folder_id = os.getenv('YANDEX_FOLDER_ID')
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        
    async def generate_history_fact(self, epoch: str, year: Optional[int], difficulty: str) -> str:
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "x-folder-id": self.folder_id
        }
        
        prompt = self._create_prompt(epoch, year, difficulty)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url,
                headers=headers,
                json={
                    "modelUri": "gpt://b1gghm0ajm9pabpu0jiu/yandexgpt",
                    "completionOptions": {
                        "stream": False,
                        "temperature": 0.6,
                        "maxTokens": "2000"
                    },
                    "messages": [
                        {
                            "role": "system",
                            "text": "Ты - историк-эксперт. Твоя задача - создавать интересные и информативные исторические справки."
                        },
                        {
                            "role": "user",
                            "text": prompt
                        }
                    ]
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Error from YandexGPT API: {error_text}")
                    return "Извините, произошла ошибка при генерации исторического факта."
                
                result = await response.json()
                print(f"YandexGPT API Response: {result}")

                try:
                    if "result" in result:
                        return result["result"]["alternatives"][0]["text"]
                    elif "results" in result:
                        return result["results"][0]["text"]
                    elif "generated_text" in result:
                        return result["generated_text"]
                    else:
                        print(f"Unknown response format: {result}")
                        return "Извините, произошла ошибка с форматом ответа."
                except (KeyError, IndexError) as e:
                    print(f"Error parsing response: {e}\nFull response: {result}")
                    return "Извините, произошла ошибка при обработке ответа."
    
    def _create_prompt(self, epoch: str, year: Optional[int], difficulty: str) -> str:
        base_prompt = f"Создай историческую справку об эпохе {epoch}"
        if year:
            base_prompt += f" в {year} году"
            
        if difficulty == "basic":
            base_prompt += ". Формат: дата и один ключевой факт."
        elif difficulty == "medium":
            base_prompt += ". Текст на 30-60 секунд чтения."
        else:  # advanced
            base_prompt += ". Подробный анализ на 3-5 минут чтения."
            
        return base_prompt

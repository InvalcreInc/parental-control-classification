from google import genai
from google.genai import types
from pydantic import BaseModel
from json import JSONEncoder
import os
import csv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the variables
gemini_key = os.getenv('GEMINI_API')

client = genai.Client(api_key=gemini_key)


class Classification(BaseModel):
    classification: str
    confidence: float
    reasons: list[str]
    details: str


def classify_content(text):
    system_instruction = "You are an advanced content classification system designed to analyze Internet resources, such as website content or text extracted from PDFs, for building parental control systems to prevent access to unwanted information. Your task is to classify the provided content as safe or unsafe based on harmful or inappropriate material, such as phishing, adult content, violence, or malicious intent. Input: You will receive a string containing raw text content of a resource (e.g., website HTML, PDF text, or transcribed audio/video), which may include metadata (e.g., URL, file name) and may be noisy. Task: 1. Analyze the content using NLP to identify patterns, keywords, or context indicative of unwanted information (e.g., phishing: suspicious URLs, login prompts; adult content: explicit language; violence: aggressive language; malware: suspicious links; other: hate speech, gambling). 2. Consider contextual cues (tone, intent, semantics) beyond keyword matching. 3. If metadata (e.g., URL) is provided, analyze it for additional signals (e.g., domain reputation). 4. Classify as \"safe\" or \"unsafe\". 5. Provide a confidence score (0-1). 6. If unsafe, specify reasons (e.g., phishing, adult content). Output: Return a JSON object: {\"classification\": \"safe\"|\"unsafe\", \"confidence\": number, \"reasons\": string[], \"details\": string}. Constraints: Handle noisy/incomplete input gracefully, avoid false positives, prioritize high recall for unsafe content, process efficiently, return lower confidence for ambiguous content, and note uncertainty in \"details\". Example Input: URL: http://fakebank.com/login Content: Welcome to FakeBank! Your account is at risk. Please login now to secure your funds. [Login Button] Example Output: {\"classification\": \"unsafe\", \"confidence\": 0.92, \"reasons\": [\"phishing\", \"suspicious URL\"], \"details\": \"Content contains urgent language and login prompt, typical of phishing. URL 'fakebank.com' is not a recognized banking domain.\"} Example Input: Content: The history of the Roman Empire spans centuries... Example Output: {\"classification\": \"safe\", \"confidence\": 0.98, \"reasons\": [], \"details\": \"Content discusses historical information with no harmful material.\"} Notes: Use knowledge of phishing patterns and safe content, assume access to domain reputation data, maintain neutrality, and return {\"error\": \"Invalid or empty input provided\"} for invalid input."
    system_instruction_ru = "Вы являетесь продвинутой системой классификации контента, предназначенной для анализа интернет-ресурсов, таких как содержимое веб-сайтов или текст, извлеченный из PDF-файлов, для создания систем родительского контроля, предотвращающих доступ к нежелательной информации. Ваша задача — классифицировать предоставленный контент как безопасный или небезопасный на основе наличия вредоносного или неподходящего материала, такого как фишинг, контент для взрослых, насилие или злонамеренные намерения. Входные данные: Вы получите строку, содержащую необработанный текстовый контент ресурса (например, HTML веб-сайта, текст PDF, транскрибированное аудио/видео), который может включать метаданные (например, URL, имя файла) и быть зашумленным. Задача: 1. Анализируйте контент с использованием методов обработки естественного языка (NLP) для выявления шаблонов, ключевых слов или контекста, указывающих на нежелательную информацию (например, фишинг: подозрительные URL, запросы входа; контент для взрослых: откровенный язык; насилие: агрессивный язык; вредоносное ПО: подозрительные ссылки; другое: язык ненависти, азартные игры). 2. Учитывайте контекстные сигналы (тон, намерение, семантику), а не только соответствие ключевым словам. 3. Если предоставлены метаданные (например, URL), анализируйте их для дополнительных сигналов (например, репутация домена). 4. Классифицируйте как \"safe\" или \"unsafe\". 5. Укажите оценку уверенности (0-1). 6. Если небезопасно, укажите причины (например, фишинг, контент для взрослых). Выходные данные: Верните JSON-объект: {\"classification\": \"safe\"|\"unsafe\", \"confidence\": number, \"reasons\": string[], \"details\": string}. Ограничения: Обрабатывайте зашумленные/неполные входные данные корректно, избегайте ложных срабатываний, приоритет — высокий охват небезопасного контента, обрабатывайте эффективно, возвращайте низкую уверенность для неоднозначного контента и указывайте неопределенность в \"details\". Пример входных данных: URL: http://fakebank.com/login Content: Добро пожаловать в FakeBank! Ваш аккаунт под угрозой. Пожалуйста, войдите сейчас, чтобы обезопасить ваши средства. [Кнопка входа] Пример выходных данных: {\"classification\": \"unsafe\", \"confidence\": 0.92, \"reasons\": [\"phishing\", \"suspicious URL\"], \"details\": \"Контент содержит срочный язык и запрос входа, типичный для фишинга. URL 'fakebank.com' не является признанным банковским доменом.\"} Пример входных данных: Content: История Римской империи охватывает столетия... Пример выходных данных: {\"classification\": \"safe\", \"confidence\": 0.98, \"reasons\": [], \"details\": \"Контент обсуждает историческую информацию без вредоносного материала.\"} Примечания: Используйте знания о шаблонах фишинга и безопасном контенте, предполагайте доступ к данным о репутации доменов, сохраняйте нейтральность, возвращайте {\"error\": \"Некорректные или пустые входные данные\"} для некорректных входных данных."
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro-exp-03-25",
            contents=[text],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type='application/json',
                response_schema=Classification,
            )
        )
        return response.text
    except Exception as e:
        print(e)
        return None


if __name__ == '__main__':
    try:
        with open('./data/example_contents.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                data_type = row[0]
                data = row[1]
                metadata = row[2]
                content = JSONEncoder().encode(
                    {"type": data_type, "content": data, "metadata": metadata})
                print(content)
                print(classify_content(content))
    except Exception as e:
        pass

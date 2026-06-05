# main.py
from openai import OpenAI
from pathlib import Path
from mdtopdf import convertMD
import os
import sys

# --- Конфигурация ---
# API_KEY = os.environ.get("DEEPSEEK_API_KEY")
# <-- Лучше вынеси в переменную окружения!
API_KEY = "sk-cef00470115144bdb24cfd4c267205b2"
if not API_KEY:
    print("Ошибка: Не найден API ключ. Установите переменную окружения DEEPSEEK_API_KEY.")
    sys.exit(1)

MODEL_NAME = "deepseek-v4-flash"   # актуальная модель
MAX_TOKENS = 8096                   # максимальная длина ответа
TEMPERATURE = 0.1                   # точность (0.0-0.3 для кода/фактов)
SAVEPDF = False

# --- Инициализация клиента ---
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")
Path("answer/").mkdir(parents=True, exist_ok=True)

messages = []
conversation_counter = 0

# --- Функция вывода статистики ---


def print_usage_stats(response, model_name, temperature, max_tokens, history_len):
    usage = response.usage
    print("\n📊 Статистика запроса:")
    print(f"   Модель: {model_name}")
    print(f"   Температура: {temperature}")
    print(f"   Max tokens: {max_tokens}")
    print(f"   Токенов в запросе (prompt): {usage.prompt_tokens}")
    print(f"   Токенов в ответе (completion): {usage.completion_tokens}")
    print(f"   Всего токенов: {usage.total_tokens}")
    print(f"   Сообщений в истории: {history_len}")
    print("-" * 40)


# --- Приветствие с настройками ---
print("=" * 50)
print(f"🤖 DeepSeek чат-бот запущен")
print(f"   Модель: {MODEL_NAME}")
print(f"   Температура: {TEMPERATURE} (низкая → точные ответы)")
print(f"   Лимит ответа: {MAX_TOKENS} токенов")
print(f"   Сохранять PDF: {'Да' if SAVEPDF else 'Нет'}")
print("=" * 50)
print("Введите 'выход' или 'exit' для завершения.\n")

while True:
    user_input = input("Вы: ")

    if user_input.lower() in ["выход", "exit"]:
        print("До свидания!")
        break

    if not user_input.strip():
        print("Пожалуйста, введите осмысленный запрос.")
        continue

    messages.append({"role": "user", "content": user_input})
    print("DeepSeek печатает...")

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )

        assistant_response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_response})

        # Выводим ответ
        print(f"DeepSeek: {assistant_response}")

        # Показываем статистику использования токенов
        print_usage_stats(
            response,
            MODEL_NAME,
            TEMPERATURE,
            MAX_TOKENS,
            len(messages)  # количество сообщений в истории
        )

        conversation_counter += 1
        with open(f'answer/answer{conversation_counter}.md', 'w', encoding='utf-8') as file:
            file.write(assistant_response)

        if SAVEPDF:
            convertMD(
                f"answer/answer{conversation_counter}", assistant_response)

    except Exception as e:
        print(f"❌ Ошибка при обращении к API: {e}")
        messages.pop()  # удаляем последний вопрос, чтобы не засорять историю

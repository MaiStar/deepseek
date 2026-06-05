# main.py
from openai import OpenAI
from pathlib import Path
from mdtopdf import convertMD
import os
import sys
import time  # для измерения времени
from datetime import datetime


def get_next_counter():
    answer_dir = Path("answer/")
    existing = list(answer_dir.glob("answer*.md"))
    if not existing:
        return 1
    numbers = []
    for f in existing:
        try:
            num = int(f.stem.replace("answer", ""))
            numbers.append(num)
        except:
            continue
    return max(numbers) + 1 if numbers else 1


# --- Конфигурация ---
# API_KEY = os.environ.get("DEEPSEEK_API_KEY")
API_KEY = "sk-cef00470115144bdb24cfd4c267205b2"  # Лучше вынеси в .env!
if not API_KEY:
    print("Ошибка: Не найден API ключ. Установите переменную окружения DEEPSEEK_API_KEY.")
    sys.exit(1)

MODEL_NAME = "deepseek-v4-flash"   # актуальная модель
# MODEL_NAME = "deepseek-v4-pro"   # актуальная модель
MAX_TOKENS = 8096                   # максимальная длина ответа
TEMPERATURE = 0.1                   # точность (0.0-0.3 для кода/фактов)
SAVEPDF = False

# --- Инициализация клиента ---
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")
Path("answer/").mkdir(parents=True, exist_ok=True)

messages = []
conversation_counter = get_next_counter()   # <-- начинаем с правильного номера


# --- Функция для сохранения ответа + статистики в один .md файл ---


def save_answer_with_stats(counter, assistant_response, usage, elapsed_time, model, temperature, max_tokens, history_len):
    # Формируем содержимое файла: сначала ответ модели, затем блок статистики
    stats_block = f"""

---
## 📊 Статистика запроса
- **Модель**: {model}
- **Температура**: {temperature}
- **Max tokens**: {max_tokens}
- **Токенов в запросе (prompt)**: {usage.prompt_tokens}
- **Токенов в ответе (completion)**: {usage.completion_tokens}
- **Всего токенов**: {usage.total_tokens}
- **Сообщений в истории**: {history_len}
- **Время выполнения запроса**: {elapsed_time:.3f} секунд
- **Время запроса (локальное)**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
---
"""
    full_content = assistant_response + stats_block

    file_path = f"answer/answer{counter}.md"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
    return file_path


# --- Приветствие с настройками ---
print("=" * 60)
print(f"🤖 DeepSeek чат-бот запущен")
print(f"   Модель: {MODEL_NAME}")
print(f"   Температура: {TEMPERATURE} (низкая → точные ответы)")
print(f"   Лимит ответа: {MAX_TOKENS} токенов")
print(f"   Сохранять PDF: {'Да' if SAVEPDF else 'Нет'}")
print("=" * 60)
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
    print("DeepSeek печатает...", end="", flush=True)

    try:
        # Засекаем время перед запросом
        start_time = time.time()
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        end_time = time.time()
        elapsed = end_time - start_time

        assistant_response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_response})

        # Извлекаем usage
        usage = response.usage
        history_len = len(messages)

        # --- Вывод в консоль ---
        print("\n" + "=" * 60)
        print(f"📝 Ответ DeepSeek:\n{assistant_response}")
        print("\n📊 Статистика:")
        print(f"   Модель: {MODEL_NAME}")
        print(f"   Температура: {TEMPERATURE}")
        print(f"   Max tokens: {MAX_TOKENS}")
        print(f"   Токенов в запросе: {usage.prompt_tokens}")
        print(f"   Токенов в ответе: {usage.completion_tokens}")
        print(f"   Всего токенов: {usage.total_tokens}")
        print(f"   Сообщений в истории: {history_len}")
        print(f"   ⏱️ Время выполнения: {elapsed:.3f} сек")
        print("=" * 60)

        # --- Сохраняем ответ + статистику в .md файл ---
        conversation_counter += 1
        saved_path = save_answer_with_stats(
            conversation_counter,
            assistant_response,
            usage,
            elapsed,
            MODEL_NAME,
            TEMPERATURE,
            MAX_TOKENS,
            history_len
        )
        print(f"💾 Ответ сохранён в {saved_path}")

        # --- Дополнительно PDF, если нужно ---
        if SAVEPDF:
            convertMD(
                f"answer/answer{conversation_counter}", assistant_response)
            print(f"📄 PDF сохранён в pdf/answer{conversation_counter}.pdf")

    except Exception as e:
        print(f"\n❌ Ошибка при обращении к API: {e}")
        messages.pop()  # удаляем последний вопрос

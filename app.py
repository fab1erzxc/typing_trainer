from flask import Flask, render_template, request, jsonify
import os
import random
import re  # модуль для регулярных выражений

app = Flask(__name__)

# --- 1. Генерация текста для печати ---

# --- 1.1.  Словари слов (по уровням сложности) ---
#  (В реальном приложении лучше загружать из файла)

EASY_WORDS = [
    "cat", "dog", "run", "sun", "big", "red", "see", "and", "the", "a",
    "is", "in", "on", "to", "go", "up", "down", "one", "two", "three"
]

MEDIUM_WORDS = [
    "apple", "banana", "orange", "table", "chair", "window", "computer", "keyboard",
    "program", "python", "flask", "happy", "bright", "water", "music", "friend"
]

HARD_WORDS = [
    "ubiquitous", "exacerbate", "quixotic", "serendipity", "ephemeral", "mellifluous",
    "pernicious", "obfuscate", "cacophony", "conundrum", "algorithm", "asynchronous",
    "encapsulation", "polymorphism", "idempotent", "optimization"
]

# --- 1.2. Функции генерации текста ---


def generate_random_letters(length):
    """Генерирует строку случайных букв (и пробелов)."""
    letters = 'abcdefghijklmnopqrstuvwxyz '
    return ''.join(random.choice(letters) for i in range(length))


def generate_random_words(num_words, difficulty='easy'):
    """Генерирует строку из случайных слов заданного уровня сложности."""
    if difficulty == 'easy':
        words = EASY_WORDS
    elif difficulty == 'medium':
        words = MEDIUM_WORDS
    elif difficulty == 'hard':
        words = HARD_WORDS
    else:
        words = EASY_WORDS  # По умолчанию используем легкий уровень

    return ' '.join(random.choice(words) for i in range(num_words))


def generate_sentence(num_words, difficulty='easy'):
    """Генерирует простое предложение из случайных слов."""
    words = generate_random_words(num_words, difficulty).split()
    # Добавляем пунктуацию
    if words:
        words[0] = words[0].capitalize()  # Первое слово с заглавной буквы
    return ' '.join(words) + random.choice(['.', '!', '?'])


def generate_paragraph(num_sentences, num_words_per_sentence, difficulty):
    """Генерирует параграф"""
    sentences = [generate_sentence(num_words_per_sentence, difficulty)
                 for _ in range(num_sentences)]
    return ' '.join(sentences)


def generate_text(mode='words', difficulty='easy', length=100, num_words=20, num_sentences=5, num_words_per_sentence=8):
    """Генерирует текст заданного типа (mode), сложности и длины."""
    if mode == 'letters':
        return generate_random_letters(length)
    elif mode == 'words':
        return generate_random_words(num_words, difficulty)
    elif mode == 'sentences':
        return generate_sentence(num_words, difficulty)
    elif mode == 'paragraph':
        return generate_paragraph(num_sentences, num_words_per_sentence, difficulty)

    else:
        # По умолчанию - слова
        return generate_random_words(num_words, difficulty)


# --- 2. Маршрут /api/text ---

@app.route('/api/text')
def get_text():
    # Получаем параметры запроса (если они есть)
    mode = request.args.get('mode', 'words')  # По умолчанию - слова
    difficulty = request.args.get(
        'difficulty', 'easy')  # По умолчанию - легкий
    # По умолчанию - 100 символов
    length = int(request.args.get('length', 100))
    num_words = int(request.args.get('num_words', 20))  # По умолчанию - 20
    num_sentences = int(request.args.get('num_sentences', 5))
    num_words_per_sentence = int(request.args.get('num_words_per_sentence', 8))

    # Генерируем текст
    text = generate_text(mode, difficulty, length, num_words,
                         num_sentences, num_words_per_sentence)

    # Возвращаем текст в формате JSON
    return jsonify({'text': text})


# --- 3. Остальной код (без изменений) ---
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/stats', methods=['POST'])
def stats():
    data = request.get_json()
    speed = data.get('speed')
    accuracy = data.get('accuracy')
    print(f"Received stats: Speed={speed}, Accuracy={accuracy}")
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True)  # не забудьте выключить дебаг перед отправкой на хероку

from flask import Flask, render_template, request, jsonify
import os
import random
import re
import psycopg2

app = Flask(__name__)

# --- Подключение к базе данных ---
if os.environ.get('DATABASE_URL'):  # Heroku
    DATABASE_URL = os.environ.get('DATABASE_URL')

    def get_db_connection():
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
else:  # Локальная разработка
    DB_HOST = "localhost"
    DB_NAME = "typing_trainer_db"
    DB_USER = "typing_trainer_user"  # !!! Имя нового пользователя !!!
    DB_PASS = "bakuman56pen56"  # !!! Пароль нового пользователя !!!
    DB_PORT = 25432

    def get_db_connection():
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        return conn

# --- Функции генерации текста ---
# (В реальном приложении лучше загружать из файла)
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

# --- Маршрут /api/text ---


@app.route('/api/text')
def get_text():
    # Получаем параметры запроса
    mode = request.args.get('mode', 'words')
    difficulty = request.args.get('difficulty', 'easy')
    length = int(request.args.get('length', 100))
    num_words = int(request.args.get('num_words', 20))
    num_sentences = int(request.args.get('num_sentences', 5))
    num_words_per_sentence = int(request.args.get('num_words_per_sentence', 8))

    text = generate_text(mode, difficulty, length, num_words,
                         num_sentences, num_words_per_sentence)
    return jsonify({'text': text})

# --- Маршрут / (главная страница) ---


@app.route('/')
def index():
    return render_template('index.html')

# --- Маршрут /api/stats (СОХРАНЕНИЕ В БД) ---


@app.route('/api/stats', methods=['POST'])
def stats():
    data = request.get_json()
    speed = data.get('speed', 0)          # Значение по умолчанию 0
    accuracy = data.get('accuracy', 100)   # Значение по умолчанию 100
    mode = data.get('mode', 'words')      # Значение по умолчанию 'words'
    difficulty = data.get('difficulty', 'easy')  # Значение по умолчанию 'easy'
    length = data.get('length', 0)       # Значение по умолчанию 0

    print(
        f"Received stats: Speed={speed}, Accuracy={accuracy}, Mode={mode}, Difficulty={difficulty}, Length: {length}")

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO results (user_id, speed, accuracy, mode, difficulty, text_length) VALUES (%s, %s, %s, %s, %s, %s)",
            # !!! user_id=1 (временно)
            (1, speed, accuracy, mode, difficulty, length)
        )
        conn.commit()
        print("Stats saved to database.")
    except Exception as e:
        print(f"Error saving to database: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True)  # Выключаем

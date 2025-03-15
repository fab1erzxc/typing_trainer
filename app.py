from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import random
import re
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import datetime  # Добавляем модуль datetime

app = Flask(__name__)
# !!! ОБЯЗАТЕЛЬНО ЗАМЕНИТЕ !!!
app.config['SECRET_KEY'] = 'your_very_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
    DB_PASS = "bakuman56pen56"  # !!!  Пароль !!!
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

# --- Модель пользователя (UserMixin) ---


class User(UserMixin):
    def __init__(self, id, username, password_hash, email=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email = email

# --- Загрузка пользователя (обязательно для Flask-Login) ---


@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, username, password, email FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        if user_data:
            return User(user_data[0], user_data[1], user_data[2], user_data[3])
        return None
    except Exception as e:
        print(f"Error loading user: {e}")
        return None
    finally:
        cur.close()
        conn.close()


# --- Функции генерации текста ---
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
    letters = 'abcdefghijklmnopqrstuvwxyz '
    return ''.join(random.choice(letters) for i in range(length))


def generate_random_words(num_words, difficulty='easy'):
    if difficulty == 'easy':
        words = EASY_WORDS
    elif difficulty == 'medium':
        words = MEDIUM_WORDS
    elif difficulty == 'hard':
        words = HARD_WORDS
    else:
        words = EASY_WORDS
    return ' '.join(random.choice(words) for i in range(num_words))


def generate_sentence(num_words, difficulty='easy'):
    words = generate_random_words(num_words, difficulty).split()
    if words:
        words[0] = words[0].capitalize()
    return ' '.join(words) + random.choice(['.', '!', '?'])


def generate_paragraph(num_sentences, num_words_per_sentence, difficulty):
    sentences = [generate_sentence(
        num_words_per_sentence, difficulty) for _ in range(num_sentences)]
    return ' '.join(sentences)


def generate_text(mode='words', difficulty='easy', length=100, num_words=20, num_sentences=5, num_words_per_sentence=8):
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

# --- Маршруты (Routes) ---


@app.route('/api/text')
def get_text():
    mode = request.args.get('mode', 'words')
    difficulty = request.args.get('difficulty', 'easy')
    length = int(request.args.get('length', 100))
    num_words = int(request.args.get('num_words', 20))
    num_sentences = int(request.args.get('num_sentences', 5))
    num_words_per_sentence = int(request.args.get('num_words_per_sentence', 8))
    text = generate_text(mode, difficulty, length, num_words,
                         num_sentences, num_words_per_sentence)
    return jsonify({'text': text})


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id, username, password, email FROM users WHERE username = %s", (username,))
            user_data = cur.fetchone()

            if user_data:
                user = User(user_data[0], user_data[1],
                            user_data[2], user_data[3])
                if check_password_hash(user.password_hash, password):
                    login_user(user)
                    return redirect(url_for('index'))
                else:
                    flash('Incorrect password', 'error')  # добавляем флеш
            else:
                flash('Incorrect username', 'error')  # если пользователя нет
        except Exception as e:
            print(f"Error during login: {e}")
            flash('An error occurred', 'error')  # Добавляем флеш

        finally:
            cur.close()
            conn.close()

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id FROM users WHERE username = %s", (username,))
            existing_user = cur.fetchone()

            if existing_user:
                flash('Username already exists', 'error')  # добавляем флеш
                return redirect(url_for('register'))

            hashed_password = generate_password_hash(password)

            cur.execute(
                "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                (username, hashed_password, email)
            )
            conn.commit()
            flash('Registration successful! Please log in.',
                  'success')  # добавляем флеш
            return redirect(url_for('login'))

        except Exception as e:
            print(f"Error during registration: {e}")
            flash('An error occurred during registration',
                  'error')  # добавляем флеш
            conn.rollback()  # откатываем изменения
        finally:
            cur.close()
            conn.close()

    return render_template('register.html')


@app.route('/api/stats', methods=['POST'])
@login_required
def stats():
    data = request.get_json()
    speed = data.get('speed', 0)
    accuracy = data.get('accuracy', 100)
    mode = data.get('mode', 'words')
    difficulty = data.get('difficulty', 'easy')
    length = data.get('length', 0)

    print(
        f"Received stats: Speed={speed}, Accuracy={accuracy}, Mode={mode}, Difficulty={difficulty}, Length: {length}")

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO results (user_id, speed, accuracy, mode, difficulty, text_length) VALUES (%s, %s, %s, %s, %s, %s)",
            (current_user.id, speed, accuracy, mode,
             difficulty, length)  # Используем current_user.id
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

# --- Новый маршрут для дэшборда ---


@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Получаем все результаты для текущего пользователя
        cur.execute(
            "SELECT speed, accuracy, mode, difficulty, created_at FROM results WHERE user_id = %s ORDER BY created_at", (current_user.id,))
        results = cur.fetchall()

        # Преобразуем данные для Chart.js
        #   labels:  Список дат (или дат и времени)
        #   speeds: Список значений скорости
        #   accuracies: Список значений точности

        labels = []
        speeds = []
        accuracies = []

        for row in results:
            #  row[4] - это created_at (TIMESTAMP WITH TIME ZONE)
            #  Преобразуем его в строку в нужном формате (например, "YYYY-MM-DD HH:MM:SS")
            # Или другой формат
            labels.append(row[4].strftime("%Y-%m-%d %H:%M:%S"))
            speeds.append(row[0])  # speed
            accuracies.append(row[1])  # accuracy

        # Передаем данные в шаблон
        return render_template('dashboard.html', labels=labels, speeds=speeds, accuracies=accuracies)

    except Exception as e:
        print(f"Error fetching stats: {e}")
        flash('Error fetching stats', 'error')
        # Перенаправляем на главную в случае ошибки
        return redirect(url_for('index'))

    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)

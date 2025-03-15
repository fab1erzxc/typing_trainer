from flask import Flask, render_template, request, jsonify
import os  # Импортируем модуль os

app = Flask(__name__)

# Заглушка для базы данных (пока не используем PostgreSQL)
# В реальном приложении здесь будет подключение к базе данных
# DATABASE_URL = os.environ.get('DATABASE_URL')  # Раскомментируйте это позже


def get_db_connection():
    # Заглушка: Вместо реального подключения возвращаем None
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/stats', methods=['POST'])
def stats():
    # Получаем данные из запроса
    data = request.get_json()
    speed = data.get('speed')
    accuracy = data.get('accuracy')

    # Логируем данные
    print(f"Received stats: Speed={speed}, Accuracy={accuracy}")

    # Заглушка: Вместо сохранения в базу данных, просто возвращаем успешный ответ
    # В реальном приложении здесь будет код для сохранения данных в PostgreSQL
    conn = get_db_connection()
    # Проверяем, что соединение установлено (сейчас всегда будет False)
    if conn:
        # ... код для сохранения данных в базу данных ...
        conn.close()
        pass  # Заглушка

    return jsonify({'status': 'success'})


if __name__ == '__main__':
    # debug=True ТОЛЬКО для локальной разработки!  Уберите это перед развертыванием на Heroku!
    app.run(debug=True)

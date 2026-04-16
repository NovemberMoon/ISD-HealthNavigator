from flask import Flask, render_template, request, jsonify
import time
import psutil
import os
import random
import logging
from database import init_db, get_db_connection

app = Flask(__name__)

# Инициализируем БД прямо при создании объекта приложения.
# Это гарантирует, что БД создастся при запуске WSGI на PythonAnywhere.
init_db()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Middleware для профилирования производительности ---
@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def log_performance(response):
    duration = time.time() - request.start_time
    process = psutil.Process(os.getpid())
    # Получаем использование памяти в мегабайтах
    mem_info = process.memory_info().rss / (1024 * 1024)
    
    # Не логируем запросы к статике для чистоты логов
    if not request.path.startswith('/static'):
        app.logger.info(
            f"API: {request.method} {request.path} | "
            f"Status: {response.status_code} | "
            f"Time: {duration:.4f}s | "
            f"RAM: {mem_info:.2f} MB"
        )
    return response

# --- Бизнес-логика (AI Mock Engine) ---
def get_recommendations(steps, heart_rate, mood):
    recs = []
    
    if steps is not None and steps < 5000:
        recs.append("🏃‍♂️ Вы сегодня мало двигались. Рекомендуем короткую 15-минутную прогулку.")
    elif steps is not None and steps > 10000:
        recs.append("🏆 Отличная активность! Вы прошли норму шагов.")

    if heart_rate is not None and mood is not None:
        if heart_rate > 85 and mood <= 3:
            recs.append("🧘 Кажется, вы испытываете стресс (повышен пульс, низкое самочувствие). Попробуйте дыхательную гимнастику.")
            
    if not recs:
        recs.append("✅ Все показатели в норме! Продолжайте в том же духе.")
        
    return recs

# --- Роуты (Контроллеры) ---
@app.route('/')
def dashboard():
    conn = get_db_connection()
    user_id = 1 # Хардкод для MVP
    
    # Получаем последние метрики
    steps_row = conn.execute("SELECT value FROM device_metrics WHERE user_id = ? AND metric_type = 'steps' ORDER BY timestamp DESC LIMIT 1", (user_id,)).fetchone()
    hr_row = conn.execute("SELECT value FROM device_metrics WHERE user_id = ? AND metric_type = 'heart_rate' ORDER BY timestamp DESC LIMIT 1", (user_id,)).fetchone()
    
    steps = int(steps_row['value']) if steps_row else 0
    heart_rate = int(hr_row['value']) if hr_row else 0

    # Получаем последние записи дневника
    diary_entries = conn.execute("SELECT * FROM diary_entries WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5", (user_id,)).fetchall()
    latest_mood = diary_entries[0]['mood_score'] if diary_entries else None

    conn.close()

    # Генерируем рекомендации
    recommendations = get_recommendations(steps if steps_row else None, heart_rate if hr_row else None, latest_mood)

    return render_template('index.html', 
                           steps=steps, 
                           heart_rate=heart_rate, 
                           diary_entries=diary_entries,
                           recommendations=recommendations)

@app.route('/api/add_diary', methods=['POST'])
def add_diary():
    data = request.json
    mood = data.get('mood_score')
    text = data.get('symptoms_text')
    
    if not mood:
        return jsonify({"error": "Оценка настроения обязательна"}), 400

    conn = get_db_connection()
    conn.execute("INSERT INTO diary_entries (user_id, mood_score, symptoms_text) VALUES (?, ?, ?)",
                 (1, int(mood), text))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "Запись добавлена"})

@app.route('/api/sync_device', methods=['POST'])
def sync_device():
    # Имитация работы носимого устройства (случайные реалистичные данные)
    new_steps = random.randint(2000, 12000)
    new_hr = random.randint(60, 100)
    
    conn = get_db_connection()
    # Сохраняем шаги
    conn.execute("INSERT INTO device_metrics (user_id, metric_type, value) VALUES (?, ?, ?)",
                 (1, 'steps', float(new_steps)))
    # Сохраняем пульс
    conn.execute("INSERT INTO device_metrics (user_id, metric_type, value) VALUES (?, ?, ?)",
                 (1, 'heart_rate', float(new_hr)))
    conn.commit()
    conn.close()

    return jsonify({
        "status": "success", 
        "data": {
            "steps": new_steps,
            "heart_rate": new_hr
        }
    })

if __name__ == '__main__':
    # Этот блок сработает только при локальном запуске (python app.py),
    # на PythonAnywhere он будет проигнорирован.
    app.run(debug=False, host='0.0.0.0', port=5000)
# HealthNavigator MVP

Прототип веб-дашборда пациента и дневника самочувствия.

## Особенности

- Фреймворк: Flask (Python)
- База данных: SQLite
- Фронтенд: HTML5 + TailwindCSS + JS (Fetch API) + Chart.js
- Логирование производительности API (время ответа, потребление памяти).

## Как запустить

1. Убедитесь, что у вас установлен Python 3.8+.
2. Создайте виртуальное окружение и активируйте его:

    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Linux/Mac
    # или
    venv/Scripts/activate     # Для Windows
    ```

3. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

4. Запустите приложение (база данных будет инициализирована автоматически при первом запуске):

    ```bash
    python app.py
    ```

5. Откройте в браузере: `http://127.0.0.1:5000`

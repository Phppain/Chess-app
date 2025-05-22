# Используем официальный образ Python 3.11
FROM python:3.11

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

RUN pip install --upgrade pip

# Копируем файл зависимостей requirements.txt в рабочую директорию контейнера
COPY requirements.txt /app/

# Устанавливаем зависимости с помощью pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект (включая manage.py и остальные файлы) в рабочую директорию контейнера
COPY . /app/

# Открываем порт 8000 для приложения
EXPOSE 8000

# Команда для запуска сервера через Daphne
CMD ["daphne", "core.asgi:application", "-b", "0.0.0.0", "-p", "8000"]
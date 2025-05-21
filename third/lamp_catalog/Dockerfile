# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем зависимости
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Команда запуска через WSGI сервер Gunicorn
CMD ["gunicorn", "your_project_name.wsgi:application", "--bind", "0.0.0.0:9000"]

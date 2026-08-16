#  Берем официальный готовый образ Python
FROM python:3.11-slim

#  Указываем рабочую папку внутри контейнера
WORKDIR /app

#  Запрещаем Python писать файлы кэша .pyc на disk (для оптимизации)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#  Копируем файл со списком библиотек и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#  Копируем весь наш код (папку src и main.py) внутрь контейнера
COPY . .

#  Открываем порт 8000 для интернета
EXPOSE 8000

#  Команда, которая запустит наш сервер Uvicorn внутри Докера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

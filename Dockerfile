# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Создаем директорию для хранения фото
RUN mkdir -p /app/fotodir

# Указываем переменные окружения (можно использовать docker-compose для секрета токена)
ENV BASE_DIR=/app/fotodir
ENV BOT_TOKEN=your_token_here
# Запускаем бота
CMD ["python", "main.py"]
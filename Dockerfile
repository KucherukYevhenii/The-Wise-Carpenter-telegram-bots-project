# Використовуємо офіційний легкий образ Python
FROM python:3.11-slim

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Спочатку копіюємо requirements.txt для встановлення залежностей
COPY requirements.txt .

# Встановлюємо бібліотеки
# --no-cache-dir допомагає зекономити пам'ять, що важливо для безкоштовних тарифів
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо всі інші файли проєкту в контейнер
COPY . .

EXPOSE 8080

# Команда для запуску вашого файлу
CMD ["python", "run.py"]
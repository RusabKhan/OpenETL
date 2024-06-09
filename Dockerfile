# Dockerfile for Streamlit app
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8500

CMD ["streamlit", "run", "main.py"]

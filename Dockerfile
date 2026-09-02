FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY sql ./sql
CMD ["python", "src/tp1_3.3.py", "--help"]

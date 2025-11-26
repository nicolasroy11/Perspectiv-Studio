# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY web /app/web
COPY data /app/data
COPY brokers /app/brokers
COPY models /app/models
COPY strategies/llm_trader /app/strategies/llm_trader
COPY strategies/rules_based /app/strategies/rules_based
COPY runtime_settings.py /app/runtime_settings.py

EXPOSE 8000

CMD ["uvicorn", "web.trader_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

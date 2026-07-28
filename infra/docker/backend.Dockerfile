FROM python:3.12-slim AS base

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# 1. Pull the requirements specifically from the backend folder
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy ONLY the backend source code, ignoring the frontend/node_modules
COPY backend/ .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
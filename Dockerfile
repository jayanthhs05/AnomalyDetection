
FROM python:3.12 AS builder
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential pkg-config default-libmysqlclient-dev
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends libmariadb3 && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /usr/local /usr/local
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["gunicorn", "config.wsgi:application", "-b", "0.0.0.0:8000"]

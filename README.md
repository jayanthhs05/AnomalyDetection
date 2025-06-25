# Anomaly Studio – Quick Start Guide

---

## 1. Prerequisites

- Docker ≥ 20.10 & Docker Compose v2
- Git

---

## 2. Clone the project

```
git clone https://github.com/jayanthhs05/AnomalyDetection.git
cd AnomalyDetection
```

The repository already contains a `docker-compose.yml` file and a
production-ready `Dockerfile`.

---

## 3. Configure secrets

```
cp .env.example .env # Edit if you need non-default passwords
```

The `.env` file is consumed by both **docker compose** and Django at
startup.

---

## 4. Build & launch the full stack

```
docker compose build # 1st time or after requirements change
docker compose up -d # starts db, redis, web, worker, beat
docker compose ps # verify containers are healthy
```

The services are:

| Container | Purpose   | Port |
| --------- | --------- | ---- |
| db        | MySQL 8   | 3306 |
| redis     | Redis 7   | 6379 |
| web       | Django    | 8000 |
| worker    | Celery    | —    |
| beat      | Scheduler | —    |

Celery worker & beat connect automatically to Redis and MySQL; no
extra steps needed.

---

## 5. Initialise the Django database

```
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

You can now log in to **/admin/** or use the UI to add data
sources.

---

## 6. Use the application

1. Open http://localhost:8000
2. Click “Add Source” and register a database or use the import script
   below.
3. Background workers will learn patterns and flag anomalies.

---

## 7. (Option A) Import a sample MySQL schema

If you have a `dump.sql` and want to try it quickly:

```
./import_db.sh dump.sql mydb appuser apppass # creates DB + user
```

The helper script pipes the dump straight into the **db** container and
prints the credentials you need to paste into the “Add Source” form.

---

## 8. (Option B) Point to an existing DB

Just fill the “Add Source” form; validation will run your query and
ensure the timestamp & series columns exist before saving.

---

## 9. Keeping it tidy

```
docker compose logs -f web # tail web logs
docker compose down # stop everything
docker compose down -v # stop & wipe volumes (fresh start)
```

---

## 10. Run the test-suite

```
docker compose exec web python manage.py test
```

Django’s built-in test runner will pick up tests in **accounts/** and
**detection/**.

---

# Anomaly Studio
***AI-Powered Anomaly Detection for your Operational Data***

## What it is
Anomaly Studio is a Django Web application that connects to one or more relational data sources, learns their normal behaviour with machine learning models, and highlights the anomalies/outliers in real time.

## Features
- **Pluggable data sources:** Register any MySQL database and register it in the application with a `SELECT` query.
- **Schemaless event ingestion:** Rows are stored as JSON payloads, adapts to heterogeneous tables.
- **Unsupervised ML:** The data itself plays a huge role, using unsupervised machine learning with automatic re-training and drift detection.
- **Real time scoring with configurable sensitivity:** New rows are fetched every five minutes (configurable), lets you choose the sensitivity to balance false positives vs misses.
- **REST API Integration:** Get anomalies easily with a REST API.
- **Container first:** One command start using Docker Compose.

## Technology Stack
| Layer                  | Tech used                                     |
|------------------------|-----------------------------------------------|
| Web framework          | Django 5, Django REST Framework               |
| Worker & Scheduling    | Celery 5 + `django-celery-beat`               |
| Message broker / cache | Redis 7                                       |
| Primary database       | MySQL 8 (via `mysqlclient` / PyMySQL)         |
| ML / Data Science      | scikit-learn 1.5, pandas 2.2, NumPy           |
| Vectorization          | FeatureHasher + StandardScaler                |
| Front-end styling      | Bootstrap 5, Django Crispy-Forms              |
| Containerisation       | Docker, Docker Compose                        |


## Getting Started
### Prerequisites
- Docker >= 20.10
- Docker Compose
- Git

### Clone and Configure
```bash
git clone https://github.com/jayanthhs05/AnomalyDetection
cd AnomalyDetection
cp .env.example .env      # adjust passwords or ports
```

### Build and Launch
```bash
docker compose build      # only first time or after deps change
docker compose up -d      # starts db, redis, web, worker, beat
docker compose ps         # verify all services are healthy
```

### Initialise the Database
```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```
Visit http://localhost:8000 - the landing page should load.

### Stop the App
```bash
docker compose down        # stop everything
docker compose down -v     # stop & wipe volumes (fresh start)
```

## Usage Guide
1. Log in (or register) using the Web UI.
2. Add a datasource via the button, provide the required details including the timestamp column and the `SELECT` query from the database. Also configure sensitivity - how many expected anomalies.
3. The worker fetches the rows, trains the model, computes the scores and flags anomalies in the background.
4. Review results:
   - **Dashboard** shows the list of all your sources with their status.
   - **Rows View** shows the events per source and highlights anomalies.
   - **Anomaly View** shows the flagged events across sources.
5. API access:
   - `GET /detect/api/datasources/` - manage sources
   - `GET /detect/api/anomalies/` - paginated anomaly list
   - **Auth**: session cookie or DRF token.

## Processes 
| Process (Container) | Purpose                                  | Port(s) |
|---------------------|------------------------------------------|---------|
| `db`                | MySQL 8 database                         | `3306`  |
| `redis`             | Redis 7 message broker / cache           | `6379`  |
| `web`               | Django 5 web app                         | `8000`  |
| `worker`            | Celery worker for background tasks       | -       |
| `beat`              | Celery beat scheduler for periodic jobs  | -       |

## Repository Layout
```
├── accounts/             -- user registration & auth
├── detection/            -- core anomaly logic, API, tasks
│   ├── management/       -- custom Django commands
│   ├── migrations/
│   ├── templates/
│   └── tasks.py          -- fetch, train, score
├── config/               -- Django project settings, Celery app
├── model_store/          -- persisted vectorisers & models
├── templates/            -- shared HTML (base, auth screens)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md             -- you are here
```

## Environment Variables (`.env`)
| Variable                  | Default value | Purpose / Notes                                          |
|---------------------------|---------------|----------------------------------------------------------|
| `MYSQL_ENGINE`            | `django.db.backends.mysql` | Django DB engine (leave as-is for MySQL 8)               |
| `MYSQL_DATABASE`          | `anomaly`     | Schema used by the Django app                            |
| `MYSQL_USER`              | `anomaly`     | DB user Django will connect with                         |
| `MYSQL_PASSWORD`          | `password`    | Password for `MYSQL_USER`                                |
| `MYSQL_HOST`              | `db`          | Hostname of the MySQL container (matches docker-compose) |
| `MYSQL_PORT`              | `3306`        | MySQL port                                               |
| `MYSQL_ROOT_PASSWORD`     | `password`    | Root password used by the helper import script           |
| `DJANGO_SECRET_KEY`       | `secretkey`   | **Change in production!**                                |
| `DJANGO_ALLOWED_HOSTS`    | `localhost 127.0.0.1` | Space-separated list of hosts Django should serve  |
| `DEBUG`                   | `1`           | Set to `0` in production                                 |

## Quickly Testing the App
If you have a dump.sql and want to try it quickly:
```bash
./import_db.sh dump.sql mydb appuser apppass # creates DB + user
```

Positional arguments in order:

| Arg | Meaning                              |
|-----|--------------------------------------|
| `dump.sql` | Path to the SQL dump you want to import |
| `mydb`     | Schema name that will be created inside the MySQL container |
| `appuser`  | DB user created for read-only access by Anomaly Studio |
| `apppass`  | Password for `appuser` |

What the helper script does:

1. **Creates the schema** `mydb` (if it doesn’t exist).  
2. **Imports** the dump straight into the `db` container.  
3. **Creates / re-creates** `appuser` with **SELECT-only** privileges on `mydb`.  
4. Prints ready-to-paste connection details for the “Add Source” form.

> The script drops the user if it already exists; do not reuse credentials you care about in production.

Once the script finishes, open the web UI, click **Add Source**, and use:
```
Alias : <choose-a-label>
Engine : mysql
Host : db
Port : 3306
Name : mydb
User : appuser
Password : apppass
SQL : <your SELECT statement>
Timestamp col : <timestamp column>
Series columns : <optional series columns>
```

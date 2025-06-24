Start Clean
```
docker compose down -v
```

Initial Django Setup
```
django-admin startproject config .
python manage.py startapp detection
```

Rebuild and Launch
```
docker compose build --no-cache
docker compose up -d
docker compose ps
```

Setup Django
```
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

#!/usr/bin/env bash

set -euo pipefail

SQL_FILE=${1:-}
DB_NAME=${2:-}
APP_USER=${3:-}
APP_PASS=${4:-}
ROOT_PWD=${MYSQL_ROOT_PASSWORD:-}

if [[ -z "$SQL_FILE" || -z "$DB_NAME" || -z "$APP_USER" || -z "$APP_PASS" ]]; then
  echo "Usage: $0 dump.sql DB_NAME APP_USER APP_PASS"
  exit 1
fi
if [[ ! -f "$SQL_FILE" ]]; then
  echo "❌ $SQL_FILE not found"; exit 1
fi
if [[ -z "$ROOT_PWD" ]]; then
  echo "❌ Set MYSQL_ROOT_PASSWORD in your environment or .env"; exit 1
fi

echo "🚢 Importing $SQL_FILE into $DB_NAME …"
docker compose exec -T -e MYSQL_PWD="$ROOT_PWD" db \
  mysql -uroot -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`;"

cat "$SQL_FILE" | docker compose exec -T -e MYSQL_PWD="$ROOT_PWD" db \
  mysql -uroot "$DB_NAME"

echo "🔐 Creating user $APP_USER usable from any container …"
docker compose exec -T -e MYSQL_PWD="$ROOT_PWD" db mysql -uroot <<SQL
DROP   USER IF EXISTS '$APP_USER'@'%';
CREATE USER          '$APP_USER'@'%' IDENTIFIED BY '$APP_PASS';
GRANT SELECT ON \`$DB_NAME\`.* TO '$APP_USER'@'%';
FLUSH  PRIVILEGES;
SQL

echo "✅ Done — register the source in the UI with the details below."
cat <<INFO

Alias           : <pick a short unique label>
Engine          : mysql   (fixed)
Host            : db      (exactly as in docker-compose.yml)
Port            : 3306
Name (schema)   : $DB_NAME
User            : $APP_USER
Password        : $APP_PASS
SQL             : <write an sql statement>
Timestamp col   : <pick the timestamp column>
Series columns  : <pick series columns>

Make sure the SQL you provide really contains the timestamp column and
any series columns you list; otherwise validation will fail with
“column … is missing”.
INFO

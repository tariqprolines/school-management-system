#!/usr/bin/env bash
# Native PostgreSQL on the runner — same idea as a local Ubuntu server.
# No Docker / Compose / Actions service containers.
set -euo pipefail

DB_USER="${SMS_DB_USER:-sms_user}"
DB_PASS="${SMS_DB_PASSWORD:-sms_password}"
DB_NAME="${SMS_DB_NAME:-sms_test_db}"

sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y postgresql postgresql-contrib

sudo service postgresql start

for i in $(seq 1 30); do
  if sudo -u postgres pg_isready -q; then
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "PostgreSQL did not become ready"
    exit 1
  fi
  sleep 1
done

sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
    CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASS}';
  ELSE
    ALTER ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASS}';
  END IF;
END
\$\$;
SELECT 'CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')\gexec
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
SQL

sudo -u postgres psql -d "${DB_NAME}" -v ON_ERROR_STOP=1 -c "GRANT ALL ON SCHEMA public TO ${DB_USER};"
sudo -u postgres psql -d "${DB_NAME}" -v ON_ERROR_STOP=1 -c "ALTER SCHEMA public OWNER TO ${DB_USER};"

echo "PostgreSQL ready: ${DB_USER}@127.0.0.1:5432/${DB_NAME}"

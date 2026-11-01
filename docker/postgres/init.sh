#!/usr/bin/env bash
set -euo pipefail

create_app_database() {
  psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
    --set=ON_ERROR_STOP=1 \
    --set=db_name="$1" \
    --set=db_user="$2" \
    --set=db_password="$3" <<'SQL'
CREATE USER :"db_user" WITH PASSWORD :'db_password';
CREATE DATABASE :"db_name" OWNER :"db_user";
REVOKE ALL ON DATABASE :"db_name" FROM PUBLIC;
SQL
}

create_app_database \
  "$WORKSPACES_DB_NAME" "$WORKSPACES_DB_USER" "$WORKSPACES_DB_PASSWORD"

create_app_database \
  "$EVENTS_DB_NAME" "$EVENTS_DB_USER" "$EVENTS_DB_PASSWORD"
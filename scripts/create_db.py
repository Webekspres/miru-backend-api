import os

import psycopg2

DB_NAME = os.environ.get("DB_NAME", "miru")
conn = psycopg2.connect(
    dbname="postgres",
    user=os.environ.get("DB_USER", "root"),
    password=os.environ.get("DB_PASSWORD", "root"),
    host=os.environ.get("DB_HOST", "127.0.0.1"),
    port=os.environ.get("DB_PORT", "5432"),
)
conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
if cur.fetchone():
    print(f"database '{DB_NAME}' already exists")
else:
    cur.execute(f'CREATE DATABASE "{DB_NAME}"')
    print(f"database '{DB_NAME}' created")
cur.close()
conn.close()

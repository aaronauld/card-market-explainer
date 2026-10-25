from pathlib import Path

import psycopg


def read_env(path=".env"):
    values = {}
    file_content = Path(path).read_text(encoding="utf-8").splitlines()
    for line in file_content:
        line = line.strip()

        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()

    return values


def connect(env):
    return psycopg.connect(
        host="localhost",
        port=5433,
        dbname=env["POSTGRES_DB"],
        user=env["POSTGRES_USER"],
        password=env["POSTGRES_PASSWORD"],
    )

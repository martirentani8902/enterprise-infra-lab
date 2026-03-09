from flask import Flask
import psycopg2
import os

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "10.10.10.30")
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASS = os.getenv("DB_PASS", "password")

def get_conn():
    # Cada request abre una conexión: es simple para el lab.
    # Más adelante hablamos de pool (PgBouncer) y por qué esto escala mal.
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        connect_timeout=3,
    )

@app.get("/health")
def health():
    # Health real: verifica DB
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
        return "ok\n", 200
    except Exception as e:
        return f"db_error: {e}\n", 500

@app.get("/")
def home():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO visits DEFAULT VALUES RETURNING id;")
            visit_id = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM visits;")
            total = cur.fetchone()[0]
    return f"visit_id={visit_id} total_visits={total}\n"

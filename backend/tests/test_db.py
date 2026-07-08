import os
from dotenv import load_dotenv
import psycopg

load_dotenv()  # reads .env into environment variables, like require('dotenv').config()

db_url = os.environ["DATABASE_URL"]

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        print(cur.fetchone())

        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        print("pgvector installed:", cur.fetchone() is not None)
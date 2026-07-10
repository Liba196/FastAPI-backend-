import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

db_url = os.environ["DATABASE_URL"]

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        # 1. Print the version
        cur.execute("SELECT version();")
        print(cur.fetchone())

        # 2. Force install the extension into THIS specific database
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()  # Save the change!

        # 3. Check again
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        print("pgvector installed:", cur.fetchone() is not None)

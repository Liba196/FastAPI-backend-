from psycopg_pool import ConnectionPool

from app.core.config import DATABASE_URL

print("DATABASE URL INSIDE DATABASE.PY:")
print(DATABASE_URL)

pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=10,
)

def test_connection():
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(version)

if __name__ == "__main__":
    test_connection()
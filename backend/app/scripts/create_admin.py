import os
import getpass
import psycopg
from dotenv import load_dotenv

from app.core.security import hash_password

load_dotenv()
DB_URL = os.environ["DATABASE_URL"]


def main():
    email = input("Email: ").strip()
    full_name = input("Full name: ").strip()
    role = input("Role (super_admin / it_admin / content_editor): ").strip()
    password = getpass.getpass("Password: ")  # hides input, unlike input()

    if role not in ("super_admin", "it_admin", "content_editor"):
        print("Invalid role.")
        return

    password_hash = hash_password(password)

    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO admin_users (email, password_hash, full_name, role) VALUES (%s, %s, %s, %s)",
                (email, password_hash, full_name, role),
            )
        conn.commit()

    print(f"Created {role} account for {email}")


if __name__ == "__main__":
    main()
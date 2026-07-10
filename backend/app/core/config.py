from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# print(DATABASE_URL) i only printed just for testing 
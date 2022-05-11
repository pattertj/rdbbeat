import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://tabloid_service:dev@localhost:5026/tabloid_service"
)

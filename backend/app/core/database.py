from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

from dotenv import load_dotenv

# Load .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"))

# Get DB URL from environment variables (which are passed from docker-compose or .env)
# Default to the Docker internal URL if not set locally
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Construct it manually if DATABASE_URL isn't fully set but components are
    user = os.getenv("POSTGRES_USER", "admin")
    password = os.getenv("POSTGRES_PASSWORD", "secret_olemiss_password")
    db = os.getenv("POSTGRES_DB", "olemiss_advisor")
    DATABASE_URL = f"postgresql://{user}:{password}@127.0.0.1:5433/{db}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

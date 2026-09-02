from sqlalchemy import create_engine, text

from medtrack_mcp.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)


def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print(f"Database connection successful: {result.scalar()}")
    return None
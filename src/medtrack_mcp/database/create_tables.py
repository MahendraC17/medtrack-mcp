from medtrack_mcp.database.connection import engine
from medtrack_mcp.database.models import Base


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")


if __name__ == "__main__":
    create_tables()
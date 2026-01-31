from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# Use DATABASE_URL directly from .env
DATABASE_URL = settings.DATABASE_URL

# Mask password for logging
masked_url = DATABASE_URL.replace(
    settings.POSTGRES_PASSWORD, 
    "***"
)
print(f"🔌 Connecting to database: {masked_url}")

# Create database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verify connections before using
    echo=settings.DEBUG,      # Log SQL queries in debug mode
    pool_size=5,              # Connection pool size
    max_overflow=10,          # Max connections beyond pool_size
    pool_recycle=3600         # Recycle connections after 1 hour
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models (using SQLAlchemy 2.0 style)
Base = declarative_base()


def get_db():
    """
    Dependency for getting database session in FastAPI
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection() -> bool:
    """
    Test database connection
    Returns True if successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            
            # Test our initialization
            result = conn.execute(text("SELECT COUNT(*) FROM connection_test;"))
            count = result.fetchone()[0]
            
            print(f"✅ Database connected successfully!")
            print(f"📊 PostgreSQL version: {version[:50]}...")
            print(f"🧪 Test records found: {count}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test when running this file directly
    test_connection()

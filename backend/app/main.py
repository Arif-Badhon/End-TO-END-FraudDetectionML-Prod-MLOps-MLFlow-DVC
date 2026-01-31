from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from .config import settings
from .database import get_db, engine, Base, test_connection
import sys

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="Production-grade fraud detection system with end-to-end MLOps pipeline",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("=" * 60)
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"API running on: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"Docs available at: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print("=" * 60)
    
    # Test database connection on startup
    connection_ok = test_connection()
    if not connection_ok:
        print("⚠️  Warning: Could not connect to database!")
        print("⚠️  Check that PostgreSQL is running: cd docker && docker-compose up -d")
        if settings.ENVIRONMENT == "production":
            print("❌ Exiting in production mode due to database failure")
            sys.exit(1)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print(f"👋 Shutting down {settings.APP_NAME}")


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": f"http://{settings.API_HOST}:{settings.API_PORT}/docs"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    
    Verifies:
    - API is running
    - Database is connected
    - Database has expected tables
    """
    try:
        # Test database connection
        result = db.execute(text("SELECT 1 as health_check"))
        result.fetchone()
        
        # Check our test table
        result = db.execute(text("SELECT COUNT(*) FROM connection_test"))
        count = result.fetchone()[0]
        
        # Check schemas exist
        schemas_query = text("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name IN ('raw_data', 'features', 'models', 'monitoring')
            ORDER BY schema_name
        """)
        result = db.execute(schemas_query)
        schemas = [row[0] for row in result.fetchall()]
        
        return {
            "status": "healthy",
            "database": {
                "status": "connected",
                "test_records": count,
                "schemas": schemas
            },
            "environment": settings.ENVIRONMENT,
            "version": settings.APP_VERSION
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )


@app.get("/config")
async def get_config():
    """
    Show current configuration (safe values only)
    ⚠️ NEVER expose passwords or secrets!
    """
    return {
        "application": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG
        },
        "api": {
            "host": settings.API_HOST,
            "port": settings.API_PORT,
            "workers": settings.API_WORKERS
        },
        "database": {
            "host": settings.POSTGRES_HOST,
            "port": settings.POSTGRES_PORT,
            "name": settings.POSTGRES_DB,
            "user": settings.POSTGRES_USER
        },
        "mlflow": {
            "tracking_uri": settings.MLFLOW_TRACKING_URI,
            "experiment_name": settings.MLFLOW_EXPERIMENT_NAME
        },
        "paths": {
            "model": settings.MODEL_PATH,
            "data": settings.DATA_PATH,
            "feast": settings.FEAST_REPO_PATH
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=settings.API_WORKERS
    )

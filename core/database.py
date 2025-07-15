import asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from core.config import settings, logging

CHAR_LENGTH = 255
CLICKHOUSE_DATABASE_URI = str(settings.CLICKHOUSE_DATABASE_URI)

# Create synchronous engine (no async driver for ClickHouse HTTP)
engine_db = create_engine(CLICKHOUSE_DATABASE_URI, echo=True, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine_db, autocommit=False, autoflush=False)

# Sync session getter
def get_db():
    db = SessionLocal()
    try:
        logging.info("Database connected")
        yield db
    except Exception as e:
        logging.critical(f"Database connection failed: {e}")
        raise
    finally:
        db.close()

# Async wrapper using asyncio.to_thread (Python 3.9+)
async def get_async_db():
    loop = asyncio.get_running_loop()
    # Run sync session getter inside threadpool
    db_gen = await loop.run_in_executor(None, get_db)
    try:
        async for session in db_gen:
            yield session
    finally:
        # cleanup handled by sync get_db finally
        pass

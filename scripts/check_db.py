import asyncio
from sqlalchemy import text
from database.engine import engine
async def check_db_connection():
    print("Try to connect...")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("Successfully connected")
            print(f"Result of test: {result.fetchone()}")
    except Exception as e:
        print("Couldn't connect to the database")
        print(e)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_db_connection())
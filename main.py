import asyncpg
from fastapi import FastAPI
from decouple import config

app = FastAPI()

# Load the database URL from the environment variable
DB_URL = config("DB_URL")

@app.on_event("startup")
async def startup_db_client():
    # Create a connection pool to the YugabyteDB database
    app.state.db_pool = await asyncpg.create_pool(DB_URL)

@app.on_event("shutdown")
async def shutdown_db_client():
    # Close the connection pool
    await app.state.db_pool.close()

@app.get("/")
async def read_root():
    # Acquire a connection from the pool
    async with app.state.db_pool.acquire() as connection:
        result = await connection.fetch("SELECT 'Hello World!' AS message")
        return {"message": result[0]['message']}

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",  # Assuming this script is named main.py
        host="0.0.0.0",
        port=8000,
        reload=True
    )

# save as test_conn.py and run: python test_conn.py
import os, asyncio, urllib.parse
import psycopg

async def check():
    user = os.getenv("PSQL_USERNAME")
    pwd = urllib.parse.quote_plus(os.getenv("PSQL_PASSWORD",""))
    host = os.getenv("PSQL_HOST")
    port = os.getenv("PSQL_PORT","5432")
    db = os.getenv("PSQL_DATABASE","postgres")
    dsn = f"postgresql://{user}:{pwd}@{host}:{port}/{db}?sslmode=require"
    try:
        conn = await psycopg.AsyncConnection.connect(dsn)
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1")
            print(await cur.fetchone())
        await conn.close()
    except Exception as e:
        print("CONN ERROR:", e)

asyncio.run(check())

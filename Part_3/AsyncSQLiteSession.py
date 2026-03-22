import asyncio
from agents import Agent, Runner
from agents.extensions.memory import AsyncSQLiteSession
import aiosqlite
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

agent = Agent(name="Assistant")

# Enable WAL mode to prevent 'database is locked' ---WAL stands for Write-Ahead Logging.

#Normal mode:
#  main.db  <-- writing locks DB
#  readers blocked

#WAL mode:
#  main.db  <-- readers read freely
#  main.db-wal  <-- writers append here

async def enable_wal():
    async with aiosqlite.connect("conversations.db") as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.commit()

async def handle_user(user_id, message, session):
    try:
        response = await Runner.run(agent, message, session=session)
        print(f"[{user_id}] Agent: {response}")
    except Exception as e:
        print(f"[{user_id}] Error: {e}")

async def main():
    await enable_wal()

    # Initialize agent with API key
    
    # Single shared async session to reduce locking
    session = AsyncSQLiteSession("global_session", db_path="conversations.db")

    user_messages = {
        "user_1": "Hello!",
        "user_2": "How does async work in Python?",
        "user_3": "Can you summarize my conversation?"
    }

    # Run all users concurrently
    await asyncio.gather(*(handle_user(uid, msg, session) for uid, msg in user_messages.items()))
    await session.close()

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from agents import Agent, Runner
from agents.extensions.memory import SQLAlchemySession
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv(override=True)
# -----------------------------
# 🔹 CONFIG (Production style)
# -----------------------------
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/SDKdb"

# -----------------------------
# 🔹 CREATE ENGINE (reusable)
# -----------------------------
engine = create_async_engine(
    DATABASE_URL,
    echo=False,          # set True for debugging SQL logs
    pool_size=5,         # connection pooling
    max_overflow=10
)

# -----------------------------
# 🔹 CREATE AGENT
# -----------------------------
agent = Agent(
    name="SmartAssistant",
    instructions="You are a helpful assistant that remembers previous conversations."
)

# -----------------------------
# 🔹 CHAT FUNCTION (CORE LOGIC)
# -----------------------------
async def chat(user_id: str, message: str):
    # Create session tied to user
    session = SQLAlchemySession(
        user_id,
        engine=engine,
        create_tables=True   # auto-create tables if first run
    )

    # Run agent with memory
    result = await Runner.run(
        agent,
        message,
        session=session
    )

    return result.final_output


# -----------------------------
# 🔹 SIMULATE MULTI-USER CHAT
# -----------------------------
async def main():
    print("---- USER 1 ----")
    print(await chat("user1", "Hi, my name is Arjun"))
    print(await chat("user1", "What is my name?"))  # should remember

    print("\n---- USER 2 ----")
    print(await chat("user2", "Hello, I am Priya"))
    print(await chat("user2", "What is my name?"))  # separate memory

    print("\n---- USER 1 AGAIN ----")
    print(await chat("user1", "Do you still remember me?"))


if __name__ == "__main__":
    asyncio.run(main())

# ============================================================
# 🔹 SQLAlchemySession - CONCEPT SUMMARY (SHORT & PRACTICAL)
# ============================================================

# SQLAlchemySession provides persistent memory for agents using a database
# (like PostgreSQL). Instead of losing conversation after each run,
# messages are stored and retrieved from DB.

# Flow:
# User → Agent → Response
#              ↓
#        Stored in DB
#              ↓
#     Retrieved in next request

# Key Points:
# - Each session is identified by a unique "user_id"
# - All conversation history is stored in DB tables
# - On every run:
#     1. Previous messages are fetched
#     2. New input is processed
#     3. Response is generated
#     4. Conversation is saved back

# This enables:
# ✅ Memory across requests
# ✅ Multi-user support
# ✅ Production-grade persistence


# ============================================================
# 🔹 MULTI-USER IMPLEMENTATION (CURRENT APPROACH)
# ============================================================

# We used:
# session = SQLAlchemySession(user_id, engine=engine)

# Meaning:
# - Each user_id has isolated memory
# - Data is stored in same DB but separated logically

# Example:
# user1 → separate chat history
# user2 → separate chat history

# This ensures:
# ✅ No data leakage between users
# ✅ Scalable for real-world apps (chatbots, SaaS, etc.)


# ============================================================
# 🔹 OTHER SESSION SHARING PATTERNS (VERY IMPORTANT)
# ============================================================


# ------------------------------------------------------------
# 1. MULTIPLE SESSIONS → COMPLETELY SEPARATE CONVERSATIONS
# ------------------------------------------------------------

# Different session IDs = totally independent histories

# Example:
# session_alice = SQLAlchemySession("user_alice", engine=engine)
# session_bob   = SQLAlchemySession("user_bob", engine=engine)

# result1 = await Runner.run(agent, "Help me", session=session_alice)
# result2 = await Runner.run(agent, "Billing issue", session=session_bob)

# Outcome:
# - Alice and Bob conversations are fully isolated
# - Even if stored in same database, they never mix

# Use Case:
# ✅ Multi-user apps
# ✅ Chat platforms
# ✅ SaaS products


# ------------------------------------------------------------
# 2. SHARED SESSION → MULTIPLE AGENTS, SAME MEMORY
# ------------------------------------------------------------

# Same session used across different agents

# Example:
# support_agent = Agent(name="Support")
# billing_agent = Agent(name="Billing")

# session = SQLAlchemySession("user_123", engine=engine)

# result1 = await Runner.run(support_agent, "Help me", session=session)
# result2 = await Runner.run(billing_agent, "My charges?", session=session)

# Outcome:
# - Both agents share same conversation history
# - Billing agent can see what Support agent already discussed

# Use Case:
# ✅ Multi-agent workflows
# ✅ Customer support handoffs
# ✅ AI pipelines with role-based agents

# Concept:
# → "One user, one conversation, multiple agents"


# ------------------------------------------------------------
# 3. PARALLEL SESSIONS → SAME USER, DIFFERENT CONTEXTS
# ------------------------------------------------------------

# Same user, but different session IDs

# Example:
# session_chat1 = SQLAlchemySession("user1_chat1", engine=engine)
# session_chat2 = SQLAlchemySession("user1_chat2", engine=engine)

# Outcome:
# - Same user can have multiple independent conversations
# - Like multiple chat tabs

# Use Case:
# ✅ ChatGPT-style UI (multiple chats per user)
# ✅ Task-based conversations


# ------------------------------------------------------------
# 4. SHARED SESSION ACROSS REQUESTS (API / BACKEND)
# ------------------------------------------------------------

# In production (FastAPI / backend):
# - session_id comes from:
#     - user login (user_id)
#     - or request/session token

# Example:
# session_id = request.user.id
# session = SQLAlchemySession(session_id, engine=engine)

# This ensures:
# - Same user continues same conversation across API calls


# ============================================================
# 🔹 PRODUCTION INSIGHT (IMPORTANT)
# ============================================================

# Think of session_id as:
# → "Conversation ID"

# Design choices:
# - One session per user → single continuous chat
# - One session per conversation → multiple chat threads
# - Shared session → multi-agent collaboration

# ============================================================
# 🔹 FINAL TAKEAWAY
# ============================================================

# Session = Memory Container

# You control:
# - Who shares memory (same session_id)
# - Who gets isolation (different session_id)

# This flexibility is what makes SQLAlchemySession powerful
# for real-world AI systems.

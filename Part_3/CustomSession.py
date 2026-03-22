import asyncio
import asyncpg
from dotenv import load_dotenv

from agents import Agent, Runner
from agents.memory.session import SessionABC

# ---------------------------------------------------
# 🔐 Load environment variables
# ---------------------------------------------------
load_dotenv()


# ---------------------------------------------------
# 🧠 HELPER: CLEAN CONTENT (VERY IMPORTANT)
# ---------------------------------------------------
def extract_text(content):
    # Case 1: Already string
    if isinstance(content, str):
        return content

    # Case 2: Structured list (AI response)
    if isinstance(content, list):
        texts = []
        for c in content:
            if isinstance(c, dict) and "text" in c:
                texts.append(c["text"])
        return " ".join(texts)

    # Fallback
    return str(content)


# ---------------------------------------------------
# 🧠 CUSTOM POSTGRES SESSION
# ---------------------------------------------------
class PostgresSession(SessionABC):

    def __init__(self, session_id: str):
        self.session_id = session_id
        self._initialized = False

    # ---------------------------------------------------
    # 🔌 DB CONNECTION
    # ---------------------------------------------------
    async def connect(self):
        return await asyncpg.connect(
            user="postgres",          # 🔁 change
            password="postgres", # 🔁 change
            database="SDKdb",       # 🔁 change
            host="localhost"
        )

    # ---------------------------------------------------
    # 🏗️ ENSURE TABLE EXISTS
    # ---------------------------------------------------
    async def ensure_table(self):
        if self._initialized:
            return

        print("🛠️ Ensuring table exists...")

        conn = await self.connect()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                user_id TEXT,
                role TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        await conn.close()

        self._initialized = True
        print("✅ Table ready")


    # ---------------------------------------------------
    # 📥 FETCH HISTORY
    # ---------------------------------------------------
    async def get_items(self, limit=None):
        await self.ensure_table()

        print(f"\n📥 [get_items] Fetching history for {self.session_id}")

        conn = await self.connect()

        rows = await conn.fetch("""
            SELECT role, content
            FROM messages
            WHERE user_id = $1
            ORDER BY id ASC
        """, self.session_id)

        await conn.close()

        items = [{"role": r["role"], "content": r["content"]} for r in rows]

        print(f"📦 Retrieved {len(items)} messages")

        return items[-limit:] if limit else items


    # ---------------------------------------------------
    # 📤 STORE MESSAGES
    # ---------------------------------------------------
    async def add_items(self, items):
        await self.ensure_table()

        print(f"\n📤 [add_items] Storing messages for {self.session_id}")

        conn = await self.connect()

        for item in items:
            clean_content = extract_text(item["content"])  # ✅ FIX

            print(f"   ➤ {item['role']} → {clean_content[:50]}")

            await conn.execute("""
                INSERT INTO messages (user_id, role, content)
                VALUES ($1, $2, $3)
            """, self.session_id, item["role"], clean_content)

        await conn.close()


    # ---------------------------------------------------
    # ↩️ REMOVE LAST MESSAGE
    # ---------------------------------------------------
    async def pop_item(self):
        await self.ensure_table()

        print(f"\n↩️ Removing last message for {self.session_id}")

        conn = await self.connect()

        row = await conn.fetchrow("""
            DELETE FROM messages
            WHERE id = (
                SELECT id FROM messages
                WHERE user_id = $1
                ORDER BY id DESC
                LIMIT 1
            )
            RETURNING role, content
        """, self.session_id)

        await conn.close()

        if row:
            print(f"❌ Removed: {row['role']} → {row['content']}")
            return {"role": row["role"], "content": row["content"]}


    # ---------------------------------------------------
    # 🗑️ CLEAR SESSION
    # ---------------------------------------------------
    async def clear_session(self):
        await self.ensure_table()

        print(f"\n🗑️ Clearing session for {self.session_id}")

        conn = await self.connect()

        await conn.execute("""
            DELETE FROM messages WHERE user_id = $1
        """, self.session_id)

        await conn.close()

        print("✅ Session cleared")


# ---------------------------------------------------
# 🤖 AGENT
# ---------------------------------------------------
agent = Agent(
    name="Assistant",
    instructions="Reply shortly and clearly."
)


# ---------------------------------------------------
# 💬 CHAT FUNCTION
# ---------------------------------------------------
async def chat(session_id, message):
    session = PostgresSession(session_id)

    result = await Runner.run(
        agent,
        message,
        session=session
    )

    return result.final_output


# ---------------------------------------------------
# 🚀 MAIN DEMO
# ---------------------------------------------------
async def main():

    print("\n=========== CUSTOM SESSION DEMO ===========")

    # ---------------- USER 1 ----------------
    print("\n👤 USER 1")

    print(await chat("user_1", "Hi, my name is Arjun"))
    print(await chat("user_1", "What is my name?"))

    # ---------------- USER 2 ----------------
    print("\n👤 USER 2")

    print(await chat("user_2", "Hello, I am Priya"))
    print(await chat("user_2", "What is my name?"))

    # ---------------- USER 1 AGAIN ----------------
    print("\n👤 USER 1 AGAIN")

    print(await chat("user_1", "Do you remember me?"))

    # ---------------- POP ----------------
    session = PostgresSession("user_1")
    await session.pop_item()

    print("\n👤 USER 1 AFTER POP")
    print(await chat("user_1", "Do you still remember me?"))

    # ---------------- CLEAR ----------------
    await session.clear_session()

    print("\n👤 USER 1 AFTER RESET")
    print(await chat("user_1", "Do you remember me?"))

    print("\n=========== DEMO COMPLETE ===========")


# ---------------------------------------------------
# ▶️ RUN
# ---------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
    
"""
🧠 ===================== CUSTOM SESSION – COMPLETE UNDERSTANDING =====================

🔴 WHAT IS A CUSTOM SESSION?

A Custom Session is a way to define how and where conversation memory is stored.
Instead of using built-in storage like SQLiteSession or SQLAlchemySession,
we implement our own storage logic by following the SessionABC interface.

In simple terms:
→ We are telling the SDK: "Use MY database for storing chat history."

---

🔴 WHY CUSTOM SESSION EXISTS?

Built-in sessions (SQLiteSession / SQLAlchemySession):
✔ Easy to use
✔ Auto-create tables
❌ Limited control
❌ Not integrated with your system

Custom Session:
✔ Full control over database
✔ Can integrate with your backend
✔ Supports real-world use cases (multi-user, analytics, APIs)

---

🔴 CORE IDEA (VERY IMPORTANT)

The SDK (Runner.run) does NOT care about database type.

It only expects 4 methods:

1. get_items()   → fetch past conversation
2. add_items()   → store new messages
3. pop_item()    → remove last message
4. clear_session() → delete all history

As long as these methods exist → ANY storage works.

---

🔴 HOW THE FLOW WORKS INTERNALLY

When you call:

```
Runner.run(agent, message, session=session)
```

The SDK does:

```
1. session.get_items()
   → Fetch conversation history from DB

2. Send history + new message to model

3. Model generates response

4. session.add_items()
   → Save new messages (user + assistant)
```

So:

```
Runner → YOUR session → YOUR database
```

---

🔴 WHAT “MY OWN DATABASE” MEANS

It does NOT mean creating a DB from scratch.

It means choosing WHERE to store data:

Examples:

* Python list (temporary)
* JSON file
* SQLite
* PostgreSQL
* MongoDB
* Redis

In this project:
→ We used PostgreSQL

---

🔴 DIFFERENCE FROM SQLAlchemySession

SQLAlchemySession:
✔ Quick setup
✔ Auto tables
❌ Fixed schema
❌ No control over structure

Custom Session:
✔ You design tables
✔ You write queries
✔ You control relationships

Key difference:
→ SQLAlchemySession stores data FOR the SDK
→ Custom Session stores data AS PART OF YOUR SYSTEM

---

🔴 DATABASE DESIGN (IN THIS PROJECT)

Table: messages

Columns:

* id          → unique identifier
* user_id     → identifies user/session
* role        → "user" or "assistant"
* content     → actual message text
* created_at  → timestamp

This enables:
✔ Multi-user support
✔ Persistent memory
✔ Query flexibility

---

🔴 AUTO TABLE CREATION

Unlike built-in sessions, custom sessions do NOT create tables automatically.

We implemented:

```
ensure_table()
```

This:
✔ Creates table if it doesn't exist
✔ Runs only once (using _initialized flag)

This makes the system:
→ Self-contained
→ Safe for first-time execution

---

🔴 CONTENT HANDLING (CRITICAL PART)

AI responses are NOT always plain strings.

Sometimes they are structured like:

```
[
    {"type": "output_text", "text": "..."}
]
```

Database expects:
→ TEXT (string)

So we implemented:

```
extract_text()
```

This:
✔ Converts structured output → plain string
✔ Prevents runtime errors
✔ Ensures DB compatibility

---

🔴 MULTI-USER SUPPORT

We use:

```
session_id → mapped to user_id
```

So:

```
user_1 → separate history
user_2 → separate history
```

This is how real apps work:
→ Each user has isolated memory

---

🔴 OPERATIONS SUPPORTED

✔ get_items()
→ Read chat history

✔ add_items()
→ Store new messages

✔ pop_item()
→ Undo last message

✔ clear_session()
→ Reset conversation

These enable:
→ Chat systems
→ Undo features
→ Reset functionality

---

🔴 WHAT THIS DEMO PROVES

✔ SDK is calling OUR methods
✔ Data is stored in OUR database
✔ We control schema and logic
✔ Multi-user memory works
✔ Real-world architecture is achieved

---

🔴 REAL-WORLD ARCHITECTURE

Frontend (UI)
↓
Backend API (FastAPI / Django)
↓
Custom Session
↓
Database (PostgreSQL)

This is how production AI systems are built.

---

🔴 PRODUCTION EXTENSIONS (NEXT STEPS)

This system can be extended with:

✔ Connection pooling (performance)
✔ JSON storage (store full AI response)
✔ Indexing (faster queries)
✔ Authentication (user login)
✔ Analytics (usage tracking)
✔ APIs (chat history endpoints)

---

🔴 FINAL UNDERSTANDING

Custom Session is NOT about rewriting code.

It is about:

```
"Owning the memory layer of your AI system"
```

Instead of:
AI → SDK → Hidden storage

You now have:
AI → YOUR logic → YOUR database

---

## 🧠 END OF CUSTOM SESSION NOTES
"""
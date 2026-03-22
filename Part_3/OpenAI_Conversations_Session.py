"""
OpenAIConversationsSession - Practical Async Demo (WORKING VERSION)

This example demonstrates:

✅ Cloud-based conversation memory (no SQLite, no local DB)
✅ Multi-user handling using separate session objects
✅ Async execution using asyncio (non-blocking)
✅ Multi-turn conversations (context is remembered)
✅ Clean output using result.final_output
✅ No manual conversation_id (SDK handles internally)

------------------------------------------------------------

🧠 CORE IDEA:

Instead of storing chat history locally (like AsyncSQLiteSession),
OpenAIConversationsSession stores everything on OpenAI servers.

Analogy:
- AsyncSQLiteSession → notebook on your desk
- OpenAIConversationsSession → notebook in the cloud

------------------------------------------------------------

⚠️ IMPORTANT (based on your SDK version):

- conversation_id is NOT exposed → DO NOT use it
- You must store SESSION OBJECTS (not IDs)
- Memory persists ONLY while session object exists

------------------------------------------------------------
"""

import asyncio
import os
from dotenv import load_dotenv

from agents import Agent, Runner, OpenAIConversationsSession


# ---------------------------------------------------
# 🔐 Load API Key from .env
# ---------------------------------------------------
load_dotenv()




# ---------------------------------------------------
# 🤖 Create Agent
# ---------------------------------------------------
"""
Agent defines behavior of the assistant.

You can customize:
- Tone
- Style
- Output format
"""
agent = Agent(
    name="Assistant",
    instructions="""
    - Reply concisely
    - Explain clearly for beginners
    - Use simple examples if needed
    """
)


# ---------------------------------------------------
# 🧠 Session Storage (IMPORTANT)
# ---------------------------------------------------
"""
We simulate a real backend using a dictionary:

user_id → session object

In production:
- Replace this with a database (Redis, PostgreSQL)
- Store conversation references 

we store session objects directly to resume the conversation
"""
USER_SESSIONS = {}


# ---------------------------------------------------
# 👤 Handle User Request
# ---------------------------------------------------
"""
This function:
1. Checks if user already has a session
2. If not → creates a new session
3. Sends message to OpenAI
4. Prints response

Key Concept:
Each session = one conversation thread
"""
async def handle_user(user_id, message):
    try:
        # ---------------------------------------------------
        # 🔁 Create or reuse session
        # ---------------------------------------------------
        if user_id not in USER_SESSIONS:
            USER_SESSIONS[user_id] = OpenAIConversationsSession()
            print(f"\n[{user_id}] 🆕 New session created")

        session = USER_SESSIONS[user_id]

        # ---------------------------------------------------
        # 🧾 Custom Input (Optional)
        # ---------------------------------------------------
        """
        You can inject extra context here:
        - user preferences
        - role info
        - metadata

        This is useful in real applications
        """
        custom_input = f"""
        User: {user_id}
        Message: {message}
        """

        # ---------------------------------------------------
        # 🚀 Run Agent (Async)
        # ---------------------------------------------------
        result = await Runner.run(
            agent,
            custom_input,
            session=session
        )

        # ---------------------------------------------------
        # 🖨️ Clean Output
        # ---------------------------------------------------
        print(f"\n[{user_id}] USER: {message}")
        print(f"[{user_id}] BOT: {result.final_output}")

    except Exception as e:
        print(f"[{user_id}] ❌ Error: {e}")


# ---------------------------------------------------
# 🚀 Main Function
# ---------------------------------------------------
async def main():
    """
    Simulates real-world concurrent users.

    asyncio.gather:
    - Runs tasks in parallel
    - Non-blocking execution

    Without async:
        user_1 → wait → user_2 → wait

    With async:
        user_1 + user_2 run together
    """

    # -------------------------------
    # Round 1 (new conversations)
    # -------------------------------
    await asyncio.gather(
        handle_user("user_1", "What city is the Golden Gate Bridge in?"),
        handle_user("user_2", "Explain async in Python"),
    )

    # -------------------------------
    # Round 2 (memory test)
    # -------------------------------
    await asyncio.gather(
        handle_user("user_1", "What state is it in?"),   # should remember context
        handle_user("user_2", "Give a simple example"),
    )

    # -------------------------------
    # Round 3 (deeper memory)
    # -------------------------------
    await handle_user(
        "user_1",
        "Tell me a fun fact about that place"
    )


# ---------------------------------------------------
# ▶️ Run Program
# ---------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())

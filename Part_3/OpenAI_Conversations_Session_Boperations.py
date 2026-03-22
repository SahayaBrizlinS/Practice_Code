"""
OpenAIConversationsSession - Basic Memory Operations Demo

This demonstrates:

✅ get_items()
✅ add_items()
✅ pop_item()
✅ clear_session()

⚠️ Important:
All operations are async and hit OpenAI servers (not local DB)
"""

import asyncio
from dotenv import load_dotenv

from agents import Agent, Runner, OpenAIConversationsSession

# ---------------------------------------------------
# 🔐 Load API Key
# ---------------------------------------------------
load_dotenv()


# ---------------------------------------------------
# 🤖 Agent
# ---------------------------------------------------
agent = Agent(
    name="Assistant",
    instructions="Reply concisely."
)


# ---------------------------------------------------
# 🚀 Demo Function
# ---------------------------------------------------
async def memory_operations_demo():

    session = OpenAIConversationsSession()

    # ---------------------------------------------------
    # 1️⃣ Initialize session (IMPORTANT)
    # ---------------------------------------------------
    """
    Session is lazy-loaded.
    Must call Runner.run() once before memory ops
    """
    await Runner.run(agent, "Hello", session=session)

    print("\n✅ Session initialized")
    print("Session ID:", session.session_id)


    # ---------------------------------------------------
    # 2️⃣ GET ITEMS (Read memory)
    # ---------------------------------------------------
    print("\n📖 GET ITEMS")

    items = await session.get_items()
    print("History:", items)


    # ---------------------------------------------------
    # 3️⃣ ADD ITEMS (Manual injection)
    # ---------------------------------------------------
    print("\n✍️ ADD ITEMS")

    await session.add_items([
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a programming language."}
    ])

    items = await session.get_items()
    print("Updated History:", items)


    # ---------------------------------------------------
    # 4️⃣ POP ITEM (Undo last message)
    # ---------------------------------------------------
    print("\n↩️ POP ITEM")

    last_item = await session.pop_item()
    print("Removed:", last_item)

    items = await session.get_items()
    print("After Pop:", items)


    # ---------------------------------------------------
    # 5️⃣ CLEAR SESSION (Reset memory)
    # ---------------------------------------------------
    print("\n🗑️ CLEAR SESSION")

    await session.clear_session()

    items = await session.get_items()
    print("After Clear:", items)


# ---------------------------------------------------
# ▶️ Run
# ---------------------------------------------------
if __name__ == "__main__":
    asyncio.run(memory_operations_demo())

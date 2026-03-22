"""
OpenAIResponsesCompactionSession - REAL CONVERSATION DEMO

This version fixes your concern:
❌ No artificial loop
✅ Real meaningful conversation
✅ Easy to understand compaction flow

------------------------------------------------------------

🧠 WHAT YOU WILL SEE:

We set compaction limit = 3 messages

Conversation flow:

User asks real questions:
1. What is Python?
2. What is async?
3. Difference between sync and async?
→ 🔥 FIRST COMPACTION

4. Give real-life example
5. Why async is faster?
6. Where is it used?
→ 🔥 SECOND COMPACTION

7. What is asyncio?
8. How to use await?
9. Common mistakes?
→ 🔥 THIRD COMPACTION

------------------------------------------------------------

🧠 EXPECTED BEHAVIOR:

After every 3 messages:
→ Old conversation is summarized
→ Stored as "compaction"
→ New messages continue

IMPORTANT:
DB will still show many messages
BUT model uses:
    latest summary + recent messages

------------------------------------------------------------

❗ WHY NOT OpenAIConversationsSession?

Because:
- You cannot SEE memory
- You cannot CONTROL compaction
- Everything is hidden on OpenAI side

Compaction requires:
✔ visibility
✔ control

So we use:
✔ SQLiteSession + Compaction

------------------------------------------------------------
"""

import asyncio
from dotenv import load_dotenv

from agents import Agent, Runner
from agents.memory import SQLiteSession
from agents.memory import OpenAIResponsesCompactionSession


# ---------------------------------------------------
# 🔐 Load API key
# ---------------------------------------------------
load_dotenv()


# ---------------------------------------------------
# 🧠 Underlying storage (FULL HISTORY)
# ---------------------------------------------------
underlying = SQLiteSession("real_demo", "real_demo.db")


# ---------------------------------------------------
# 🧠 Compaction trigger (LIMIT = 3 messages)
# ---------------------------------------------------
def trigger_compaction(items):
    return len(items) >= 3   # 🔥 force compaction for demo


# ---------------------------------------------------
# 🧠 Compaction session
# ---------------------------------------------------
session = OpenAIResponsesCompactionSession(
    session_id="real_demo",
    underlying_session=underlying,
    should_trigger_compaction=trigger_compaction,
)


# ---------------------------------------------------
# 🤖 Agent
# ---------------------------------------------------
agent = Agent(
    name="Assistant",
    instructions="Explain in simple beginner-friendly way."
)


# ---------------------------------------------------
# 🔍 Debug function (SEE STORAGE)
# ---------------------------------------------------
async def debug_storage():
    items = await underlying.get_items()

    print("\n📦 STORAGE VIEW:")
    for i, item in enumerate(items):
        print(f"{i+1}. {item['type']} → {item.get('role', 'N/A')}")


# ---------------------------------------------------
# 🚀 MAIN (REAL CONVERSATION)
# ---------------------------------------------------
async def main():

    # -------------------------------
    # 🧩 Conversation (REAL QUESTIONS)
    # -------------------------------
    questions = [
        "What is Python?",
        "What is async programming?",
        "Difference between sync and async?",

        "Give a real-life example of async",
        "Why is async faster?",
        "Where is async used in real apps?",

        "What is asyncio in Python?",
        "How does await work?"
        
    ]

    # -------------------------------
    # 💬 Run conversation step by step
    # -------------------------------
    for i, question in enumerate(questions):

        result = await Runner.run(
            agent,
            question,
            session=session
        )

        print(f"\n🧠 USER: {question}")
        print(f"🤖 BOT: {result.final_output[:80]}...")

        # 🔍 Show DB state after each step
        await debug_storage()


# ---------------------------------------------------
# ▶️ RUN
# ---------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())

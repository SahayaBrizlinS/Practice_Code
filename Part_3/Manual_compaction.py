"""
============================================================
🧠 OPENAI RESPONSES COMPACTION - MANUAL MODE (PRODUCTION STYLE)
============================================================

✔ Manual compaction (NO auto delay)
✔ Full control over when compaction happens
✔ Real conversation flow
✔ Debug storage visibility

------------------------------------------------------------
🧠 FLOW:

User → Agent → Response (FAST)
                    ↓
            (Manual Compaction Triggered Separately)

------------------------------------------------------------
"""

import asyncio
from dotenv import load_dotenv

from agents import Agent, Runner
from agents.memory import SQLiteSession
from agents.memory import OpenAIResponsesCompactionSession


# ---------------------------------------------------
# 🔐 Load environment variables (API KEY)
# ---------------------------------------------------
load_dotenv()


# ---------------------------------------------------
# 🧠 UNDERLYING STORAGE (FULL HISTORY)
# ---------------------------------------------------
# Stores ALL messages (no deletion)
# Compaction only changes what model sees, not DB
#
underlying = SQLiteSession(
    "manual_demo",
    "manual_demo.db"
)


# ---------------------------------------------------
# 🧠 DISABLE AUTO COMPACTION
# ---------------------------------------------------
# This ensures:
#   ❌ No compaction during Runner.run()
#   ✅ No latency delay
#
session = OpenAIResponsesCompactionSession(
    session_id="manual_demo",
    underlying_session=underlying,
    should_trigger_compaction=lambda _: False   # 🔥 manual mode
)


# ---------------------------------------------------
# 🤖 AGENT
# ---------------------------------------------------
agent = Agent(
    name="Assistant",
    instructions="Explain in simple beginner-friendly way."
)


# ---------------------------------------------------
# 🔍 DEBUG STORAGE FUNCTION
# ---------------------------------------------------
# Shows what is actually stored in DB
#
async def debug_storage():
    items = await underlying.get_items()

    print("\n📦 STORAGE VIEW:")

    for i, item in enumerate(items):

        item_type = item.get("type", "message")
        role = item.get("role", "N/A")

        # Extract readable content safely
        content = ""

        if "content" in item:
            if isinstance(item["content"], list):
                content = " ".join(
                    c.get("text", "") for c in item["content"] if isinstance(c, dict)
                )
            else:
                content = str(item["content"])

        print(f"{i+1}. [{item_type}] ({role}) → {content[:60]}")


# ---------------------------------------------------
# ⚙️ MANUAL COMPACTION FUNCTION
# ---------------------------------------------------
async def run_manual_compaction():
    print("\n⚙️ RUNNING MANUAL COMPACTION...")

    # Force compaction regardless of size
    await session.run_compaction({"force": True})

    print("✅ Compaction complete!")

    # Show updated DB
    await debug_storage()


# ---------------------------------------------------
# 🚀 MAIN (REAL CONVERSATION)
# ---------------------------------------------------
async def main():

    print("\n================= MANUAL COMPACTION DEMO =================")

    questions = [
        # ---- Block 1 ----
        "What is Python?",
        "What is async programming?",
        "Difference between sync and async?",

        # ---- Block 2 ----
        "Give a real-life example of async",
        "Why is async faster?",
        "Where is async used in real apps?",

        # ---- Block 3 ----
        "What is asyncio in Python?",
        "How does await work?",
        "Common mistakes in async programming?"
    ]

    # ---------------------------------------------------
    # 💬 CONVERSATION LOOP
    # ---------------------------------------------------
    for i, question in enumerate(questions):

        result = await Runner.run(
            agent,
            question,
            session=session
        )

        print(f"\n🧠 USER: {question}")
        print(f"🤖 BOT: {result.final_output[:80]}...")

        # 🔍 Show DB after each step
        await debug_storage()

        # ---------------------------------------------------
        # 🔥 MANUAL COMPACTION TRIGGER
        # ---------------------------------------------------
        # Run compaction every 3 turns
        #
        if (i + 1) % 3 == 0:
            await run_manual_compaction()

    print("\n================= DEMO COMPLETE =================")


# ---------------------------------------------------
# ▶️ RUN
# ---------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())

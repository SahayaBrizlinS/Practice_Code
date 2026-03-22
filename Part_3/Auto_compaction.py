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
    

"""

# 🧠 OPENAI RESPONSES COMPACTION - COMPLETE CONCEPT NOTES

---

## 🔷 WHAT IS COMPACTION?

Compaction is a memory optimization technique used in AI systems.

Problem:
As conversation grows → token size increases
→ Higher cost
→ Slower responses
→ Risk of exceeding model context limit

Solution:
Old conversation is summarized into a compact form

So instead of sending full history:
Q1, A1, Q2, A2, Q3, A3, Q4...

Model receives:
SUMMARY(Q1–Q3) + Q4

---

## 🔷 CORE IDEA (MOST IMPORTANT)

Compaction does NOT delete data ❌
Compaction COMPRESSES data ✅

Full history remains in database
BUT model only uses:
summary + recent messages

---

## 🔷 HOW COMPACTION WORKS INTERNALLY

Step 1:
Collect old conversation messages
(user + assistant messages)

Step 2:
Send them to OpenAI compaction API
→ "Summarize this conversation"

Step 3:
Model generates summary

Step 4:
Store summary as:
type = "compaction"

Step 5:
Future responses use:
summary + new messages

---

## 🔷 WHAT HAPPENS TO OLD MESSAGES?

Before compaction:
user → assistant → user → assistant → ...

After compaction:
compaction (summary)
+ recent messages

Assistant responses may not appear separately in DB view
because they are already included in summary

---

## 🔷 MODEL VIEW vs DATABASE VIEW

Database:
Stores ALL messages (full history)

Model Input:
Uses ONLY:
summary + recent messages

This is why DB may look large,
but model context remains small

---

## 🔷 TYPES OF COMPACTION

1. DEFAULT AUTO COMPACTION

---

No custom trigger provided

System decides:
WHEN → based on token size
WHAT → which messages to summarize
HOW MUCH → summary size

Behavior:
Small conversation → no compaction
Large conversation → compaction triggers

Pros:
✔ Easy to use
✔ Adaptive

Cons:
❌ Unpredictable
❌ Can introduce latency

---

2. CUSTOM AUTO COMPACTION

---

User defines trigger condition

Example:
should_trigger_compaction=lambda items: len(items) >= 3

Behavior:
Compaction runs automatically based on custom logic

Pros:
✔ Predictable
✔ Good for demos/testing

Cons:
❌ Not token-aware
❌ Can over-compact
❌ Not ideal for production

---

3. MANUAL COMPACTION (BEST FOR PRODUCTION)

---

Auto compaction disabled:
should_trigger_compaction=lambda _: False

Compaction triggered manually:
await session.run_compaction()

Behavior:
Developer controls WHEN compaction happens

Pros:
✔ Full control
✔ No latency during response
✔ Best for real-time apps

Cons:
❌ Requires manual handling

---

## 🔷 AUTO COMPACTION FLOW (IMPORTANT)

During Runner.run():

```
1. User sends message
2. Model generates response
3. Response is returned to user
4. System checks token size
5. If too large → compaction runs
```

NOTE:
Compaction happens AFTER response
→ may cause slight delay in streaming apps

---

## 🔷 MANUAL COMPACTION FLOW

```
1. User sends message
2. Model responds immediately (fast)
3. Developer triggers compaction separately
```

This avoids latency during user interaction

---

## 🔷 WHY TOKEN-BASED TRIGGER (DEFAULT)?

Message count is unreliable:

```
3 long messages → very large tokens
10 short messages → very small tokens
```

So default system uses:
token size (context length)

NOT number of messages

---

## 🔷 COMMON CONFUSION

❓ "Why assistant messages disappear?"

Answer:
They are not deleted
They are included inside the summary (compaction)

---

## 🔷 DEBUGGING COMPACTION

To detect compaction:
Look for:
type = "compaction"

To inspect summary:
print full item using pprint

Example:
import pprint
pprint.pprint(item)

---

## 🔷 FREQUENT ISSUE (CUSTOM TRIGGER)

Using:
len(items) >= 3

Problem:
items = ALL stored messages

So condition becomes TRUE repeatedly
→ compaction runs too often

Better approach:
Count only recent non-compaction messages

---

## 🔷 WHEN COMPACTION HAPPENS REPEATEDLY

Compaction is continuous:

```
Old summary + new messages
    → new summary
```

This keeps conversation size under control

---

## 🔷 WHY COMPACTION IS CRITICAL

Without compaction:
❌ High token usage
❌ Expensive API calls
❌ Slow responses
❌ Context limit overflow

With compaction:
✅ Reduced tokens
✅ Faster responses
✅ Lower cost
✅ Scalable conversations

---

## 🔷 REAL-WORLD USAGE

Used in:
- ChatGPT-like apps
- Customer support bots
- Long conversations
- AI copilots

Production pattern:
User request → fast response
Compaction → background process

---

## 🔷 FINAL MENTAL MODEL

Full conversation:
Q1 → A1 → Q2 → A2 → Q3 → A3 → Q4

After compaction:
SUMMARY(Q1–Q3) + Q4

---

## 🔷 KEY TAKEAWAYS

✔ Compaction reduces context size, not DB size
✔ Summary replaces multiple messages
✔ Model sees summary, not full history
✔ Default compaction is token-based
✔ Manual compaction is best for production
✔ Custom compaction is useful for learning/demo

============================================================
"""

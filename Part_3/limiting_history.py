import asyncio
from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    SQLiteSession,
    RunConfig,
    SessionSettings
)

# Load API key from .env
load_dotenv()

#--------------------------------------------------------------------------------------------------
#SQLite Session DB
#(20 stored messages)
#        ↓
#SessionSettings(limit=8)
#        ↓
#Retrieve last 8 messages
#        ↓
#session_input_callback
#        ↓
#Trim to last 3 messages
#        ↓
#Send to LLM
#--------------------------------------------------------------------------------------------------
# These both are applicable for only local session database.(SQLiteSession)
# -------------------------------------------------------
# SESSION INPUT CALLBACK
# Runs AFTER history is retrieved from the session store
# -------------------------------------------------------
def trim_history(history, new_input):

    print("\n--- SESSION INPUT CALLBACK ---")
    print("History retrieved from session:", len(history))

    # Keep only last 3 messages
    trimmed = history[-3:]

    print("History after trimming:", len(trimmed))

    return trimmed + new_input


async def main():

    agent = Agent(
        name="Assistant",
        instructions="Answer concisely.",
        model="gpt-4o-mini"
    )

    # Local session database
    session = SQLiteSession("demo_conversation")

    run_config = RunConfig(

        # 1️⃣ Limit how much history is retrieved from DB
        session_settings=SessionSettings(limit=8),

        # 2️⃣ Modify history before sending to model
        session_input_callback=trim_history
    )

    # Multiple turns to build history
    questions = [
        "What is the capital of France?",
        "What country is it in?",
        "What is its population?",
        "What river flows through it?",
        "Name a famous museum there.",
        "Who built the Eiffel Tower?",
        "When was it built?",
        "Why is Paris famous?"
    ]

    for i, q in enumerate(questions):

        print(f"\n====== TURN {i+1} ======")
        print("User:", q)

        result = await Runner.run(
            agent,
            q,
            session=session,
            run_config=run_config
        )

        print("Agent:", result.final_output)


# Run program
asyncio.run(main())
#--------------------------------------------------------------------------------------------------
#SQLite Session DB
#      ↓
#      ↓  (retrieve history)
#      ↓
#SessionSettings (optional)
#      ↓
#      ↓
#session_input_callback
#(history manipulation)
#      ↓
#      ↓
#Prepared prompt
#      ↓
#      ↓
#call_model_input_filter
#(final prompt editing)
#      ↓
#      ↓
#LLM call
#--------------------------------------------------------------------------------------------------



import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, SQLiteSession, RunConfig
from agents.run import CallModelData, ModelInputData

# ---------------------------------------------------
# Load API key from .env
# ---------------------------------------------------
load_dotenv()


# ---------------------------------------------------
# 1️⃣ SESSION INPUT CALLBACK
# Runs when session history is loaded
# Used to trim stored conversation
# ---------------------------------------------------
def session_callback(history, new_input):

    print("\n===== SESSION INPUT CALLBACK =====")
    print("History loaded from session:", len(history))

    # Keep only last 4 messages from session
    trimmed_history = history[-4:]

    print("History after trimming:", len(trimmed_history))

    return trimmed_history + new_input


# ---------------------------------------------------
# 2️⃣ CALL MODEL INPUT FILTER
# Runs right before the LLM call
# Used to modify final prompt sent to model
# ---------------------------------------------------
def model_filter(data: CallModelData) -> ModelInputData:

    print("\n===== CALL MODEL INPUT FILTER =====")
    print("Messages before filtering:", len(data.model_data.input))

    # Trim again (example logic)
    filtered_input = data.model_data.input[-3:]

    print("Messages sent to model:", len(filtered_input))

    # Example: inject dynamic instruction
    new_instructions = (
        data.model_data.instructions +
        "\nAlways answer in one short sentence."
    )

    return ModelInputData(
        input=filtered_input,
        instructions=new_instructions
    )
#--------------------------------------------------------------------------------------------------
#User message
#      ↓
#Session loads old conversation
#      ↓
#session_input_callback runs
#      ↓
#Agent instructions + tools added
#      ↓
#call_model_input_filter runs
#      ↓
#Final prompt sent to LLM

# ---------------------------------------------------
# MAIN TEST
# ---------------------------------------------------
async def main():

    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant.",
        model="gpt-4o-mini"
    )

    # Session stores conversation history
    session = SQLiteSession("demo_session")

    config = RunConfig(
        session_input_callback=session_callback,
        call_model_input_filter=model_filter
    )

    print("\n=== TURN 1 ===")

    result = await Runner.run(
        agent,
        "What is the capital of France?",
        session=session,
        run_config=config
    )

    print("Agent:", result.final_output)

    print("\n=== TURN 2 ===")

    result = await Runner.run(
        agent,
        "What country is it in?",
        session=session,
        run_config=config
    )

    print("Agent:", result.final_output)

    print("\n=== TURN 3 ===")

    result = await Runner.run(
        agent,
        "What is its population?",
        session=session,
        run_config=config
    )

    print("Agent:", result.final_output)

    print("\n=== TURN 4 ===")

    result = await Runner.run(
        agent,
        "Tell me something famous about it.",
        session=session,
        run_config=config
    )

    print("Agent:", result.final_output)


# Run async program
asyncio.run(main())

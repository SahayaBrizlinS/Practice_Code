import asyncio
from dotenv import load_dotenv

from agents import Agent, Runner, SQLiteSession

# -----------------------------------------------------
# Load API key from .env file
# -----------------------------------------------------
load_dotenv()


async def main():

    # -----------------------------------------------------
    # Create Agent
    # -----------------------------------------------------
    agent = Agent(
        name="Assistant",
        instructions="Reply concisely.",
        model="gpt-4o-mini"
    )

    # -----------------------------------------------------
    # Create SQLite session
    # This creates/uses a database file to store conversation
    # -----------------------------------------------------
    session = SQLiteSession(
        "demo_user",              # unique session ID
        "conversation_demo.db"    # database file
    )


    # =====================================================
    # 1️⃣ add_items()  → manually insert conversation history
    # =====================================================

    print("\n--- Manually inserting conversation history ---")

    # We manually insert messages into the session
    # This simulates an already existing conversation
    await session.add_items([
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ])

    print("Manual messages inserted into session.")


    # =====================================================
    # 2️⃣ get_items() → read the session memory
    # =====================================================

    print("\n--- Reading session memory using get_items() ---")

    items = await session.get_items()

    # This returns all stored conversation messages
    for item in items:
        print(item)

    # Useful for debugging or displaying chat history


    # =====================================================
    # 3️⃣ Runner.run() → agent continues conversation
    # =====================================================

    print("\n--- Running agent with stored session history ---")

    result = await Runner.run(
        agent,
        "What did I say first?",
        session=session
    )

    print("Agent:", result.final_output)

    # The agent knows the first message was "Hello"
    # because we inserted it manually using add_items()


    # =====================================================
    # 4️⃣ pop_item() → remove the most recent message
    # =====================================================

    print("\n--- Removing last message using pop_item() ---")

    last_item = await session.pop_item()

    print("Removed item:", last_item)

    # pop_item removes the most recent message
    # This is useful for undo functionality


    # =====================================================
    # Verify session after pop_item()
    # =====================================================

    print("\n--- Session memory after pop_item() ---")

    items = await session.get_items()

    for item in items:
        print(item)


    # =====================================================
    # Example: Undo entire previous conversation
    # =====================================================

    print("\n--- Undoing previous user question and assistant reply ---")

    await session.pop_item()
    await session.pop_item()

    print("Two items removed (undo operation).")

    items = await session.get_items()

    print("Current session memory:", items)


    # =====================================================
    # 5️⃣ clear_session() → delete entire conversation
    # =====================================================

    print("\n--- Clearing entire session ---")

    await session.clear_session()

    print("Session cleared.")


    # =====================================================
    # Verify session is empty
    # =====================================================

    items = await session.get_items()

    print("\nSession memory after clear_session():", items)


# Run program
asyncio.run(main())

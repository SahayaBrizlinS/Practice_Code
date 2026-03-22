import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner

# ---------------------------------------------------------
# Load environment variables (.env file should contain API key)
# ---------------------------------------------------------
load_dotenv()


async def main():

    # ---------------------------------------------------------
    # Agent Definition
    # ---------------------------------------------------------
    agent = Agent(
        name="Assistant",
        instructions="Reply concisely.",
        model="gpt-4o-mini"
    )

    # ---------------------------------------------------------
    # This variable stores ONLY the last response ID.
    #
    # IMPORTANT:
    # The actual conversation history is NOT stored in our program.
    # It is stored on OpenAI's cloud servers.
    #
    # previous_response_id acts like a POINTER to that history.
    # ---------------------------------------------------------
    previous_response_id = None

    while True:

        # ---------------------------------------------------------
        # User input (one turn of conversation)
        # ---------------------------------------------------------
        user_input = input("You: ")

        # Exit condition
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Agent: Goodbye!")
            break

        # ---------------------------------------------------------
        # Runner.run() sends the request to OpenAI servers.
        #
        # We pass previous_response_id so OpenAI can find the
        # previous conversation and continue it.
        #
        # Only the LAST response ID is passed, but OpenAI can
        # reconstruct the ENTIRE conversation chain internally.
        #
        # Example internal chain on OpenAI server:
        #
        # r1 → r2 → r3 → r4
        #
        # Passing r4 allows OpenAI to load:
        # r1 + r2 + r3 + r4
        #
        # That means the model still understands references
        # to earlier messages.
        # ---------------------------------------------------------
        result = await Runner.run(
            agent,
            user_input,
            
            # previous_response_id links the new request to the previous response
            # so the conversation can continue using server-managed history.

            previous_response_id=previous_response_id,
            
            # auto_previous_response_id=True automatically handles the first turn
            # of the conversation when previous_response_id is None.
            #
            # Behavior:
            # - If previous_response_id is None → a new conversation starts.
            # - If previous_response_id exists → the request is chained to the
            #   previous response and the conversation continues.
            #
            # This removes the need for manual checks to determine whether the
            # current request is the first message or a continuation.
            auto_previous_response_id=True
        )

        # ---------------------------------------------------------
        # Save the new response ID.
        #
        # This ID points to the entire conversation chain stored
        # on OpenAI servers.
        #
        # If we restart the program and reuse this ID,
        # the conversation can continue.
        #
        # If we lose this ID, the conversation cannot be resumed.
        # ---------------------------------------------------------
        previous_response_id = result.last_response_id

        # ---------------------------------------------------------
        # Print agent reply
        # ---------------------------------------------------------
        print("Agent:", result.final_output)


# ---------------------------------------------------------
# Event loop runs the async program
# ---------------------------------------------------------
asyncio.run(main())

# ---------------------------------------------------------
# If a server-managed conversation is unused for some period of time, 
# OpenAI may automatically delete it from the cloud.
# This is temporary solution to store the conversation in cloud (Client side Server) database.
# ---------------------------------------------------------
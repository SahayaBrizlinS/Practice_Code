import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner

# Load .env file
load_dotenv()

async def main():

    agent = Agent(
        name="Assistant",
        instructions="Reply very concisely.",
        model="gpt-4o-mini"
    )

    # ---- Turn 1 ----
    result = await Runner.run(
        agent,
        "What city is the Golden Gate Bridge in?"
    )

    print("Turn 1:", result.final_output)

    # ---- Turn 2 (manual history) ----
    new_input = result.to_input_list() + [
        {"role": "user", "content": "What state is it in?"}
    ]
    #--------------------------------------------------------------------------------------------------
    # ----- We can manually update it in database like postgres, mysql, etc. Full Control Over it. ---Database Management System (DBMS)
    # We can limit the history length like 1000 messages, 500 messages, etc.
    #--------------------------------------------------------------------------------------------------
    result = await Runner.run(agent, new_input)

    print("Turn 2:", result.final_output)


asyncio.run(main())

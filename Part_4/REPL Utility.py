import asyncio
from agents import Agent, run_demo_loop
from dotenv import load_dotenv

load_dotenv(override=True)

async def main():
    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant."
    )

    # Starts interactive chat in terminal
    await run_demo_loop(agent)


if __name__ == "__main__":
    asyncio.run(main())

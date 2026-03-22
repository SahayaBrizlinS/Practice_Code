import asyncio
from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv(override=True)

def dynamic_instructions(ctx, agent):
    user = ctx.context
    return f"You are helping {user}. Give short answers."

agent = Agent(
    name="Assistant",
    instructions=dynamic_instructions,
    model="gpt-4o-mini",
)

async def main():
    result = await Runner.run(
        agent,
        "Give me study tips",
        context="Arun"
    )

    print(result.final_output)

asyncio.run(main())

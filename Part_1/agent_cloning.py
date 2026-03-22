import asyncio
from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv(override=True)

pirate = Agent(
    name="Pirate",
    instructions="Speak like a pirate.",
    model="gpt-4o-mini"
)

robot = pirate.clone(
    name="Robot",
    instructions="Speak like a robot."
)

async def main():

    r1 = await Runner.run(pirate, "Say hello")
    r2 = await Runner.run(robot, "Say hello")

    print("Pirate:", r1.final_output)
    print("Robot:", r2.final_output)

asyncio.run(main())

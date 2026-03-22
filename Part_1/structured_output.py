import asyncio
from pydantic import BaseModel
from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv(override=True)

class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

agent = Agent(
    name="EventExtractor",
    instructions="Extract event details from text.",
    model="gpt-4o-mini",
    output_type=CalendarEvent
)

async def main():
    result = await Runner.run(
        agent,
        "Project meeting Friday 9am with Alice and Bob"
    )

    event = result.final_output
    print(event.name)
    print(event.date)
    print(event.participants)

asyncio.run(main())

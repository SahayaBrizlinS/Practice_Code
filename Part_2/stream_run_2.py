import asyncio
from agents import Agent, Runner
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
load_dotenv()

agent = Agent(
    name="StoryWriter",
    instructions="Write creatively.",
    model="gpt-4o-mini"
)

async def main():

    print("\nSTREAMING OUTPUT:\n")

    result = Runner.run_streamed(
        agent,
        "Write a short story about a robot learning Python."
    )

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)

    print("\n\nFinal Output:\n")
    print(result.final_output)


asyncio.run(main())
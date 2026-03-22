import asyncio
from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv(override=True)

# -----------------------------
# Specialist Agents
# -----------------------------

flight_agent = Agent(
    name="FlightAgent",
    instructions="""
You help users with flight related questions such as booking flights,
flight duration, and airline suggestions.
""",
    model="gpt-4o-mini"
)

hotel_agent = Agent(
    name="HotelAgent",
    instructions="""
You help users find hotels, accommodation, and stay options.
""",
    model="gpt-4o-mini"
)

tour_agent = Agent(
    name="TourGuideAgent",
    instructions="""
You recommend tourist attractions, sightseeing places, and travel activities.
""",
    model="gpt-4o-mini"
)

# -----------------------------
# Router / Triage Agent
# -----------------------------

router_agent = Agent(
    name="TravelRouter",
    instructions="""
You are a routing agent.

Your job is to transfer the user request to the correct specialist.

Rules:
- Flight related questions → FlightAgent
- Hotel or stay questions → HotelAgent
- Tourist places or sightseeing → TourGuideAgent

Do not answer yourself. Always hand off to the correct agent.
""",
    model="gpt-4o-mini",
    handoffs=[flight_agent, hotel_agent, tour_agent]
)

# -----------------------------
# Run Example
# -----------------------------

async def main():

    question = "Suggest some tourist places to visit in Tokyo"

    result = await Runner.run(router_agent, question)

    print("\nFinal Answer:\n")
    print(result.final_output)


asyncio.run(main())

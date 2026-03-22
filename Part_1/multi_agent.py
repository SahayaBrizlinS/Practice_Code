import asyncio
from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv(override=True)
# -----------------------------
# Specialist Agents
# -----------------------------

booking_agent = Agent(
    name="BookingAgent",
    instructions="Handle flight or hotel booking questions.",
    model="gpt-4o-mini"
)

refund_agent = Agent(
    name="RefundAgent",
    instructions="Handle refund related questions.",
    model="gpt-4o-mini"
)

# -----------------------------
# Manager Agent
# -----------------------------

manager = Agent(
    name="CustomerSupport",
    instructions="Help users and delegate tasks to the correct specialist.",
    model="gpt-4o-mini",
    tools=[
        booking_agent.as_tool(
            tool_name="booking_expert",
            tool_description="Use for booking related queries."
        ),
        refund_agent.as_tool(
            tool_name="refund_expert",
            tool_description="Use for refund related queries."
        ),
    ],
)

# -----------------------------
# Run
# -----------------------------

async def main():

    result = await Runner.run(
        manager,
        "I want to book a flight to Tokyo"
    )

    print("\nFinal Response:")
    print(result.final_output)


asyncio.run(main())

import asyncio
from agents import Agent, Runner, AgentHooks, function_tool
from dotenv import load_dotenv

load_dotenv(override=True)

# -----------------------------
# Tool
# -----------------------------

@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."


# -----------------------------
# Hooks
# -----------------------------

class MyHooks(AgentHooks):

    async def on_start(self, ctx, agent):
        print(f"\n[HOOK] Agent started: {agent.name}")

    async def on_tool_start(self, ctx, agent, tool):
        print(f"[HOOK] Tool about to run: {tool.name}")

    async def on_tool_end(self, ctx, agent, tool, result):
        print(f"[HOOK] Tool finished: {tool.name}")
        print(f"[HOOK] Tool result: {result}")

    async def on_end(self, ctx, agent, output):
        print(f"[HOOK] Agent finished: {agent.name}")
        print(f"[HOOK] Final output: {output}")


# -----------------------------
# Agent
# -----------------------------

agent = Agent(
    name="WeatherAgent",
    instructions="Use the weather tool if someone asks about weather.",
    model="gpt-4o-mini",
    tools=[get_weather],
    hooks=MyHooks()
)


# -----------------------------
# Run
# -----------------------------

async def main():

    result = await Runner.run(
        agent,
        "What is the weather in Tokyo?"
    )

    print("\nUser Response:")
    print(result.final_output)


asyncio.run(main())

import asyncio
from agents import (
    Agent,
    ModelSettings,
    function_tool,
    Runner,
    StopAtTools,
    ToolsToFinalOutputResult
)
from dotenv import load_dotenv

load_dotenv(override=True)

# -------- TOOL 1 --------
@function_tool
def get_weather(city: str) -> str:
    """Returns weather for a city."""
    print(f"[TOOL CALLED] get_weather({city})")
    return f"Sunny in {city}"


# -------- TOOL 2 --------
@function_tool
def get_clothing_advice(weather: str) -> str:
    """Suggest clothing based on weather."""
    print(f"[TOOL CALLED] get_clothing_advice({weather})")

    if "sunny" in weather.lower():
        return "Wear sunglasses, t-shirt and stay hydrated."
    else:
        return "Carry a jacket."


# -------- AGENT 1 --------
# Stops immediately after first tool
agent1 = Agent(
    name="Stop First Tool Agent",
    instructions="Check weather and optionally suggest clothing.",
    model="gpt-4o-mini",
    tools=[get_weather, get_clothing_advice],
    tool_use_behavior="stop_on_first_tool",
    model_settings=ModelSettings(tool_choice="auto"),
)

# -------- AGENT 2 --------
# Stops only when weather tool runs
agent2 = Agent(
    name="StopAtTools Agent",
    instructions="Check weather and optionally suggest clothing.",
    model="gpt-4o-mini",
    tools=[get_weather, get_clothing_advice],
    tool_use_behavior=StopAtTools(stop_at_tool_names=["get_weather"]),
    model_settings=ModelSettings(tool_choice="auto"),
)

# -------- AGENT 3 --------
# Custom handler
def my_handler(context, results):
    print("[CUSTOM HANDLER] Tool output:", results[0].output)

    if "Sunny" in results[0].output:
        return ToolsToFinalOutputResult(
            is_final_output=False,  # allow agent to continue
            final_output=None
        )

    return ToolsToFinalOutputResult(
        is_final_output=True,
        final_output=results[0].output
    )


agent3 = Agent(
    name="Custom Handler Agent",
    instructions="Check weather then suggest clothing.",
    model="gpt-4o-mini",
    tools=[get_weather, get_clothing_advice],
    tool_use_behavior=my_handler,
    model_settings=ModelSettings(tool_choice="auto"),
)


# -------- RUN TEST --------
async def main():

    question = "What's the weather in Tokyo and what should I wear?"

    print("\n===== Agent 1: stop_on_first_tool =====")
    r1 = await Runner.run(agent1, question)
    print("Final Output:", r1.final_output)

    print("\n===== Agent 2: StopAtTools(get_weather) =====")
    r2 = await Runner.run(agent2, question)
    print("Final Output:", r2.final_output)

    print("\n===== Agent 3: Custom Handler =====")
    r3 = await Runner.run(agent3, question)
    print("Final Output:", r3.final_output)


asyncio.run(main())

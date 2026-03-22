from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

load_dotenv()

# ---------------- TOOL ----------------

@function_tool
def get_weather(city: str) -> str:
    print(f"[TOOL EXECUTED] get_weather({city})")
    return f"The weather in {city} is sunny."

# ---------------- AGENT ----------------

agent = Agent(
    name="WeatherAssistant",
    instructions="Use the weather tool if user asks about weather.",
    model="gpt-4o-mini",
    tools=[get_weather],
)

# ---------------- RUN ----------------

print("\nSYNC RUN (Runner.run_sync)\n")

result = Runner.run_sync(
    agent,
    "What is the weather in Paris?"
)

print("\nFinal Output:")
print(result.final_output)

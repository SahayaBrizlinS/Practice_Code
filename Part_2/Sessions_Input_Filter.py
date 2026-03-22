from dotenv import load_dotenv
from agents import Agent, Runner, RunConfig, SQLiteSession
from agents.run import CallModelData, ModelInputData

load_dotenv()

def keep_last_3(data: CallModelData) -> ModelInputData:
    trimmed = data.model_data.input[-3:]
    print("FILTER: trimming session history to last 3 messages")
    return ModelInputData(
        input=trimmed,
        instructions=data.model_data.instructions
    )

agent = Agent(
    name="Assistant",
    instructions="Reply briefly.",
    model="gpt-4o-mini"
)

session = SQLiteSession("demo_session")

while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    result = Runner.run_sync(
        agent,
        user_input,
        session=session,
        run_config=RunConfig(call_model_input_filter=keep_last_3)
    )

    print("Agent:", result.final_output)

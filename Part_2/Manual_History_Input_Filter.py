from dotenv import load_dotenv
from agents import Agent, Runner, RunConfig
from agents.run import CallModelData, ModelInputData

load_dotenv()

# -------- INPUT FILTER --------
def keep_last_3(data: CallModelData) -> ModelInputData:
    trimmed = data.model_data.input[-3:]
    print("FILTER: sending only last 3 messages to LLM")
    return ModelInputData(
        input=trimmed,
        instructions=data.model_data.instructions
    )

agent = Agent(
    name="Assistant",
    instructions="Reply briefly.",
    model="gpt-4o-mini"
)

history = []

while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    history.append({"role": "user", "content": user_input})

    result = Runner.run_sync(
        agent,
        history,
        run_config=RunConfig(call_model_input_filter=keep_last_3)
    )

    print("Agent:", result.final_output)

    history = result.to_input_list()

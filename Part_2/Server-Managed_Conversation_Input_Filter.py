import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, RunConfig
from agents.run import CallModelData, ModelInputData

load_dotenv()

def keep_last_3(data: CallModelData) -> ModelInputData:
    trimmed = data.model_data.input[-3:]
    print("FILTER: limiting server conversation to last 3 messages")
    return ModelInputData(
        input=trimmed,
        instructions=data.model_data.instructions
    )

async def main():

    agent = Agent(
        name="Assistant",
        instructions="Reply briefly.",
        model="gpt-4o-mini"
    )

    previous_response_id = None

    while True:

        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        result = await Runner.run(
            agent,
            user_input,
            previous_response_id=previous_response_id,
            auto_previous_response_id=True,
            run_config=RunConfig(call_model_input_filter=keep_last_3)
        )

        previous_response_id = result.last_response_id

        print("Agent:", result.final_output)

asyncio.run(main())

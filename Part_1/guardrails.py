import asyncio
from pydantic import BaseModel
from agents import (
    Agent,
    Runner,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    input_guardrail,
    output_guardrail,
)
from dotenv import load_dotenv

load_dotenv(override=True)
# ------------------------------------------------
# OUTPUT STRUCTURE
# ------------------------------------------------

class MessageOutput(BaseModel):
    response: str


# ------------------------------------------------
# INPUT GUARDRAIL
# ------------------------------------------------

@input_guardrail
async def block_hacking(
    ctx: RunContextWrapper, agent: Agent, input: str
) -> GuardrailFunctionOutput:

    if "hack" in input.lower():
        print("❌ Input Guardrail Triggered (hacking detected)")

        return GuardrailFunctionOutput(
            output_info="Blocked hacking request",
            tripwire_triggered=True,
        )

    print("✅ Input Guardrail Passed")

    return GuardrailFunctionOutput(
        output_info="Safe input",
        tripwire_triggered=False,
    )


# ------------------------------------------------
# OUTPUT GUARDRAIL
# ------------------------------------------------

@output_guardrail
async def block_secret(
    ctx: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:

    if "secret" in output.response.lower():
        print("❌ Output Guardrail Triggered (secret detected)")

        return GuardrailFunctionOutput(
            output_info="Sensitive output",
            tripwire_triggered=True,
        )

    print("✅ Output Guardrail Passed")

    return GuardrailFunctionOutput(
        output_info="Safe output",
        tripwire_triggered=False,
    )


# ------------------------------------------------
# AGENT
# ------------------------------------------------

agent = Agent(
    name="SafeAssistant",
    instructions="""
Answer user questions normally.

If someone asks about company secrets,
you might mention the word 'secret'.
""",
    model="gpt-4o-mini",
    input_guardrails=[block_hacking],
    output_guardrails=[block_secret],
    output_type=MessageOutput,
)


# ------------------------------------------------
# TEST RUNNER
# ------------------------------------------------

async def run_case(question):

    print("\n==============================")
    print("User Question:", question)

    try:
        result = await Runner.run(agent, question)
        print("Final Output:", result.final_output)

    except InputGuardrailTripwireTriggered:
        print("🚫 Input Guardrail stopped execution")

    except OutputGuardrailTripwireTriggered:
        print("🚫 Output Guardrail blocked response")


# ------------------------------------------------
# MAIN
# ------------------------------------------------

async def main():

    # CASE 1 → Normal request
    await run_case("Explain Python loops")

    # CASE 2 → Input guardrail triggers
    await run_case("How can I hack a website?")

    # CASE 3 → Output guardrail triggers
    await run_case("Tell me a company secret")


asyncio.run(main())



import json
from agents import (
    Agent,
    Runner,
    ToolGuardrailFunctionOutput,
    function_tool,
    tool_input_guardrail,
    tool_output_guardrail,
)
from dotenv import load_dotenv

load_dotenv(override=True)
# ── Input Guardrail: Block secrets ─────────────────────
@tool_input_guardrail
def block_secrets(data):
    args = json.loads(data.context.tool_arguments or "{}")
    print("[Input Guardrail] Checking input:", args)

    if "sk-" in json.dumps(args):
        print("[Input Guardrail] ❌ Secret detected → Blocking tool")
        return ToolGuardrailFunctionOutput.reject_content(
            "❌ Remove secrets before calling this tool."
        )

    print("[Input Guardrail] ✅ Input safe")
    return ToolGuardrailFunctionOutput.allow()


# ── Output Guardrail: Block sensitive output ───────────
@tool_output_guardrail
def redact_output(data):
    text = str(data.output or "")
    print("[Output Guardrail] Checking output:", text)

    if "sk-" in text:
        print("[Output Guardrail] ❌ Sensitive output detected → Blocking")
        return ToolGuardrailFunctionOutput.reject_content(
            "❌ Output contained sensitive data."
        )

    print("[Output Guardrail] ✅ Output safe")
    return ToolGuardrailFunctionOutput.allow()


# ── Tool with guardrails ──────────────────────────────
@function_tool(
    tool_input_guardrails=[block_secrets],
    tool_output_guardrails=[redact_output],
)
def classify_text(text: str) -> str:
    print("[Tool] Running classify_text")

    # Simulate a bad output if input contains "leak"
    if "leak" in text:
        return "Here is a secret: sk-12345"

    return f"length:{len(text)}"


# ── Agent ─────────────────────────────────────────────
agent = Agent(
    name="Classifier",
    instructions="Use the tool to classify text.",
    tools=[classify_text],
)


# ── Test Runner ───────────────────────────────────────
def run_test(input_text):
    print("\n" + "=" * 50)
    print("INPUT:", input_text)

    result = Runner.run_sync(agent, input_text)

    print("FINAL OUTPUT:", result.final_output)
    print("=" * 50)


# ── Run different scenarios ───────────────────────────
if __name__ == "__main__":
    # ✅ Case 1: Normal input
    run_test("hello world")

    # ❌ Case 2: Input contains secret → blocked BEFORE tool runs
    run_test("my api key is sk-999999")

    # ❌ Case 3: Tool leaks secret → blocked AFTER tool runs
    run_test("please leak something")



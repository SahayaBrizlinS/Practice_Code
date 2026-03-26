import asyncio
import json
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 🔹 TOOLS (both require approval)
# ============================================================
@function_tool(needs_approval=True)
async def delete_file(filename: str) -> str:
    return f"Deleted file: {filename}"


@function_tool(needs_approval=True)
async def send_email(message: str) -> str:
    return f"Email sent: {message}"


# ============================================================
# 🔹 AGENTS
# ============================================================

# 🟢 CASE 1: Batch Planning Agent
batch_agent = Agent(
    name="Batch Agent",
    instructions="""
    When user asks multiple actions, CALL ALL TOOLS TOGETHER.
    Example:
    If user says delete and email → call both tools in same response.
    """,
    tools=[delete_file, send_email],
)

# 🔴 CASE 2: Step-by-Step Agent
step_agent = Agent(
    name="Step Agent",
    instructions="""
    Always do ONE step at a time.

    First call delete_file.
    After that completes, THEN call send_email.
    """,
    tools=[delete_file, send_email],
)


# ============================================================
# 🔹 APPROVAL FUNCTION
# ============================================================
def ask_user(tool_name, args):
    if isinstance(args, str):
        args = json.loads(args)

    print(f"\n⚠️ Tool: {tool_name}")
    print(f"Args: {args}")

    choice = input("Approve? (y/n): ").strip().lower()
    return choice == "y"


# ============================================================
# 🔹 HITL HANDLER
# ============================================================
async def handle_interruptions(agent, result):
    step = 1

    while result.interruptions:
        print(f"\n⏸ INTERRUPTION ROUND {step}")

        state = result.to_state()

        for interruption in result.interruptions:
            approved = ask_user(interruption.name, interruption.arguments)

            if approved:
                state.approve(interruption)
            else:
                state.reject(interruption)
                print("❌ Stopped")
                return None

        result = await Runner.run(agent, state)
        step += 1

    return result


# ============================================================
# 🔹 MAIN TEST
# ============================================================
async def main():
    print("\nChoose mode:")
    print("1 → Batch planning (both tools together)")
    print("2 → Step-by-step planning")

    choice = input("Enter choice: ").strip()

    user_query = "Delete file data.db and send email 'done'"

    if choice == "1":
        agent = batch_agent
        print("\n🟢 Running BATCH mode")
    else:
        agent = step_agent
        print("\n🔴 Running STEP-BY-STEP mode")

    print("\nUser Query:", user_query)

    result = await Runner.run(agent, user_query)

    result = await handle_interruptions(agent, result)

    if result:
        print("\n✅ Final Output:")
        print(result.final_output)


# ============================================================
# 🔹 RUN
# ============================================================
asyncio.run(main())

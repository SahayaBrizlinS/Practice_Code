import asyncio
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

load_dotenv()
# ============================================================
# 🔹 TOOL (HITL TRIGGER)
# ============================================================

@function_tool(needs_approval=True)
async def dangerous_delete(filename: str) -> str:
    print("⚙️ Tool is executing inside Agent C...")
    return f"Deleted file: {filename}"

# ============================================================
# 🔹 AGENT C (FINAL EXECUTOR)
# ============================================================

agent_c = Agent(
    name="Agent C",
    instructions="""
    You are a file deletion agent.

    RULES:
    - ALWAYS use the tool to delete files
    - NEVER explain
    - NEVER respond with text
    - ALWAYS call the tool directly
    """,
    tools=[dangerous_delete],
)

# ============================================================
# 🔹 AGENT B (MIDDLE → MUST HANDOFF)
# ============================================================

agent_b = Agent(
    name="Agent B",
    instructions="""
    You are a routing agent.

    RULES:
    - If request is about deleting files:
        → IMMEDIATELY handoff to Agent C
    - DO NOT explain anything
    - DO NOT respond with text
    """,
    handoffs=[agent_c],
)

# ============================================================
# 🔹 AGENT A (MAIN AGENT)
# ============================================================

agent_a = Agent(
    name="Agent A",
    instructions="""
    You are the main controller.

    RULES:
    - If request involves file deletion:
        → IMMEDIATELY handoff to Agent B
    - DO NOT explain
    - DO NOT respond with text
    """,
    handoffs=[agent_b],
)

# ============================================================
# 🔹 APPROVAL FUNCTION
# ============================================================

def ask_user(interruption):
    print("\n⏸ INTERRUPTED!")
    
    # Safe printing
    print(f"Tool: {interruption.name}")
    print(f"Args: {interruption.arguments}")

    choice = input("Approve? (y/n): ").strip().lower()
    return choice == "y"

# ============================================================
# 🔹 MAIN EXECUTION
# ============================================================

async def main():
    user_input = input("Enter request: ")

    # 👉 ALWAYS start with MAIN agent
    result = await Runner.run(agent_a, user_input)

    # 👉 Handle interruptions (no matter how deep)
    while result.interruptions:
        state = result.to_state()

        for interruption in result.interruptions:
            approved = ask_user(interruption)

            if approved:
                state.approve(interruption)
            else:
                state.reject(interruption)

        # 👉 ALWAYS resume with MAIN agent
        result = await Runner.run(agent_a, state)

    print("\n✅ Final Output:")
    print(result.final_output)


# ============================================================
# 🔹 RUN
# ============================================================

asyncio.run(main())

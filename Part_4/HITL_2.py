import asyncio
import json
from pathlib import Path
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 📁 MEMORY FILE (to remember approvals)
# ============================================================
MEMORY_FILE = Path("approvals.json")


def load_memory():
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text())
    return {}


def save_memory(data):
    MEMORY_FILE.write_text(json.dumps(data, indent=2))


# ============================================================
# 🔹 TOOL 1: APPROVAL CHECKPOINT (HITL)
# ============================================================
@function_tool(needs_approval=True)
async def approval_checkpoint(reason: str) -> str:
    return f"Approved: {reason}"


# ============================================================
# 🔹 TOOL 2: DELETE FILE
# ============================================================
@function_tool
async def delete_file(filename: str) -> str:
    return f"Deleted file: {filename}"


# ============================================================
# 🔹 AGENT
# ============================================================
agent = Agent(
    name="File Assistant",
    instructions="""
    You can:
    - call approval_checkpoint when asked
    - delete files when asked
    """,
    tools=[approval_checkpoint, delete_file],
)


# ============================================================
# 🔹 HUMAN APPROVAL FUNCTION
# ============================================================
def ask_user(tool_name, args):
    if isinstance(args, str):
        args = json.loads(args)

    print(f"\n⚠️ Tool wants to run: {tool_name}")
    print(f"Arguments: {args}")

    choice = input("Approve? (y/n): ").strip().lower()
    return choice == "y"


# ============================================================
# 🔹 HITL HANDLER (CORE ENGINE)
# ============================================================
async def handle_interruptions(result):
    while result.interruptions:
        print("\n⏸ INTERRUPTION DETECTED")

        state = result.to_state()   # 🔥 VERY IMPORTANT

        for interruption in result.interruptions:
            approved = ask_user(interruption.name, interruption.arguments)

            if approved:
                state.approve(interruption)
            else:
                state.reject(interruption)
                print("❌ Process stopped")
                return None

        result = await Runner.run(agent, state)

    return result


# ============================================================
# 🔹 MAIN FLOW (FULL CONTROL LOGIC)
# ============================================================
async def main():
    user_input = input("Enter request: ")

    memory = load_memory()

    # --------------------------------------------------------
    # 🔥 STEP 1: EXTRACT FILENAME (simple logic)
    # --------------------------------------------------------
    if "delete file" in user_input.lower():
        filename = user_input.lower().replace("delete file", "").strip()
    else:
        print("❌ Unsupported request")
        return

    key = f"delete:{filename}"

    # --------------------------------------------------------
    # 🔥 STEP 2: PYTHON RISK LOGIC (FULL CONTROL)
    # --------------------------------------------------------
    risky = filename.endswith(".db")

    # --------------------------------------------------------
    # 🔥 STEP 3: CHECK MEMORY (AUTO APPROVAL)
    # --------------------------------------------------------
    if memory.get(key):
        print("✅ Already approved before. Skipping HITL.")
    else:
        if risky:
            print("\n🚨 Risk detected → Approval required")

            # 🔥 MANUAL TOOL TRIGGER (MID-FLOW)
            result = await Runner.run(
                agent,
                f"Call approval_checkpoint for deleting {filename}"
            )

            result = await handle_interruptions(result)

            if result is None:
                return

            # 💾 Save approval
            memory[key] = True
            save_memory(memory)
            print("💾 Approval saved for future")

    # --------------------------------------------------------
    # 🔥 STEP 4: EXECUTE REAL TOOL
    # --------------------------------------------------------
    print("\n⚙️ Executing delete operation...")

    result = await Runner.run(
        agent,
        f"Delete file {filename}"
    )

    result = await handle_interruptions(result)

    print("\n✅ Final Output:")
    print(result.final_output)


# ============================================================
# 🔹 RUN
# ============================================================
asyncio.run(main())

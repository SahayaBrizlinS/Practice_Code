import asyncio
import json
from agents import Agent, Runner, function_tool
from agents.extensions.memory import SQLAlchemySession
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 🔹 SESSION (PostgreSQL)
# ============================================================
session = SQLAlchemySession.from_url(
    "user-123",   # session id
    url="postgresql+asyncpg://postgres:postgres@localhost:5432/SDKdb",
    create_tables=True
)

# ============================================================
# 🔹 TOOLS
# ============================================================
@function_tool(needs_approval=True)
async def validate_category(category: str) -> str:
    return f"Validated category: {category}"


@function_tool
async def process_request(category: str) -> str:
    return f"Processed request with category: {category}"


# ============================================================
# 🔹 AGENT
# ============================================================
agent = Agent(
    name="Smart Assistant",
    instructions="""
    Step 1: Categorize the request.

    Step 2: Call validate_category.

    Step 3: Call process_request.

    IMPORTANT:
    If category is already provided, skip categorization.
    """,
    tools=[validate_category, process_request],
)

# ============================================================
# 🔹 HUMAN INPUT
# ============================================================
def ask_user(interruption):
    args = interruption.arguments

    if isinstance(args, str):
        args = json.loads(args)

    category = args.get("category")

    print("\n🤖 Suggested category:", category)

    print("1 → Approve")
    print("2 → Edit")
    print("3 → Reject")

    choice = input("Choose: ").strip()

    if choice == "1":
        return "approve", category
    elif choice == "2":
        new_cat = input("Enter new category: ")
        return "edit", new_cat
    else:
        return "reject", None


# ============================================================
# 🔹 HITL HANDLER
# ============================================================
async def handle_interruptions(result):
    while result.interruptions:
        state = result.to_state()

        print("\n💾 State automatically stored in session DB")

        for interruption in result.interruptions:
            action, value = ask_user(interruption)

            if action == "approve":
                state.approve(interruption)

            elif action == "edit":
                print("\n✏️ Restarting with corrected category...\n")

                return await Runner.run(
                    agent,
                    f"""
                    Final category: {value}

                    IMPORTANT:
                    Skip categorization and directly process request.
                    """,
                    session=session
                )

            else:
                state.reject(interruption)
                print("❌ Rejected")
                return None

        result = await Runner.run(agent, state, session=session)

    return result


# ============================================================
# 🔹 MAIN
# ============================================================
async def main():
    print("\n🔁 This session persists automatically in PostgreSQL")

    user_input = input("Enter request: ")

    # 🔥 Run with session
    result = await Runner.run(agent, user_input, session=session)

    result = await handle_interruptions(result)

    if result:
        print("\n✅ Final Output:")
        print(result.final_output)
    else:
        print("\n❌ No output")


# ============================================================
# RUN
# ============================================================
asyncio.run(main())

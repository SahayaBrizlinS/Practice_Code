import asyncio
from agents import Agent, Runner
from agents.extensions.memory import AdvancedSQLiteSession
from dotenv import load_dotenv

load_dotenv(override=True)
# -----------------------------
# 🔹 SETUP SESSION
# -----------------------------
session = AdvancedSQLiteSession(
    session_id="demo_conversation",
    db_path="conversations.db",
    create_tables=True
)

# -----------------------------
# 🔹 CREATE AGENT
# -----------------------------
agent = Agent(
    name="Assistant",
    instructions="Reply concisely and clearly."
)

# -----------------------------
# 🔹 HELPER FUNCTION (LOGGING)
# -----------------------------
async def run_and_log(user_input: str):
    print(f"\n🧑 USER: {user_input}")

    result = await Runner.run(agent, user_input, session=session)

    print(f"🤖 AI: {result.final_output}")

    # IMPORTANT → store usage
    await session.store_run_usage(result)

    return result


# -----------------------------
# 🔹 MAIN DEMO FLOW
# -----------------------------
async def main():

    print("\n================= START DEMO =================")

    # -------------------------
    # 1. BASIC CONVERSATION
    # -------------------------
    await run_and_log("What is the capital of France?")
    await run_and_log("What is the weather there?")
    await run_and_log("Tell me something interesting about it")

    # -------------------------
    # 2. USAGE TRACKING
    # -------------------------
    print("\n📊 USAGE STATS (SESSION LEVEL)")
    usage = await session.get_session_usage()

    print(f"Total tokens: {usage['total_tokens']}")
    print(f"Input tokens: {usage['input_tokens']}")
    print(f"Output tokens: {usage['output_tokens']}")
    print(f"Total turns: {usage['total_turns']}")

    print("\n📊 USAGE PER TURN")
    turns_usage = await session.get_turn_usage()
    for turn in turns_usage:
        print(f"Turn {turn['user_turn_number']} → {turn['total_tokens']} tokens")

    # -------------------------
    # 3. BRANCHING
    # -------------------------
    print("\n🌿 CREATING BRANCH FROM TURN 2")

    branch_id = await session.create_branch_from_turn(2, "tourist_branch")
    print(f"Created branch: {branch_id}")

    print("\n🌿 ASKING IN BRANCH")
    await run_and_log("What are the top tourist places there?")

    print("\n🌿 LIST ALL BRANCHES")
    branches = await session.list_branches()
    for b in branches:
        print(f"Branch: {b['branch_id']} | Turns: {b['user_turns']}")

    print("\n🌿 SWITCH BACK TO MAIN")
    await session.switch_to_branch("main")

    await run_and_log("What food is famous there?")

    # -------------------------
    # 4. STRUCTURED QUERIES
    # -------------------------
    print("\n🔍 FULL CONVERSATION (STRUCTURED)")
    conversation = await session.get_conversation_turns()

    for turn in conversation:
        print(f"Turn {turn['turn']} → {turn['content']}")

    print("\n🔍 SEARCH FOR 'weather'")
    matches = await session.find_turns_by_content("weather")
    for m in matches:
        print(f"Found in Turn {m['turn']}: {m['content']}")

    print("\n🔍 TOOL USAGE (if any)")
    tools = await session.get_tool_usage()
    for tool_name, count, turn in tools:
        print(f"{tool_name} used {count} times in turn {turn}")

    print("\n================= END DEMO =================")


# -----------------------------
# 🔹 RUN
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())

# =========================================================
# SESSION SETUP (AdvancedSQLiteSession)
# =========================================================
# This session object acts as a persistent memory layer for the agent.
# Instead of storing conversation in memory (temporary), it stores everything in a SQLite database file.
#
# session_id:
#   - Unique identifier for a conversation thread
#   - In production → this maps to chat_id / user_session_id
#   - Ensures conversations are isolated per user/session
#
# db_path:
#   - File where all conversation data is stored
#   - Internally stores:
#       → conversation messages (history)
#       → branches (multiple conversation paths)
#       → token usage per turn
#
# create_tables=True:
#   - Automatically creates required tables if they don't exist
#   - Useful for development
#   - In production → handled via migrations instead
#
# NOTE:
# This is a "stateful system" → conversation persists across runs
# =========================================================
# AGENT CONFIGURATION
# =========================================================
# Defines how the AI behaves.
#
# instructions:
#   - Acts like a system prompt
#   - Controls tone, style, and behavior of responses
#
# In production:
#   - Different agents may have different roles
#   - Example: support agent, coding assistant, sales assistant
# =========================================================
# CORE EXECUTION FUNCTION (run_and_log)
# =========================================================
# This function simulates one "chat turn"
#
# Flow:
#   1. Accept user input
#   2. Send it to the agent
#   3. Retrieve response
#   4. Store conversation in DB
#   5. Store token usage separately
#
# IMPORTANT:
# This is where the "memory system" interacts with the agent
# Runner.run(...) does the following internally:
#
#   1. Fetch previous conversation history from database
#   2. Combine history + new user input
#   3. Send full context to the LLM
#   4. Generate response
#   5. Store response back into database
#
# This is why the agent "remembers" past messages
# =========================================================
# TOKEN USAGE TRACKING (CRITICAL)
# =========================================================
# This explicitly stores token usage for the current run
#
# What gets stored:
#   - input tokens (user + context)
#   - output tokens (AI response)
#   - total tokens
#
# IMPORTANT:
#   - This is NOT automatic
#   - Must be called after every run
#
# If skipped:
#   ❌ No usage analytics
#   ❌ No cost tracking
#
# Production use:
#   - Billing users based on usage
#   - Monitoring API costs
#   - Detecting expensive prompts
# =========================================================
# BASIC CONVERSATION FLOW
# =========================================================
# Each call represents one "turn"
#
# A turn includes:
#   - user message
#   - AI response
#
# These are stored sequentially in the database
#
# Because history is fetched each time:
#   → AI maintains context
#   → Responses are not stateless
# =========================================================
# SESSION-LEVEL USAGE ANALYTICS
# =========================================================
# Aggregated statistics across entire conversation
#
# Includes:
#   - total tokens used
#   - total input tokens
#   - total output tokens
#   - total number of turns
#
# Production use:
#   - Cost dashboards
#   - User billing systems
#   - Monitoring system performance
# =========================================================
# PER-TURN TOKEN ANALYSIS
# =========================================================
# Provides token usage for each individual turn
#
# Useful for:
#   - Identifying expensive queries
#   - Debugging token spikes
#   - Optimizing prompts
#
# Example:
#   Turn 3 → unusually high tokens → investigate prompt/context size
# Creates a new branch from a specific turn
#
# What happens internally:
#   - Copies conversation state up to that turn
#   - Creates a new branch pointer
#   - Future messages go into that branch
#
# NOTE:
#   - Original conversation remains unchanged
#   - New branch evolves independently
# Switches active branch
#
# After switching:
#   - All new messages are stored in selected branch
#
# Production:
#   - UI controls this (user never sees raw function calls)
#   - Example: selecting a different conversation path
# Lists all branches in the session
#
# Each branch contains:
#   - branch_id
#   - number of turns
#
# Production:
#   - Used to display alternative conversation paths in UI
# =========================================================
# STRUCTURED CONVERSATION VIEW
# =========================================================
# Returns conversation as structured data instead of raw text
#
# Each turn includes:
#   - turn number
#   - content
#   - metadata (branching info)
#
# Useful for:
#   - debugging
#   - analytics dashboards
#   - building chat UI
# =========================================================
# SEARCHING CONVERSATIONS
# =========================================================
# Allows querying conversation history by keyword
#
# Example:
#   find_turns_by_content("weather")
#
# Production use:
#   - chat search feature
#   - debugging conversations
#   - analyzing user intent patterns
#
# NOTE:
#   - Avoids manual scanning of conversations
#   - Uses structured querying instead
# =========================================================
# TOOL USAGE ANALYTICS
# =========================================================
# Tracks which tools/APIs were used by the agent
#
# Returns:
#   - tool name
#   - number of times used
#   - turn number
#
# Useful when:
#   - agent calls APIs
#   - uses external tools
#
# Production:
#   - monitor tool performance
#   - detect failures
#   - optimize workflows
# =========================================================
# ADVANCED SQLITE SESSION - COMPLETE UNDERSTANDING
# =========================================================
# This implementation demonstrates a production-style
# conversational memory system with:
#
# 1. Persistent Memory
#    - Conversations stored in database
#    - Context preserved across turns
#
# 2. Token Usage Tracking
#    - Per-turn and session-level analytics
#    - Used for billing and monitoring
#
# 3. Conversation Branching
#    - Explore alternative paths from past turns
#    - Used for regenerate, debugging, experimentation
#
# 4. Structured Querying
#    - Search conversations
#    - Analyze usage
#    - Build dashboards
#
# IMPORTANT PRODUCTION INSIGHT:
#   - Branching is NOT manual exploration
#   - It is triggered by:
#       → user actions (UI events)
#       → system logic
#       → known turn IDs
#
# This system represents:
#   → A stateful AI architecture
#   → Not just a simple chatbot
#
# =========================================================

import asyncio
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

load_dotenv(override=True)
# ── 🔧 Tools ───────────────────────────────────────

@function_tool
def web_search(query: str) -> str:
    return f"[Search results for '{query}']"

@function_tool
def send_email(to: str, content: str) -> str:
    return f"Email sent to {to}: {content}"


# ── 🧠 Research Flow (LLM-driven chain) ─────────────

analysis_agent = Agent(
    name="Analysis Agent",
    instructions="Analyze research data and summarize.",
)

research_agent = Agent(
    name="Research Agent",
    instructions="""
    Search for product info using web_search.
    Then handoff to Analysis Agent.
    """,
    tools=[web_search],
    handoffs=[analysis_agent],
)


# ── 📧 Email Agent ─────────────────────────────────

email_agent = Agent(
    name="Email Agent",
    instructions="Send a professional email using the tool.",
    tools=[send_email],
)


# ── 🧠 Triage Agent (LLM decides WHAT) ─────────────

triage_agent = Agent(
    name="Triage Agent",
    instructions="""
    Analyze the user request and return actions:
    - research
    - email

    Return comma-separated values like: research,email
    """,
)


# ── 💻 Hybrid Orchestrator (YOU control flow) ───────

async def hybrid_orchestrator(user_input: str):
    print("\n=== 🧠 TRIAGE (LLM decides WHAT) ===")

    triage_result = await Runner.run(triage_agent, user_input)
    actions = triage_result.final_output.lower()

    print("Actions:", actions)

    results = []

    # ── 💻 Code controls execution ─────────────

    if "research" in actions:
        print("\n=== 🔍 RESEARCH FLOW (LLM chain) ===")
        research_result = await Runner.run(research_agent, user_input)
        results.append(research_result.final_output)

        # 🔍 Trace research flow
        print("\n--- Research Flow Trace ---")
        for item in research_result.new_items:
            if item.type == "handoff_output_item":
                print(f"{item.source_agent.name} → {item.target_agent.name}")

    if "email" in actions:
        print("\n=== 📧 EMAIL FLOW ===")
        email_result = await Runner.run(email_agent, user_input)
        results.append(email_result.final_output)

    return "\n".join(results)


# ── 🚀 RUN ─────────────────────────────────────────

async def main():
    user_input = "Research Tesla car and send email to customer"

    final = await hybrid_orchestrator(user_input)

    print("\n=== 🎯 FINAL OUTPUT ===")
    print(final)


if __name__ == "__main__":
    asyncio.run(main())

# ============================================================
# 🔀 HYBRID ORCHESTRATION (LLM + CODE CONTROL)
# ============================================================

# 1️⃣ WHAT IS HYBRID ORCHESTRATION?
# ------------------------------------------------------------
# Hybrid orchestration = combining:
# 🧠 LLM decisions (WHAT to do)
# 💻 Code control (HOW to execute)

# Pattern:
# LLM → decides intent/actions
# Code → routes execution
# LLM → handles complex sub-flows (handoffs/tools)


# 2️⃣ WHY USE HYBRID APPROACH?
# ------------------------------------------------------------
# Pure LLM orchestration:
# ❌ Unpredictable
# ❌ Expensive
# ❌ Hard to debug

# Pure code orchestration:
# ❌ Not flexible
# ❌ Cannot handle unknown tasks

# Hybrid:
# ✅ Flexible + Controlled
# ✅ Production-ready
# ✅ Easy to debug


# 3️⃣ BASIC FLOW
# ------------------------------------------------------------
# User Input
#    ↓
# 🧠 Triage Agent (LLM decides WHAT actions are needed)
#    ↓
# 💻 Code Orchestrator (routes execution)
#    ├── Flow A (LLM-driven chain with handoffs)
#    └── Flow B (direct tool/agent execution)
#    ↓
# Final Output


# 4️⃣ TRIAGE AGENT (LLM ROLE)
# ------------------------------------------------------------
# Triage agent analyzes user input and returns actions.

# Example output:
# "research,email"

# Important:
# - LLM only decides WHAT to do
# - It does NOT control execution order


# 5️⃣ CODE ORCHESTRATOR (DEVELOPER CONTROL)
# ------------------------------------------------------------
# Code reads LLM output and decides execution:

# if "research" in actions:
#     run research flow

# if "email" in actions:
#     run email flow

# This ensures:
# - Predictability
# - Safety
# - Cost control


# 6️⃣ INNER FLOWS (LLM-DRIVEN)
# ------------------------------------------------------------
# Inside each flow, LLM can still:
# - Use tools
# - Perform handoffs
# - Chain multiple agents

# Example:
# Research Agent → Analysis Agent → Pricing Agent

# So hybrid = code outside + LLM inside


# 7️⃣ FLOW VISUALIZATION
# ------------------------------------------------------------
# Example:

# User
#  ↓
# Triage (LLM)
#  ↓
# Code Orchestrator
#  ├── Research → Analysis (LLM handoffs)
#  └── Email → send_email tool


# 8️⃣ TRACE AND DEBUG (VERY IMPORTANT)
# ------------------------------------------------------------
# Use result.new_items to track execution:

# for item in result.new_items:
#     if item.type == "handoff_output_item":
#         print(f"{item.source_agent.name} → {item.target_agent.name}")

# This shows inner LLM-driven flow


# 9️⃣ RESPONSIBILITY SPLIT
# ------------------------------------------------------------
# LLM responsibilities:
# - Understand user intent
# - Decide actions
# - Handle complex reasoning

# Code responsibilities:
# - Control execution flow
# - Enforce rules
# - Prevent unsafe actions


# 🔟 BEST PRACTICES
# ------------------------------------------------------------
# ✔ Use LLM for:
#   - Open-ended decisions
#   - Complex reasoning

# ✔ Use code for:
#   - Critical actions
#   - Routing logic
#   - Cost control

# ✔ Always:
#   - Log new_items (flow trace)
#   - Limit deep handoffs
#   - Add guardrails for safety


# 1️⃣1️⃣ MENTAL MODEL
# ------------------------------------------------------------
# LLM = Brain 🧠 (decides WHAT)
# Code = Controller 💻 (decides HOW)

# Hybrid = Best of both worlds


# 🎯 FINAL SUMMARY
# ------------------------------------------------------------
# Hybrid orchestration:
# - LLM decides intent
# - Code controls execution
# - LLM handles inner workflows
# - System remains flexible + predictable
# ============================================================

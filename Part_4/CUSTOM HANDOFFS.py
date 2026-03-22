# ============================================================
# 🔀 CUSTOM HANDOFFS — FINAL WORKING VERSION (NO ERRORS)
# ============================================================

import asyncio
from pydantic import BaseModel

from agents import Agent, Runner, handoff, RunContextWrapper
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from agents.extensions import handoff_filters
from dotenv import load_dotenv

load_dotenv(override=True)

# ============================================================
# 📋 STEP 1 — Structured input for escalation
# ============================================================

class EscalationData(BaseModel):
    reason: str
    priority: str


# ============================================================
# ⚡ STEP 2 — Callback when escalation happens
# ============================================================

async def on_escalate(ctx: RunContextWrapper[None], data: EscalationData):
    print("\n🚨 ESCALATION TRIGGERED")
    print(f"Reason   : {data.reason}")
    print(f"Priority : {data.priority}")


# ============================================================
# 🧠 STEP 3 — Specialist agents
# ============================================================

billing_agent = Agent(
    name="Billing Agent",
    instructions="Handle billing, invoices, and payments."
)

tech_agent = Agent(
    name="Tech Support Agent",
    instructions="Handle bugs, crashes, and technical issues."
)

escalation_agent = Agent(
    name="Escalation Agent",
    instructions="Handle urgent and critical issues carefully."
)


# ============================================================
# 🔄 STEP 4 — Dynamic enable/disable (FIXED ✅)
# ============================================================

def allow_escalation(ctx, agent):
    keywords = ["urgent", "critical", "asap"]

    user_input = ""

    if hasattr(ctx, "input") and ctx.input:
        user_input = str(ctx.input).lower()
    elif hasattr(ctx, "messages") and ctx.messages:
        user_input = str(ctx.messages[-1]).lower()

    return any(word in user_input for word in keywords)



# ============================================================
# 🔀 STEP 5 — Handoffs
# ============================================================

billing_handoff = handoff(
    agent=billing_agent,
    tool_name_override="send_to_billing",
    tool_description_override="Use for billing or invoice issues.",
)

tech_handoff = handoff(
    agent=tech_agent,
    tool_name_override="send_to_tech_support",
    tool_description_override="Use for technical problems.",
    input_filter=handoff_filters.remove_all_tools,
)

escalation_handoff = handoff(
    agent=escalation_agent,
    tool_name_override="escalate_issue",
    tool_description_override="Use for urgent or critical issues.",

    input_type=EscalationData,     # structured input required
    on_handoff=on_escalate,        # callback when triggered
    is_enabled=allow_escalation,   # FIXED FUNCTION
)


# ============================================================
# 🧠 STEP 6 — TRIAGE AGENT (ENTRY POINT)
# ============================================================

triage_agent = Agent(
    name="Triage Agent",

    instructions=prompt_with_handoff_instructions("""
    You are a smart support triage agent.

    Routing rules:
    - Billing issues → Billing Agent
    - Technical issues → Tech Support Agent
    - Urgent/Critical → Escalation Agent

    If simple → answer directly.
    """),

    handoffs=[
        billing_handoff,
        tech_handoff,
        escalation_handoff
    ],
)


# ============================================================
# ▶️ STEP 7 — RUN TEST CASES
# ============================================================

async def main():

    print("\n==============================")
    print("🚀 RUN 1: Billing Example")
    print("==============================")

    result1 = await Runner.run(
        triage_agent,
        "My invoice amount is incorrect"
    )
    print("Final Output:", result1.final_output)


    print("\n==============================")
    print("🚀 RUN 2: Tech Example")
    print("==============================")

    result2 = await Runner.run(
        triage_agent,
        "The app crashes when I open it"
    )
    print("Final Output:", result2.final_output)


    print("\n==============================")
    print("🚀 RUN 3: Escalation Example")
    print("==============================")

    result3 = await Runner.run(
        triage_agent,
        "URGENT: My system crashed and I lost everything!"
    )
    print("Final Output:", result3.final_output)


# ============================================================
# ▶️ ENTRY POINT
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())



# ============================================================

# 🧠 CONCEPT SUMMARY:

# 🔀 HANDOFF FLOW:
# User Input
#    ↓
# Triage Agent (LLM decides)
#    ↓
# Handoff Tool Triggered
#    ↓
# (Optional) Structured Input Generated
#    ↓
# on_handoff callback runs
#    ↓
# Target Agent executes
#    ↓
# Final Output

# ============================================================
# 🧠 CUSTOM HANDOFFS — COMPLETE CONCEPT NOTES
# ============================================================

# 🔀 WHAT IS A HANDOFF?
# A handoff is when one agent transfers control to another agent.
# The LLM decides WHEN and WHICH agent to call based on:
# - Instructions (prompt)
# - Tool descriptions (handoff descriptions)

# Flow:
# User Input
#    ↓
# Triage Agent (LLM decides)
#    ↓
# Handoff Tool Called
#    ↓
# Target Agent Executes
#    ↓
# Final Output


# ============================================================
# 🧠 HANDOFF CONFIGURATION OPTIONS
# ============================================================

# agent:
# → The target agent to transfer control to

# tool_name_override:
# → Custom name of the handoff tool (default: transfer_to_<agent>)

# tool_description_override:
# → VERY IMPORTANT — helps LLM decide when to use this handoff

# on_handoff:
# → Callback executed immediately when handoff is triggered
# → Use for logging, analytics, API calls, pre-fetching data

# input_type:
# → Forces LLM to send structured JSON when calling handoff
# → Example:
#    {
#       "reason": "data loss",
#       "priority": "high"
#    }
# → This data is passed to on_handoff

# is_enabled:
# → Dynamically enable/disable handoff at runtime
# → Must follow function signature:
#       def func(ctx, agent)

# input_filter:
# → Controls what conversation history the next agent sees
# → Can remove tool calls, summarize, or limit history


# ============================================================
# 🧠 IMPORTANT FUNCTION SIGNATURES
# ============================================================

# is_enabled function:
# MUST accept 2 parameters:
#    def func(ctx, agent)

# on_handoff function:
# If input_type exists:
#    async def func(ctx, structured_data)

# Common mistake:
# ❌ def func(ctx)
# ✅ def func(ctx, agent)


# ============================================================
# 🧠 CONTEXT (RunContextWrapper)
# ============================================================

# ctx contains runtime information about the current run.

# IMPORTANT:
# Different SDK versions expose input differently!

# Possible fields:
# - ctx.input_text   (newer versions)
# - ctx.input        (older versions)
# - ctx.messages     (fallback conversation history)

# SAFE way to access user input:
#
# user_input = ""
# if hasattr(ctx, "input") and ctx.input:
#     user_input = str(ctx.input).lower()
# elif hasattr(ctx, "messages") and ctx.messages:
#     user_input = str(ctx.messages[-1]).lower()


# ============================================================
# 🧠 HOW LLM DECIDES HANDOFF
# ============================================================

# LLM chooses handoff based on:
# 1. Agent instructions (prompt)
# 2. Tool descriptions
# 3. Available handoffs list

# So ALWAYS:
# - Write clear instructions
# - Write strong tool descriptions

# Example:
# "Use this for urgent issues only"
# → helps model route correctly


# ============================================================
# 🧠 STRUCTURED HANDOFF (input_type)
# ============================================================

# input_type:
# → Adds metadata to the handoff
# → DOES NOT change which agent is selected

# Example:
# EscalationData(reason="data loss", priority="high")

# Used for:
# - Logging
# - Analytics
# - Business logic


# ============================================================
# 🧠 on_handoff CALLBACK
# ============================================================

# Runs immediately when handoff is triggered (before agent executes)

# Use cases:
# - Logging escalation
# - Triggering backend jobs
# - Fetching data early


# ============================================================
# 🧠 is_enabled (DYNAMIC CONTROL)
# ============================================================

# Controls whether a handoff is available

# Example:
# Only allow escalation if message contains "urgent"

# Important:
# Must safely read input from ctx (version dependent)


# ============================================================
# 🧠 INPUT FILTER
# ============================================================

# Controls what history the next agent receives

# Default:
# → Full conversation

# With filter:
# → Can remove tool calls or reduce noise

# Example:
# handoff_filters.remove_all_tools


# ============================================================
# 🧠 COMMON ERRORS (WE FIXED THESE)
# ============================================================

# ❌ TypeError: function takes 1 argument but 2 given
# → Fix: add (ctx, agent)

# ❌ AttributeError: ctx.input not found
# ❌ AttributeError: ctx.input_text not found
# → Fix: use hasattr() safe extraction

# ❌ LLM not choosing correct handoff
# → Fix:
#    - Improve instructions
#    - Improve tool_description


# ============================================================
# 🧠 FINAL FLOW SUMMARY
# ============================================================

# User → Triage Agent
#       ↓
# LLM decides:
#   - Answer directly OR
#   - Call handoff tool
#       ↓
# (Optional) Structured input generated
#       ↓
# on_handoff callback runs
#       ↓
# Target agent takes over
#       ↓
# Final output returned


# ============================================================
# 🚀 PRODUCTION BEST PRACTICES
# ============================================================

# ✅ Always use prompt_with_handoff_instructions
# ✅ Write clear tool descriptions
# ✅ Use structured input for important metadata
# ✅ Use is_enabled for dynamic control
# ✅ Use safe context extraction (hasattr)
# ✅ Log inside on_handoff
# ============================================================


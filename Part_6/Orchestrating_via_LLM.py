from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

load_dotenv(override=True)
# ── 🔧 BASE TOOLS ───────────────────────────────────

@function_tool
def web_search(query: str) -> str:
    return f"[Search Results for '{query}']"

@function_tool
def calculate_price(cost: float, margin: float) -> float:
    return cost * (1 + margin)

@function_tool
def send_email(to: str, content: str) -> str:
    return f"Email sent to {to}: {content}"

@function_tool
def generate_marketing_email(product: str) -> str:
    return f"Amazing offer on {product}! Buy now!"


# ── 🧠 DEEP AGENTS ──────────────────────────────────

# Marketing Agent
marketing_agent = Agent(
    name="Marketing Agent",
    instructions="""
    Create marketing campaigns.
    Use generate_marketing_email tool.
    """,
    tools=[generate_marketing_email],
)

# Pricing Agent
pricing_agent = Agent(
    name="Pricing Agent",
    instructions="""
    Calculate pricing strategies.
    Then handoff to Marketing Agent.
    """,
    tools=[calculate_price],
    handoffs=[marketing_agent],
)

# Analysis Agent
analysis_agent = Agent(
    name="Analysis Agent",
    instructions="""
    Analyze research data and trends.
    Then decide:
    - pricing → Pricing Agent
    - marketing → Marketing Agent
    """,
    handoffs=[pricing_agent, marketing_agent],
)

# Research Agent
research_agent = Agent(
    name="Research Agent",
    instructions="""
    Perform deep research using web_search.
    Then handoff to Analysis Agent.
    """,
    tools=[web_search],
    handoffs=[analysis_agent],
)

# ── 🏢 OPERATIONS SIDE ───────────────────────────────

# Email Tool Agent (Agent-as-tool)
email_agent = Agent(
    name="Email Agent",
    instructions="Send professional emails.",
    tools=[send_email],
)

# Customer Ops Agent
customer_ops_agent = Agent(
    name="Customer Ops Agent",
    instructions="""
    Handle customer requests.
    Use Email Agent if needed.
    """,
    handoffs=[email_agent],
)

# Operations Agent
operations_agent = Agent(
    name="Operations Agent",
    instructions="""
    Handle operational tasks.
    Decide between:
    - customer support → Customer Ops Agent
    - internal ops → handle directly
    """,
    handoffs=[customer_ops_agent],
)

# ── 🎯 TRIAGE AGENT ─────────────────────────────────

triage_agent = Agent(
    name="Triage Agent",
    instructions="""
    Understand the user request and route:

    - Research / market / product → Research Agent
    - Customer / email / support → Operations Agent
    """,
    handoffs=[research_agent, operations_agent],
)

# ── 🧠 MAIN ORCHESTRATOR ────────────────────────────

main_agent = Agent(
    name="Main Orchestrator",
    instructions="""
    You are the top-level orchestrator.

    Your job:
    - Understand user intent
    - Delegate to correct agents
    - Allow multi-step workflows
    - Combine outputs

    Always start with Triage Agent.
    """,
    handoffs=[triage_agent],
)

# ── 🚀 RUN SYSTEM ───────────────────────────────────

result = Runner.run_sync(
    main_agent,
    """
    Research Tesla car, analyze market, calculate price with 30% margin,
    create marketing email, and also send it to customer.
    """
)
print("\n=== 🔍 EXECUTION TRACE ===\n")

for item in result.new_items:

    # 🧠 Agent messages
    if item.type == "message_output_item":
        print(f"[🧠 {item.raw_item.role}] {item.raw_item.content}\n")

    # 🔁 Handoff tracking (MOST IMPORTANT)
    elif item.type == "handoff_output_item":
        print(f"[🔀 HANDOFF] {item.source_agent.name} → {item.target_agent.name}\n")

    # 🔧 Tool call
    elif item.type == "tool_call_item":
        print(f"[🛠 TOOL CALL] {item.raw_item.name}\n")

    # 📤 Tool output
    elif item.type == "tool_call_output_item":
        print(f"[📦 TOOL OUTPUT] {item.output}\n")

    # 🧠 Reasoning (if enabled)
    elif item.type == "reasoning_item":
        print(f"[💭 REASONING] {item.raw_item.content}\n")

print("\n=== FINAL OUTPUT ===\n")
print(result.final_output)


# ============================================================
# 🎼 ORCHESTRATION + 🔍 FLOW TRACKING (MULTI-AGENT SYSTEM)
# ============================================================

# 1️⃣ WHAT IS ORCHESTRATION?
# ------------------------------------------------------------
# Orchestration = controlling how agents execute:
# - Which agent runs
# - In what order
# - Who decides next step

# Types:
# 🧠 LLM-Driven → LLM decides flow dynamically (using handoffs/tools)
# 💻 Code-Driven → Developer controls flow (if/else, pipelines)
# 🔀 Hybrid → LLM decides "what", code controls "how" (best practice)


# 2️⃣ HANDOFFS (AGENT → AGENT)
# ------------------------------------------------------------
# A handoff transfers control from one agent to another.

# Example:
# agent_A → agent_B → agent_C

# Important:
# - After handoff, new agent becomes ACTIVE
# - It behaves like a FULL agent (not restricted)

# A handoff agent can:
# ✅ Have tools
# ✅ Have multiple handoffs
# ✅ Call other agents
# ✅ Act as orchestrator itself


# 3️⃣ MULTI-LEVEL HANDOFFS (CHAIN)
# ------------------------------------------------------------
# Agents can form deep hierarchies:

# Main → Triage → Research → Analysis → Pricing → Marketing

# Each agent can further:
# - Call tools
# - Handoff to multiple agents
# - Create branching flows

# This creates a GRAPH (not just a linear flow)


# 4️⃣ HOW FLOW ACTUALLY HAPPENS
# ------------------------------------------------------------
# LLM dynamically decides:

# - Which agent to call
# - Whether to call multiple agents
# - Order of execution

# Example Flow:
# Main → Triage
# Triage → Research
# Research → Analysis
# Analysis → Pricing
# Pricing → Marketing

# AND ALSO:
# Triage → Operations → Email


# 5️⃣ TRACKING FLOW (VERY IMPORTANT)
# ------------------------------------------------------------
# result.new_items contains EVERYTHING that happened.

# Think:
# final_output → final answer
# new_items → full execution trace (like logs)


# 6️⃣ RUN ITEM TYPES (USED FOR DEBUGGING)
# ------------------------------------------------------------
# item.type can be:

# "message_output_item"      → LLM message
# "tool_call_item"           → tool was called
# "tool_call_output_item"    → tool returned result
# "handoff_output_item"      → agent → agent transition
# "reasoning_item"           → internal reasoning step


# 7️⃣ HOW TO TRACE AGENT FLOW
# ------------------------------------------------------------
# Most important part for understanding flow:

# for item in result.new_items:
#     if item.type == "handoff_output_item":
#         print(f"{item.source_agent.name} → {item.target_agent.name}")

# This shows EXACT agent-to-agent flow


# 8️⃣ COMPLETE TRACE LOGGING
# ------------------------------------------------------------
# Example:

# for item in result.new_items:
#     if item.type == "handoff_output_item":
#         print(f"[HANDOFF] {item.source_agent.name} → {item.target_agent.name}")
#     elif item.type == "tool_call_item":
#         print(f"[TOOL CALL] {item.raw_item.name}")
#     elif item.type == "tool_call_output_item":
#         print(f"[TOOL OUTPUT] {item.output}")
#     elif item.type == "message_output_item":
#         print(f"[LLM MESSAGE] {item.raw_item.content}")


# 9️⃣ BUILDING FLOW PATH (GRAPH UNDERSTANDING)
# ------------------------------------------------------------
# You can store the flow:

# flow = []
# for item in result.new_items:
#     if item.type == "handoff_output_item":
#         flow.append((item.source_agent.name, item.target_agent.name))

# Then print:
# for step in flow:
#     print(f"{step[0]} → {step[1]}")


# 🔟 MENTAL MODEL
# ------------------------------------------------------------
# Without tracing:
# ❌ System is a BLACK BOX

# With new_items:
# ✅ FULL VISIBILITY of execution


# 1️⃣1️⃣ PRODUCTION BEST PRACTICES
# ------------------------------------------------------------
# Always log:
# - new_items → execution flow
# - last_agent → where execution ended
# - raw_responses → debugging API output

# Also:
# - Limit deep handoffs (avoid loops)
# - Use clear agent instructions
# - Add guardrails for safety


# 🎯 FINAL SUMMARY
# ------------------------------------------------------------
# - Orchestration controls agent flow
# - Handoffs transfer control between agents
# - Agents can have nested handoffs + tools
# - Flow is dynamic in LLM-driven systems
# - Use result.new_items to TRACE EVERYTHING
# ============================================================

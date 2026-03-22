from agents import Agent, function_tool
from agents.extensions.visualization import draw_graph
from dotenv import load_dotenv

load_dotenv(override=True)

# ── 🔧 Tools ─────────────────────────────

@function_tool
def web_search(query: str) -> str:
    return f"Search results for {query}"

@function_tool
def send_email(to: str) -> str:
    return f"Email sent to {to}"


# ── 🧠 Agents ────────────────────────────

marketing_agent = Agent(
    name="Marketing Agent",
    instructions="Create marketing content.",
    tools=[web_search],  # uses tool
)

analysis_agent = Agent(
    name="Analysis Agent",
    instructions="Analyze data and decide next step.",
    handoffs=[marketing_agent],  # handoff
)

research_agent = Agent(
    name="Research Agent",
    instructions="Do research.",
    tools=[web_search],
    handoffs=[analysis_agent],  # chain
)

email_agent = Agent(
    name="Email Agent",
    instructions="Send emails.",
    tools=[send_email],
)

operations_agent = Agent(
    name="Operations Agent",
    instructions="Handle ops tasks.",
    handoffs=[email_agent],
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="Route user request.",
    handoffs=[research_agent, operations_agent],
    tools=[web_search],
)

# ── 🎯 DRAW GRAPH ────────────────────────

draw_graph(triage_agent, filename="agent_graph")

# ============================================================
# 🗺️ AGENT VISUALIZATION (GRAPH-BASED VIEW)
# ============================================================

# WHAT IS THIS?
# ------------------------------------------------------------
# draw_graph(agent) generates a visual diagram of:
# - Agents
# - Tools
# - MCP servers
# - Handoffs (connections)

# WHY USE IT?
# ------------------------------------------------------------
# - Understand system architecture
# - Debug complex agent flows
# - Visualize relationships between components

# GRAPH ELEMENTS
# ------------------------------------------------------------
# 🟡 Yellow box → Agent
# 🟢 Green oval → Tool
# ⬜ Grey box → MCP Server
# 🔵 __start__ → Entry point
# 🔴 __end__ → Exit point

# ARROW TYPES
# ------------------------------------------------------------
# →   (solid)  = Agent → Agent (handoff)
# ···→ (dotted) = Agent → Tool
# - - → (dashed) = Agent → MCP server

# IMPORTANT NOTE
# ------------------------------------------------------------
# This graph shows POSSIBLE paths, NOT actual execution.

# To see real execution flow, use:
# result.new_items

# USAGE
# ------------------------------------------------------------
# draw_graph(agent) → display graph
# draw_graph(agent).view() → open in viewer
# draw_graph(agent, filename="graph") → save as PNG

# BEST PRACTICE
# ------------------------------------------------------------
# Use:
# - draw_graph() → for architecture
# - new_items → for runtime debugging
# ============================================================

# ============================================================
# 🗺️ AGENT VISUALIZATION SETUP (GRAPHVIZ INSTALLATION)
# ============================================================

# ❗ IMPORTANT:
# Agent visualization requires BOTH:
# 1. Python package (graphviz wrapper)
# 2. Graphviz system software (dot executable)

# ------------------------------------------------------------
# 📦 STEP 1 — Install Python Dependency
# ------------------------------------------------------------
# Add to requirements.txt:
# openai-agents[viz]

# OR install manually:
# pip install "openai-agents[viz]"

# This installs:
# - agents visualization module
# - Python graphviz wrapper


# ------------------------------------------------------------
# 🪟 STEP 2 — Install Graphviz (SYSTEM SOFTWARE)
# ------------------------------------------------------------
# Download from:
# https://graphviz.org/download/

# Choose:
# Windows → Stable release → .exe installer

# Install to default path:
# C:\Program Files\Graphviz\


# ------------------------------------------------------------
# 🔑 STEP 3 — Add Graphviz to PATH
# ------------------------------------------------------------
# Add this path to Environment Variables:
# C:\Program Files\Graphviz\bin

# Steps:
# 1. Search "Environment Variables"
# 2. Open "Edit the system environment variables"
# 3. Click "Environment Variables"
# 4. Under System Variables → find "Path"
# 5. Click Edit → New
# 6. Add:
#    C:\Program Files\Graphviz\bin
# 7. Click OK → OK → OK


# ------------------------------------------------------------
# 🔄 STEP 4 — Restart Terminal
# ------------------------------------------------------------
# Close PowerShell / CMD completely
# Open a new terminal


# ------------------------------------------------------------
# 🧪 STEP 5 — Verify Installation
# ------------------------------------------------------------
# Run:
# dot -V

# Expected output:
# dot - graphviz version X.X.X

# If error:
# "dot is not recognized"
# → PATH is not set correctly


# ------------------------------------------------------------
# 🚀 STEP 6 — Use Visualization
# ------------------------------------------------------------
# from agents.extensions.visualization import draw_graph
# draw_graph(agent, filename="agent_graph")

# Output:
# agent_graph.png will be generated


# ------------------------------------------------------------
# ⚠️ COMMON ERRORS
# ------------------------------------------------------------

# ❌ Error:
# ExecutableNotFound: failed to execute 'dot'
# → Graphviz not installed OR not in PATH

# ❌ Error:
# 'dot' is not recognized
# → PATH not configured correctly


# ------------------------------------------------------------
# 🧠 IMPORTANT CONCEPT
# ------------------------------------------------------------
# Python graphviz = wrapper (pip install)
# Graphviz software = actual engine (dot.exe)

# 👉 Both are required for visualization to work


# ------------------------------------------------------------
# 🎯 FINAL SUMMARY
# ------------------------------------------------------------
# 1. Install Python package → pip install openai-agents[viz]
# 2. Install Graphviz software
# 3. Add Graphviz/bin to PATH
# 4. Restart terminal
# 5. Run dot -V to verify
# ============================================================

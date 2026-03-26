import asyncio
import json
from pathlib import Path
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

load_dotenv(override=True)
# 📁 Memory file
APPROVAL_FILE = Path("approvals.json")

# ── Load approval memory ──────────────────────────────
def load_approvals():
    if APPROVAL_FILE.exists():
        return json.loads(APPROVAL_FILE.read_text())
    return {}

# ── Save approval memory ──────────────────────────────
def save_approvals(data):
    APPROVAL_FILE.write_text(json.dumps(data, indent=2))

# ── Approval logic (uses memory) ──────────────────────
async def approve_delete(_ctx, params, _id):
    approvals = load_approvals()

    filename = params.get("filename", "")
    key = f"delete_file:{filename}"

    # ✅ If already approved → skip approval
    if approvals.get(key):
        return False

    # ❗ Otherwise require approval for .db files
    return filename.endswith(".db")

# ── Tool ─────────────────────────────────────────────
@function_tool(needs_approval=approve_delete)
async def delete_file(filename: str) -> str:
    return f"Deleted file: {filename}"

# ── Agent ────────────────────────────────────────────
agent = Agent(
    name="File Assistant",
    instructions="Help manage files.",
    tools=[delete_file],
)

# ── Ask user for approval ────────────────────────────
def ask_user(tool_name, args):
    # 🔧 Fix: convert string → dict
    if isinstance(args, str):
        args = json.loads(args)

    print(f"\n⚠️ Tool: {tool_name}")
    print(f"Args: {args}")

    choice = input("Approve? (y/n): ").strip().lower()
    return choice == "y", args


# ── Main HITL flow ───────────────────────────────────
async def main():
    user_input = input("Enter request: ")
    result = await Runner.run(agent, user_input)

    while result.interruptions:
        state = result.to_state()
        print("State: ",state)
        approvals = load_approvals()

        for interruption in result.interruptions:
            approved, args = ask_user(interruption.name, interruption.arguments)

            # 🔧 Safe key creation
            key = f"{interruption.name}:{args.get('filename')}"

            if approved:
                state.approve(interruption)

                # 💾 Save approval memory
                approvals[key] = True
                save_approvals(approvals)
                print("💾 Approval saved!")

            else:
                state.reject(interruption)
                print("❌ Action rejected!")

        result = await Runner.run(agent, state)

    print("\n✅ Final Output:")
    print(result.final_output)


# ── Run ──────────────────────────────────────────────
asyncio.run(main())

# ============================================================
# 🧠 HUMAN-IN-THE-LOOP (HITL) — COMPLETE NOTES
# ============================================================

# ------------------------------------------------------------
# 🔹 1. WHAT IS HUMAN-IN-THE-LOOP (HITL)?
# ------------------------------------------------------------
# HITL is a system where the AI pauses before performing
# sensitive or risky actions and asks a human for approval.
#
# Example:
# Agent → wants to delete file → PAUSE → human approves → continue
#
# Analogy:
# Like a surgeon preparing for operation but waiting for final consent.


# ------------------------------------------------------------
# 🔹 2. WHY DO WE NEED HITL?
# ------------------------------------------------------------
# Some actions are dangerous or irreversible:
# - Deleting files
# - Sending emails
# - Cancelling orders
# - Making payments
#
# We don't want AI to do these automatically.


# ------------------------------------------------------------
# 🔹 3. DEFAULT FLOW (HOW HITL WORKS)
# ------------------------------------------------------------
# 1. User gives input
# 2. Agent decides to call a tool
# 3. Tool has needs_approval=True
# 4. Execution PAUSES
# 5. Human approves/rejects
# 6. Agent resumes execution


# ------------------------------------------------------------
# 🔹 4. WHAT CAUSES AN INTERRUPTION?
# ------------------------------------------------------------
# An interruption happens ONLY when:
# → A tool is marked with needs_approval=True
#
# Example:
# @function_tool(needs_approval=True)


# ------------------------------------------------------------
# 🔹 5. WHAT IS result.interruptions?
# ------------------------------------------------------------
# After running the agent:
# result = await Runner.run(agent, input)
#
# If approval is needed:
# result.interruptions will NOT be empty
#
# It contains:
# - tool name
# - arguments
# - agent info


# ------------------------------------------------------------
# 🔹 6. WHAT IS result.to_state()?
# ------------------------------------------------------------
# VERY IMPORTANT 🔥
#
# result → read-only snapshot
# state  → editable version of the run
#
# result.to_state() converts the paused run into a state
# so that we can:
# - approve
# - reject
# - resume execution
#
# Without this, HITL won't work.


# ------------------------------------------------------------
# 🔹 7. HITL LOOP (CORE PATTERN)
# ------------------------------------------------------------
# result = await Runner.run(agent, input)
#
# while result.interruptions:
#     state = result.to_state()
#
#     for interruption in result.interruptions:
#         state.approve(interruption) OR state.reject(interruption)
#
#     result = await Runner.run(agent, state)
#
# This loop continues until no interruptions remain.


# ------------------------------------------------------------
# 🔹 8. APPROVAL MEMORY (IMPORTANT CONCEPT)
# ------------------------------------------------------------
# Problem:
# → Agent asks approval EVERY time
#
# Solution:
# → Store approvals in a file (approvals.json)
#
# Example:
# {
#   "delete_file:data.db": true
# }
#
# This allows:
# First time → ask
# Next time → auto approve


# ------------------------------------------------------------
# 🔹 9. HOW AUTO-APPROVAL WORKS
# ------------------------------------------------------------
# In approval function:
#
# if approvals.get(key):
#     return False   # skip approval
#
# Meaning:
# → Already approved before → don't ask again


# ------------------------------------------------------------
# 🔹 10. WHY WE STORE True (NOT False)
# ------------------------------------------------------------
# True  = approved → skip next time
# False = rejected → usually ask again
#
# We store True because:
# → It changes future behavior (auto approval)
#
# False is often ignored in simple systems.


# ------------------------------------------------------------
# 🔹 11. TYPES OF HITL SYSTEMS
# ------------------------------------------------------------
# 1. Always approval:
#    needs_approval=True
#
# 2. Conditional approval:
#    needs_approval=function
#
# Example:
# → Only ask if filename ends with ".db"


# ------------------------------------------------------------
# 🔹 12. CONDITIONAL APPROVAL LOGIC
# ------------------------------------------------------------
# async def approve_delete(ctx, params, id):
#     if already_approved:
#         return False
#
#     if risky_condition:
#         return True
#
#     return False


# ------------------------------------------------------------
# 🔹 13. MULTI-STEP HITL (ADVANCED)
# ------------------------------------------------------------
# Instead of one tool:
# delete_file()
#
# Break into:
# - prepare_delete()
# - validate_delete()  (needs approval)
# - execute_delete()
#
# This allows multiple checkpoints.


# ------------------------------------------------------------
# 🔹 14. HOW TO ADD INTERRUPTION IN BETWEEN FLOW
# ------------------------------------------------------------
# IMPORTANT 🔥
#
# You CANNOT pause normal Python execution directly.
#
# You MUST convert pause into a TOOL.
#
# Solution:
# Create a checkpoint tool:
#
# @function_tool(needs_approval=True)
# async def approval_checkpoint(step: str):
#     return f"Approved {step}"


# ------------------------------------------------------------
# 🔹 15. CONDITIONAL INTERRUPTION (CUSTOM LOGIC)
# ------------------------------------------------------------
# Example:
#
# if amount > 10000:
#     → trigger approval tool
#
# So instead of:
# pause()
#
# You do:
# call_tool("approval_checkpoint")


# ------------------------------------------------------------
# 🔹 16. MANUAL CHECKPOINT (WITHOUT AGENT)
# ------------------------------------------------------------
# You can also do:
#
# def human_checkpoint():
#     input("Continue? y/n")
#
# But:
# ❌ This is NOT true HITL
# ✅ This is just manual control


# ------------------------------------------------------------
# 🔹 17. HANDOFF INTERRUPTION (ADVANCED)
# ------------------------------------------------------------
# Agent A → wants to pass to Agent B
#
# Insert checkpoint:
# approve_handoff()
#
# Flow:
# Agent A → checkpoint → Agent B


# ------------------------------------------------------------
# 🔹 18. IMPORTANT LIMITATION
# ------------------------------------------------------------
# HITL only works via tools.
#
# You cannot:
# ❌ pause random Python code
#
# You must:
# ✅ use tool with needs_approval=True


# ------------------------------------------------------------
# 🔹 19. REAL-WORLD USE CASES
# ------------------------------------------------------------
# - Payments approval
# - Refund processing
# - Email sending
# - DevOps actions (deploy/delete)
# - Admin operations


# ------------------------------------------------------------
# 🔹 20. FINAL MENTAL MODEL
# ------------------------------------------------------------
# Agent Flow:
#
# Decision → Check → Pause → Human → Resume → Learn
#
# OR:
#
# Agent → Tool → (needs approval?) → YES → Pause
#                                     ↓
#                                Human decision
#                                     ↓
#                                Resume execution


# ------------------------------------------------------------
# 🔹 21. ONE-LINE SUMMARY
# ------------------------------------------------------------
# HITL = "AI pauses before risky actions, asks human,
# and can remember decisions to improve future behavior."
# ============================================================
# ============================================================
# 🧠 HUMAN-IN-THE-LOOP (HITL) — ADVANCED SDK NOTES
# ============================================================

# ------------------------------------------------------------
# 🔹 1. CORE IDEA
# ------------------------------------------------------------
# HITL allows pausing agent execution before a tool runs,
# waiting for human approval, and then resuming execution.


# ------------------------------------------------------------
# 🔹 2. INTERRUPTION IS GLOBAL (VERY IMPORTANT)
# ------------------------------------------------------------
# Approval is NOT limited to one agent.
#
# It works across:
# - Current agent
# - Handoff agents
# - Nested Agent.as_tool() calls
#
# 👉 All interruptions appear in ONE place:
#     result.interruptions (outer run)


# ------------------------------------------------------------
# 🔹 3. NESTED AGENTS (IMPORTANT)
# ------------------------------------------------------------
# If Agent A calls Agent B (via Agent.as_tool()):
#
# If B triggers approval:
# 👉 interruption still appears in A's result
#
# 👉 You ALWAYS approve using the TOP-LEVEL agent state


# ------------------------------------------------------------
# 🔹 4. TWO LEVELS OF APPROVAL
# ------------------------------------------------------------
# 1. Agent-level approval:
#    Agent.as_tool(needs_approval=True)
#
# 2. Tool-level approval:
#    function_tool(needs_approval=True)
#
# 👉 Both flow through SAME interruption system


# ------------------------------------------------------------
# 🔹 5. HOW APPROVAL FLOW WORKS
# ------------------------------------------------------------
# Step 1:
#   Agent decides to call tool
#
# Step 2:
#   Runner checks needs_approval
#
# Step 3:
#   If approval needed → execution PAUSES
#
# Step 4:
#   result.interruptions contains:
#   - tool_name
#   - arguments
#   - agent info
#
# Step 5:
#   Convert to state:
#   state = result.to_state()
#
# Step 6:
#   Approve or reject:
#   state.approve(interruption)
#   state.reject(interruption)
#
# Step 7:
#   Resume:
#   result = Runner.run(agent, state)


# ------------------------------------------------------------
# 🔹 6. PARTIAL APPROVALS
# ------------------------------------------------------------
# You DON'T need to approve all interruptions at once.
#
# Example:
# - Approve 1 tool
# - Leave others pending
#
# 👉 Runner will resume and pause again


# ------------------------------------------------------------
# 🔹 7. STICKY DECISIONS (VERY IMPORTANT)
# ------------------------------------------------------------
# state.approve(interruption, always_approve=True)
#
# 👉 Future calls to same tool auto-approved
#
# state.reject(interruption, always_reject=True)
#
# 👉 Future calls auto-rejected
#
# 👉 Stored in RunState (persisted across sessions)


# ------------------------------------------------------------
# 🔹 8. SERIALIZATION (SAVE & RESUME LATER)
# ------------------------------------------------------------
# Save:
#   state.to_string()
#   state.to_json()
#
# Load:
#   RunState.from_string(...)
#   RunState.from_json(...)
#
# 👉 Allows:
# - Pause today
# - Resume tomorrow
# - Resume in another system


# ------------------------------------------------------------
# 🔹 9. CUSTOM REJECTION MESSAGES
# ------------------------------------------------------------
# Default rejection message can be overridden:
#
# Run-wide:
#   RunConfig.tool_error_formatter
#
# Per-call:
#   state.reject(interruption, rejection_message="Custom msg")
#
# 👉 Per-call overrides global config


# ------------------------------------------------------------
# 🔹 10. AUTOMATIC APPROVAL (NO HUMAN)
# ------------------------------------------------------------
# Some tools support programmatic approval:
#
# - ShellTool → on_approval callback
# - ApplyPatchTool → on_approval
# - HostedMCPTool → on_approval_request
#
# 👉 If callback returns decision → NO pause


# ------------------------------------------------------------
# 🔹 11. STREAMING + HITL
# ------------------------------------------------------------
# With streaming:
#
# result = Runner.run_streamed(...)
#
# Then:
# - consume stream_events()
# - check interruptions
# - approve/reject
# - resume with run_streamed()
#
# 👉 Same logic, just streaming output


# ------------------------------------------------------------
# 🔹 12. SESSION SUPPORT
# ------------------------------------------------------------
# If using sessions:
#
# 👉 Always pass SAME session when resuming
#
# This ensures:
# - conversation history preserved
# - approvals persist


# ------------------------------------------------------------
# 🔹 13. LONG-RUNNING APPROVALS
# ------------------------------------------------------------
# You can:
# - store state in DB
# - queue it
# - resume later
#
# 👉 RunState is designed to be durable


# ------------------------------------------------------------
# 🔹 14. WHAT IS STORED IN STATE
# ------------------------------------------------------------
# - conversation history
# - tool calls
# - approvals
# - nested agent states
# - execution position
#
# ⚠️ Avoid storing secrets in context


# ------------------------------------------------------------
# 🔹 15. VERSIONING (IMPORTANT FOR REAL SYSTEMS)
# ------------------------------------------------------------
# If storing state long-term:
#
# 👉 Save version info of:
# - agent
# - tools
# - SDK
#
# 👉 Prevents mismatch errors when resuming later


# ------------------------------------------------------------
# 🔹 16. GOLDEN RULES
# ------------------------------------------------------------
# 1. Interruptions ONLY come from tools
# 2. Always resume with TOP-LEVEL agent
# 3. Use state.to_state() before approve/reject
# 4. Runner controls execution
# 5. Tools do NOT control flow


# ------------------------------------------------------------
# 🔹 17. FINAL MENTAL MODEL
# ------------------------------------------------------------
# Agent → Tool → (needs approval?)
#                 ↓
#             YES → ⏸ Pause
#                     ↓
#                Human decision
#                     ↓
#                Resume execution
#
# ============================================================

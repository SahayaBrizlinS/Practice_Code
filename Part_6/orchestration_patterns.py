# ============================================================
# 💻 CODE-DRIVEN ORCHESTRATION (ALL PATTERNS COMBINED)
# ============================================================

import asyncio
from pydantic import BaseModel
from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv(override=True)
# ============================================================
# 🧩 PATTERN 1 — STRUCTURED OUTPUT ROUTING
# ============================================================

# 👉 LLM classifies input → code decides next agent

class TaskCategory(BaseModel):
    category: str  # "billing" | "tech_support" | "general"

classifier = Agent(
    name="Classifier",
    instructions="Classify user query into: billing, tech_support, or general.",
    output_type=TaskCategory,
)

billing_agent = Agent(
    name="Billing Agent",
    instructions="Handle billing-related queries."
)

tech_agent = Agent(
    name="Tech Support Agent",
    instructions="Handle technical issues."
)

general_agent = Agent(
    name="General Agent",
    instructions="Handle general queries."
)


# ============================================================
# 🔗 PATTERN 2 — AGENT CHAINING (PIPELINE)
# ============================================================

# 👉 Fixed pipeline (deterministic flow)

research_agent = Agent(
    name="Researcher",
    instructions="Research the given topic."
)

outline_agent = Agent(
    name="Outliner",
    instructions="Create an outline from research."
)

writer_agent = Agent(
    name="Writer",
    instructions="Write a blog post from outline."
)

critic_agent = Agent(
    name="Critic",
    instructions="Improve and refine the blog post."
)


# ============================================================
# 🔁 PATTERN 3 — EVALUATOR LOOP
# ============================================================

# 👉 Keep improving until quality passes

class EvalResult(BaseModel):
    passes: bool
    feedback: str

task_agent = Agent(
    name="Task Agent",
    instructions="Write a high-quality poem."
)

eval_agent = Agent(
    name="Evaluator",
    instructions="Check if output is high quality. Return passes=True/False with feedback.",
    output_type=EvalResult
)


# ============================================================
# ⚡ PATTERN 4 — PARALLEL EXECUTION
# ============================================================

# 👉 Run multiple agents at the same time

weather_agent = Agent(
    name="Weather Agent",
    instructions="Provide today's weather."
)

news_agent = Agent(
    name="News Agent",
    instructions="Provide today's headlines."
)

calendar_agent = Agent(
    name="Calendar Agent",
    instructions="Provide today's meetings."
)


# ============================================================
# 🚀 MAIN ORCHESTRATOR FUNCTION
# ============================================================

async def main():

    user_input = "My invoice is wrong"

    print("\n==============================")
    print("🧩 PATTERN 1: ROUTING")
    print("==============================")

    # 🧠 Step 1: Classify input
    result = await Runner.run(classifier, user_input)

    category = result.final_output.category
    print("Detected category:", category)

    # 💻 Step 2: Code decides routing
    if category == "billing":
        final = await Runner.run(billing_agent, user_input)
    elif category == "tech_support":
        final = await Runner.run(tech_agent, user_input)
    else:
        final = await Runner.run(general_agent, user_input)

    print("Final Response:", final.final_output)


    # =========================================================

    print("\n==============================")
    print("🔗 PATTERN 2: AGENT CHAINING")
    print("==============================")

    topic = "AI trends 2025"

    # 💻 Fixed pipeline execution
    research = await Runner.run(research_agent, topic)
    outline = await Runner.run(outline_agent, research.final_output)
    post = await Runner.run(writer_agent, outline.final_output)
    final_post = await Runner.run(critic_agent, post.final_output)

    print("Final Blog Post:\n", final_post.final_output)


    # =========================================================

    print("\n==============================")
    print("🔁 PATTERN 3: EVALUATOR LOOP")
    print("==============================")

    feedback = "Initial attempt"

    # 🔁 Loop until evaluator approves
    while True:
        task_result = await Runner.run(
            task_agent,
            f"Write a poem. Improve using feedback: {feedback}"
        )

        eval_result = await Runner.run(eval_agent, task_result.final_output)

        print("Evaluation:", eval_result.final_output)

        if eval_result.final_output.passes:
            final_poem = task_result.final_output
            break

        # Update feedback for next iteration
        feedback = eval_result.final_output.feedback

    print("Final Poem:\n", final_poem)


    # =========================================================

    print("\n==============================")
    print("⚡ PATTERN 4: PARALLEL EXECUTION")
    print("==============================")

    # ⚡ Run all agents simultaneously
    weather, news, calendar = await asyncio.gather(
        Runner.run(weather_agent, "Today's weather"),
        Runner.run(news_agent, "Today's headlines"),
        Runner.run(calendar_agent, "Today's meetings"),
    )

    print("Weather:", weather.final_output)
    print("News:", news.final_output)
    print("Calendar:", calendar.final_output)


# ============================================================
# ▶️ RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())

# ============================================================
# 💻 CODE-DRIVEN ORCHESTRATION — COMPLETE GUIDE
# ============================================================

# 🧠 WHAT IS CODE-DRIVEN ORCHESTRATION?
# ------------------------------------------------------------
# In this approach, YOUR CODE controls the execution flow.
# The LLM is only used for specific tasks (like classification,
# generation, evaluation), but it does NOT decide what runs next.

# 👉 Key idea:
# Code = Controller (decides flow)
# LLM  = Worker (performs tasks)

# Benefits:
# ✅ Deterministic (predictable flow)
# ✅ Faster (no unnecessary reasoning)
# ✅ Cheaper (fewer LLM calls)
# ✅ Easier to debug


# ============================================================
# 🧩 PATTERN 1 — STRUCTURED OUTPUT ROUTING
# ============================================================

# 👉 Use LLM to classify input → code decides next step

# Flow:
# User Input
#   ↓
# Classifier Agent (LLM returns structured output)
#   ↓
# Code checks result.final_output.category
#   ↓
# Route to correct agent

# Example:
# "My invoice is wrong" → category = "billing"
# → Code runs Billing Agent

# Why use this?
# - Clean routing logic
# - Replace complex if/else with LLM classification
# - Safer than LLM deciding full flow

# Key concept:
# output_type = Pydantic model → structured response


# ============================================================
# 🔗 PATTERN 2 — AGENT CHAINING (PIPELINE)
# ============================================================

# 👉 Fixed sequence of steps (deterministic pipeline)

# Flow:
# Input
#   ↓
# Research Agent
#   ↓
# Outline Agent
#   ↓
# Writer Agent
#   ↓
# Critic Agent
#   ↓
# Final Output

# Each step depends on previous output:
# next_input = previous_result.final_output

# Why use this?
# - Content generation pipelines
# - Data processing workflows
# - Multi-step transformations

# Key idea:
# Code strictly defines order (no LLM decision-making)


# ============================================================
# 🔁 PATTERN 3 — EVALUATOR LOOP
# ============================================================

# 👉 Run until quality is good enough

# Flow:
# Generate output
#   ↓
# Evaluate output
#   ↓
# If passes → stop
# Else → improve using feedback → repeat

# Example:
# Task Agent → generates poem
# Evaluator → checks quality
# If fails → gives feedback
# Task Agent improves → loop continues

# Why use this?
# - Quality control
# - Self-improving systems
# - Iterative refinement

# Key concept:
# while True loop controlled by evaluation result


# ============================================================
# ⚡ PATTERN 4 — PARALLEL EXECUTION
# ============================================================

# 👉 Run multiple agents simultaneously

# Flow:
# Run:
# - Weather Agent
# - News Agent
# - Calendar Agent
# at the same time using asyncio.gather()

# Why use this?
# - Independent tasks
# - Faster execution (no waiting)
# - Better performance

# Key concept:
# asyncio.gather() → concurrent execution


# ============================================================
# 🔍 RESULT HANDLING
# ============================================================

# Every Runner.run() returns a result object:

# result.final_output → main answer
# result.new_items → full execution trace
# result.last_agent → last agent used

# Use final_output for:
# - Passing data to next step
# - Displaying results


# ============================================================
# 🧠 MENTAL MODEL
# ============================================================

# Code-driven orchestration:

# YOU define:
# - Order of execution
# - Which agent runs next
# - Loop conditions
# - Parallel tasks

# LLM only:
# - Generates content
# - Classifies input
# - Evaluates output


# ============================================================
# ⚠️ LIMITATIONS
# ============================================================

# ❌ Not flexible for unknown tasks
# ❌ Requires predefined flows
# ❌ Cannot dynamically adapt like LLM-driven systems


# ============================================================
# ✅ BEST PRACTICES
# ============================================================

# ✔ Use structured output for routing
# ✔ Use chaining for pipelines
# ✔ Use loops for quality control
# ✔ Use parallel execution for independent tasks
# ✔ Keep agents small and focused
# ✔ Always log outputs for debugging


# ============================================================
# 🎯 FINAL SUMMARY
# ============================================================

# Code-driven orchestration = full control + predictability

# 4 Core Patterns:
# 1. Routing      → LLM decides category, code routes
# 2. Chaining     → Fixed pipeline
# 3. Loop         → Improve until quality passes
# 4. Parallel     → Run tasks simultaneously

# 👉 Use this when:
# - Flow is known
# - Reliability is critical
# - Cost needs to be controlled
# ============================================================

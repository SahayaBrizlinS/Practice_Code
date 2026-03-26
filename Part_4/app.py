import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from agents import Agent, Runner, function_tool
from agents.extensions.memory import SQLAlchemySession
from dotenv import load_dotenv

load_dotenv()
# ============================================================
# 🔹 APP
# ============================================================
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ============================================================
# 🔹 DB SESSION (Persistent)
# ============================================================
session = SQLAlchemySession.from_url(
    "user-123",
    url="postgresql+asyncpg://postgres:postgres@localhost:5432/SDKdb",
    create_tables=True
)

# ============================================================
# 🔹 GLOBAL STATE (for demo)
# ============================================================
current_state = None
current_interruption = None

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

    If category is already provided, skip categorization.
    """,
    tools=[validate_category, process_request],
)

# ============================================================
# 🔹 UI
# ============================================================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ============================================================
# 🔹 START REQUEST
# ============================================================
@app.post("/start")
async def start(request: Request):
    global current_state, current_interruption

    data = await request.json()
    user_input = data["query"]

    result = await Runner.run(agent, user_input, session=session)

    if result.interruptions:
        current_state = result.to_state()
        current_interruption = result.interruptions[0]

        args = current_interruption.arguments
        if isinstance(args, str):
            args = json.loads(args)

        return JSONResponse({
            "status": "approval",
            "category": args.get("category")
        })

    return JSONResponse({
        "status": "done",
        "output": result.final_output
    })


# ============================================================
# 🔹 APPROVAL HANDLER
# ============================================================
@app.post("/approve")
async def approve(request: Request):
    global current_state, current_interruption

    data = await request.json()
    action = data["action"]

    if action == "approve":
        current_state.approve(current_interruption)

        result = await Runner.run(agent, current_state, session=session)

    elif action == "edit":
        new_category = data["category"]

        result = await Runner.run(
            agent,
            f"Final category: {new_category}. Process directly.",
            session=session
        )

    else:
        return JSONResponse({
            "status": "done",
            "output": "❌ Rejected"
        })

    if result.interruptions:
        current_state = result.to_state()
        current_interruption = result.interruptions[0]

        args = current_interruption.arguments
        if isinstance(args, str):
            args = json.loads(args)

        return JSONResponse({
            "status": "approval",
            "category": args.get("category")
        })

    return JSONResponse({
        "status": "done",
        "output": result.final_output
    })


# ============================================================
# 🔹 RESUME AFTER RESTART
# ============================================================
@app.get("/resume")
async def resume():
    global current_state, current_interruption

    try:
        result = await Runner.run(agent, "", session=session)

        if result.interruptions:
            current_state = result.to_state()
            current_interruption = result.interruptions[0]

            args = current_interruption.arguments
            if isinstance(args, str):
                args = json.loads(args)

            return JSONResponse({
                "status": "approval",
                "category": args.get("category")
            })

        return JSONResponse({"status": "idle"})

    except Exception as e:
        return JSONResponse({"status": "idle", "error": str(e)})

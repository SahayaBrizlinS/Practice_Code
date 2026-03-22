# ============================================================
# 🚀 PRODUCTION AGENT API WITH REDIS SESSION
# ============================================================

import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from agents import Agent, Runner
from agents.extensions.memory import RedisSession
from dotenv import load_dotenv

load_dotenv(override=True)

# ============================================================
# 🧾 REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    user_id: str
    message: str


# ============================================================
# 🤖 AGENT SETUP
# ============================================================

agent = Agent(
    name="Assistant",
    instructions="""
    You are a helpful AI assistant.
    Remember user context and answer accordingly.
    """
)


# ============================================================
# 🌐 FASTAPI APP
# ============================================================

app = FastAPI()


# ============================================================
# 🔴 REDIS SESSION HELPER
# ============================================================

def get_session(user_id: str):
    """
    Create or fetch Redis session for a user
    """
    return RedisSession.from_url(
        user_id,
        url="redis://localhost:6379/0"
    )


# ============================================================
# 💬 CHAT ENDPOINT
# ============================================================

@app.post("/chat")
async def chat(request: ChatRequest):

    # Get Redis session for this user
    session = get_session(request.user_id)

    # Run agent with memory
    result = await Runner.run(
        agent,
        request.message,
        session=session
    )

    return {
        "response": result.final_output
    }


# ============================================================
# ▶️ RUN SERVER
# ============================================================

# Run using:
# uvicorn app:app --reload
# docker run -d -p 6379:6379 redis
# try it in SwaggerUI
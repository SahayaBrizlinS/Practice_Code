import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, SQLiteSession

# Load .env file
load_dotenv()

async def main():

    agent = Agent(
        name="Assistant",
        instructions="Reply very concisely.",
        model="gpt-4o-mini"
    )

  #session = SQLiteSession("user_session_1") ---In memory Database 
    session = SQLiteSession(
    "user_session_1",
    db_path="chat_sessions.db"
)  #---File based Database ---It will store the session data in a file called chat_sessions.db (Permanently stored and manged by the Us ---Partial Control Over it ---Cannot limit history length)

    # ---- Turn 1 ----
    result = await Runner.run(
        agent,
        "What city is the Golden Gate Bridge in?",
        session=session
    )

    print("Turn 1:", result.final_output)

    # ---- Turn 2 ----
    result = await Runner.run(
        agent,
        "What state is it in?",
        session=session
    )

    print("Turn 2:", result.final_output)


asyncio.run(main())

"""
Ask a question across ALL past studies in research memory (the RAG path).

Usage:
    python ask_memory.py "what have users said about confusing instructions?"
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from research_memory.agent import build_librarian

load_dotenv()
APP_NAME, USER_ID = "research_memory", "designer"


async def ask(question: str) -> str:
    librarian = build_librarian()
    ss = InMemorySessionService()
    runner = Runner(agent=librarian, app_name=APP_NAME, session_service=ss)
    session = await ss.create_session(app_name=APP_NAME, user_id=USER_ID)
    msg = types.Content(role="user", parts=[types.Part(text=question)])
    answer = ""
    async for event in runner.run_async(
        user_id=USER_ID, session_id=session.id, new_message=msg
    ):
        if event.is_final_response() and event.content and event.content.parts:
            answer = event.content.parts[0].text or ""
    return answer


def main():
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set. Add it to your .env first.")
        return
    question = " ".join(sys.argv[1:]) or "What do users say about confusing instructions?"
    print(f"\nQuestion: {question}\n" + "-" * 60)
    print(asyncio.run(ask(question)))


if __name__ == "__main__":
    main()

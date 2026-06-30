"""
Run the Design Research Synthesis Agent on a text file of research notes.

Usage:
    python run_synthesis.py sample_interview_notes.txt

Requires a free Google Gemini API key in a .env file (see .env.example).
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from synthesis_agent.agent import root_agent

load_dotenv()  # loads GOOGLE_API_KEY (and friends) from .env

APP_NAME = "design_research_synthesis"
USER_ID = "designer"


# --- A small security guard --------------------------------------------
# Basic input hygiene before anything reaches the model:
#   - cap the input size so a huge file can't run up cost or hang the run
#   - the agents themselves are instructed to treat notes as DATA, not
#     commands, which mitigates prompt-injection hidden inside uploaded notes.
MAX_CHARS = 20_000


def sanitize(raw: str) -> str:
    text = raw.strip()
    if not text:
        raise ValueError("The notes file is empty.")
    if len(text) > MAX_CHARS:
        print(f"[guard] Notes were long, truncating to {MAX_CHARS} characters.")
        text = text[:MAX_CHARS]
    return text


async def synthesize(notes: str) -> dict:
    """Run the 3-agent pipeline once and return each stage's output."""
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )

    message = types.Content(role="user", parts=[types.Part(text=notes)])

    # Drive the pipeline. Each sub-agent runs in turn; we just let it finish.
    async for event in runner.run_async(
        user_id=USER_ID, session_id=session.id, new_message=message
    ):
        if event.author and event.is_final_response():
            print(f"[done] {event.author}")

    # Each agent saved its result into shared session state via output_key.
    final = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session.id
    )
    return {
        "pain_points": final.state.get("pain_points", ""),
        "themes": final.state.get("themes", ""),
        "personas": final.state.get("personas", ""),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_synthesis.py <notes_file.txt>")
        sys.exit(1)

    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set.")
        print("Copy .env.example to .env and paste your free key from")
        print("https://aistudio.google.com/apikey")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        notes = sanitize(f.read())

    results = asyncio.run(synthesize(notes))

    def section(title, body):
        print("\n" + "=" * 64)
        print(title)
        print("-" * 64)
        print(body.strip() or "(empty)")

    section("PAIN POINTS", results["pain_points"])
    section("THEMES", results["themes"])
    section("PERSONAS", results["personas"])
    print("=" * 64 + "\n")


if __name__ == "__main__":
    main()

"""
The enhanced multi-agent system: a coordinator that routes between two paths.

         ┌─────────────── research_coordinator (router) ───────────────┐
         │                                                             │
   new notes to synthesise                          question about past research
         │                                                             │
         v                                                             v
  design_research_synthesis                                  research_librarian
  (Extractor->Clusterer->Persona)                       (searches the vector DB)

The coordinator is an LlmAgent that reads each request and TRANSFERS control to
the right specialist based on their descriptions. The librarian uses the
ChromaDB-backed `search_research_memory` tool (RAG) to answer across studies.
"""

from google.adk.agents import LlmAgent

from synthesis_agent.agent import build_pipeline, MODEL
from research_memory.memory import search_research_memory


def build_librarian() -> LlmAgent:
    """A standalone librarian agent (used by ask_memory.py)."""
    return LlmAgent(
        name="research_librarian",
        model=MODEL,
        description=(
            "Answers questions about insights across PAST user-research studies "
            "stored in memory."
        ),
        instruction=(
            "You are a research librarian. When asked what users have said across "
            "past studies, ALWAYS call the search_research_memory tool with a "
            "focused query first, then answer using ONLY what it returns. Name the "
            "study each point came from. If nothing relevant is found, say so."
        ),
        tools=[search_research_memory],
    )


def build_coordinator() -> LlmAgent:
    """The router that ties the synthesis pipeline and the librarian together."""
    return LlmAgent(
        name="research_coordinator",
        model=MODEL,
        description="Routes design-research requests to the right specialist.",
        instruction=(
            "You coordinate a design-research assistant. Decide what the user needs "
            "and transfer to exactly one specialist; do not answer yourself.\n"
            "- If the user pastes NEW interview notes to be analysed, transfer to "
            "'design_research_synthesis'.\n"
            "- If the user asks a question about PAST research or what users have "
            "said across studies, transfer to 'research_librarian'."
        ),
        sub_agents=[build_pipeline(), build_librarian()],
    )


# ADK discovers this when you run `adk web` on the research_memory package.
root_agent = build_coordinator()

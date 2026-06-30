# Enhanced Version — Research Memory + Coordinator (vector DB + more agents)

This builds on the original 3-agent synthesis pipeline by adding a **vector
database (ChromaDB)** of past studies and **two more agents**, tied together by
a coordinator that routes each request.

## What's new

```
                  ┌──────────── research_coordinator (router) ────────────┐
                  │                                                       │
        "synthesise these new notes"                  "what did users say about X?"
                  │                                                       │
                  v                                                       v
       design_research_synthesis                              research_librarian
       (Extractor → Clusterer → Persona)                  (searches the vector DB)
                                                                  │
                                                                  v
                                                   ChromaDB memory of PAST studies
```

- **research_librarian** — a new agent that answers questions *across all past
  studies* by calling a retrieval tool (`search_research_memory`).
- **research_coordinator** — a router agent that reads each request and hands it
  to the right specialist (synthesis vs. librarian).
- **ChromaDB vector store** — past study notes are chunked, embedded with
  Gemini, and stored on disk so they can be searched by meaning, not keywords.

## Concepts now demonstrated
- **Multi-agent system (ADK)** — a coordinator routing to a sequential pipeline
  and a tool-using librarian (5 agents total).
- **Retrieval-Augmented Generation (vector DB)** — ChromaDB + Gemini embeddings.
- **Security features** — input sanitisation + injection-resistant instructions.
- **Deployability** — runs as scripts, a Streamlit app, and `adk web`.

## Setup (in addition to the base setup)

Install the extra dependency (already in `requirements.txt`):
```
pip install -r requirements.txt
```

## Run it

**1. Load the past studies into the vector DB (run once):**
```
python ingest_memory.py
```
This reads every file in `past_studies/` and stores it in a local ChromaDB
folder (`research_memory_db/`, which is git-ignored).

**2. Ask a question across all past studies (the RAG path):**
```
python ask_memory.py "what have users said about confusing instructions?"
```
The librarian searches the vector DB and answers, naming which study each point
came from — pulling related insights from *different* studies at once.

**3. Run the full coordinator with the web UI:**
```
adk web
```
Pick `research_memory` from the dropdown. Paste new notes → it routes to the
synthesis pipeline. Ask about past research → it routes to the librarian.

## Files added
```
research_memory/
├── memory.py      # ChromaDB store + Gemini embeddings + search tool
└── agent.py       # librarian agent + coordinator (router)
past_studies/      # sample past studies to load into memory
ingest_memory.py   # one-time loader for the vector DB
ask_memory.py      # CLI to query past research
```

## Notes
- The vector DB (`research_memory_db/`) is created on disk and git-ignored, so
  no data or keys are committed.
- Embeddings use the same `GOOGLE_API_KEY`; no separate service is needed.
- If your machine has trouble installing ChromaDB on a very new Python version,
  create the project's virtual environment with Python 3.12 (ChromaDB has the
  widest wheel support there).

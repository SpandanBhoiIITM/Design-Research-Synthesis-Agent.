# Design Research Synthesis Agent

Turn messy user-research notes into structured design insight — pain points, themes, and personas — in one run, and search across all your past studies by meaning.

Built for the **Kaggle AI Agents: Intensive — Vibe Coding Capstone** (Track: Agents for Good / Freestyle).

<img width="1875" height="902" alt="image" src="https://github.com/user-attachments/assets/3971cf31-570a-4074-b1da-91b13bec2ca6" />

> `![Design Research Hub](docs/screenshot.png)`

---

## The problem

After user interviews, designers spend hours on synthesis: reading every transcript, pulling out pain points, grouping them into themes (affinity mapping), and writing personas. It's slow, manual, and the part of research everyone dreads. This agent does that first pass automatically, so the designer spends their time on judgement and ideas instead of sorting notes.

## Why agents?

Synthesis isn't one task — it's a sequence of distinct reasoning steps, each depending on the last. That maps cleanly onto a multi-agent pipeline: one agent extracts, the next clusters, the next builds personas. Each is a small specialist with a single job, and they hand work to each other through shared state. That's more reliable and easier to explain than one giant prompt trying to do everything at once.

---

## What's inside

The project has two parts:

**1. The synthesis pipeline** — three agents run in order to process a single set of notes:

```
   Your research notes
           |
           v
   [ 1. Extractor ]        finds pain points + quotes   -> state["pain_points"]
           |
           v
   [ 2. Clusterer ]        groups them into themes       -> state["themes"]
           |
           v
   [ 3. Persona builder ]  turns themes into personas    -> state["personas"]
           |
           v
   Design insights, ready to use
```

**2. The research memory (RAG)** — a searchable memory of past studies:

- Past studies are chunked, embedded with Gemini, and stored in a local **ChromaDB** vector database.
- A **research librarian** agent answers questions across all past studies by meaning (not keywords), citing which study each point came from.
- A **research coordinator** agent routes each request — new notes go to the synthesis pipeline, questions go to the librarian.

So five reasoning agents in total: three in the synthesis pipeline, plus the librarian and coordinator in the memory layer.

---

## Tech stack

- **Google Agent Development Kit (ADK)** — multi-agent orchestration
- **Gemini** — `gemini-2.5-flash` for reasoning, `gemini-embedding-001` for embeddings (free tier)
- **ChromaDB** — local vector database for semantic search over past studies
- **Streamlit** — web frontend

---

## Setup

You need **Python 3.12** (ChromaDB has the widest support there) and a free Google Gemini API key.

**1. Get a free API key**
Go to https://aistudio.google.com/apikey and create a key. If your key creation is blocked on a school/institutional account, use a personal Gmail account instead.

**2. Install dependencies**

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Mac / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Add your key**
Copy `.env.example` to a new file named `.env` and paste your key in (no quotes, no spaces):
```
GOOGLE_API_KEY=your_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```
`.env` is git-ignored, so your key never gets committed. Never put your key directly in the code.

---

## Run it

**Step 1 — build the research memory (run once).**
This loads the studies in `past_studies/` into the local vector database. Do this before using the RAG tab.
```
python ingest_memory.py
```

**Step 2 — launch the app.**

Windows (PowerShell):
```powershell
python -m streamlit run app.py
```

Mac / Linux:
```bash
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501` with two tabs:

- **New Synthesis** — upload a `.txt` of interview notes or paste them in, and generate pain points, themes, and personas.
- **Research Memory (RAG)** — ask questions across your past studies and get answers that cite their source study.

### Other ways to run it

Command line synthesis (good for a quick demo):
```
python run_synthesis.py sample_interview_notes.txt
```

Query past studies from the command line:
```
python ask_memory.py "what have users said about confusing instructions?"
```

Swap in your own research by replacing `sample_interview_notes.txt`, or drop new `.txt` files into `past_studies/` and re-run `python ingest_memory.py`.

---

## Project structure

```
design-research-synthesis-agent/
├── synthesis_agent/
│   ├── __init__.py         # lets ADK discover the agent
│   └── agent.py            # the 3 synthesis agents + the SequentialAgent pipeline
├── research_memory/
│   ├── __init__.py
│   ├── agent.py            # librarian + coordinator agents
│   └── memory.py           # ChromaDB + Gemini embeddings (RAG)
├── app.py                  # Streamlit frontend
├── run_synthesis.py        # CLI synthesis runner + input security guard
├── ask_memory.py           # CLI research-memory query
├── ingest_memory.py        # loads past_studies/ into the vector DB (run once)
├── past_studies/           # sample past studies for the RAG memory
├── sample_interview_notes.txt
├── requirements.txt
├── .env.example            # template for your API key (copy to .env)
└── .gitignore
```

---

## Notes on security

- No API keys or secrets are committed — the key lives only in the git-ignored `.env`.
- Input is size-capped and sanitised before reaching the model, and each agent is instructed to treat notes as data, not commands — a guard against prompt injection hidden in uploaded files.
- The project runs entirely on the free Gemini tier and needs no external services beyond the model API.

---

## Troubleshooting

- **`GOOGLE_API_KEY not set`** — make sure `.env` exists (not `.env.example`), the line starts with `GOOGLE_API_KEY=`, and there are no quotes or spaces.
- **`models/text-embedding-004 is not found`** — Google retired that model; this project uses `gemini-embedding-001`. Make sure `research_memory/memory.py` uses the current name.
- **`streamlit is not recognized`** (Windows) — run it through Python instead: `python -m streamlit run app.py`.
- **ChromaDB install trouble** — use Python 3.12, which has the widest wheel support.

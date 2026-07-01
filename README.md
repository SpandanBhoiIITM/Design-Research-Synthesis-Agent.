# Design Research Synthesis Agent

Turn messy user-research notes into structured design insight — pain points,
themes, and personas — in one run.

Built for the **Kaggle AI Agents: Intensive Vibe Coding Capstone**.
Track: *Agents for Good / Freestyle*.

---

## The problem

After user interviews, designers spend hours on synthesis: reading every
transcript, pulling out pain points, grouping them into themes (affinity
mapping), and writing personas. It's slow, manual, and the part of design
research everyone dreads. This agent does that first pass automatically, so
the designer spends their time on judgement and ideas instead of sorting notes.

## Why agents?

Synthesis isn't one task — it's a sequence of distinct reasoning steps, each
depending on the last. That maps perfectly onto a **multi-agent pipeline**:
one agent extracts, the next clusters, the next builds personas. Each is a
small specialist with a single job, and they hand work to each other through
shared state. That's cleaner, more reliable, and easier to explain than one
giant prompt trying to do everything at once.

## Architecture

A single ADK `SequentialAgent` runs three `LlmAgent` specialists in order.
Each writes its result into shared session state (`output_key`); the next
reads it back via `{key}` in its instruction.

```
   Your research notes
           |
           v
   [ 1. Extractor ]        finds pain points + quotes      -> state["pain_points"]
           |
           v
   [ 2. Clusterer ]        groups them into themes          -> state["themes"]
           |
           v
   [ 3. Persona builder ]  turns themes into personas       -> state["personas"]
           |
           v
   Design insights, ready to use
```

## Course concepts demonstrated

1. **Multi-agent system (ADK)** — a `SequentialAgent` orchestrating three
   `LlmAgent` specialists with state hand-off (`synthesis_agent/agent.py`).
2. **Security features** — input is size-capped and sanitised before reaching
   the model, and every agent is instructed to treat notes as *data, not
   commands* to resist prompt injection hidden in uploaded files
   (`run_synthesis.py`, `sanitize()` + agent instructions).
3. **Deployability** — runs locally as a script *and* ships with ADK's built-in
   web UI via `adk web` (see below), so it can be demoed or hosted with no
   extra code.

---

## Setup

You need **Python 3.10+** and a **free Google Gemini API key**.

### 1. Get a free API key
Go to https://aistudio.google.com/apikey and create a key (free tier is plenty).

### 2. Install dependencies

**Mac / Linux**
```bash
cd design-research-synthesis-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**
```powershell
cd design-research-synthesis-agent
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Add your key
Copy `.env.example` to a new file called `.env` and paste your key in:
```
GOOGLE_API_KEY=your_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```
> The `.env` file is git-ignored, so your key never gets committed. **Never put
> your key directly in the code.**

---

## Run it

**Option A — command line (great for the video demo):**
```bash
python run_synthesis.py sample_interview_notes.txt
```
It prints the pain points, themes, and personas in sequence.

**Option B — ADK web UI (nice visual demo):**
```bash
adk web
```
Then open the local URL it prints, pick `synthesis_agent`, and paste your notes
into the chat. You'll see each agent run in turn.

**Option C — Streamlit UI (Full Research Hub):**
```bash
streamlit run app.py
```
This opens a robust, multi-tab web application where you can:
- **Synthesize Notes**: Upload `.txt` files or paste your raw notes to instantly generate pain points, themes, and personas.
- **Research Memory (RAG)**: Upload past studies into a ChromaDB vector database and ask questions to search across all your historical user research using semantic meaning.

Swap in your own research by replacing `sample_interview_notes.txt` with any
plain-text notes.

---

## Project structure
```
design-research-synthesis-agent/
├── synthesis_agent/
│   ├── __init__.py        # lets ADK discover the agent
│   └── agent.py           # the 3 agents + the SequentialAgent pipeline
├── run_synthesis.py       # CLI runner + input security guard
├── app.py                 # Streamlit frontend app
├── sample_interview_notes.txt
├── requirements.txt
├── .env.example           # template for your API key (copy to .env)
├── .gitignore
├── WRITEUP.md             # draft Kaggle writeup
└── VIDEO_SCRIPT.md        # 5-minute demo video script
```

## Notes for judges
No API keys or secrets are committed. The agent runs entirely on the free
Gemini tier and needs no external services beyond the model API.

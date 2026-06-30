# Design Research Synthesis Agent

### An AI agent that does the synthesis grunt-work of user research, so designers can spend their time on insight instead of sorting sticky notes.

**Track:** Agents for Good / Freestyle

---

## The problem

Anyone who has run user interviews knows the wall that comes after fieldwork.
You have a dozen messy transcripts, pages of scribbled notes, and a daunting
job ahead: read all of it, pull out every pain point, group the related ones
into themes, and distil those into personas the team can actually design for.

This step — synthesis — is the heart of design research, and it is also the
slowest, most manual, most error-prone part of it. It is the classic
sticky-notes-on-a-wall exercise: hours of reading, highlighting, and
clustering before a single design decision can be made. Junior designers and
solo founders often skip it entirely because of the time cost, which means
they design from gut feeling instead of evidence.

We built an AI agent that does the *first pass* of synthesis automatically.
You give it raw research notes; it gives you back structured pain points,
themes, and personas in under a minute. The designer stays in control and
refines the output, but starts from a structured draft instead of a blank wall.

## Why an agent — and why multiple agents?

Synthesis is not a single task. It is a *sequence* of distinct reasoning steps,
each depending on the output of the last:

1. Read the raw notes and extract concrete pain points with supporting quotes.
2. Cluster those pain points into higher-level themes (affinity mapping).
3. Turn those themes into usable personas with goals and design questions.

A single large prompt could attempt all of this at once, but it would be
brittle: hard to debug, hard to steer, and prone to skipping steps. Splitting
the work across **specialist agents** mirrors how a real research team operates
— one person extracts, another clusters, another synthesises — and it gives us
a system where each stage has one clear responsibility and one clear output.

This is exactly what an agent pipeline is good at: decomposing a fuzzy human
workflow into discrete, reliable, inspectable steps.

## Architecture

The system is a single **`SequentialAgent`** (Google's Agent Development Kit)
that orchestrates three **`LlmAgent`** specialists in a fixed order. The agents
communicate through shared session state: each writes its result to a named key
via `output_key`, and the next reads it back by referencing that key in its
instruction.

```
   Raw research notes
          |
   [ Extractor ]        -> state["pain_points"]
          |
   [ Clusterer ]        -> state["themes"]
          |
   [ Persona builder ]  -> state["personas"]
          |
   Structured design insight
```

- **Extractor** plays the role of a UX research analyst. It reads the raw notes
  and returns a numbered list of distinct pain points, each with a verbatim
  supporting quote so insights stay traceable to real user voices.
- **Clusterer** plays a design strategist doing affinity mapping. It takes the
  pain points and groups them into three to five named themes.
- **Persona builder** plays a product designer. It turns the themes into one or
  two concise personas, each with goals, frustrations, and a "How Might We…"
  design question to kick off ideation.

Keeping each agent narrow makes the system easy to reason about and easy to
extend — adding a journey-map agent later is just one more link in the chain.

## Course concepts applied

We demonstrate three of the course's key concepts:

1. **Multi-agent system (ADK).** The core of the project is a `SequentialAgent`
   orchestrating three `LlmAgent` specialists, with state hand-off between them.
   This is the meaningful, central use of agents in our solution rather than a
   bolted-on feature.

2. **Security features.** User research often contains sensitive, free-form text
   from real people, and uploaded files are an untrusted input. We add a small
   security layer: input is size-capped and sanitised before it reaches any
   model, and every agent is explicitly instructed to treat the notes as *data,
   not commands*, which mitigates prompt-injection attempts hidden inside an
   uploaded transcript. We also keep all secrets out of the codebase — the API
   key lives only in a git-ignored `.env` file.

3. **Deployability.** The agent runs two ways with no extra code: as a
   command-line script for batch synthesis, and through ADK's built-in web UI
   via `adk web`, which exposes the same pipeline as an interactive app. This
   makes the project trivial to demo or host.

## How we built it

We built the pipeline with Google's Agent Development Kit in Python. The
hardest design decision was *how much* to split the work. We started with a
single prompt, found its output inconsistent and hard to steer, and refactored
into the three-agent chain — at which point each stage became dramatically
easier to test and tune in isolation.

The shared-state hand-off (`output_key` writing to state, the next agent
reading `{key}`) is what turns three separate prompts into one coherent system,
and it is the part we are most pleased with: it is simple, transparent, and you
can watch the insight build up stage by stage.

We tested with realistic interview data — a set of five mock usability
interviews for a meal-kit packaging redesign — to make sure the extractor
preserved real user quotes, the clusterer produced themes a designer would
recognise, and the persona builder produced personas grounded in the evidence
rather than invented from nothing.

## Value and who it helps

This is an **Agents for Good** tool for the design and research community:
students, solo designers, small startups, and non-profits who do user research
but lack the time or team to synthesise it properly. By collapsing hours of
manual clustering into a structured first draft, it lowers the barrier to
evidence-based design — so more decisions get made from real user voices
instead of assumptions.

## What's next

Natural extensions include a journey-mapping agent, an opportunity-sizing
agent that flags which themes affect the most users, and a connector that
pulls notes straight from a research repository. The sequential architecture
makes each of these a single additional link in the chain.

---

*No API keys or secrets are included in the codebase. The project runs on the
free Gemini tier.*

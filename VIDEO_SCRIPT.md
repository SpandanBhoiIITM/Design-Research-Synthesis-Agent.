# 5-Minute Video Script — Design Research Synthesis Agent

Total target: under 5:00. Record screen + voice. Keep it calm and clear —
judges reward clarity over flash. Practice once, then record.

Tip: have the terminal and the architecture diagram open in tabs before you
start so you're not fumbling.

---

## [0:00 – 0:40] The problem (hook)
> "If you've ever run user interviews, you know the worst part isn't the
> interviews — it's what comes after. You're left with a pile of messy notes,
> and you have to read all of it, pull out every pain point, group them into
> themes, and write personas. It takes hours, it's tedious, and a lot of people
> skip it — which means they end up designing from gut feeling instead of real
> evidence. So we built an agent that does that first pass for you."

## [0:40 – 1:20] Why agents
> "We could have written one big prompt, but synthesis isn't one task — it's a
> chain of steps, where each one depends on the last. Extract pain points,
> then cluster them, then build personas. That maps perfectly onto a multi-agent
> pipeline: three small specialist agents, each with one job, handing their work
> down the line. It's more reliable and far easier to steer than one giant
> prompt."

## [1:20 – 2:10] Architecture (show the diagram)
*(Show the architecture diagram on screen.)*
> "Here's the whole system. It's one ADK SequentialAgent running three agents in
> order. The Extractor reads the raw notes and pulls out pain points with real
> quotes. It saves that to shared state. The Clusterer reads those and groups
> them into themes — that's affinity mapping, automated. The Persona builder
> reads the themes and produces personas with goals and a 'How Might We'
> question. Each agent writes to shared state, and the next one reads it — that
> hand-off is what makes it a real multi-agent system."

## [2:10 – 3:40] Live demo
*(Switch to terminal. Run the command.)*
> "Let me show it. Here are five mock interviews about a meal-kit packaging
> redesign. I run one command…"
```
python run_synthesis.py sample_interview_notes.txt
```
*(As output appears, narrate.)*
> "First the Extractor returns the pain points — notice each one keeps a real
> quote from a user. Then the Clusterer groups them into themes like
> 'environmental guilt' and 'hard to organise'. And finally the Persona builder
> turns those into personas with goals, frustrations, and a design question.
> That's hours of synthesis in about thirty seconds."

## [3:40 – 4:30] The build & the smart bits
> "We built it with Google's Agent Development Kit in Python. Two things we're
> proud of. First, the shared-state hand-off — that's the trick that turns three
> prompts into one coherent system. Second, security: research notes are
> untrusted input, so we cap and sanitise the input, and we instruct every agent
> to treat notes as data, not commands, which blocks prompt-injection hidden in
> an uploaded file. And no API keys live in the code — they stay in a git-ignored
> file."

## [4:30 – 5:00] Value & close
> "This is a tool for students, solo designers, and small teams who do research
> but don't have time to synthesise it properly. It lowers the barrier to
> evidence-based design. It also deploys as a web app with one command, so it's
> ready to use today. Thanks for watching."

---

## Recording checklist
- [ ] Run the demo once before recording so output is fast and clean.
- [ ] Increase terminal font size so text is readable on video.
- [ ] Show the architecture diagram clearly during section 3.
- [ ] Keep it under 5:00 — trim the demo narration if you run long.
- [ ] Upload to YouTube as Public or Unlisted, then attach the link.

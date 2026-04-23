# AI 201 — Week 4: AI Safety & Guardrails

## Instructor Demo Guide

This repo powers the Week 4 live demo: building a multi-layer content moderation system for a Discord server dedicated to Kendrick Lamar fans. Students watch you write the LLM filter from scratch while the other layers are pre-built and narrated.

---

## Notebooks

| Notebook | Purpose |
|---|---|
| `demo_starter.ipynb` | **Use this in class.** Pre-built layers + one live coding cell. |
| `demo_solution.ipynb` | Complete reference. All cells implemented. |

---

## What You'll Build Live

Only one cell is written live — the LLM filter (~3 min). Everything else is pre-built; you run and narrate it.

| Layer | What It Does | In Class |
|---|---|---|
| Rate limiter | Stops volume abuse | Pre-built, narrate |
| Input validation | Keyword + length checks | Pre-built, narrate |
| Injection defense | Blocks prompt manipulation | Pre-built, narrate |
| **LLM content filter** | **Handles edge cases** | **✍️ Write live** |

**Total demo time: ~10 minutes.**

---

## Setup (Do This Before Class)

### 1. Get an OpenRouter API Key

Go to [openrouter.ai/keys](https://openrouter.ai/keys) and create a free account. Copy your API key.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your API key

```bash
cp .env.example .env
```

Open `.env` and replace `your_openrouter_api_key_here` with your actual key.

### 4. Verify everything works

```bash
python setup/verify_setup.py
```

You should see:

```
[1/3] Checking test messages...
  ✓ clean: 4 messages
  ✓ obvious_violation: 4 messages
  ✓ edge_case: 5 messages
  ✓ injection: 5 messages
  ✓ raid: 15 messages

[2/3] Checking rate limiter...
  ✓ Per-user limit fires correctly at 3 messages
  ✓ Server-wide limit fired at message 11 of 12

[3/3] Checking OpenRouter LLM with JSON mode...
  ✓ LLM returned valid JSON: decision='allow', confidence='high'

✓ All checks passed. Open demo_starter.ipynb to begin.
```

### 5. Open the starter notebook

```bash
jupyter notebook demo_starter.ipynb
```

Run the setup cell. Do **not** run the live coding cell before class — students should see you write it.

---

## Repo Structure

```plaintext
ai201-week4-starter-repo/
├── data/
│   └── test_messages.py      # 5 scenario groups: clean, obvious, edge, injection, raid
├── layers/
│   ├── rate_limiter.py       # Sliding window rate limiter (pre-built)
│   └── logger.py             # Structured moderation log (pre-built)
├── utils/
│   └── llm.py                # OpenRouter client with JSON mode (pre-built)
├── setup/
│   └── verify_setup.py       # Pre-demo health check
├── demo_starter.ipynb        # ← Use in class
├── demo_solution.ipynb       # ← Complete reference
├── requirements.txt
├── .env.example
└── README.md
```

---

## Demo Script

### Hook (~30 sec) — Before opening the notebook

> "Discord mods burn out. Popular servers get hundreds of messages per hour and moderators are volunteers — they miss things, they get harassed, they quit. What if you could take the first pass off their plate? Not replace them, but handle the obvious stuff automatically, 24/7, in under a second. That's what we're building."

---

### Architecture (~1 min)

Draw or show:

```
Message → [Rate Limiter] → [Injection Defense] → [Input Validator] → [LLM Filter] → Decision
```

Two points to land:

- **Cheapest first.** Rate limiting costs nothing; LLM calls cost money. Filter as much as possible before the model sees anything.
- **Injection defense before LLM.** You never want a prompt injection to reach the model at all.

---

### Pre-built layers (~2 min) — Run and narrate

Run the COMMUNITY_RULES, validate_input, detect_injection, and moderate cells one at a time. For each, say what it does and why it runs where it does. Don't read the code line by line — just orient students to what's there.

Key narration for the injection defense cell:
> "This is pattern matching, not LLM reasoning. That's intentional — you don't want to use the thing that can be fooled to decide whether something is trying to fool it."

---

### Live Cell: LLM Filter (~3 min)

> "Now the smart layer. This handles the messages the keyword check can't — the ambiguous ones. Two functions: one that formats our community rules into a system prompt, and one that calls the model and returns a structured verdict."

Write `build_system_prompt()` and `llm_filter()` live.

Key point while writing the system prompt:
> "This prompt IS the safety policy. Every word matters. And notice: 'when in doubt, prefer allow.' False positives — banning legitimate messages — damage community trust more than an occasional miss. You tune this based on your community."

After writing, ask:
> "What would happen if we put the rules in the user turn instead of the system turn?"

---

### Demo Scenarios (~2 min)

Run the edge cases cell first. Before running:
> "What would you decide for each of these?"

Take a few answers, then run it and compare.

Run the injection cell. After:
> "Why can't we just tell the LLM to ignore injection attempts?"

---

### Wrap (~30 sec)

> "Four layers. The most expensive one runs last and only when everything else passes. That's the architecture — cheapest first, LLM last, injection defense before the model sees anything."

---

## Timing Guide

| Step | Content | Time |
|---|---|---|
| Hook | Setup the problem | 0.5 min |
| Architecture | Draw the pipeline | 1 min |
| Pre-built cells | Run and narrate all 4 layers | 2 min |
| Live code | LLM filter | 3 min |
| Scenarios | Edge cases + injection | 2 min |
| Wrap | One-sentence summary | 0.5 min |
| Buffer | Student questions | 1 min |
| **Total** | | **~10 min** |

---

## Troubleshooting

**`OPENROUTER_API_KEY not found`** — Make sure you copied `.env.example` to `.env` (not just edited the example file).

**`openai` module not found** — Run `pip install -r requirements.txt`.

**LLM returns different decisions each run** — Normal. Temperature is set to 0.1 for consistency but the model isn't deterministic. Edge cases may vary. The demo is designed so only edge cases have ambiguous results.

**Notebook kernel error** — Make sure you're running the correct Python environment (the one where you installed requirements).

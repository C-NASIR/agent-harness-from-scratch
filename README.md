# Build an AI Agent Harness from Scratch, by Hand

A customer service agent built step by step in plain Python and SQLite. No agent frameworks, no LangChain, no magic. Every piece of the harness is written by hand so you can see what is actually happening underneath.

This is the code for my YouTube series **[Build an AI Harness from Scratch, by Hand](https://www.youtube.com/playlist?list=PLRDzL3zlOIDE)**. There's a written walkthrough at [cnasir.dev/work/agent-harness](https://cnasir.dev/work/agent-harness).

## Why build it by hand

Frameworks make agents look like magic. Underneath, an agent is a loop: call the model, run the tools it asks for, feed the results back, and repeat. The hard parts are the engineering around that loop, like what the model sees, what gets saved, what happens when the conversation outgrows the context window, and how the agent finds information it no longer remembers. This repo builds each of those parts one lesson at a time.

## What it does

```
customer: can I return shoes I bought 10 days ago?
we are using --> search_knowledge_base tool
Yes. Shoes can be returned up to 30 days after purchase.
```

The agent can:
- look up orders (`get_order`)
- search the store's policy articles before it answers policy questions (`search_knowledge_base`)
- look up earlier parts of the conversation that have been compacted out of its context (`search_history`)
- remember everything across restarts, because every turn is saved to SQLite
- compact its own context when it gets close to the model's limit, without losing the full history

## How it works

```
             ┌──────────────── the agent loop (max 5 steps) ────────────────┐
customer ──▶ │ compact if needed ─▶ call model ─▶ tool calls? ─yes─▶ run tools │
             │        ▲                               │                 │    │
             │        └───────── add results ◀────────┼─────────────────┘    │
             └────────────────────────────────────────┼──────────────────────┘
                                                      no
                                                      ▼
                                       save history + context ─▶ answer
```

Two lists drive everything:

- **History** is every message and tool result, kept forever. It's the record.
- **Context** is what the model actually sees on the next call. It starts as a copy of the history, but it gets compacted when it grows too large.

Keeping them separate is the core idea. Compaction can shrink the context as much as it needs to, because nothing is ever lost from the history. When the agent needs something that has left its context, it calls `search_history` and looks it up. That's retrieval on demand.

**Compaction rules** (`src/services/model.py`): before each model call, the harness counts input tokens. At 75% of the window it compacts, but only at a clean boundary (the start of a turn, not in the middle of a tool exchange). At 95% it compacts no matter what. After compacting it checks there's still room for a full response, and fails loudly if there isn't.

## The lessons

Each lesson is a commit, so you can check out any point in the series and see the code as it was.

| # | Lesson | What gets built | Code |
|---|---|---|---|
| 1 | The agent loop | Setup, a first model call, tools and the call-act-observe loop | [`2478bd9`](https://github.com/C-NASIR/agent-harness-from-scratch/tree/2478bd9) |
| 2 | Structure | Split into agent, model, tools and prompt modules | [`c7ee9ef`](https://github.com/C-NASIR/agent-harness-from-scratch/tree/c7ee9ef) |
| 3 | Saving conversations to a database | SQLite persistence, so conversations survive restarts | [`4a8ad91`](https://github.com/C-NASIR/agent-harness-from-scratch/tree/4a8ad91) |
| 4 | Context compression | Token counting, soft and hard limits, history kept separate from context | [`4c27a1d`](https://github.com/C-NASIR/agent-harness-from-scratch/tree/4c27a1d) |
| 5 | Retrieval on demand | `search_history`, so the agent can look up what it no longer remembers | [`1751cc4`](https://github.com/C-NASIR/agent-harness-from-scratch/tree/1751cc4) |
| 6 | Retrieving external knowledge | A knowledge base of policy articles and `search_knowledge_base` *(video coming soon)* | [`83e5fb1`](https://github.com/C-NASIR/agent-harness-from-scratch/tree/83e5fb1) |

```bash
git checkout 4c27a1d   # jump to the end of lesson 4
git checkout main      # back to the latest
```

## Run it

You need Python 3.12+, [uv](https://docs.astral.sh/uv/) and an OpenAI API key.

```bash
git clone https://github.com/C-NASIR/agent-harness-from-scratch
cd agent-harness-from-scratch
echo "OPENAI_API_KEY=sk-..." > .env
uv run main.py
```

Type a message after `customer:` and `exit` to quit. Try the questions in `question.txt`. The SQLite database (`customer_service_agent_database.db`) is created on first run and loads the policy articles from `articles/`.

## Project layout

```
main.py                         entry point
src/PROMPT.py                   system instructions
src/db.py                       SQLite setup and knowledge-article loading
src/services/agent.py           the agent loop
src/services/model.py           model calls, token counting, compaction
src/services/tools.py           tool definitions and dispatch
src/services/internal_tools.py  search_history and search_knowledge_base
src/services/conversations.py   load and save history and context
src/services/knowledge_service.py
src/services/orders.py          a fake order system
articles/                       store policy articles (the knowledge base)
```

Search is plain keyword matching on purpose. It's simple enough to read in a minute, and it makes the retrieval step easy to see. Swapping in embeddings later only changes one function.

## Author

Abdinasir Muhumed (cnasir), a full-stack engineer who builds AI products end to end.
[cnasir.dev](https://cnasir.dev) · [YouTube](https://www.youtube.com/@cnasir) · [LinkedIn](https://www.linkedin.com/in/cnasir2) · [X](https://x.com/CNASIR2_0)

# Building agents with the Claude Agent SDK

One runnable example per module, in `agent_sdk_examples.ipynb`. Every code cell ends in an
`assert`, so a broken example fails the run instead of printing something plausible.

| Module | Example |
|---|---|
| 1 | The loop, branching on `stop_reason` — plus the three stopping rules that get it wrong |
| 2 | The same tools as an in-process MCP server; `tool_choice` auto / any / forced |
| 3 | A PreToolUse gate and ceiling that always run; a PostToolUse hook that normalises dates |
| 4 | Structured errors: retry a timeout, never retry a policy violation; empty is not failure |
| 5 | Fixed steps (prompt chaining) and a multi-part request split three ways |
| 6 | A coordinator with search, analysis and writing subagents, spawned in parallel |
| 7 | A scratchpad file, then `resume` and `fork_session` |
| 8 | An escalation handoff a human can act on without reading the conversation |
| — | Capstone: all of it on one message with four problems |

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # add your ANTHROPIC_API_KEY
jupyter lab agent_sdk_examples.ipynb
```

Run the cells in order: later modules reuse the tools, hooks and subagents defined earlier.
The Agent SDK runs the Claude Code CLI as a subprocess, so `npm i -g @anthropic-ai/claude-code`
has to have happened once.

The backend is three dicts (`CUSTOMERS`, `ORDERS`, `POLICY`) — nothing here touches a real service.
`setting_sources=[]` stops the SDK reading `CLAUDE.md`, skills and hooks from your machine, so the
notebook behaves the same on every laptop. `permission_mode="bypassPermissions"` stops a notebook
run hanging on a permission prompt; do not carry that into production.

The whole run is roughly 20 short API calls.

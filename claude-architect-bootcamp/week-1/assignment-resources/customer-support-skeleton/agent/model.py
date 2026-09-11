"""Two interchangeable model backends. GIVEN TO YOU.

The loop never learns which one it is talking to. It reads `response.stop_reason`
and `response.blocks`, and appends `response.history_content`.

LiveModel      calls the real Messages API. Needs ANTHROPIC_API_KEY.
ScriptedModel  replays a fixed sequence of assistant turns, so you can smoke-test
               the wiring, and write deterministic tests, without spending money.
               The tools, the gates and the tool results are all REAL in scripted
               mode: only the model's choice of what to call next is pre-written.

Your two submitted transcripts should come from LiveModel. ScriptedModel is for
tests and for the adversarial enforcement test, where you want the agent to
attempt something specific every single run.
"""

from __future__ import annotations

from dataclasses import dataclass, field

MODEL_ID = "claude-opus-5"
MAX_TOKENS = 16000


@dataclass
class Block:
    """A uniform read-only view of one assistant content block."""

    type: str
    text: str | None = None
    id: str | None = None
    name: str | None = None
    input: dict = field(default_factory=dict)


@dataclass
class AgentResponse:
    stop_reason: str
    blocks: list[Block]
    history_content: object  # appended verbatim to messages as assistant content

    @property
    def tool_uses(self) -> list[Block]:
        return [b for b in self.blocks if b.type == "tool_use"]

    @property
    def text(self) -> str:
        return "\n".join(b.text for b in self.blocks if b.type == "text" and b.text).strip()


class LiveModel:
    """The real thing. `pip install anthropic`, set ANTHROPIC_API_KEY."""

    name = "live"

    def __init__(self, model: str = MODEL_ID, max_tokens: int = MAX_TOKENS):
        import anthropic  # imported lazily so the scripted path needs no SDK

        self.client = anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens

    def create(self, *, system: str, tools: list[dict], messages: list[dict]) -> AgentResponse:
        # Thinking is on by default on claude-opus-5. Thinking blocks come back in
        # `content` and are appended to history unchanged along with everything
        # else, which is what the API expects on the next turn. Do not filter them
        # out of history.
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            tools=tools,
            messages=messages,
        )
        blocks = [
            Block(
                type=b.type,
                text=getattr(b, "text", None),
                id=getattr(b, "id", None),
                name=getattr(b, "name", None),
                input=getattr(b, "input", {}) or {},
            )
            for b in response.content
        ]
        return AgentResponse(
            stop_reason=response.stop_reason,
            blocks=blocks,
            history_content=response.content,
        )


class ScriptedModel:
    """Replays pre-written assistant turns against real tools and real gates.

    A turn is a dict shaped like a Messages API response:

        {"stop_reason": "tool_use",
         "content": [{"type": "text", "text": "..."},
                     {"type": "tool_use", "id": "toolu_1",
                      "name": "get_customer", "input": {"email": "..."}}]}
    """

    name = "scripted"

    def __init__(self, turns: list[dict]):
        self.turns = turns
        self.index = 0

    def create(self, *, system: str, tools: list[dict], messages: list[dict]) -> AgentResponse:
        if self.index >= len(self.turns):
            raise RuntimeError(
                f"the agent asked for turn {self.index + 1} but the script only has "
                f"{len(self.turns)}. The loop ran longer than the script expected."
            )
        turn = self.turns[self.index]
        self.index += 1

        content = turn["content"]
        blocks = [
            Block(
                type=b["type"],
                text=b.get("text"),
                id=b.get("id"),
                name=b.get("name"),
                input=b.get("input", {}) or {},
            )
            for b in content
        ]
        return AgentResponse(
            stop_reason=turn["stop_reason"],
            blocks=blocks,
            history_content=content,
        )

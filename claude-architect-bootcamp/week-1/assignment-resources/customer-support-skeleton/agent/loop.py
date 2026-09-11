"""The agentic loop. RUNS, BUT INCOMPLETE. Finishing it is Task 2.

What is here already: control flow driven by `stop_reason`, tool results appended
to history with matching `tool_use_id`, and a turn cap.

What is missing is marked with TODO, and each gap is a rubric line:

  A. Three stop_reasons are unhandled and fall through to a silent `break`, which
     is the same bug as parsing the text: the loop stops for a reason it did not
     understand.
  B. Only the FIRST tool_use block in a response is executed. That single line is
     why multi-concern handling does not work yet.
  C. The turn cap is currently doing the job of control flow. Decide what it is
     for, label it in a comment, and make its behaviour match the label.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from . import enforcement
from .errors import TRANSIENT, VALIDATION, fail
from .handlers import HANDLERS
from .model import AgentResponse, Block
from .session import Session
from .tools import TOOLS

MAX_TURNS = 12

SYSTEM_PROMPT = (
    "You are the customer support resolution agent for Ridgeline Home, a mid-size "
    "e-commerce retailer selling kitchen and homeware. You speak with customers directly.\n"
    "\n"
    "Work from the tools. Read each tool's description before choosing it, and read the "
    "structured result you get back: `errorCategory` and `isRetryable` tell you what to do "
    "next. When a customer raises several issues in one message, deal with all of them and "
    "answer once, at the end, in a single reply.\n"
    "\n"
    "Be warm, brief and concrete. Give real numbers, order IDs, refund IDs and ticket "
    "numbers rather than vague reassurance. Never promise an outcome you have not already "
    "obtained from a tool.\n"
    "\n"
    "# DO NOT ADD THE IDENTITY RULE OR THE $500 CEILING TO THIS PROMPT.\n"
    "# Both are graded on being enforced in code. See agent/enforcement.py."
)


class LoopError(RuntimeError):
    pass


@dataclass
class Result:
    final_text: str
    turns: int
    session: Session


def execute_tool(block: Block, session: Session, recorder=None) -> dict:
    """Run one tool_use block through the enforcement hook and its handler."""
    blocked = enforcement.intercept(block.name, block.input, session)

    if blocked is not None:
        # The handler is never called. This is the whole point of the hook.
        payload = blocked
    else:
        handler = HANDLERS.get(block.name)
        if handler is None:
            payload = fail(VALIDATION, f"There is no tool named '{block.name}'.")
        else:
            try:
                payload = handler(session, **block.input)
            except TypeError as exc:
                payload = fail(
                    VALIDATION,
                    f"Wrong arguments for {block.name}: {exc}. Check the tool's input schema.",
                )
            except NotImplementedError as exc:
                # Starter-only: remove once you have implemented every handler.
                payload = fail(TRANSIENT, f"Not built yet: {exc}")
            except Exception:
                # A tool must never raise into the loop.
                payload = fail(
                    TRANSIENT,
                    f"{block.name} failed unexpectedly. Retry once; if it fails again, "
                    "escalate to a human.",
                )

    session.log(
        event="tool_call",
        tool=block.name,
        input=block.input,
        ok=payload["ok"],
        category=payload.get("errorCategory"),
    )
    if recorder:
        recorder.tool_result(block, payload, blocked=blocked is not None)

    return {
        "type": "tool_result",
        "tool_use_id": block.id,  # must match the tool_use block it answers
        "content": json.dumps(payload),
        "is_error": not payload["ok"],
    }


def run_agent(
    *,
    user_message: str,
    model,
    session: Session,
    system: str = SYSTEM_PROMPT,
    tools: list[dict] | None = None,
    recorder=None,
) -> Result:
    tools = TOOLS if tools is None else tools
    messages: list[dict] = [{"role": "user", "content": user_message}]
    if recorder:
        recorder.user(user_message)

    turn = 0
    while turn < MAX_TURNS:
        turn += 1

        response: AgentResponse = model.create(system=system, tools=tools, messages=messages)
        if recorder:
            recorder.assistant(response, turn)

        # TODO (Task 2A): three stop_reasons you will meet in production are not
        # handled here, and each wants different behaviour:
        #
        #   max_tokens   the answer was cut off mid-thought. A truncated answer is
        #                not an answer, so returning it as though it were is worse
        #                than failing. What should happen?
        #   refusal      the model declined. Do not paper over it.
        #   pause_turn   a server-side tool paused the turn and it can be resumed.
        #                Different from both of the above.
        #
        # Also: `stop_sequence` is terminal, like end_turn. And anything you do not
        # recognise should be loud, not a silent fall-through to the break below.

        messages.append({"role": "assistant", "content": response.history_content})

        if response.stop_reason == "end_turn":
            return Result(final_text=response.text, turns=turn, session=session)

        if response.stop_reason == "tool_use":
            # TODO (Task 2B): this executes only the FIRST tool_use block, and
            # drops the rest on the floor. When a customer raises two issues in one
            # message, Claude asks for two lookups in a single assistant turn, and
            # right now the second one silently never happens.
            #
            # Execute EVERY tool_use block in the response, and append ALL the
            # tool_result blocks in a SINGLE user message. Splitting them across
            # several user messages is its own bug: it teaches the model to stop
            # batching calls, which is exactly the behaviour multi-concern handling
            # depends on.
            first = response.tool_uses[0]
            results = [execute_tool(first, session, recorder)]
            messages.append({"role": "user", "content": results})
            if recorder:
                recorder.tool_results_appended(len(results))
            continue

        break  # unrecognised stop_reason. See Task 2A: this should not be silent.

    # TODO (Task 2C): you arrive here two ways: the loop ran out of turns, or it hit
    # an unhandled stop_reason. Right now both look like a normal answer to the
    # caller, which means the turn cap is acting as your termination mechanism.
    # A cap is a safety net. Decide what a safety net should do when it catches
    # something, label it as one in the comment above MAX_TURNS, and make this
    # behave accordingly.
    return Result(final_text=response.text, turns=turn, session=session)

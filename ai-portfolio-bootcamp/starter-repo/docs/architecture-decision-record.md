# ADR <N>: <the decision in a short phrase>

> AI Engineer track. One ADR per significant decision. Keep them short and keep
> the rejected options - the rejected options are the evidence of judgment.

- **Status:** Accepted | Superseded by ADR <n>
- **Date:** <YYYY-MM-DD>

## Context

<What forced a decision. The constraint, the requirement, or the failure that
made the status quo untenable. Two to four sentences.>

## Decision

<What you decided, in one sentence, in the active voice.>

## Options considered

| Option | Why not |
| --- | --- |
| <Agent loop> | <Step count never varies; the loop would be decoration> |
| <RAG over past tickets> | <No retrieval need; the ticket text is self-contained> |
| **<Single structured-output call>** | **<Chosen: matches the actual shape of the task>** |

## Consequences

**Good:** <what this buys you>

**Bad:** <what it costs you, honestly - every real decision has a cost>

**Revisit when:** <the concrete signal that would make you change your mind>

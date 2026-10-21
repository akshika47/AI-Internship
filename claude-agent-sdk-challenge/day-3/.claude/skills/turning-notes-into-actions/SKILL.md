---
name: turning-notes-into-actions
description: Turns raw meeting notes into a clean list of actions, decisions and open questions. Use when given meeting notes, a call transcript or a stand-up summary. Don't use it for writing minutes in full or summarising documents that aren't a meeting.
---

# Turning notes into actions

## Rules
1. **An action has an owner and a date, or it isn't an action.** If the notes don't name
   one, write "owner: not stated" or "due: not stated". Never guess a name.
2. **Start each action with a verb**: "Email beta users about the new date", not "Beta users".
3. **Decisions are separate from actions.** A decision is something agreed, not something to do.
4. **Open questions get their own list**, so nothing unresolved hides inside an action.
5. Keep the speaker's words for anything with a number or a date.

## Output
```
## Decisions
- ...
## Actions
| Action | Owner | Due |
## Open questions
- ...
```

## Example
Notes: "Tom: webhook still failing, I'll pair with Sam tomorrow. We agreed launch moves to 28 Oct."
→ Decision: Launch moves to 28 Oct. · Action: Fix the failing webhook | Tom, with Sam | tomorrow

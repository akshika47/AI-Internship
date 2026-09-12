# Discovery and deployment plan

> FDE track. Two halves: what you learned before building, and how it reaches
> production.

## Part 1 - Discovery

### Who I spoke to

| Role | What I was trying to learn |
| --- | --- |
| | |

### What I found that changed the plan

<The thing you did not expect. If nothing surprised you, you did not do
discovery, you did requirements gathering.>

### Constraints I inherited

- **Data:** <what exists, what format, how much, who owns it>
- **Systems:** <what this has to talk to>
- **Policy:** <what is not allowed, and who says so>
- **People:** <who has to change their workflow for this to work>

### What I scoped out, and who agreed

| Cut | Why | Agreed with |
| --- | --- | --- |

## Part 2 - Deployment plan

### Rollout

| Stage | Who | Success signal | Rollback trigger |
| --- | --- | --- | --- |
| Shadow | - | Outputs logged, not shown | - |
| Pilot | <5 users> | <metric> | <metric falls below x> |
| General | <all> | <metric> | <metric falls below x> |

### What breaks it

| Failure | Blast radius | Detection | Response |
| --- | --- | --- | --- |

### Handover

<What the receiving team needs to run this without you. Be specific: runbook,
dashboard, on-call, who owns the prompt.>

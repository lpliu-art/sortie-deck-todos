# Design docs

This tree holds **product / system design** (why we built it this way). Module guides under [Modules](../modules/auth.md) cover implementation plans.

## Contents

| Doc | What it covers |
|-----|----------------|
| [Goals & non-goals](goals.md) | Problem statement and boundaries |
| [Pipeline & graph](pipeline-and-graph.md) | Planning, parallel branches, artifact contracts |
| [Human-in-the-loop](human-in-the-loop.md) | Gates, confirmation, permission modes |
| [Threat model](threat-model.md) | Trust boundaries and security assumptions |
| [ADRs](adr/index.md) | Significant technical decisions |

Architecture overview: [architecture/overview.md](../architecture/overview.md). Product backlog: [`TODO.md`](../../TODO.md).

## Suggested reading order

1. Goals & non-goals  
2. Architecture overview + data flow  
3. Pipeline & graph, HITL  
4. ADRs as needed  

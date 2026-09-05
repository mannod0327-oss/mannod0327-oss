---
description: Write an ECC status or handoff report separating what was verified from what was not.
argument-hint: [audience or context, e.g. "handoff" or "weekly status" — optional]
---

Write an ECC report on the current work.

Context: $ARGUMENTS

Read `${CLAUDE_PLUGIN_ROOT}/skills/ecc/references/reporting.md` and follow its structure: status, what changed, verified, not verified, blockers, next.

Before writing, establish the facts — check git state, run the relevant checks, and read their output. Do not report from memory of what you did earlier; evidence must be current.

Every verified claim names its evidence and when it was gathered. The "not verified" section is mandatory; write "nothing outstanding" only if that is literally true. Redact client-confidential and personal data if this report leaves its authorized audience.

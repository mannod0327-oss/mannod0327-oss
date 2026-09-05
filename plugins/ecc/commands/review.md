---
description: Review a change against ECC standards before it ships.
argument-hint: [diff, branch, PR number, or path — defaults to the working tree]
---

Review this change to the ECC standard.

Target: $ARGUMENTS

If no target was given, review the uncommitted working tree and the commits on the current branch that are not on the default branch.

Read `${CLAUDE_PLUGIN_ROOT}/skills/ecc/references/review.md`, `${CLAUDE_PLUGIN_ROOT}/skills/ecc/references/policy.md`, and `${CLAUDE_PLUGIN_ROOT}/skills/ecc/references/stack.md`.

Get the actual diff first. Then read the tests, then the surrounding code the diff assumes — do not review from the diff alone.

Report blocking findings first, each with file and line, what breaks, and a concrete input that breaks it. Then non-blocking observations, labelled as such. If the gate passes cleanly, say so plainly and name what you ran to establish it.

Do not modify files unless asked to fix what you found.

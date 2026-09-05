---
description: Scope an ECC request into verifiable acceptance criteria before any work begins.
argument-hint: [the request, or a path/issue reference]
---

Scope this request to the ECC intake standard. Do not implement anything yet.

Request: $ARGUMENTS

Read `${CLAUDE_PLUGIN_ROOT}/skills/ecc/references/intake.md` and follow it. Read `${CLAUDE_PLUGIN_ROOT}/skills/ecc/references/policy.md` if the request touches credentials, client or personal data, money, or an outward-facing surface.

If no request was given above, ask what is being scoped rather than guessing.

Inspect the repository before writing criteria — existing tests, interfaces, and conventions decide what "verifiable" means here. Then produce: outcome, in scope, out of scope, numbered acceptance criteria each naming its evidence, constraints, and open questions.

End by stating which open questions block implementation and which do not.

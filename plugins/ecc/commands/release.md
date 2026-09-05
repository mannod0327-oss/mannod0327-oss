---
description: Run the ECC release sequence — checks, regeneration, version, changelog, package, approval, tag, verify.
argument-hint: [version, or "patch" | "minor" | "major"]
---

Run the ECC release sequence.

Version intent: $ARGUMENTS

Read `${CLAUDE_PLUGIN_ROOT}/skills/ecc/references/release.md` and follow its steps in order. Read `${CLAUDE_PLUGIN_ROOT}/skills/ecc/references/policy.md` — publishing is an outward-facing, hard-to-reverse action.

Work through steps 1 to 6 and report the result of each with its actual output. Then stop at step 7 and present, for explicit approval: the version, the changelog entry, the artifact contents, and the publish destination.

Do not tag, push a tag, or publish until that approval is given in this conversation. If any earlier step fails, stop there and report the cause — do not continue and do not re-run hoping for a different result.

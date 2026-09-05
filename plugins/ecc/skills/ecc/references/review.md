# ECC Review

Review the change, not the author. Every finding names a file and line, states what breaks, and gives a concrete failing case. A finding you cannot make concrete is a question, so ask it as one.

## Gate — blocks the merge

1. **Policy.** No secret in the diff. No unapproved destructive, outward-facing, or spending action. No client or personal data in code, fixtures, or logs. Read `references/policy.md`.
2. **Correctness.** Walk the changed paths with real inputs — empty, missing, malformed, boundary, concurrent, and the failure path of every external call. Name the input that breaks it.
3. **Evidence.** The relevant tests were run after the change and their output was read. New behavior has a test that fails without the change.
4. **Scope.** The diff does what the acceptance criteria asked and does not quietly do more. Unrelated changes are split out.
5. **Conventions.** Matches `references/stack.md` and the surrounding file.

## Non-blocking — raise, do not hold

Naming, duplication that is not yet a problem, a preference about structure, an idea for later. Say it is non-blocking so the author can judge.

## Order

Read the acceptance criteria, then the diff in full, then the tests, then the surrounding code the diff assumes. Re-read the diff adversarially once more before signing off: what input would make this fail in production?

## Rules

- Do not approve a change whose tests you have not seen pass.
- A failing check is never "flaky" without evidence — a second identical failure, or a green run on the same commit.
- Never skip, disable, or delete a test to get a green result. If a test is wrong, fix the test and say why in the pull request.
- Approving is a claim. It is subject to `references/policy.md` rule 4 like any other.

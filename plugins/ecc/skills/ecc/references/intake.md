# ECC Intake

Turn a request into something that can be verified before any code is written. Intake is finished when someone other than the author could tell whether the work succeeded.

## Produce

**Outcome.** One sentence, in the requester's terms, describing what is true after the work that is not true now.

**In scope.** What will be built or changed.

**Out of scope.** What will explicitly not be touched. This is the half that prevents scope creep — write it even when it feels obvious.

**Acceptance criteria.** Numbered, each independently checkable, each naming the evidence that settles it:

    1. `POST /invoices` with a missing `amount` returns 422 and does not write a row.
       Evidence: test `test_invoice_rejects_missing_amount` passes.

Not acceptance criteria: "works correctly", "is fast", "handles errors properly". If it cannot fail a check, it is not a criterion.

**Constraints.** Deadlines, systems that must not change, compatibility that must hold, data the work may not touch.

**Open questions.** What is genuinely undecided, and who decides it.

## Rules

- Do not start implementation while an open question would change the design. Ask it now.
- Where a question would not change the design, record the assumption and proceed — do not block on it.
- Anything touching credentials, client data, money, or an outward-facing surface is named at intake, not discovered at review. Read `references/policy.md`.
- An estimate is not a commitment until the acceptance criteria are agreed.
- If the request is already well-specified, say so and skip to the work. Intake is a tool, not a ritual.

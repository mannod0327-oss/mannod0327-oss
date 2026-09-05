# ECC Reporting

A report separates what was verified from what was not. That separation is the whole value; a report that blurs it is worse than none.

## Structure

**Status.** One line: what state the work is in. `Done`, `Blocked on X`, `In progress — N of M criteria met`.

**What changed.** Files, behavior, and interfaces — enough that the reader can find it without asking.

**Verified.** Each claim with the evidence behind it and when it was gathered:

    Verified: invoice validation rejects missing amount.
      Evidence: `pytest tests/test_invoice.py` — 14 passed, run after the final commit.

**Not verified.** Everything you did not check, and why. Untested paths, platforms not run, assumptions still standing. Never leave this section out; write "nothing outstanding" when that is true.

**Blockers.** What is stopping progress, what decision or access would unblock it, and who can give it.

**Next.** The single next action, or nothing if the work is finished.

## Rules

- Every completion word obeys `references/policy.md` rule 4. No exception for a status message, a stand-up note, or a chat reply.
- Report the outcome that happened, not the one intended. If tests failed, say so and paste the failure. If a step was skipped, say it was skipped.
- Do not pad with what you attempted. The reader wants state, not effort.
- No client-confidential or personal data in a report that leaves its authorized audience. Redact first.
- Uncertainty is stated once, plainly, and not hedged around every sentence.

# RC2 content audit — Turbo Reading, Reading Challenge 2 (units 1–20)

## Objective

The teacher asked for all 20 Reading Challenge 2 units to be reviewed from scratch
(the RC1 release shipped with many wrong questions and answers). The goal is to find every
place where an RC2 unit shows a wrong question, a wrong option, or accepts or rejects the wrong
answer, and to fix it in all three places: the student pages (DEMO and CONNECTED), and the
Supabase question bank that grades the CONNECTED pages. The sources of truth are the book
(`book.pdf`) and the official answer key (`key.pdf`, "Reading Challenge 2 2nd – Answer Key").

## Requirements

Scope: "questions, tests, tasks and their answers" (savollar, testlar, topshiriqlar va ularning javoblari).

- REQ-01 For every unit, the Vocabulary Preview answer in the page key equals the official key letter for items 1–6.
- REQ-02 For every unit, the Reading Comprehension answer equals the official key letter for items 1–5.
- REQ-03 For every unit, the Idiomatic Expressions accepted answer equals the official key text for items 1–3 (case, punctuation and apostrophe style ignored).
- REQ-04 For every unit, the Summary accepted answer equals the official key text for items 1–6.
- REQ-05 For every unit, the Listening answer equals the official key (a letter for choice items; the key's text or its gap-fill fragment for written items).
- REQ-06 For every unit, the Vocabulary & Idiom Review answer equals the official key letter for items 1–10.
- REQ-07 For every unit, the Grammar items that come from the book reproduce the book's grammar sentences, and the page key selects the option that makes the key's sentence.
- REQ-08 For every unit, each teacher-authored extra Grammar item has exactly one grammatically correct option, and the page key points to it (checked by a human-style review of all 60 items).
- REQ-09 Question stems and option texts of Vocabulary Preview, Reading Comprehension, Listening and Review match the book's wording (checked by fuzzy comparison; every difference is listed and judged).
- REQ-10 Every choice item's key index is within its option list, the item has no duplicate options, and each Vocabulary Preview option is used by exactly one item.
- REQ-11 Every cloze/text item has an accepted answer that fits its blank: the stem with the answer filled in is a sentence that appears in, or is consistent with, the book/key.
- REQ-12 The sample answers shown for Pre-Reading and Discussion equal the official key's sample answers.
- REQ-13 The Supabase bank (`reading_question_bank_v1`, `item_code LIKE 'RC2-%'`) has, for every unit, the same number of rows as the page's QCOUNT, and every row's `correct_answer`/`accepted_answers` equals the page key.
- REQ-14 Server grading gives 100 % on the objective items of every unit when the official answers are submitted (run through the real `turbo-reading-rc2-api` code locally).
- REQ-15 Every defect found by REQ-01…REQ-13 is fixed in the unit content, both page sets (DEMO + CONNECTED) are rebuilt, and the bank rows are updated, followed by a re-run of the audit with zero open defects.
- REQ-16 A written audit report lists every defect: unit, section, item, what was wrong, what it is now, and the source line that proves it.

## Out of scope

- Uzbek glossary translations, hero images, audio files, page design.
- The reading passage text itself (only used as evidence for REQ-11).
- RC1 pages and the RC1 bank.
- Deploying to Netlify (the teacher drags the rebuilt folder; the rebuilt files are delivered).

## Edge cases

- EDGE-01 The official key contains a typo (e.g. unit 2 grammar "Difference cultures"): the page keeps the correct form, and the report lists it as a key typo, not a page defect.
- EDGE-02 The key gives a written answer where the page uses a shorter gap-fill fragment (e.g. unit 2 listening): it passes when the fragment filled into the stem reproduces the key sentence.
- EDGE-03 The key and the book disagree (e.g. the key's letter points at an option that contradicts the passage): the report flags it for the teacher, and the page follows the passage, with the reason stated.
- EDGE-04 A multi-blank item (one bank row, several blanks): the accepted answer is the full fragment including the text between blanks, and grading accepts it.
- EDGE-05 A key letter that is outside the option range, or a missing key entry: reported as a defect, never silently mapped.

## Definition of done

- [x] REQ-01…REQ-07, REQ-10, REQ-12: `python3 audit.py` prints `0 defects` for each check id across 20 units.
- [x] REQ-08: the report contains the list of 60 extra grammar items with a verdict per item.
- [x] REQ-09, REQ-11: the report lists every fuzzy mismatch with a verdict (ok / fixed).
- [x] REQ-13: SQL comparison of the bank against the page keys returns 0 mismatched rows, and the per-unit counts equal QCOUNT.
- [x] REQ-14: the local grading run prints `objective 100%` for all 20 units.
- [x] REQ-15: after the fixes, `audit.py` re-run is clean, e2e page tests pass for 20 units, and the md5 of the bank rows matches the regenerated bank file.
- [x] REQ-16: the report file exists and is delivered to the teacher.
- [x] EDGE-01…EDGE-05: each case that occurs is named in the report with its handling.

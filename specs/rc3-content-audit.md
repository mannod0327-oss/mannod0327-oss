# RC3 units — Turbo Reading, Reading Challenge 3 (units 1–20)

## Objective

Build all 20 Reading Challenge 3 units as self-contained DEMO pages, using the same page engine as
RC2, with no wrong questions or answers. The RC1 release shipped with many content errors, so every
question, option and accepted answer is checked against two sources: the book
("Reading Challenge 3 2nd Ed", 130 pages, 40 audio tracks) and the official answer key.
Where the key contradicts the book, the page follows the book and the report says so.

## Requirements

- REQ-01 Vocabulary Preview key = official key letter, items 1–6, all units.
- REQ-02 Reading Comprehension key = official key letter, items 1–5.
- REQ-03 Idiomatic Expressions accepted answers include the official key text, items 1–3. Case, punctuation and apostrophe style are ignored. Multi-blank items (`con / into`) are accepted as the joined fragment.
- REQ-04 Summary:
  - cloze units: every blank's answer = key word, and the word bank = the set of answers;
  - paraphrase units: sample answers = key samples.
- REQ-05 Listening:
  - True/False and multiple choice = key;
  - written items: the stem with the answer filled in reproduces the key sentence.
- REQ-06 Vocabulary & Idiom Review key = official key letter, items 1–10.
- REQ-07 Grammar items taken from the book reproduce the book's sentences, and the page key picks the option that makes the key's sentence.
- REQ-08 Every teacher-authored extra Grammar item has exactly one correct option, and the key points to it (human review).
- REQ-09 Question stems and options match the book's wording.
- REQ-10 Structure checks:
  - every key index is in range;
  - no item has duplicate options;
  - Vocabulary Preview options form a permutation;
  - listening items are strings (not parser objects).
- REQ-11 Cloze and chart-summary text is consistent with the book, and idiom fills read as correct sentences (human review).
- REQ-12 Pre-Reading, Discussion and paraphrase sample answers = key samples. Corrections of key typos are listed.
- REQ-13 No text-extraction artefacts: broken hyphenation, private-use glyphs, stray page numbers, wrong dialog titles. Every English string is spell-checked.
- REQ-14 End-to-end browser test per unit:
  - hero, images and both audio tracks load;
  - the glossary works;
  - answering with the page key gives 100 % with 0 wrong marks and no console errors;
  - no horizontal scroll.
- REQ-15 A written report lists every correction and every key/book error found.

## Out of scope

- Supabase question bank and CONNECTED site for RC3 (next step, same as RC2).
- Audio quality, image cropping taste, Uzbek translation style.

## Edge cases

- EDGE-01 Key typo in a sentence the page reproduces: the page keeps the book form, and the report lists it.
- EDGE-02 Key answer that contradicts the book (U6 idioms): the page follows the book, and the audit marks it KNOWN, not DEFECT.
- EDGE-03 Book typo: corrected on the page through a named manual override, and listed.
- EDGE-04 Chart or timeline summaries (U2, 5, 8, 11, 14, 17, 20): converted into a cloze text, with facts checked against the book chart.

## Definition of done

- [x] `python3 audit/audit.py` → `DEFECTS: 0` (KNOWN: 2, both U6 official-key errors).
- [x] REQ-08 / REQ-11 review lists read in full (59 extra grammar items, 41 book grammar items, 60 idiom fills).
- [x] `audit/lint.py` and `audit/spell.py`: no remaining artefacts or misspellings (only proper nouns).
- [x] e2e: 20/20 units pass, objective score 100 %.
- [x] Report delivered: `specs/rc3-content-audit-report.md`.

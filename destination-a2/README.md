# Destination A2 practice

Interactive grammar and vocabulary practice for A2 learners, in the unit order of the *Destination A2* book:
42 units, a review after every three units and two progress tests (58 pages plus an index).
All exercises are original material, not copied from the coursebook.

*O'zbekcha:* Destination A2 kitobi tartibidagi 42 ta unit uchun interaktiv mashqlar. Har bir sahifa internetsiz ham ishlaydi.

## What a learner gets

- **Learner passport** on the index: stamps, XP, a day streak and a "Continue" button that remembers where you stopped.
- **Route map** of the book: units grouped into legs of three, each leg ending in a review; filters (grammar, vocabulary,
  reviews, "no stamp yet") and search.
- **Unit pages** styled as a boarding pass, with a sticky route of sections that ticks off what you have finished.
- **Instant feedback**: multiple-choice answers are marked the moment you choose; gap-fill answers are checked with Enter,
  and wrong ones show the right answer.
- **Build the sentence** (Exercise D): tap the words into the right order.
- **Word games** on vocabulary units: flip flashcards with pronunciation, and a timed English–Uzbek matching game.
- **Tests one question at a time**, with keys 1–3, a progress bar, a result card, stars and a passport stamp at 70% or more.
- **Speaking & writing** box that keeps your draft and can read it aloud.
- Sound effects (can be muted), light and dark theme, works on phones.

Progress is kept in the browser's `localStorage`, so it stays on that device and browser only.
Repeating an exercise never gives extra XP; only a better score does.

## Build

```sh
python build.py        # writes ./html (58 pages + index.html)
```

Requires Python 3.9 or newer; no packages. Open `html/index.html` in any browser. Pages are self-contained
(inline CSS and JS). Web fonts load from Google Fonts when online and fall back to system fonts offline.

## Edit the content

Unit data lives in `units_a.py` (units 1–14), `units_b.py` (15–28) and `units_c.py` (29–42):

- Grammar units have `lesson`: a list of `(heading, [lines])`. A line starting with `UZ: ` becomes an Uzbek note.
- Vocabulary units have `words`: `(english, uzbek, example sentence)` and a `tip`.
- `ex`: three exercises `(instruction, "mc" | "gap", items[, word bank])`.
  Multiple choice items are `(question with ___, [correct, wrong, wrong])`; options are shuffled at build time.
  Gap items are `(sentence with one ___, [accepted answers])`.
- `test`: ten multiple-choice items. `task`: the speaking and writing task.

`build.py` validates the data before writing anything (numbering, three options, one gap per sentence, enough
sentences for the word-order game) and stops with a message that names the unit.

## Test

```sh
python build.py
npm install playwright   # once
node tests/smoke.js
```

The smoke test plays every exercise type, test, game and the index filters in Chromium, checks the saved progress,
and loads all 59 pages at phone width with web fonts blocked to confirm there are no script errors and no sideways scrolling.

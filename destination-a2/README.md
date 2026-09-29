# Destination A2

An English grammar and vocabulary game for A2 learners, built from the 42 units of the *Destination A2* book.
All exercises are original material, not copied from the coursebook.

*O'zbekcha:* Destination A2 kitobining 42 ta uniti asosidagi o'yin. Laylak bilan Toshkentdan Sidneygacha sayohat:
har bir unitda 3 ta toj, har 3 unitdan keyin boss jangi, ikkita aeroport imtihoni, kunlik chaqiruv, Blitz va
xatolar ustida ishlash. Bitta `index.html` fayli internetsiz ham ishlaydi.

## How it plays

- **Short sessions (3–4 minutes).** One question at a time with a big answer button, instant green/red feedback,
  the correct sentence with pronunciation, and a combo counter. A missed question comes back at the end of the session.
- **Question types** made from the book content: multiple choice, listen and choose, word bank, type the answer,
  build the sentence, English–Uzbek word choice and a pairs-matching round for vocabulary units.
- **Three crown levels per unit:** 1 Tanishuv (choose), 2 Mashq (listen, word bank, mixed), 3 Usta (type it yourself).
- **Journey map of 14 cities** (Tashkent, Samarkand, Bukhara … Sydney). Every leg of three units ends with a
  **boss battle** (12 mixed questions, 3 lives) that stamps the city and shows a short "Did you know?" fact.
  **Airport exams** after units 21 and 42 (20 questions, pass at 70%).
- **Daily challenge:** the same 10 questions for everyone on the same day, so a class can compare results.
  The result is saved once and can be copied to share.
- **Blitz:** 60 seconds, answers checked on tap, personal record.
- **Mistakes review:** every missed question is saved and comes back until it is answered right.
- **Progression:** XP, levels and ranks, a daily XP goal with a streak, 16 badges, and Laylak the Bukhara stork
  reacting to answers. Interface language is Uzbek; the content is English.
- **Profile:** stats, badges, daily goal, sound, light/dark theme, a progress code to move to another device, and reset.

Progress lives in the browser's `localStorage`: it stays on that device and browser unless moved with the progress code.

## Build

```sh
python build.py        # writes ./html/index.html
```

Python 3.9 or newer, no packages. Open `html/index.html` in any browser. The page is self-contained
(inline CSS, JS and data, about 210 KB). Web fonts load from Google Fonts when online and fall back to system fonts offline.

## Edit the content

Unit data lives in `units_a.py` (units 1–14), `units_b.py` (15–28) and `units_c.py` (29–42):

- Grammar units have `lesson`: a list of `(heading, [lines])`. A line starting with `UZ: ` becomes an Uzbek note.
- Vocabulary units have `words`: `(english, uzbek, example sentence)` and a `tip`.
- `ex`: three exercises `(instruction, "mc" | "gap", items[, word bank])`.
  Multiple choice items are `(question with ___, [correct, wrong, wrong])`.
  Gap items are `(sentence with one ___, [accepted answers])`.
- `test`: ten multiple-choice items. `task`: the speaking and writing task (a bonus card on the unit screen).

The game uses these as follows: exercise A and the test feed multiple-choice, listening and exam questions;
the gap exercises feed the word bank and typing questions; full sentences (answers filled in, plus vocabulary
examples) feed the word-order game. Cities and their facts are in `CITIES` in `build.py`.

`build.py` validates the data before writing anything and stops with a message that names the unit.

## Test

```sh
python build.py
npm install playwright   # once
node tests/smoke.js
```

The smoke test plays through Chromium like a learner: a unit at each level (including wrong answers and their
retry), the mistakes review, a lost and a won boss battle, an airport exam, the daily challenge (and checks it is
identical in a second tab), a blitz with a fast-forwarded clock, the quit dialog, the unit screen, the profile
(theme, progress code export, reset and import), and every screen at 360 px phone width with web fonts blocked.

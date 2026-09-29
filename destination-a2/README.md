# Destination A2

An English grammar and vocabulary game for A2 learners, built from the 42 units of the *Destination A2* book.
All exercises are original material, not copied from the coursebook.

*O'zbekcha:* Destination A2 kitobining 42 ta uniti asosidagi o'yin. Laylak bilan Toshkentdan Sidneygacha sayohat:
28 ta grammatika va 14 ta lug'at uniti, har bir unitda 3 ta toj va 20 savollik unit testi (qog'oz varianti javoblar
kaliti bilan), 14 ta Review (boss jangi), 2 ta Progress Test, har bir shahar uchun suhbat sahnasi, kunlik chaqiruv,
Blitz, 4 ta so'z o'yini, seriya muzlatgichi va xatolarni oraliq takrorlash. Bitta `index.html` fayli internetsiz ham ishlaydi.
**O'qituvchi bo'limi** (`#teacher`): o'quvchiga butun o'yinni emas, faqat tanlangan unit va vazifalardan iborat alohida
HTML fayl yaratiladi; o'quvchi natija matnini kod bilan qaytaradi, o'qituvchi uni tekshiradi va sinf jadvalini oladi.

## How it plays

The book structure stays visible: **28 grammar units, 14 vocabulary units, 42 unit tests, 14 reviews, 2 progress tests**,
plus a story scene for each of the 14 cities.

- **Short sessions (3–4 minutes).** One question at a time with a big answer button, instant green/red feedback,
  the correct sentence with pronunciation, and a combo counter. A missed question comes back at the end of the session.
- **Question types** made from the book content: multiple choice, listen and choose, word bank, type the answer,
  build the sentence, **spot the error** (tap the wrong word), **dictation** (listen and write), English–Uzbek word
  choice and a pairs-matching round for vocabulary units.
- **Three crown levels per unit:** 1 Tanishuv (choose), 2 Mashq (listen, spot the error, word bank), 3 Usta (type, dictation).
- **Hint ladder** in practice: the first hint removes a wrong option (or gives the first letter, or places the first
  word); the second narrows it further. A hinted answer earns half the XP.
- **Confidence bet** ("Aniq bilaman ×2"): double XP if right, −5 XP if wrong; the result shows how well the learner
  judged their own knowledge.
- **Unit test for every unit:** 20 questions (the book's test items plus 10 new items per unit from `unit_tests.py`),
  none of which appear in practice. No feedback until the end, then a grade on the 5-point scale
  (86%+ = 5, 70%+ = 4, 55%+ = 3) and a list of every answer. Each test also has a **printable sheet with an answer key**.
- **Review = boss battle** after every three units: knock the city's dev (giant) down to zero HP. Every right answer hits,
  combos hit harder, a wrong answer costs one of three lives. **Power-ups** (50/50, +1 life) are earned with
  5 right answers in a row. Winning stamps the city and shows a "Did you know?" fact.
- **Story scene for each city** (`scenes.py`): a 5-line dialogue with Emma, a seller, a guide… built on that leg's grammar.
  Each line has one best reply, one with a typical grammar mistake and one that does not fit the talk; the learner gets
  coaching and tries again. It ends with a 45-second speaking task and a self-check list.
- **Progress Test 1 and 2** after units 21 and 42: 30 questions, pass at 70%, printable too.
- **Daily challenge:** the same 10 questions for everyone on the same day, so a class can compare results.
- **Blitz:** 60 seconds, answers checked on tap, personal record.
- **Word games** (vocabulary of the units the learner has started): *Xotira* (flip cards to pair English words with
  Uzbek meanings, stars by number of moves), *Harf jumbog'i* (build the word from scrambled letters, with a letter hint),
  *Yashirin so'z* (guess the word letter by letter from its Uzbek meaning, 6 lives) and *Omon qolish* (endless mixed
  questions until the third mistake). Physical keyboard works in all of them.
- **Streak freeze:** earned once per 5 days with the daily goal met (up to 2); it fills a missed day so the streak survives.
- **Spaced review of mistakes:** a missed question is due the same day, then 1 day and 3 days after each right answer;
  three right answers clear it.
- **Progression:** XP, levels and ranks, a daily XP goal with a streak, 20 badges, and Laylak the Bukhara stork
  reacting to answers. The profile lists the units with the most mistakes. Interface language is Uzbek; content is English.

## Teacher assignments

The teacher page (`#teacher`, linked at the bottom of the map and in the profile) turns a chosen slice of the course into
a separate file for students, so they do not get the whole game:

1. **Pick** units (per city or one by one), tasks (crown levels 1–3, unit test, review battle over the chosen units,
   story scenes of those cities, word games), the number of unit-test attempts (1, 2, 3 or unlimited), a title,
   an optional due date and a note. *Oldindan ko'rish* opens the student view in the same tab.
2. **Send** the downloaded `Topshiriq-….html` (about 150–250 KB, works offline) through Telegram or any messenger.
   It holds only the chosen units' data: no other units, no printable sheets, no answer keys. Students type their name,
   see a checklist of tasks, and play only those. While test attempts remain, a result shows which answers were wrong
   but not the right ones; an attempt counts as soon as it starts. With unlimited attempts the first score is reported too.
3. **Check.** The student copies a plain-text result (each task with its score, done count, average, time) that ends
   with a code. Pasting one or many results into *Natijalarni tekshirish* marks each as genuine, edited or unknown
   and builds a class table that copies into Excel.

The code is a hash of the result lines and a per-assignment secret kept in the teacher's browser, so checking works in the
browser that created the assignment (move it with the progress code). It catches an edited result text; it cannot stop a
student who edits the browser's storage, so treat it as a check, not a lock. Downloads need a normal browser: the file
cannot be saved from inside a sandboxed preview such as the claude.ai artifact view.

Progress lives in the browser's `localStorage`: it stays on that device and browser unless moved with the progress code.

## Where the ideas came from

Mechanics were chosen after reviewing open-source teaching projects and an evidence-based pedagogy library:

- Boss HP battle and power-ups: *Grammar Battle* / *Word Battle* in `Mohammed7765/English-master`.
- Dialogue scenes with coaching and a timed speaking finale: *Dialogue Theatre* in `invitationstudio6/english-teacher-hub`,
  and the Context → Anticipate → Enact → Reflect practice loop in `mit-teaching-systems-lab/threeflows`.
- Spot the error: `spot-mistakes.html` in `English-master`, and *erroneous-example-designer* in `GarethManning/education-agent-skills`.
- Hint ladder: Moodle's *interactive with multiple tries* quiz behaviour and *progressive-hint-ladder*.
- Confidence bet: Moodle's *certainty-based marking* and *confidence-calibration-check*.
- Spaced review: *spaced-practice-scheduler*; retrieval-first design: *retrieval-practice-generator*, *retrieve-first-gate*.
- Weak topics: the error taxonomy in `rafukei/EnglishAITeacherPlatform-`.
- Word games (memory, scramble, hidden word, survival): the games hub in `v1pper717/Destination-B1-quizes`.
- Streak freeze: the check-in freeze in `ava-agent/english-agent`.

## Build

```sh
python build.py        # writes ./html/index.html
```

Python 3.9 or newer, no packages. Open `html/index.html` in any browser. The page is self-contained
(inline CSS, JS and data, about 300 KB). Web fonts load from Google Fonts when online and fall back to system fonts offline.

## Edit the content

Unit data lives in `units_a.py` (units 1–14), `units_b.py` (15–28) and `units_c.py` (29–42); extra test items in
`unit_tests.py`; story scenes in `scenes.py`:

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

The smoke test plays through Chromium like a learner: a unit at each level (including wrong answers and their retry),
a passed and a failed unit test, the printable sheets (and that they are stable), spaced review over three simulated days,
a lost and a won boss battle, the hint ladder and confidence bet, a story scene, a progress test, the daily challenge
(and checks it is identical in a second tab), a blitz with a fast-forwarded clock, all four word games, a streak freeze, the quit dialog, the unit screen,
the profile (theme, progress code export, reset and import), the teacher flow (build and download an assignment file,
play it as a student with the name gate, blocked routes, level, test attempt limits and hidden answers, review battle,
result text, then verify genuine, edited and unknown results and the Excel table, preview and delete), and every screen
at 360 px phone width with web fonts blocked.

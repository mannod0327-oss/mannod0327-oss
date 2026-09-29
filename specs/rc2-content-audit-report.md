# RC2 audit hisoboti — Reading Challenge 2, Unit 1–20

Sana: 2026-09-29 · Spec: `specs/rc2-content-audit.md`

## Xulosa

- 20 ta unit tekshirildi: jami 882 ta savol, shundan 718 tasi avtomatik baholanadi.
- Solishtirish uchta manba asosida qilindi: kitob (`book.pdf`), rasmiy javoblar kaliti (`key.pdf`, "Reading Challenge 2 2nd – Answer Key") va Supabase'dagi savollar banki.
- Birorta ham noto'g'ri javob topilmadi. Vocabulary, Comprehension, Idiom, Summary, Listening, Review va kitobdagi Grammar savollarining hammasida sahifa kaliti rasmiy kalit bilan bir xil.
- **Bitta nuqson topildi va tuzatildi.** U7, Review 3-savol: variantlar `effects / problems / values / problems` edi, ya'ni "problems" ikki marta takrorlangan. Bu kitobning o'zidagi matbaa xatosi. d) variant `injuries` ga almashtirildi. To'g'ri javob o'zgarmadi: c) values.
- Rasmiy kalitlar bilan server baholash testi o'tkazildi: 20 ta unitning hammasida natija 100%.

## Talablar bo'yicha natija

| ID | Nima tekshirildi | Natija |
|---|---|---|
| REQ-01 | Vocabulary Preview (20×6) ↔ rasmiy kalit | ✅ 0 ta farq |
| REQ-02 | Reading Comprehension (20×5) ↔ kalit | ✅ 0 ta farq |
| REQ-03 | Idiomatic Expressions (20×3) ↔ kalit, jumladan muqobil shakllar (`is/was named after`, `is made (out) of`) | ✅ muqobillarning hammasi qabul qilinadi |
| REQ-04 | Summary: 14 ta cloze × 6 + 6 ta ochiq unitning namuna javoblari ↔ kalit | ✅ 0 ta farq |
| REQ-05 | Listening (60): True/False, test va yozma javob | ✅ 0 ta farq |
| REQ-06 | Vocabulary & Idiom Review (20×10) ↔ kalit | ✅ 0 ta farq |
| REQ-07 | Kitobdagi Grammar gaplari (40) ↔ kitob/kalit | ✅ sahifa kitob bilan bir xil; kalitdagi 5 ta matbaa xatosi quyida |
| REQ-08 | Qo'shimcha Grammar mashqlari (60), qo'lda o'qib chiqildi | ✅ har birida bitta to'g'ri variant bor va kalit shunga ishora qiladi |
| REQ-09 | Savol va variantlar matni ↔ kitob | ✅ hammasi kitobda bor (bittasi — yangi `injuries` — ataylab qo'shilgan) |
| REQ-10 | Tuzilish: kalit indeksi, takroriy variantlar, Vocabulary almashtirishi | ✅ U7 R3 tuzatilgandan keyin 0 ta |
| REQ-11 | Ibora gaplari to'ldirilgan holda (60) va Summary jadval → matn ko'chirmasi (7 unit) | ✅ kitob jadvallari rasm qilib ochildi va faktlar solishtirildi |
| REQ-12 | Pre-Reading/Discussion namuna javoblari ↔ kalit | ✅ 0 ta farq |
| REQ-13 | Supabase banki ↔ sahifalar: soni + javoblar | ✅ 882 ta qator; md5 4 ta partiyaning hammasida mos |
| REQ-14 | Rasmiy kalit javoblari real server kodi orqali | ✅ objective 100%, 20/20 unit |
| REQ-15 | Tuzatish → qayta tekshiruv | ✅ audit `0 defects`; U7 DEMO e2e 38/38, CONNECTED e2e 38/38 |
| REQ-16 | Ushbu hisobot | ✅ |

## Tuzatilgan nuqson

| Unit | Bo'lim | Savol | Oldin | Hozir | Dalil |
|---|---|---|---|---|---|
| 7 | Vocabulary & Idiom Review | 3 — "Her parents tried to teach her good ______." | a) effects b) problems c) values **d) problems** | d) **injuries** | Kitob, 46-bet: d) variant ham "problems" (takror). Kalit: 3. c |

Tuzatish kiritilgan joylar:
- `unit-7.html` (CONNECTED sayt);
- `Turbo_Reading_Challenge_2_Unit_7_Are_Sports_Bad_for_Kids_DEMO.html`;
- Supabase `RC2-U7-REVIEW-03.options`. Bazadagi 6–10-unitlar partiyasining md5 xeshi yangilangan bank fayli bilan mos: `4cc9e197…`.

## Kalitdagi matbaa xatolari (sahifada to'g'ri shakl qoldirildi, EDGE-01)

| Unit | Kalitda | Kitob va sahifada |
|---|---|---|
| 2 | "**Difference** cultures follow…" | "Different cultures follow…" |
| 3 | "As plates move away from…" | "As plates move **both** away from…" |
| 5 | "…there is no need **to be**." | "…there is no need to feel this way." |
| 12 | "first gift **of** life", "preference **of** dictated" | "first gift in life", "preference or dictated" |
| 17 | "switch **hand**" | "switch hands" |
| 20 | "car **theif**" | "car thief" |

## Qo'shimcha eslatmalar

- **Ko'p bo'sh joyli savollar (EDGE-04):** U6 I2–3, U7 I1–2, U8 L2, U11 L3, U17 I1, U20 I3, L2–3. O'quvchi yuborgan to'liq gap ham, qismlar ham qabul qilinadi. Bu server testida tekshirildi.
- **U4 Grammar 2:** variantlar `what / ,`, to'g'ri javob vergul. Bu kitobning o'zidagi mashq ("The truth is, eating…"), xato emas.
- **Summary jadvallari:** U2, U5, U8, U11, U14 kitobda jadval yoki timeline ko'rinishida. Sahifadagi matnga ko'chirma kitob rasmi bilan birma-bir solishtirildi, faktlar mos. U17 va U20 kalit javoblari asosida qurilgan.
- **Tekshiruv doirasidan tashqarida qolganlar:** o'zbekcha lug'at tarjimalari, rasmlar, audio sifati, o'qish matni.

## Qanday qayta tekshiriladi

Scratchpad'dagi `rc2/audit/` papkasidan:
- `python3 audit/audit.py` — natija `DEFECTS: 0` bo'lishi kerak.
- `deno run -A audit/grade_test.ts` — lokal API ishga tushirilgan holda; natija `REQ-14 PASS` bo'lishi kerak.

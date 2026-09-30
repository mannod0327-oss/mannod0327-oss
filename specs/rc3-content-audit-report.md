# RC3 hisoboti — Reading Challenge 3, Unit 1–20 (DEMO)

Sana: 2026-09-29 · Spec: `specs/rc3-content-audit.md`

## Xulosa

- 20 ta unit to'liq tayyorlandi.
  - Sahifa dvigateli, dizayni, lug'at, audio pleyer va natija kartasi RC2 bilan bir xil.
  - Jami 924 ta savol bor, shundan 766 tasi avtomatik baholanadi.
- Har bir savol, variant va javob ikki manba bilan solishtirildi:
  - kitob — "Reading Challenge 3 2nd Ed", 130 bet, 40 audio;
  - rasmiy javoblar kaliti.
- Avtomatik audit natijasi `DEFECTS: 0`. Brauzer testi (e2e) 20/20 unitda 100% berdi: 0 ta noto'g'ri belgi, konsolda xato yo'q.
- Qo'lda to'liq o'qib chiqildi:
  - 59 ta qo'shimcha grammar mashqi;
  - kitobdagi 41 ta grammar gapi;
  - 60 ta ibora gapi;
  - Pre-Reading, Discussion va Summary namuna javoblari (≈180 gap).

## Tekshiruv natijalari

| ID | Nima tekshirildi | Natija |
|---|---|---|
| REQ-01 | Vocabulary Preview (20×6) ↔ kalit | ✅ 0 ta farq |
| REQ-02 | Reading Comprehension (20×5) ↔ kalit | ✅ 0 ta farq |
| REQ-03 | Idiomatic Expressions (20×3) ↔ kalit | ✅ faqat U6 1–2 farq qiladi, sababi — kalitdagi xato (quyida) |
| REQ-04 | Summary: 14 ta cloze/jadval + 6 ta paraphrase | ✅ 0 ta farq |
| REQ-05 | Listening (60): True/False, test, yozma | ✅ 0 ta farq |
| REQ-06 | Vocabulary & Idiom Review (20×10) ↔ kalit | ✅ 0 ta farq |
| REQ-07 | Kitobdagi grammar gaplari (41) | ✅ sahifa kitob bilan bir xil; kalitdagi 3 ta matbaa xatosi quyida |
| REQ-08 | Qo'shimcha grammar (59), qo'lda | ✅ har birida bitta to'g'ri variant bor, faktlar matn bilan mos |
| REQ-09 | Savol va variantlar matni ↔ kitob | ✅ hammasi kitobda so'zma-so'z bor |
| REQ-10 | Tuzilish (indeks, takror variant, permutatsiya) | ✅ 0 ta |
| REQ-11 | Jadvaldan matnga ko'chirish (7 unit) + ibora gaplari (60) | ✅ faktlar kitob jadvali bilan mos |
| REQ-12 | Namuna javoblar ↔ kalit | ✅ kalitdagi 7 ta xato tuzatib ko'rsatildi (quyida) |
| REQ-13 | PDF'dan ajratishdagi izlar, imlo | ✅ 5 ta chiziqcha bo'linishi va 1 ta dialog nomi tuzatildi |
| REQ-14 | e2e brauzer testi | ✅ 20/20, objective 100% (DEMO ham, CONNECTED ham) |

## Rasmiy kalitdagi xato — sahifa kitobga amal qiladi

**U6, Idiomatic Expressions 1–2.** Kalitda `1. undergone`, `2. one such` deb yozilgan. Bular ibora emas: Summary bo'limidagi so'zlar kalitga adashib tushib qolgan. Kitobdagi iboralar: *set up, take away, tear down*.

Sahifada qabul qilinadigan javoblar:

| Savol | Gap | Javob |
|---|---|---|
| 1 | "…there was nothing left to ___." | **take away** |
| 2 | "The teacher needed to ___ her classroom…" | **set up** |
| 3 | — | **tear down** (kalit bilan bir xil) |

O'qituvchi e'tiboriga: kitobning qog'oz kalitidan foydalansangiz, U6 I1–I2 javoblarini shunga qarab tuzating.

## Tuzatilgan joylar

**Kitobdagi matbaa xatolari** (sahifada to'g'ri shakl ko'rsatiladi):

| Unit | Kitobda | Sahifada |
|---|---|---|
| 10 | Summary: "Thieves were **breakings** into" | "breaking" |
| 11 | Lug'at: "frescoe" | "fresco" |
| 17 | Lug'at: "aide" | "aid" |
| 19 | Grammar qoidasi: "a **casual** relationship" | "a **causal** relationship" |

**Kalitdagi namuna javoblardagi xatolar** ("Javobni ko'rish" tugmasi ortida):

| Unit | Kalitda | Sahifada |
|---|---|---|
| 3 | Summary 2: "its **road** and utility poles" | "its roads and utility poles" |
| 4 | Discussion 3: "**I order** to stay healthy" | "In order to stay healthy" |
| 13 | Discussion 2: "they **will could** become popular" | "they could become popular" |
| 16 | Discussion 2: "**the** Apple's iTunes site" | "Apple's iTunes site" |
| 18 | Summary 2: "awarded **a** gold-plated replicas" | "awarded gold-plated replicas" |
| 18 | Summary 1–3: ortiqcha "a + b:", "c + d:", "e + f:" prefikslari | olib tashlandi (boshqa unitlar bilan bir xil) |
| 19 | Pre-Reading 3: "our **computerss**" | "our computers" |

**Kalitdagi grammar matbaa xatolari** (sahifada kitob shakli qoldi):

| Unit | Kalitda | Kitobda |
|---|---|---|
| 6 | "torn down and **replaces**" | "replaced" |
| 8 | "inline **skates** had become" | "inline skating had become" |
| 10 | "around their **homes**" | "around their houses" |

**PDF'dan ajratishda topilgan va tuzatilgan izlar:**

- Satr oxirida bo'lingan so'zlarga ortiqcha bo'shliq tushgan edi. Endi quyidagicha ko'rsatiladi:
  - U13: "non-defining", "earthquake-resistant";
  - U14: "youth-promoting";
  - U18: "gold-plated";
  - U19: "seventy-five".
- Kitobning o'zidagi matn xatolari (o'qish matnida):
  - U3: "**ninty**-nine percent" → "ninety-nine percent";
  - U18: "teams**---**enough" → "teams—enough".
- U18 Listening dialog nomi "Cup" deb chiqayotgan edi. To'g'risi "A Sure Winner?". Unit nomi kitobda ikki qatorga bo'lingani sabab bo'lgan.
- True/False listening unitlarida (3, 6, 9, 12, 15, 18) parser savollar o'rniga Summary obyektlarini qo'yib yuborgan edi. Audit buni ushladi va parser tuzatildi. Hozir 18 ta savolning hammasi kitobdagi bilan bir xil.

## Qo'shimcha eslatmalar

- **Ko'p bo'sh joyli savollar.** Quyidagi savollarda to'liq javob ham, qismlar ham qabul qilinadi:

  | Unit | Savollar |
  |---|---|
  | U5 | L3 |
  | U8 | L1, L3 |
  | U11 | L1 |
  | U14 | L2 |
  | U17 | I1, L3 |
  | U19 | I3 |
  | U20 | I2, I3, L1–L3 |

- **Jadval ko'rinishidagi Summary.** U2, U5, U8, U11, U14, U17 va U20'da kitobdagi jadval yoki reja bo'sh joyli matnga aylantirildi. Faktlar kitob bilan birma-bir solishtirildi.
- **Grammar mashqlari tuzilishi.** Har bir unitda 5 ta mashq bor: kitobdan 2 tasi, qo'shimcha 3 tasi. U14 bundan mustasno: kitobning uch qismli mashqi 3 ta alohida savolga bo'lingan, qo'shimcha mashq 2 ta.
- **Tekshiruv doirasidan tashqarida qolganlar:** o'zbekcha tarjima uslubi, rasm kesimi, audio sifati.

## CONNECTED sayt (o'qituvchi paneliga ulangan)

- **Supabase savollar banki.** `reading_question_bank_v1` jadvaliga `RC3-%` kodli 924 qator qo'shildi, ulardan 766 tasi avtomatik baholanadi.
  - Qo'shish 4 partiyada bajarildi. Har bir partiyaning md5 xeshi fayl bilan mos:

    | Unitlar | Qatorlar | md5 |
    |---|---|---|
    | 1–5 | 234 | `4d714661…` |
    | 6–10 | 227 | `6c68725a…` |
    | 11–15 | 229 | `0209947c…` |
    | 16–20 | 234 | `4d89b51b…` |

  - RC1 va RC2 qatorlari o'zgarmadi (875 + 882).
- **API.** Yangi `turbo-reading-rc3-api` funksiyasi joylandi. RC1 va RC2 endpointlariga tegilmadi.
  - Jonli tekshiruvda U1, U6 va U20 savollari to'g'ri qaytdi.
  - Mavjud bo'lmagan U21 so'ralganda xato qaytaradi.
- **O'qituvchi paneli.** `turbo-reading-teacher-api` v8 ga yangilandi: katalogda "Reading Challenge 3" va 20 ta unit nomi chiqadi.
- **Sinovlar:**
  - CONNECTED sahifalar haqiqiy API kodi orqali (lokal nusxa) 20/20 unitda 100% oldi.
  - Noto'g'ri javoblar 0% oladi, aralash javoblarda natija kutilganiga teng (22/42).
  - Qayta topshirish rad etiladi.
- **Netlify.** `turbo-reading-rc3` loyihasi yaratildi. Kirish sozlamalari RC1/RC2 bilan bir xil: production ochiq, faqat preview uchun login.
- **Jonli sinov (2026-09-30).**
  - Sayt `turbo-reading-rc3.netlify.app` joylandi: 21 ta sahifa va `_headers` qoidasi. 20 ta unitning hammasi ochiladi.
  - O'qituvchining U4 bo'yicha sinov topshirig'i bazaga to'liq saqlandi: 47 ta javob va audio yozuv.
  - Ball qo'lda qayta tekshirildi: 9/40, 22.5%. Har bir javob kalit bilan mos keldi.
  - Natija o'qituvchi panelida audio havolasi bilan ko'rindi.
  - Sinov yozuvi (natija, javoblar, sessiya, audio) keyin o'chirildi. RC3 banki 924 qator bo'lib qoldi, RC1/RC2 natijalariga tegilmadi.

## Joylash

1. Ikkala `RC3_SAYT_*.zip` faylini **bitta papkaga** oching. Natijada bitta `turbo-reading-rc3` papkasi hosil bo'lishi kerak: ichida 22 ta fayl (`index.html`, `_headers`, `unit-1…20.html`).
2. Netlify → Projects → **turbo-reading-rc3** → Deploys bo'limini oching va shu papkani sudrab tashlang.
3. Tayyor manzillar: `https://turbo-reading-rc3.netlify.app/unit-1` … `/unit-20`.

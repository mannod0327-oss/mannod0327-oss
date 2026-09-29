"""Build the Destination A2 practice game into ./html/index.html: one self-contained page (inline CSS, JS and data)
that works offline and from file://.

The book content (28 grammar and 14 vocabulary units, in units_a/b/c.py) is turned into short game sessions:
a journey map of 14 cities, three crown levels per unit, a 20-question test for every unit (unit_tests.py adds
10 items per unit that practice never shows), 14 reviews played as boss battles, 2 progress tests, a daily
challenge, a 60-second blitz and a mistakes review. Every test also has a printable sheet with an answer key. Progress is kept in the browser's localStorage.
Run: py build.py"""
import json, random, pathlib, re
from units_a import UNITS_A
from units_b import UNITS_B
from units_c import UNITS_C
from unit_tests import TESTS, SPARE
from scenes import SCENES

OUT = pathlib.Path(__file__).parent / "html"
UNITS = sorted(UNITS_A + UNITS_B + UNITS_C, key=lambda u: u["n"])

# One city per leg of three units. Facts are short A2-level reading shown after the boss battle.
CITIES = [
    ("Tashkent", "Toshkent", "Tashkent is the capital of Uzbekistan. Its metro opened in 1977."),
    ("Samarkand", "Samarqand", "Samarkand is more than 2,700 years old. Registan Square has three beautiful madrasas."),
    ("Bukhara", "Buxoro", "The Kalyan Minaret in Bukhara was built in 1127. It is about 46 metres tall."),
    ("Khiva", "Xiva", "The old town of Khiva, Itchan Kala, became a UNESCO World Heritage Site in 1990."),
    ("Fergana", "Farg'ona", "The Fergana Valley is famous for silk. In Margilan, people still make silk by hand."),
    ("Istanbul", "Istanbul", "Istanbul is on two continents: Europe and Asia."),
    ("Rome", "Rim", "The Colosseum in Rome is almost 2,000 years old."),
    ("Paris", "Parij", "The Eiffel Tower was built for the World's Fair in 1889."),
    ("London", "London", "Big Ben is not the name of the tower. It is the name of the big bell."),
    ("New York", "Nyu-York", "The Statue of Liberty was a gift from France to the USA in 1886."),
    ("Rio de Janeiro", "Rio-de-Janeyro", "The statue of Christ the Redeemer in Rio is about 30 metres tall."),
    ("Cairo", "Qohira", "The Great Pyramid near Cairo is about 4,500 years old."),
    ("Tokyo", "Tokio", "About 37 million people live in the Tokyo area."),
    ("Sydney", "Sidney", "The Sydney Opera House opened in 1973."),
]


def validate():
    assert [u["n"] for u in UNITS] == list(range(1, 43)), "units must be numbered 1..42"
    assert len(CITIES) == 14, "one city per leg of three units"
    for u in UNITS:
        assert len(u["ex"]) == 3, f"unit {u['n']}: needs exercises A, B, C"
        assert len(u["test"]) == 10, f"unit {u['n']}: test needs 10 questions"
        for ex in u["ex"]:
            for q, a in ex[2]:
                if ex[1] == "mc":
                    assert q.count("___") == 1, f"unit {u['n']}: multiple choice needs one gap: {q}"
                    assert len(a) == 3 and len(set(a)) == 3, f"unit {u['n']}: bad options {q}"
                else:
                    assert q.count("___") == 1 and a and all(a), f"unit {u['n']}: bad gap {q}"
        for q, a in u["test"]:
            assert q.count("___") == 1, f"unit {u['n']}: test question needs one gap: {q}"
            assert len(a) == 3 and len(set(a)) == 3, f"unit {u['n']}: bad test options {q}"
        assert len(gaps(u)) >= 4, f"unit {u['n']}: needs at least 4 gap-fill items"
        assert len(order_sentences(u)) >= 4, f"unit {u['n']}: not enough sentences for the word-order game"
        if "words" in u:
            assert len(u["words"]) >= 6, f"unit {u['n']}: vocabulary units need at least 6 words"
        t = TESTS.get(u["n"])
        assert t and len(t["mc"]) == 5 and len(t["gap"]) == 5, f"unit {u['n']}: unit_tests.py needs 5 mc + 5 gap items"
        for q, o in t["mc"]:
            assert q.count("___") == 1 and len(o) == 3 and len(set(o)) == 3, f"unit {u['n']}: bad test item {q}"
        for q, a in t["gap"]:
            assert q.count("___") == 1 and a and all(a), f"unit {u['n']}: bad test gap {q}"
        book, extra, tg = test_items(u)
        assert len(book) + len(extra) == 15 and len(tg) == 5, f"unit {u['n']}: unit test needs 20 items; add spares"
        seen = practice_sentences(u)
        for q, o in extra + [(q, [a[0]]) for q, a in tg]:
            assert plain(q.replace("___", o[0])) not in seen, f"unit {u['n']}: test item repeats practice: {q}"
    assert sum(1 for u in UNITS if "words" in u) == 14 and sum(1 for u in UNITS if "lesson" in u) == 28
    assert len(SCENES) == 14, "one story scene per city"
    for sc in SCENES:
        assert len(sc["lines"]) == 5 and sc["finale"], f"scene {sc['title']}: needs 5 lines and a finale"
        for line, opts in sc["lines"]:
            assert sorted(k for _, k, _ in opts) == [0, 1, 2], f"scene {sc['title']}: each line needs one best, one grammar-error and one off-topic reply"


def plain(s):
    return re.sub(r"\s*\([^)]*\)", "", s).lower().strip(" .!?")


def practice_sentences(u):
    return ({plain(q.replace("___", a[0])) for ex in u["ex"] for q, a in ex[2]}
            | {plain(ex) for _, _, ex in u.get("words", [])})


def test_items(u):
    """The unit test: book test items that practice never shows + unit_tests.py items (spares fill any gap)."""
    seen = practice_sentences(u)
    book = [(q, o) for q, o in u["test"] if plain(q.replace("___", o[0])) not in seen]
    extra = TESTS[u["n"]]["mc"] + SPARE.get(u["n"], [])[:10 - len(book)]
    return book, extra, TESTS[u["n"]]["gap"]


def gaps(u):
    return [[q, a] for ex in u["ex"] if ex[1] == "gap" for q, a in ex[2]]


def order_sentences(u):
    """Full sentences for the word-order game: practice items with the right answer filled in, plus the example
    sentences of vocabulary units. Short, plain sentences only. Test items are left out so tests stay unseen."""
    cands = [q.replace("___", opts[0]) for q, opts in u["ex"][0][2]]
    cands += [re.sub(r"\s*\([^)]*\)", "", q.replace("___", a[0])) for q, a in gaps(u)]  # drop "(verb)" hints
    cands += [ex for _, _, ex in u.get("words", [])]
    keep = list(dict.fromkeys(s for s in cands if 4 <= len(s.split()) <= 11 and not any(c in s for c in "—→/()…")))
    random.Random(f"order-{u['n']}").shuffle(keep)
    return keep[:12]


def unit_data(u):
    d = {"n": u["n"], "t": u["title"], "k": "v" if "words" in u else "g", "task": u["task"],
         "mc": [[q, list(o)] for q, o in u["ex"][0][2]],  # practice: exercise A
         "gaps": [[q, list(a)] for q, a in gaps(u)], "ord": order_sentences(u),
         # tests only (never in practice): book test items, extra items from unit_tests.py, write-in items
         "test": [[q, list(o)] for q, o in test_items(u)[0]],
         "tx": [[q, list(o)] for q, o in test_items(u)[1]],
         "tg": [[q, list(a)] for q, a in test_items(u)[2]]}
    if "words" in u:
        d["W"] = [list(w) for w in u["words"]]
        d["tip"] = u["tip"]
    else:
        d["L"] = [[head, lines] for head, lines in u["lesson"]]
    return d


def page():
    data = {"units": [unit_data(u) for u in UNITS],
            "cities": [{"name": a, "uz": b, "fact": c} for a, b, c in CITIES],
            "scenes": [{"title": sc["title"], "who": sc["who"], "intro": sc["intro"], "finale": sc["finale"],
                        "lines": [[line, [list(o) for o in opts]] for line, opts in sc["lines"]]} for sc in SCENES]}
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f"""<!doctype html><html lang="uz"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Destination A2</title>
<meta name="description" content="Destination A2 grammatika va lug'at o'yini: 28 grammatika va 14 lug'at uniti, har unit uchun test, 14 review, 2 progress test.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@400;600;700;800&display=swap">
<style>{CSS}</style>
<script>try{{var t=(JSON.parse(localStorage.getItem('destA2.v3'))||{{}}).theme;if(t)document.documentElement.setAttribute('data-theme',t)}}catch(e){{}}</script>
</head><body><div id="app"><noscript><p style="padding:24px">Bu o'yin uchun JavaScript kerak. / This game needs JavaScript.</p></noscript></div>
<script id="a2-data" type="application/json">{blob}</script>
<script>{JS}</script></body></html>"""


CSS = r"""
/* Layout: phone-first single column (max 720px). Home = greeting card, quick modes, then a winding journey map
   of 14 cities; play = full-height quiz screen with a bottom action bar. Samarkand-tile pattern as the one motif. */
:root{
--bg:#f2f5fb;--surface:#fff;--sunk:#e9eff8;--ink:#14213d;--muted:#57658a;--line:#d5deee;
--lapis:#1f4fd1;--lapis-deep:#15389a;--on-lapis:#fff;--tile:#0e98a8;--tile-deep:#0a6f7b;--tile-soft:#d9f3f5;
--gold:#f2b200;--gold-deep:#b98700;--gold-soft:#fff3cc;--flame:#ff7417;--pom:#d7263d;--pom-deep:#9e1528;--pom-soft:#fde3e6;
--ok:#1a9a58;--ok-deep:#12703f;--ok-soft:#daf5e6;--bad:#df3b33;--bad-deep:#a52620;--bad-soft:#fde3e1;
--m-line:#14213d;--pat:rgba(14,152,168,.10);--shadow:0 2px 0 rgba(20,33,61,.06),0 10px 24px rgba(20,33,61,.08);
--f-display:"Fredoka","Baloo 2","Trebuchet MS",system-ui,sans-serif;
--f-body:"Nunito",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
--bg:#0a1120;--surface:#131c31;--sunk:#1a2540;--ink:#e9efff;--muted:#9eaed0;--line:#26345a;
--lapis:#6d93ff;--lapis-deep:#3c61cf;--on-lapis:#0a1120;--tile:#37c4d4;--tile-deep:#1f8f9c;--tile-soft:#0f3037;
--gold:#ffc83a;--gold-deep:#c79400;--gold-soft:#3a2e08;--flame:#ff9146;--pom:#ff5b70;--pom-deep:#c73248;--pom-soft:#3d1520;
--ok:#3fd18a;--ok-deep:#23965c;--ok-soft:#0f3121;--bad:#ff6a61;--bad-deep:#c2413a;--bad-soft:#3b1717;
--m-line:#0a1120;--pat:rgba(55,196,212,.10);--shadow:0 2px 0 rgba(0,0,0,.25),0 10px 24px rgba(0,0,0,.3);color-scheme:dark}}
:root[data-theme="dark"]{
--bg:#0a1120;--surface:#131c31;--sunk:#1a2540;--ink:#e9efff;--muted:#9eaed0;--line:#26345a;
--lapis:#6d93ff;--lapis-deep:#3c61cf;--on-lapis:#0a1120;--tile:#37c4d4;--tile-deep:#1f8f9c;--tile-soft:#0f3037;
--gold:#ffc83a;--gold-deep:#c79400;--gold-soft:#3a2e08;--flame:#ff9146;--pom:#ff5b70;--pom-deep:#c73248;--pom-soft:#3d1520;
--ok:#3fd18a;--ok-deep:#23965c;--ok-soft:#0f3121;--bad:#ff6a61;--bad-deep:#c2413a;--bad-soft:#3b1717;
--m-line:#0a1120;--pat:rgba(55,196,212,.10);--shadow:0 2px 0 rgba(0,0,0,.25),0 10px 24px rgba(0,0,0,.3);color-scheme:dark}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.55 var(--f-body)}
[hidden]{display:none!important}
a{color:var(--lapis)}
button{font:inherit;color:inherit}
:focus-visible{outline:3px solid var(--lapis);outline-offset:3px}
h1,h2,h3{font-family:var(--f-display);font-weight:600;line-height:1.1;text-wrap:balance;margin:0}
.wrap{max-width:720px;margin:0 auto;padding-inline:16px;padding-block:8px 56px}
.eyebrow{font:800 12px/1.3 var(--f-body);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
svg.i{width:20px;height:20px;flex:none}

/* chunky buttons */
.btn{--b:var(--lapis);--bd:var(--lapis-deep);--t:var(--on-lapis);display:inline-flex;align-items:center;justify-content:center;gap:10px;font:700 17px/1.2 var(--f-display);letter-spacing:.02em;padding:13px 20px;border-radius:16px;border:0;background:var(--b);color:var(--t);box-shadow:0 5px 0 var(--bd);cursor:pointer;text-decoration:none;text-align:center;transition:transform .08s,box-shadow .08s,filter .15s}
.btn:hover{filter:brightness(1.06)}
.btn:active{transform:translateY(4px);box-shadow:0 1px 0 var(--bd)}
.btn.big{width:100%;font-size:19px;padding:15px 20px}
.btn.ok{--b:var(--ok);--bd:var(--ok-deep);--t:#fff}.btn.bad{--b:var(--bad);--bd:var(--bad-deep);--t:#fff}
.btn.gold{--b:var(--gold);--bd:var(--gold-deep);--t:#241900}
.btn.ghost{--b:var(--surface);--bd:var(--line);--t:var(--ink);border:2px solid var(--line)}
.btn:disabled{--b:var(--sunk);--bd:var(--line);--t:var(--muted);cursor:default;filter:none;transform:none}
.actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:18px}.actions>*{flex:1 1 200px}

/* top bar */
.bar{display:flex;align-items:center;justify-content:space-between;gap:10px;padding-block:10px}
.logo{font:700 22px var(--f-display);color:var(--ink);text-decoration:none;letter-spacing:.01em;white-space:nowrap}.logo b{color:var(--pom);font-weight:700}
.chips{display:flex;gap:6px;align-items:center}
.chip{display:inline-flex;align-items:center;gap:5px;padding:6px 10px;border-radius:99px;background:var(--surface);border:2px solid var(--line);font:700 15px var(--f-display);color:var(--ink);text-decoration:none;font-variant-numeric:tabular-nums;white-space:nowrap}
.chip.streak svg{color:var(--flame)}.chip.xp svg{color:var(--gold)}.chip.lvl{background:var(--lapis);color:var(--on-lapis);border-color:var(--lapis)}
.chip.dim svg{color:var(--muted)}
@media (max-width:440px){.logo .lg{display:none}.logo b{font-size:26px}.chip{padding:5px 8px;font-size:14px}}
.back{display:inline-flex;align-items:center;gap:6px;font-weight:800;text-decoration:none;color:var(--muted);padding-block:12px 4px}

/* mascot: Laylak, the Bukhara stork */
.mascot{position:relative;display:flex;align-items:flex-end;gap:10px}
.stork{width:96px;height:96px;flex:none;overflow:visible}
.stork .eye-happy{display:none}
.mascot.happy .eye-open,.mascot.cheer .eye-open{display:none}.mascot.happy .eye-happy,.mascot.cheer .eye-happy{display:inline}
.mascot.idle .stork{animation:bob 2.6s ease-in-out infinite}
.mascot.happy .stork{animation:hop .55s ease-out}
.mascot.cheer .stork{animation:hop .6s ease-out 2}
.mascot.cheer .st-wing{transform-origin:62px 72px;animation:flap .3s ease-in-out 4}
.mascot.sad .stork{animation:tilt .6s ease-out both}
@keyframes bob{50%{transform:translateY(-4px)}}
@keyframes hop{30%{transform:translateY(-16px) rotate(-4deg)}60%{transform:translateY(0)}80%{transform:translateY(-4px)}}
@keyframes flap{50%{transform:rotate(-18deg)}}
@keyframes tilt{to{transform:rotate(8deg) translateY(4px)}}
.bubble{position:relative;background:var(--surface);border:2px solid var(--line);border-radius:16px;padding:10px 14px;font:700 16px/1.35 var(--f-body);max-width:300px;margin-bottom:34px;min-width:0}
.bubble::before{content:"";position:absolute;left:-9px;bottom:14px;width:14px;height:14px;background:var(--surface);border-left:2px solid var(--line);border-bottom:2px solid var(--line);transform:rotate(45deg)}
.bubble small{display:block;font-weight:600;color:var(--muted)}

/* home */
.hero{position:relative;overflow:hidden;background:var(--surface);border:2px solid var(--line);border-radius:24px;padding:18px;box-shadow:var(--shadow)}
.hero::before{content:"";position:absolute;inset:0 0 auto 0;height:64px;background:repeating-conic-gradient(from 45deg,var(--pat) 0 25%,transparent 0 50%) 0 0/22px 22px;pointer-events:none}
.hero>*{position:relative}
.goal{display:flex;align-items:center;gap:14px;margin:6px 0 16px}
.ring{width:64px;height:64px;flex:none}
.ring circle{fill:none;stroke-width:8}.ring .trk{stroke:var(--sunk)}.ring .val{stroke:var(--gold);stroke-linecap:round;transform:rotate(-90deg);transform-origin:50% 50%;transition:stroke-dashoffset .8s}
.goal b{font:600 22px var(--f-display)}.goal p{margin:0;color:var(--muted);font-size:15px}
.cont-sub{margin:10px 0 0;text-align:center;color:var(--muted);font-size:15px;font-weight:700}
.modes{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:14px}
.mode{display:grid;gap:4px;align-content:start;padding:14px 12px;border-radius:18px;background:var(--surface);border:2px solid var(--line);border-bottom-width:5px;color:var(--ink);text-decoration:none;min-width:0;transition:transform .1s}
.mode:hover{transform:translateY(-2px)}.mode:active{transform:translateY(2px)}
.mode svg{width:30px;height:30px}.mode b{font:600 17px/1.15 var(--f-display)}.mode span{font-size:13px;color:var(--muted);line-height:1.3}
.mode.daily svg{color:var(--lapis)}.mode.blitz svg{color:var(--flame)}.mode.fix svg{color:var(--pom)}
.mode.off{opacity:.6}
@media (max-width:460px){.modes{grid-template-columns:minmax(0,1fr)}.mode{grid-template-columns:auto 1fr;column-gap:12px;align-items:center}.mode svg{grid-row:span 2}}

/* journey map */
.map-h{display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin:28px 0 6px}
.map-h h2{font-size:26px}.map-h span{color:var(--muted);font-weight:700;font-size:14px}
.city{position:relative;display:flex;align-items:center;justify-content:space-between;gap:12px;margin:22px 0 10px;padding:14px 16px;border-radius:20px;background:var(--tile-deep);color:#fff;overflow:hidden}
.city::before{content:"";position:absolute;inset:0;background:repeating-conic-gradient(from 45deg,rgba(255,255,255,.1) 0 25%,transparent 0 50%) 0 0/20px 20px}
.city>*{position:relative}.city h2{font-size:26px;color:#fff}.city p{margin:0;font-weight:700}.city .eyebrow{color:#fff}
.city.airport{background:var(--gold);color:#241900}.city.airport h2,.city.airport .eyebrow{color:#241900}
.path{list-style:none;margin:0;padding:6px 0;display:grid;gap:14px;justify-items:center}
.node-row{position:relative;display:grid;justify-items:center;gap:6px;transform:translateX(calc(var(--o,0)*72px));max-width:100%}
@media (max-width:400px){.node-row{transform:translateX(calc(var(--o,0)*48px))}}
.node{--ring:var(--gold);--fill:var(--lapis);--deep:var(--lapis-deep);display:grid;place-items:center;width:82px;height:82px;border-radius:50%;padding:6px;background:conic-gradient(var(--ring) calc(var(--c,0)*1turn),var(--line) 0);text-decoration:none;transition:transform .12s}
.node:hover{transform:scale(1.05)}
.node-in{display:grid;place-items:center;width:100%;height:100%;border-radius:50%;background:var(--fill);color:#fff;box-shadow:inset 0 -6px 0 var(--deep);font:700 26px var(--f-display);padding-bottom:4px}
.node.v{--fill:var(--tile);--deep:var(--tile-deep)}
.node.full .node-in{--fill:var(--gold);--deep:var(--gold-deep);color:#241900}
.node.boss{border-radius:26px;--fill:var(--pom);--deep:var(--pom-deep)}.node.boss .node-in{border-radius:20px}
.node.exam{--fill:var(--gold);--deep:var(--gold-deep)}.node.exam .node-in{color:#241900}
.node.won .node-in{--fill:var(--ok);--deep:var(--ok-deep);color:#fff}
.node svg{width:34px;height:34px}
.node.next{animation:pulse 1.8s ease-in-out infinite}
@keyframes pulse{50%{box-shadow:0 0 0 10px color-mix(in srgb,var(--lapis) 22%,transparent)}}
.node-label{max-width:170px;text-align:center;font-weight:800;font-size:14px;line-height:1.25}
.node-label small{display:block;font-weight:700;color:var(--muted)}
.you{position:absolute;left:calc(50% + 34px);top:-10px;display:flex;align-items:flex-start;gap:2px;pointer-events:none}
.you .stork{width:56px;height:56px}
.you span{font:700 12px var(--f-display);background:var(--ink);color:var(--bg);padding:3px 8px;border-radius:99px;white-space:nowrap}
.you.l{left:auto;right:calc(50% + 34px);flex-direction:row-reverse}.you.l .stork{transform:scaleX(-1)}
.leg{overflow-x:hidden;padding-inline:4px;margin-inline:-4px}
.crowns{display:inline-flex;gap:2px;color:var(--gold)}.crowns .off{color:var(--line)}
.crowns svg{width:18px;height:18px}
.stamp{display:inline-grid;place-items:center;align-content:center;width:74px;height:74px;border-radius:50%;border:3px double currentColor;transform:rotate(-12deg);text-align:center;line-height:1.05;flex:none}
.stamp b{font:700 14px var(--f-display);text-transform:uppercase}.stamp small{font-size:10px;font-weight:800;letter-spacing:.1em}
.stamp.press{animation:press .55s cubic-bezier(.2,1.5,.4,1) both}
@keyframes press{from{transform:rotate(-30deg) scale(2);opacity:0}to{transform:rotate(-12deg) scale(1);opacity:1}}

/* unit screen */
.unit-head{padding:18px;border-radius:24px;background:var(--lapis);color:var(--on-lapis);position:relative;overflow:hidden}
.unit-head.v{background:var(--tile-deep);color:#fff}
.unit-head::after{content:"";position:absolute;right:-20px;top:-20px;width:140px;height:140px;background:repeating-conic-gradient(from 45deg,rgba(255,255,255,.14) 0 25%,transparent 0 50%) 0 0/20px 20px;border-radius:50%}
.unit-head>*{position:relative;z-index:1}
.unit-head .eyebrow{color:inherit}.unit-head h1{font-size:clamp(28px,6vw,40px);margin-bottom:10px}
.unit-head .crowns{color:var(--gold)}.unit-head .crowns .off{color:currentColor;opacity:.35}.unit-head .crowns svg{width:26px;height:26px}
.card{background:var(--surface);border:2px solid var(--line);border-radius:22px;padding:18px;margin-top:16px}
.card h2{font-size:22px;margin-bottom:10px}
.rule h3{font-size:21px;color:var(--lapis);margin-bottom:8px}
.rule ul{margin:0;padding-left:20px}.rule li{margin:6px 0}
.rule li.uz{list-style:none;margin:12px 0 0 -20px;padding:10px 12px;border-radius:14px;background:var(--gold-soft);display:flex;gap:10px;align-items:baseline}
.uzchip{flex:none;font:800 11px var(--f-body);letter-spacing:.08em;border:2px solid var(--gold-deep);color:var(--gold-deep);border-radius:6px;padding:0 5px}
.learn-nav{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:14px}
.dots{display:flex;gap:6px}.dots i{width:9px;height:9px;border-radius:50%;background:var(--line)}.dots i.on{background:var(--lapis)}
.words{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px}
.word{display:flex;gap:10px;align-items:center;padding:10px 12px;border-radius:16px;background:var(--sunk);min-width:0}
.word div{min-width:0}.word b{display:block;font-size:18px}.word span{display:block;color:var(--muted);font-weight:700;font-size:15px;overflow-wrap:anywhere}
.tip{margin:12px 0 0;padding:10px 14px;border-radius:14px;background:var(--gold-soft)}
.levels{display:grid;gap:12px;margin-top:16px}
.level{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:14px;padding:14px 16px;border-radius:20px;background:var(--surface);border:2px solid var(--line);border-bottom-width:5px;color:var(--ink);text-decoration:none;transition:transform .1s}
.level:hover{transform:translateY(-2px)}.level:active{transform:translateY(2px)}
.level .lv-c{display:grid;place-items:center;width:52px;height:52px;border-radius:16px;background:var(--sunk);color:var(--line)}
.level .lv-c svg{width:30px;height:30px}.level.done .lv-c{background:var(--gold-soft);color:var(--gold)}
.level b{display:block;font:600 19px var(--f-display)}.level span{display:block;color:var(--muted);font-size:14px;line-height:1.35}
.level .go{font:700 15px var(--f-display);color:var(--lapis)}
.task p{margin:0 0 12px}

/* play */
.play{max-width:720px;margin:0 auto;min-height:100vh;min-height:100dvh;display:flex;flex-direction:column;padding-inline:16px}
.play-top{display:flex;align-items:center;gap:12px;padding-block:14px 8px}
.x{display:grid;place-items:center;width:40px;height:40px;border-radius:12px;border:0;background:none;color:var(--muted);cursor:pointer;flex:none}
.x svg{width:24px;height:24px}
.pbar{flex:1;height:16px;border-radius:99px;background:var(--sunk);overflow:hidden}
.pbar i{display:block;height:100%;width:0;border-radius:99px;background:var(--ok);box-shadow:inset 0 -4px 0 rgba(0,0,0,.12);transition:width .35s}
.hearts,.timer{display:inline-flex;align-items:center;gap:4px;font:700 18px var(--f-display);font-variant-numeric:tabular-nums}
.hearts svg{color:var(--pom);width:24px;height:24px}.timer svg{color:var(--lapis);width:22px;height:22px}
.timer.low{color:var(--bad)}
.combo-pill{align-self:center;display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:99px;background:var(--flame);color:#fff;font:700 15px var(--f-display);animation:pop .3s}
.combo-pill svg{width:18px;height:18px}
@keyframes pop{from{transform:scale(.6)}70%{transform:scale(1.12)}}
.q-area{flex:1;padding-block:10px 16px;animation:slidein .25s ease-out}
@keyframes slidein{from{opacity:0;transform:translateX(18px)}}
.inst{font:600 22px/1.2 var(--f-display);margin:4px 0 16px}
.prompt{font-size:21px;font-weight:700;line-height:1.5;margin-bottom:18px;overflow-wrap:anywhere}
.big-word{display:inline-flex;align-items:center;gap:10px;font:600 34px/1.15 var(--f-display);color:var(--lapis)}
.blank{display:inline-block;min-width:64px;border-bottom:3px solid var(--muted);margin-inline:4px;transform:translateY(-4px)}
.opts{display:grid;gap:10px}
.opt{display:flex;align-items:center;gap:12px;width:100%;padding:14px 16px;border-radius:16px;border:2px solid var(--line);border-bottom-width:5px;background:var(--surface);font:700 19px/1.3 var(--f-body);text-align:left;cursor:pointer;transition:transform .08s,border-color .15s,background-color .15s}
.opt:hover{border-color:var(--lapis)}
.opt:active{transform:translateY(2px)}
.opt kbd{display:grid;place-items:center;flex:none;width:28px;height:28px;border-radius:8px;border:2px solid var(--line);font:700 14px var(--f-display);color:var(--muted)}
.opt span{min-width:0;overflow-wrap:anywhere}
.opt.sel{border-color:var(--lapis);background:color-mix(in srgb,var(--lapis) 12%,var(--surface))}
.opt.sel kbd{border-color:var(--lapis);color:var(--lapis)}
.opt.right{border-color:var(--ok);background:var(--ok-soft)}.opt.right kbd{border-color:var(--ok);color:var(--ok)}
.opt.wrong{border-color:var(--bad);background:var(--bad-soft)}.opt.wrong kbd{border-color:var(--bad);color:var(--bad)}
.opt:disabled{cursor:default}
.opts.chips{display:flex;flex-wrap:wrap}.opts.chips .opt{width:auto}
.listen-row{display:flex;align-items:center;gap:12px;margin-bottom:18px}
.speak{display:inline-grid;place-items:center;width:44px;height:44px;border-radius:14px;border:0;background:var(--lapis);color:var(--on-lapis);box-shadow:0 4px 0 var(--lapis-deep);cursor:pointer;flex:none}
.speak svg{width:22px;height:22px}.speak:active{transform:translateY(3px);box-shadow:0 1px 0 var(--lapis-deep)}
.speak.huge{width:84px;height:84px;border-radius:24px}.speak.huge svg{width:40px;height:40px}
.speak.sm{width:34px;height:34px;border-radius:10px;box-shadow:0 3px 0 var(--lapis-deep)}.speak.sm svg{width:18px;height:18px}
.slow{font:700 15px var(--f-display);padding:8px 14px;border-radius:12px;border:2px solid var(--line);background:var(--surface);cursor:pointer}
.no-tts .speak,.no-tts .slow{display:none}
.type-in{font:inherit;font-weight:800;color:var(--lapis);width:12ch;max-width:100%;padding:2px 8px;border:0;border-bottom:3px solid var(--lapis);background:var(--sunk);border-radius:8px 8px 0 0}
.type-in:focus{outline:none;background:color-mix(in srgb,var(--lapis) 12%,var(--surface))}
.type-in.ok{color:var(--ok);border-color:var(--ok)}.type-in.bad{color:var(--bad);border-color:var(--bad)}
.ord-line{min-height:64px;display:flex;flex-wrap:wrap;align-content:flex-start;gap:8px;padding:10px 4px;border-bottom:2px solid var(--line)}
.ord-bank{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-top:22px;min-height:52px}
.tile{font:700 18px var(--f-body);padding:9px 14px;border-radius:14px;border:2px solid var(--line);border-bottom-width:5px;background:var(--surface);cursor:pointer;animation:pop .2s}
.tile:active{transform:translateY(2px)}
.ord-line.ok .tile{border-color:var(--ok)}.ord-line.bad .tile{border-color:var(--bad)}
.pairs{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.pairs .col{display:grid;gap:10px;align-content:start;min-width:0}
.pair{padding:12px;border-radius:14px;border:2px solid var(--line);border-bottom-width:5px;background:var(--surface);font:700 16px/1.3 var(--f-body);cursor:pointer;min-height:54px;text-align:center;overflow-wrap:anywhere}
.pair.sel{border-color:var(--lapis);background:color-mix(in srgb,var(--lapis) 12%,var(--surface))}
.pair.done{border-color:var(--ok);background:var(--ok-soft);color:var(--ok);opacity:.7;cursor:default}
.pair.bad{border-color:var(--bad);background:var(--bad-soft)}
.shake{animation:shake .4s}
@keyframes shake{20%,60%{transform:translateX(-6px)}40%,80%{transform:translateX(6px)}}
.play-mascot{display:flex;justify-content:flex-start;min-height:0}
.play-mascot .stork{width:74px;height:74px}.play-mascot .bubble{margin-bottom:24px;font-size:15px}
.play-foot{position:sticky;bottom:0;margin-inline:-16px;padding:14px 16px calc(16px + env(safe-area-inset-bottom,0px));background:var(--bg);border-top:2px solid var(--line)}
.play-foot.ok{background:var(--ok-soft);border-color:transparent}.play-foot.bad{background:var(--bad-soft);border-color:transparent}
.sheet{display:none;margin-bottom:12px}
.play-foot.ok .sheet,.play-foot.bad .sheet{display:flex;gap:12px;align-items:flex-start;animation:up .25s ease-out}
@keyframes up{from{transform:translateY(20px);opacity:0}}
.sheet>svg{width:36px;height:36px;flex:none}
.play-foot.ok .sheet>svg,.play-foot.ok .sheet b{color:var(--ok)}.play-foot.bad .sheet>svg,.play-foot.bad .sheet b{color:var(--bad)}
.sheet div{min-width:0}
.sheet b{font:700 21px var(--f-display);display:block}
.sheet p{margin:4px 0 0;font-weight:700;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.sheet .ans{color:var(--bad)}
.overlay{position:fixed;inset:0;z-index:20;display:grid;place-items:center;padding:16px;background:rgba(10,17,32,.55)}
.dialog{width:min(420px,100%);background:var(--surface);border-radius:24px;padding:22px;text-align:center}
.dialog .mascot{justify-content:center}
.dialog h2{font-size:24px;margin-bottom:6px}.dialog p{margin:0 0 6px;color:var(--muted)}

/* unit tests, grades, printable sheets */
.node{position:relative}
.tb{position:absolute;right:-2px;top:-2px;display:grid;place-items:center;width:28px;height:28px;border-radius:50%;font:700 15px var(--f-display);border:3px solid var(--bg);color:#fff;background:var(--ok)}.tb.fail{background:var(--bad)}
.book{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 4px}.bk{padding:4px 10px;border-radius:99px;background:var(--surface);border:2px solid var(--line);font-weight:800;font-size:13px}.bk b{color:var(--lapis)}
.grade{display:grid;place-items:center;width:52px;height:52px;border-radius:16px;font:700 30px var(--f-display);color:#fff;background:var(--ok);flex:none}
.grade.g4{background:var(--lapis);color:var(--on-lapis)}.grade.g3{background:var(--gold);color:#241900}.grade.g2{background:var(--bad)}
.tc-h{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}.tc-h>div{min-width:0}
.testcard{border-color:var(--gold);border-bottom-width:5px}
.answers{text-align:left}.answers ol{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.answers li{display:flex;gap:10px;align-items:flex-start;padding:10px 12px;border-radius:14px;background:var(--ok-soft)}.answers li.bad{background:var(--bad-soft)}
.answers .mk svg{width:22px;height:22px}.answers li.ok .mk{color:var(--ok)}.answers li.bad .mk{color:var(--bad)}
.answers div{min-width:0}.answers p{margin:0;font-weight:700;overflow-wrap:anywhere}.answers .yours{font-weight:600;color:var(--muted);font-size:14px}
.sheet-p{background:#fff;color:#111;border:1px solid var(--line);border-radius:12px;padding:28px;margin-top:16px;font:15px/1.5 var(--f-body)}
.sheet-p h1{font-size:28px;color:#111}.sheet-p h2{font-size:18px;margin:18px 0 8px;color:#111}.sheet-p h2 small{font:600 13px var(--f-body);color:#555}
.sheet-p .eyebrow,.sheet-p .sub{color:#555}
.sp-h{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;border-bottom:2px solid #111;padding-bottom:12px}
.sp-f{display:grid;gap:6px;font-weight:700;font-size:14px}
.sp-q{padding-left:26px;margin:0}.sp-q li{margin:0 0 10px;break-inside:avoid}.sp-q p{margin:0}
.sp-o{display:flex;flex-wrap:wrap;gap:2px 24px;color:#222}
.pl{display:inline-block;width:110px;max-width:40%;border-bottom:1.5px solid #111;margin-inline:3px}
.sp-grade{margin:18px 0 0;font-size:13px;color:#555;border-top:1px solid #ccc;padding-top:8px}
.sp-k{columns:2;column-gap:28px;padding-left:26px;margin:0}.sp-k li{margin:2px 0;break-inside:avoid}
@media (max-width:460px){.sheet-p{padding:18px}.sp-k{columns:1}}
@media print{@page{size:A4;margin:14mm}body{background:#fff}.no-print,.toast{display:none!important}.wrap.print{max-width:none;padding:0}.sheet-p{border:0;border-radius:0;padding:0;margin:0}.sheet-p.key{break-before:page}}

/* hints, confidence bet, powers, boss battle, spot the error, scenes */
.inst-row{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}.inst-row .inst{min-width:0}
.hint-btn{flex:none;display:inline-flex;align-items:center;gap:6px;font:700 14px var(--f-display);padding:7px 12px;border-radius:12px;border:2px solid var(--gold);background:var(--gold-soft);color:var(--ink);cursor:pointer}
.hint-btn svg{color:var(--gold-deep);width:18px;height:18px}.hint-btn:disabled{opacity:.5;cursor:default}
.hint-msg{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:-6px 0 14px;padding:8px 12px;border-radius:12px;background:var(--gold-soft);font-weight:700;letter-spacing:.02em}.hint-msg svg{color:var(--gold-deep)}.hint-msg small{font-weight:600;color:var(--muted);letter-spacing:0}
.opt.gone{opacity:.25;text-decoration:line-through}
.foot-row{display:flex;gap:10px;align-items:stretch}.foot-row .btn{flex:1}
.sure{flex:none;font:700 14px/1.15 var(--f-display);padding:8px 12px;border-radius:16px;border:2px solid var(--line);border-bottom-width:5px;background:var(--surface);color:var(--muted);cursor:pointer;max-width:120px}
.sure[aria-pressed="true"]{border-color:var(--gold-deep);background:var(--gold);color:#241900}
.powers{display:flex;gap:8px;justify-content:flex-end;margin-top:-2px}
.pw{display:inline-flex;align-items:center;gap:5px;font:700 14px var(--f-display);padding:5px 10px;border-radius:99px;border:2px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer}
.pw svg{width:16px;height:16px;color:var(--pom)}.pw b{background:var(--sunk);border-radius:99px;padding:0 7px}
.mode-boss .pbar i{background:var(--pom)}
.battle{display:flex;align-items:center;gap:12px;padding:8px 12px;border-radius:18px;background:var(--pom-soft);border:2px solid var(--pom);margin:4px 0 8px}
.dev{position:relative;flex:none;width:64px;height:64px}.dev-svg{width:100%;height:100%;overflow:visible}
.dev.hit{animation:hit .45s}.dev.atk{animation:atk .5s}
@keyframes hit{20%{transform:translateX(8px) rotate(8deg);filter:brightness(1.6)}60%{transform:translateX(-4px)}}
@keyframes atk{40%{transform:scale(1.25) translateY(6px)}}
.dmg{position:absolute;left:50%;top:0;transform:translateX(-50%);font:700 22px var(--f-display);color:var(--bad);opacity:0;pointer-events:none;text-shadow:0 2px 0 var(--surface)}
.dmg.show{animation:dmg .8s ease-out}
@keyframes dmg{0%{opacity:1;transform:translate(-50%,0)}100%{opacity:0;transform:translate(-50%,-34px)}}
.bhp{flex:1;min-width:0}.bhp b{font:700 17px var(--f-display)}.bhp small{display:block;color:var(--muted);font-size:12px;font-weight:700}
.hpbar{height:14px;border-radius:99px;background:var(--surface);overflow:hidden;margin:4px 0;border:2px solid var(--pom)}
.hpbar i{display:block;height:100%;width:100%;background:var(--pom);transition:width .4s}
.spot{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px}
.stok{font:700 19px var(--f-body);padding:8px 12px;border-radius:12px;border:2px solid var(--line);border-bottom-width:4px;background:var(--surface);cursor:pointer}
.stok.sel{border-color:var(--lapis);background:color-mix(in srgb,var(--lapis) 12%,var(--surface))}
.stok.err{border-color:var(--ok);background:var(--ok-soft);color:var(--ok)}.stok.wrong{border-color:var(--bad);background:var(--bad-soft);text-decoration:line-through}
.type-in.wide{width:100%;display:block;margin-top:6px}
.banner.calib{background:var(--tile-soft);border-color:var(--tile)}.big-n{font:700 30px var(--f-display);color:var(--tile-deep);flex:none}
.node.scene{--fill:var(--tile-deep);--deep:var(--tile)}
.scene-intro{margin:0;opacity:.95;font-weight:700}.scene-step{position:absolute;right:16px;top:14px;z-index:1;font:700 14px var(--f-display);background:rgba(255,255,255,.2);padding:3px 10px;border-radius:99px}
.chat{display:grid;gap:12px;margin:18px 0}
.msg{display:flex;gap:10px;align-items:flex-end;max-width:92%}.msg .bub{padding:10px 14px;border-radius:18px;background:var(--surface);border:2px solid var(--line);min-width:0}
.msg .bub p{margin:0;font-weight:700;font-size:18px}.msg .bub b{font:600 13px var(--f-display);color:var(--tile-deep)}
.msg.them .bub{border-bottom-left-radius:4px}.msg.me{justify-self:end}.msg.me .bub{background:var(--lapis);border-color:var(--lapis);color:var(--on-lapis);border-bottom-right-radius:4px}
.av{display:grid;place-items:center;flex:none;width:38px;height:38px;border-radius:50%;background:var(--tile-deep);color:#fff;font:700 18px var(--f-display)}
.c-note{justify-self:center;margin:0;font-size:13px;font-weight:800;color:var(--muted);background:var(--sunk);padding:3px 10px;border-radius:99px}
.replies{margin-bottom:24px}
.coach{margin:12px 0 0;padding:10px 14px;border-radius:14px;font-weight:700}.coach small{display:block;font-weight:600;color:var(--muted)}
.coach.good{background:var(--ok-soft)}.coach.good svg{color:var(--ok);vertical-align:-4px}.coach.gram{background:var(--bad-soft)}.coach.odd{background:var(--gold-soft)}
.turn .prompt-sm{font-size:19px;font-weight:700;margin:0 0 8px}
.t45{font:700 64px/1 var(--f-display);color:var(--lapis);text-align:center;margin:10px 0;font-variant-numeric:tabular-nums}
.check{list-style:none;padding:0;margin:0;display:grid;gap:8px}.check label{display:flex;gap:10px;align-items:center;font-weight:700;padding:10px 12px;border-radius:12px;background:var(--sunk);cursor:pointer}
.check input{width:20px;height:20px;accent-color:var(--ok)}
.res-stars{display:flex;justify-content:center;gap:6px;color:var(--gold);margin:6px 0}.res-stars svg{width:40px;height:40px}.res-stars .off{color:var(--line)}
.weak{list-style:none;margin:0;padding:0;display:grid;gap:8px}.weak li{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 12px;border-radius:14px;background:var(--bad-soft)}
.weak li div{min-width:0}.weak b{display:block}.weak span{color:var(--muted);font-weight:700;font-size:14px}
@media (max-width:420px){.sure{max-width:96px;font-size:13px;padding:6px 8px}.battle small{display:none}}

/* word games */
.mode.games svg{color:var(--tile)}
@media (min-width:461px){.modes{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (min-width:700px){.modes{grid-template-columns:repeat(4,minmax(0,1fr))}}
.fz{display:inline-flex;align-items:center;gap:2px;margin-left:4px;font-style:normal;color:var(--lapis)}.fz svg{width:14px;height:14px;color:var(--lapis)}
.page-h{font-size:clamp(30px,7vw,42px);margin:6px 0 4px}
.ghub{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin-top:14px}
.gcard{display:grid;gap:6px;align-content:start;padding:18px;border-radius:22px;background:var(--surface);border:2px solid var(--line);border-bottom-width:6px;color:var(--ink);text-decoration:none;transition:transform .1s}
.gcard:hover{transform:translateY(-3px)}.gcard b{font:600 22px var(--f-display)}.gcard>span:not(.gic){color:var(--muted);font-size:15px}.gcard small{font-weight:800;color:var(--lapis)}
.gic{display:grid;place-items:center;width:56px;height:56px;border-radius:18px;color:#fff;background:var(--lapis)}.gic svg{width:30px;height:30px}
.g-scramble .gic{background:var(--gold);color:#241900}.g-hidden .gic{background:var(--tile-deep)}.g-survival .gic{background:var(--pom)}
.g-head{margin:4px 0 10px}.g-head h1{font-size:clamp(28px,6vw,38px)}.g-head p{margin:4px 0 0;color:var(--muted);font-weight:700}
.g-stat{display:flex;flex-wrap:wrap;gap:8px 18px;font:600 15px var(--f-display);color:var(--muted);margin:0 0 12px}.g-stat b{color:var(--ink)}
.lives{display:inline-flex;align-items:center;gap:4px;color:var(--ink)}.lives svg{color:var(--pom);width:18px;height:18px}
.mem{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
@media (max-width:460px){.mem{grid-template-columns:repeat(3,minmax(0,1fr))}}
.mcard{aspect-ratio:3/4;max-width:100%;padding:0;border:0;background:none;perspective:800px;cursor:pointer;font:inherit;color:inherit}
.mc-in{position:relative;display:block;width:100%;height:100%;transition:transform .35s;transform-style:preserve-3d}
.mcard.open .mc-in{transform:rotateY(180deg)}
.mc-f,.mc-b{position:absolute;inset:0;display:grid;place-items:center;border-radius:16px;backface-visibility:hidden;-webkit-backface-visibility:hidden;padding:6px;text-align:center;overflow-wrap:anywhere}
.mc-f{background:var(--lapis);color:var(--on-lapis);font:700 34px var(--f-display);box-shadow:inset 0 -6px 0 var(--lapis-deep)}
.mc-b{transform:rotateY(180deg);background:var(--surface);border:2px solid var(--line);font:700 15px/1.2 var(--f-body)}.mc-b.en{font:600 18px var(--f-display);color:var(--lapis)}
.mcard.done .mc-b{border-color:var(--ok);background:var(--ok-soft)}
.clue{font:600 26px/1.25 var(--f-display);text-align:center;margin:6px 0 16px;color:var(--tile-deep)}
.slots,.hidden-w{display:flex;flex-wrap:wrap;justify-content:center;gap:6px;margin-bottom:18px}
.slot,.hl{display:grid;place-items:center;width:40px;height:48px;border-radius:10px;border:2px solid var(--line);border-bottom-width:4px;background:var(--surface);font:700 24px var(--f-display);text-transform:lowercase}
.slot.fixed{background:var(--gold-soft);border-color:var(--gold)}.slots.ok .slot{border-color:var(--ok);background:var(--ok-soft)}
.hl.on{border-color:var(--lapis)}.gap{width:18px}
.letters{display:flex;flex-wrap:wrap;justify-content:center;gap:8px}
.ltr{width:48px;height:52px;border-radius:12px;border:2px solid var(--line);border-bottom-width:5px;background:var(--surface);font:700 24px var(--f-display);cursor:pointer}
.ltr:disabled{opacity:.25;cursor:default}
.kbd{display:grid;grid-template-columns:repeat(9,minmax(0,1fr));gap:6px}
@media (max-width:460px){.kbd{grid-template-columns:repeat(7,minmax(0,1fr))}}
.key{height:46px;border-radius:10px;border:2px solid var(--line);border-bottom-width:4px;background:var(--surface);font:700 20px var(--f-display);cursor:pointer;padding:0}
.key.hit{background:var(--ok-soft);border-color:var(--ok);color:var(--ok)}.key.miss{background:var(--bad-soft);border-color:var(--bad);color:var(--bad)}.key:disabled{cursor:default}
.g-ex{text-align:center;font-weight:700;margin:14px 0 0;padding:10px;border-radius:12px}.g-ex.ok{background:var(--ok-soft)}.g-ex.bad{background:var(--bad-soft)}.g-ex i{display:block;font-weight:600;color:var(--muted)}

/* result and intro */
.center{text-align:center}
.center .mascot{justify-content:center;margin-top:16px}
.center .bubble{text-align:left}
.result h1,.intro h1{font-size:clamp(30px,7vw,42px);margin:8px 0 6px}
.sub{color:var(--muted);margin:0 0 8px;font-weight:700}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:18px}
.stat{padding:12px 8px;border-radius:18px;border:2px solid var(--line);background:var(--surface);display:grid;gap:2px}
.stat b{font:700 26px var(--f-display);font-variant-numeric:tabular-nums}.stat span{font-size:13px;font-weight:800;color:var(--muted)}
.stat.xp{border-color:var(--gold);background:var(--gold-soft)}.stat.xp b{color:var(--gold-deep)}
@media (max-width:460px){.stats{grid-template-columns:repeat(2,minmax(0,1fr))}}
.banner{display:flex;align-items:center;gap:14px;text-align:left;margin-top:16px;padding:14px 16px;border-radius:18px;background:var(--gold-soft);border:2px solid var(--gold)}
.banner>div{min-width:0}
.banner .crowns svg{width:30px;height:30px}.banner b{font:600 19px var(--f-display);display:block}.banner p{margin:0 0 6px}
.banner.city{background:var(--tile-soft);border-color:var(--tile);color:var(--ink)}.banner.city .stamp{color:var(--tile)}
.new-badges{display:flex;flex-wrap:wrap;justify-content:center;gap:12px;margin-top:12px}
.rules{text-align:left;margin:16px auto 0;max-width:460px;padding-left:22px}.rules li{margin:6px 0}
.share-box{display:block;width:100%;margin:6px 0 10px;font:inherit;padding:10px;border-radius:12px;border:2px solid var(--line);background:var(--sunk);color:var(--ink);resize:none}

/* badges */
.badges{display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));gap:12px}
.badge{display:grid;justify-items:center;gap:6px;text-align:center;font-size:13px;line-height:1.25;max-width:140px}
.medal{display:grid;place-items:center;width:64px;height:64px;border-radius:50%;background:var(--gold);color:#241900;box-shadow:inset 0 -6px 0 var(--gold-deep),0 0 0 4px var(--gold-soft);font:700 18px var(--f-display)}
.badge b{font-weight:800}.badge .desc{color:var(--muted)}
.badge.locked .medal{background:var(--sunk);color:var(--muted);box-shadow:inset 0 -6px 0 var(--line)}
.new-badges .medal{animation:press .6s cubic-bezier(.2,1.5,.4,1) both}

/* profile */
.profile{display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.lvbar{height:14px;border-radius:99px;background:var(--sunk);overflow:hidden;margin-top:8px}
.lvbar i{display:block;height:100%;background:var(--lapis);border-radius:99px}
.grid-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
@media (max-width:460px){.grid-stats{grid-template-columns:repeat(2,minmax(0,1fr))}}
.seg{display:inline-flex;flex-wrap:wrap;gap:6px}
.seg button{padding:8px 14px;border-radius:12px;border:2px solid var(--line);background:var(--surface);font-weight:800;cursor:pointer}
.seg button[aria-pressed="true"]{background:var(--lapis);border-color:var(--lapis);color:var(--on-lapis)}
.setting{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;padding-block:10px;border-top:2px solid var(--sunk)}
.setting:first-of-type{border-top:0}
textarea.code{display:block;width:100%;min-height:80px;font:14px ui-monospace,Menlo,monospace;padding:10px;border-radius:12px;border:2px solid var(--line);background:var(--sunk);color:var(--ink);overflow-wrap:anywhere}
.note{color:var(--muted);font-size:14px;margin:6px 0 10px}
.toast{position:fixed;left:50%;bottom:calc(118px + env(safe-area-inset-bottom,0px));transform:translate(-50%,20px);opacity:0;background:var(--ink);color:var(--bg);font:700 16px var(--f-display);padding:10px 18px;border-radius:99px;pointer-events:none;transition:opacity .25s,transform .25s;z-index:40;display:flex;gap:8px;align-items:center;max-width:calc(100% - 32px)}
.toast.show{opacity:1;transform:translate(-50%,0)}.toast svg{color:var(--flame)}
.confetti{position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:30}
footer.foot{color:var(--muted);font-size:13px;text-align:center;margin-top:36px}
/* teacher page and assignment mode */
.teach-link{display:flex;gap:14px;align-items:center;margin-top:28px;padding:14px 16px;border-radius:20px;border:2px dashed var(--line);color:var(--ink);text-decoration:none;background:var(--surface)}
.teach-link svg{width:34px;height:34px;color:var(--tile);flex:none}.teach-link span{min-width:0}.teach-link b{display:block;font:600 18px var(--f-display)}.teach-link small{color:var(--muted);font-weight:700}
.how{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;list-style:none;padding:0;margin:14px 0 0}
.how li{padding:12px 14px;border-radius:16px;background:var(--gold-soft);font-size:14px;font-weight:700;color:var(--muted)}.how b{display:block;font:600 17px var(--f-display);color:var(--ink)}
.text-in{display:block;width:100%;font:inherit;font-weight:700;padding:11px 12px;border-radius:12px;border:2px solid var(--line);background:var(--sunk);color:var(--ink);resize:vertical}
.text-in:focus{outline:none;border-color:var(--lapis)}
.fl{display:block;font-weight:800;margin:14px 0 6px}.fl:first-of-type{margin-top:0}
.legs-pick{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px}
.lp{border:2px solid var(--line);border-radius:16px;padding:6px 10px 8px;margin:0;min-width:0}
.lp legend{display:flex;gap:8px;align-items:center;font:600 16px var(--f-display);padding:0 6px}
.mini{font:800 12px var(--f-body);padding:3px 9px;border-radius:99px;border:2px solid var(--line);background:var(--surface);color:var(--lapis);cursor:pointer}
.ck{display:flex;gap:10px;align-items:flex-start;padding:6px 4px;cursor:pointer;border-radius:10px}
.ck input{width:20px;height:20px;margin:2px 0 0;accent-color:var(--lapis);flex:none}
.ck span{min-width:0;line-height:1.3;overflow-wrap:anywhere}.ck small{display:block;color:var(--muted);font-weight:700;font-size:13px}.ck.big b{font:600 17px var(--f-display)}
.kd{font-style:normal;font-size:11px;font-weight:800;padding:1px 7px;border-radius:99px;background:var(--sunk);color:var(--muted);white-space:nowrap}.kd.v{background:var(--tile-soft);color:var(--tile-deep)}
.parts{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:4px 12px;margin-bottom:8px}
.sum{margin:0}.sum b{display:block;font:600 20px var(--f-display)}.sum small{display:block;color:var(--bad);font-weight:800}
.as-list{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.as-list li{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px;padding:12px;border-radius:14px;background:var(--sunk)}
.as-list li>div{min-width:0;flex:1 1 220px}.as-list b{display:block;overflow-wrap:anywhere}.as-list small{color:var(--muted);font-weight:700}
.as-list .actions{margin:0;flex:1 1 260px}.as-list .actions>*{flex:1 1 120px;padding:10px 14px;font-size:15px}
.vgroup h3{font-size:19px;margin:18px 0 8px}.vgroup small{color:var(--muted);font:700 14px var(--f-body)}
.vtable-w{overflow-x:auto}.vtable{width:100%;border-collapse:collapse;font-size:15px}
.vtable th,.vtable td{text-align:left;padding:8px;border-bottom:2px solid var(--sunk);vertical-align:top}
.vtable th{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.vtable summary{font-weight:800;cursor:pointer}.vtable ul{margin:6px 0 0;padding-left:18px;color:var(--muted);font-size:14px}
.vst{display:inline-block;padding:3px 10px;border-radius:99px;font-weight:800;font-size:13px;white-space:nowrap}
.vst.ok{background:var(--ok-soft);color:var(--ok-deep)}.vst.bad{background:var(--bad-soft);color:var(--bad-deep)}.vst.unk{background:var(--sunk);color:var(--muted)}
.as-head{margin-top:12px;padding:20px;border-radius:24px;background:var(--lapis);color:var(--on-lapis)}
.as-head .eyebrow{color:inherit;opacity:.85}.as-head h1{font-size:clamp(28px,6vw,40px);margin-bottom:6px;overflow-wrap:anywhere}
.as-note{margin:0 0 10px;font-weight:700;white-space:pre-line;overflow-wrap:anywhere}
.due{display:inline-flex;gap:6px;align-items:center;margin:0;padding:4px 12px;border-radius:99px;background:rgba(255,255,255,.2);font-weight:800}.due svg{width:18px;height:18px}.due.late{background:var(--pom);color:#fff}
.as-prog{display:flex;gap:14px;align-items:center}.as-prog>div{min-width:0}.as-prog b{font:600 20px var(--f-display);display:block}.as-prog p{margin:0;color:var(--muted);font-weight:700}
.linkish{border:0;background:none;padding:0;color:var(--lapis);font:inherit;text-decoration:underline;cursor:pointer}
.au-h{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:10px}.au-h>div{min-width:0}.au-h h2{margin:0;overflow-wrap:anywhere}.au-h .btn{padding:9px 14px;font-size:15px;flex:none}
.tasks{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.trow{display:grid;grid-template-columns:auto 1fr auto;gap:12px;align-items:center;padding:10px 12px;border-radius:16px;border:2px solid var(--line);border-bottom-width:4px;color:var(--ink);text-decoration:none;background:var(--surface)}
.trow .tk{display:grid;place-items:center;width:30px;height:30px}.trow .tk i{width:22px;height:22px;border-radius:50%;border:3px solid var(--line)}
.trow .tk svg{width:28px;height:28px;color:var(--bad)}.trow.done .tk svg{color:var(--ok)}.trow.done{background:var(--ok-soft);border-color:var(--ok)}
.trow .tl{min-width:0}.trow b{display:block;font:600 17px var(--f-display)}.trow small{color:var(--muted);font-weight:700;font-size:13px;overflow-wrap:anywhere}
.trow .go{font:700 15px var(--f-display);color:var(--lapis)}
.name-f{display:flex;flex-wrap:wrap;gap:10px}.name-f .text-in{flex:1 1 220px;width:auto}.name-f .btn{flex:1 1 120px}
.send .share-box{font:14px/1.45 ui-monospace,Menlo,monospace;resize:vertical}
.banner.pv{background:var(--tile-soft);border-color:var(--tile);flex-wrap:wrap}.banner.pv>div{flex:1 1 220px}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""

JS = r"""
(()=>{
'use strict';
const DATA=JSON.parse(document.getElementById('a2-data').textContent);
const UNITS=DATA.units,CITIES=DATA.cities,SCENES=DATA.scenes,UMAP={};UNITS.forEach(u=>UMAP[u.n]=u);const U=n=>UMAP[n];
/* Assignment mode: a teacher-made file carries only the chosen units plus a config (#a2-assign);
   the teacher's own preview keeps the config in sessionStorage. Then the app shows only those tasks. */
let AS=null,PREVIEW=false;
try{const el=document.getElementById('a2-assign');if(el)AS=JSON.parse(el.textContent)}catch(e){}
if(!AS)try{const pv=sessionStorage.getItem('destA2.preview');if(pv){AS=JSON.parse(pv);PREVIEW=true}}catch(e){}
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const app=$('#app');
const h=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm=s=>String(s).toLowerCase().replace(/[’‘`ʻʼ]/g,"'").replace(/\s+/g,' ').trim().replace(/[.!?]+$/,'');
const RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
let RNG=Math.random;
const shuffle=a=>{a=a.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(RNG()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a};
const pick=(a,n)=>shuffle(a).slice(0,n);
const range=n=>Array.from({length:n},(_,i)=>i);
const any=a=>a[Math.floor(RNG()*a.length)];
const rnd=n=>Math.floor(RNG()*n);
function seeded(str){let x=2166136261;for(const c of str){x^=c.charCodeAt(0);x=Math.imul(x,16777619)}return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return(x>>>0)/4294967296}}
const dayKey=(d=new Date())=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
const fmt=s=>Math.floor(s/60)+':'+String(s%60).padStart(2,'0');
const fill=(q,a)=>q.replace('___',a);

/* ---------- icons ---------- */
const svg=p=>`<svg class="i" viewBox="0 0 24 24" aria-hidden="true">${p}</svg>`;
const I={
 flame:svg('<path fill="currentColor" d="M12 2c1 3.5-1.6 5.3-2.8 7.4C8.1 11.3 8.4 13 9.6 13c-2.7-.4-3.7-3-3.2-5C3.8 10.3 3 13 3 15a9 9 0 0 0 18 0c0-4.6-3.4-7.2-4.3-10.2-.8 2-2 3-3.3 3.3C14.2 6 13.6 3.8 12 2z"/>'),
 gem:svg('<path fill="currentColor" d="M6 3h12l4 6-10 12L2 9z"/><path fill="rgba(255,255,255,.45)" d="M6 3l3 6H2zm12 0l-3 6h7zM9 9h6l-3 12z"/>'),
 heart:svg('<path fill="currentColor" d="M12 21s-8-5.2-8-11.2A4.8 4.8 0 0 1 12 6.6a4.8 4.8 0 0 1 8 3.2C20 15.8 12 21 12 21z"/>'),
 crown:svg('<path fill="currentColor" d="M3 7l4.5 4L12 4l4.5 7L21 7l-2 12H5z"/>'),
 x:svg('<path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" fill="none"/>'),
 check:svg('<circle cx="12" cy="12" r="11" fill="currentColor"/><path d="M7 12.5l3.2 3.2L17 9" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'),
 cross:svg('<circle cx="12" cy="12" r="11" fill="currentColor"/><path d="M8.5 8.5l7 7m0-7l-7 7" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/>'),
 speaker:svg('<path fill="currentColor" d="M4 9h4l5-4v14l-5-4H4z"/><path d="M16 8.5a5 5 0 0 1 0 7M18.5 6a8.5 8.5 0 0 1 0 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'),
 clock:svg('<circle cx="12" cy="13" r="8" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M12 9v4l3 2M9 2h6" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" fill="none"/>'),
 bolt:svg('<path fill="currentColor" d="M13 2L4 14h6l-1 8 9-12h-6z"/>'),
 cal:svg('<rect x="3" y="5" width="18" height="16" rx="3" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M3 10h18M8 3v4m8-4v4" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/><rect x="7" y="13" width="4" height="4" rx="1" fill="currentColor"/>'),
 redo:svg('<path d="M20 12a8 8 0 1 1-2.4-5.7M20 4v5h-5" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'),
 shield:svg('<path fill="currentColor" d="M12 2l8 3v6c0 5-3.4 9.4-8 11-4.6-1.6-8-6-8-11V5z"/><path d="M8 12l3 3 5-6" fill="none" stroke="rgba(0,0,0,.35)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'),
 swords:svg('<path d="M4 4l9 9M20 4l-9 9M6 16l-2 2 2 2 2-2M18 16l2 2-2 2-2-2M7 13l4 4M17 13l-4 4" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" fill="none"/>'),
 plane:svg('<path fill="currentColor" d="M21 16v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5z"/>'),
 back:svg('<path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'),
 bulb:svg('<path fill="currentColor" d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/><path d="M9 20h6M10 23h4" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>'),
 snow:svg('<path d="M12 2v20M3.3 7l17.4 10M3.3 17 20.7 7M9 4l3 3 3-3M9 20l3-3 3 3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'),
 cards:svg('<rect x="3" y="4" width="11" height="15" rx="2" fill="currentColor" opacity=".45"/><rect x="10" y="5" width="11" height="15" rx="2" fill="currentColor"/>'),
 abc:svg('<path d="M3 18 6.5 6h1L11 18M4.3 14h5.4M13 6h4a3 3 0 0 1 0 6h-4zm0 6h4.5a3 3 0 0 1 0 6H13z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>'),
 eye:svg('<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z" fill="none" stroke="currentColor" stroke-width="2.2"/><circle cx="12" cy="12" r="3.5" fill="currentColor"/>'),
 clip:svg('<rect x="5" y="4" width="14" height="18" rx="2.5" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M9 4.5V2.5h6v2M8.5 11l2 2 4-4M8.5 17h7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'),
 chat:svg('<path fill="currentColor" d="M4 4h16a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H9l-5 4v-4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/><path d="M7 9h10M7 12h6" stroke="rgba(0,0,0,.35)" stroke-width="2" stroke-linecap="round"/>')
};
const DEV=`<svg class="dev-svg" viewBox="0 0 100 100" aria-hidden="true"><path d="M24 34 10 6l24 18zM76 34 90 6 66 24z" fill="var(--gold)" stroke="var(--m-line)" stroke-width="3" stroke-linejoin="round"/>
<circle cx="50" cy="56" r="36" fill="var(--pom)" stroke="var(--m-line)" stroke-width="3"/><path d="M31 45l13 6M69 45l-13 6" stroke="var(--m-line)" stroke-width="4.5" stroke-linecap="round"/>
<circle cx="39" cy="58" r="6" fill="#fff" stroke="var(--m-line)" stroke-width="2"/><circle cx="61" cy="58" r="6" fill="#fff" stroke="var(--m-line)" stroke-width="2"/><circle cx="40" cy="59" r="2.5" fill="var(--m-line)"/><circle cx="60" cy="59" r="2.5" fill="var(--m-line)"/>
<path d="M35 77q15-11 30 0" fill="none" stroke="var(--m-line)" stroke-width="4" stroke-linecap="round"/><path d="M41 73l3 6 3-5 3 5 3-5 3 6" fill="#fff" stroke="var(--m-line)" stroke-width="1.5" stroke-linejoin="round"/></svg>`;
const STORK=`<svg class="stork" viewBox="0 0 120 120" aria-hidden="true">
<g stroke="#e5533d" stroke-width="3.5" stroke-linecap="round" fill="none"><path d="M52 88L50 112l-6 2"/><path d="M64 88l3 24 6 2"/></g>
<ellipse cx="58" cy="74" rx="28" ry="17" fill="#fff" stroke="var(--m-line)" stroke-width="2.5"/>
<path class="st-wing" d="M62 64C46 57 28 61 20 76c10 5 28 7 42 2z" fill="#1c2233" stroke="var(--m-line)" stroke-width="2"/>
<path d="M72 72C80 60 83 49 80 37" fill="none" stroke="var(--m-line)" stroke-width="12" stroke-linecap="round"/>
<path d="M72 72C80 60 83 49 80 37" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round"/>
<path d="M73 50c3 3 8 3 11 0l-1 8c-3 2-7 2-10 0z" fill="var(--tile)" stroke="var(--m-line)" stroke-width="1.5"/>
<circle cx="80" cy="30" r="12" fill="#fff" stroke="var(--m-line)" stroke-width="2.5"/>
<path d="M89 26l27 7-27 3z" fill="#f28c28" stroke="var(--m-line)" stroke-width="2" stroke-linejoin="round"/>
<circle class="eye-open" cx="82" cy="27" r="2.8" fill="var(--m-line)"/>
<path class="eye-happy" d="M78.5 28.5q3.5-4.5 7 0" fill="none" stroke="var(--m-line)" stroke-width="2.4" stroke-linecap="round"/>
<circle cx="76" cy="34" r="2.6" fill="#ff9aa2" opacity=".75"/></svg>`;
const mascot=(mood,text)=>`<div class="mascot ${mood||'idle'}">${STORK}${text?`<div class="bubble">${text}</div>`:''}</div>`;

/* ---------- state ---------- */
const KEY=AS?'destA2.as.'+AS.id:'destA2.v3';
const FRESH=()=>({xp:0,days:{},crowns:{},boss:{},exam:{},mistakes:{},fixed:0,badges:{},blitz:0,daily:{},tests:{},errs:{},powers:{half:1,heal:0},scenes:{},sure:{n:0,ok:0},games:{},freeze:0,goalDays:0,frozen:[],stats:{sessions:0,correct:0,answered:0,maxCombo:0,secs:0},goal:50,sound:true,theme:null,tasks:{},assigns:{},name:'',lv:{},tries:{},firstT:{},rev:null,revFail:0});
let S=FRESH();
function load(raw){const o=Object.assign(FRESH(),raw);o.stats=Object.assign(FRESH().stats,raw.stats||{});o.powers=Object.assign(FRESH().powers,raw.powers||{});o.sure=Object.assign(FRESH().sure,raw.sure||{});
 for(const k in o.mistakes)if(typeof o.mistakes[k]!=='object')o.mistakes[k]={b:0,d:dayKey()}; // older saves stored a counter
 return o}
try{const raw=JSON.parse(localStorage.getItem(KEY));if(raw&&typeof raw==='object')S=load(raw)}catch(e){}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}};
const todayXP=()=>S.days[dayKey()]||0;
function streak(){const d=new Date();let n=0;if(!(dayKey(d) in S.days))d.setDate(d.getDate()-1);while(dayKey(d) in S.days){n++;d.setDate(d.getDate()-1)}return n}
function addXP(g){const t=dayKey(),before=S.days[t]||0;S.xp+=g;S.days[t]=before+g;
 if(before<S.goal&&S.days[t]>=S.goal){S.goalDays++;if(S.goalDays%5===0&&S.freeze<2){S.freeze++;setTimeout(()=>toast(`${I.snow} Seriya muzlatgichi qo'lga kiritildi!`),900)}}} // 1 freeze per 5 days with the goal met
/* A streak freeze fills missed days (up to the number owned) so one busy day does not break the streak. */
function applyFreeze(){const keys=Object.keys(S.days).sort(),t=dayKey();if(!S.freeze||!keys.length)return;const last=keys[keys.length-1];if(last>=t)return;
 const gap=[],d=new Date(last+'T12:00:00');for(let i=0;i<60;i++){d.setDate(d.getDate()+1);const k=dayKey(d);if(k>=t)break;gap.push(k)}
 if(gap.length&&gap.length<=S.freeze){gap.forEach(k=>{S.days[k]=0;S.frozen.push(k)});S.freeze-=gap.length;save();setTimeout(()=>toast(`${I.snow} Seriya muzlatgichi ishlatildi: seriya saqlandi!`),700)}}
const lvStart=L=>50*(L-1)*L;
const levelOf=xp=>{let L=1;while(xp>=lvStart(L+1))L++;return L};
const RANKS=['Tourist','Traveller','Explorer','Navigator','Pilot','Captain','Globetrotter','Legend'];
const rankOf=L=>RANKS[Math.min(RANKS.length-1,Math.floor((L-1)/2))];
const crowns=n=>S.crowns[n]||0;
/* Mistakes come back with spaced review: due today, then 1 day and 3 days after each right answer; the third right answer clears it. */
const addDays=n=>{const d=new Date();d.setDate(d.getDate()+n);return dayKey(d)};
function addMistake(k){if(!k)return;S.mistakes[k]={b:0,d:dayKey()};const n=+k.split(':')[0];S.errs[n]=(S.errs[n]||0)+1}
function reviewMistake(k,ok){const m=S.mistakes[k];if(!m)return;if(!ok){m.b=0;m.d=addDays(1);const n=+k.split(':')[0];S.errs[n]=(S.errs[n]||0)+1;return}
 if(m.b>=2){delete S.mistakes[k];S.fixed++}else{m.d=addDays([1,3][m.b]);m.b++}}
const isDue=k=>S.mistakes[k]&&S.mistakes[k].d<=dayKey();
const mistakeCount=()=>Object.keys(S.mistakes).length;
const dueKeys=()=>Object.keys(S.mistakes).filter(isDue);

/* ---------- sound, speech, toast, confetti ---------- */
let AC;
function tone(seq){if(!S.sound)return;try{AC=AC||new(window.AudioContext||window.webkitAudioContext)();const t0=AC.currentTime;
 seq.forEach(([f,d,st,type])=>{const o=AC.createOscillator(),g=AC.createGain();o.type=type||'sine';o.frequency.value=f;
 g.gain.setValueAtTime(.0001,t0+st);g.gain.exponentialRampToValueAtTime(.17,t0+st+.012);g.gain.exponentialRampToValueAtTime(.0001,t0+st+d);
 o.connect(g).connect(AC.destination);o.start(t0+st);o.stop(t0+st+d+.03)})}catch(e){}}
const sfx={ok:()=>tone([[660,.12,0],[990,.2,.09]]),bad:()=>tone([[220,.14,0,'triangle'],[165,.26,.12,'triangle']]),tap:()=>tone([[540,.05,0]]),
 combo:()=>tone([[784,.1,0],[988,.1,.08],[1319,.2,.16]]),win:()=>tone([[523,.14,0],[659,.14,.12],[784,.14,.24],[1047,.4,.36]]),
 lose:()=>tone([[392,.2,0,'triangle'],[330,.2,.18,'triangle'],[262,.45,.36,'triangle']])};
const TTS='speechSynthesis' in window;if(!TTS)document.documentElement.classList.add('no-tts');
function say(t,slow){if(!TTS||!t)return;try{speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(t);u.lang='en-GB';u.rate=slow?.6:.92;
 const vs=speechSynthesis.getVoices();const v=vs.find(x=>/^en[-_]GB/i.test(x.lang))||vs.find(x=>/^en/i.test(x.lang));if(v)u.voice=v;speechSynthesis.speak(u)}catch(e){}}
if(TTS)try{speechSynthesis.getVoices()}catch(e){}
if(AS)document.title=AS.title+' · Destination A2';
function toast(html){let t=$('.toast');if(!t){t=document.createElement('div');t.className='toast';t.setAttribute('role','status');document.body.appendChild(t)}
 t.innerHTML=html;t.classList.remove('show');void t.offsetWidth;t.classList.add('show');clearTimeout(t._h);t._h=setTimeout(()=>t.classList.remove('show'),1800)}
function confetti(){if(RM)return;const c=document.createElement('canvas');c.className='confetti';document.body.appendChild(c);
 const W=c.width=innerWidth,H=c.height=innerHeight,ctx=c.getContext('2d'),cs=getComputedStyle(document.documentElement);
 const cols=['--lapis','--tile','--gold','--pom','--ok'].map(v=>cs.getPropertyValue(v).trim());
 const P=Array.from({length:160},()=>({x:W/2+(Math.random()-.5)*W*.5,y:H*.35,vx:(Math.random()-.5)*15,vy:-Math.random()*14-4,r:Math.random()*7+4,c:cols[Math.random()*5|0],a:Math.random()*6,va:(Math.random()-.5)*.35}));
 let t=0;(function f(){ctx.clearRect(0,0,W,H);P.forEach(p=>{p.vy+=.36;p.x+=p.vx;p.y+=p.vy;p.vx*=.985;p.a+=p.va;ctx.save();ctx.translate(p.x,p.y);ctx.rotate(p.a);ctx.fillStyle=p.c;ctx.fillRect(-p.r/2,-p.r/4,p.r,p.r/2);ctx.restore()});
 if(++t<130)requestAnimationFrame(f);else c.remove()})()}
const shake=el=>{if(!el)return;el.classList.remove('shake');void el.offsetWidth;el.classList.add('shake')};
const PRAISE=['Zo\'r!','Barakalla!','Ajoyib!','Great!','Perfect!','Nice one!','Qoyil!','Well done!'];
const COMFORT=['Hechqisi yo\'q!','Almost!','Keyingisi chiqadi!','Don\'t give up!','Oz qoldi!'];

/* ---------- question builders ---------- */
// Each question: {kind:'choice'|'type'|'order'|'pairs', inst, prompt, say, auto, opts, ans, accept, words, pairs, full, key}
// key = "unit:type:index" so a missed question can come back in the mistakes review.
const blankHTML=q=>h(q).replace('___','<span class="blank"></span>');
const clean=t=>t.replace(/\s*\([^)]*\)/g,'');
const SRC={m:'mc',t:'test',x:'tx'}; // m = practice (exercise A); t, x = test-only items
function qMC(u,i,src='m'){const[q,o]=u[SRC[src]][i];return{kind:'choice',inst:'To\'g\'ri variantni tanlang',prompt:blankHTML(q),opts:shuffle(o),ans:o[0],full:fill(q,o[0]),key:u.n+':'+src+':'+i}}
function qTestGap(u,i){const[q,a]=u.tg[i];return{kind:'type',inst:'Bo\'sh joyni yozing',prompt:h(q),accept:a,ans:a[0],full:clean(fill(q,a[0])),key:u.n+':y:'+i}}
function qListen(u,i){if(!TTS)return qMC(u,i);const[q,o]=u.mc[i];const s=o.map(x=>fill(q,x));
 return{kind:'choice',inst:'Tinglang va eshitgan gapni tanlang',say:s[0],auto:true,opts:shuffle(s),ans:s[0],full:s[0],long:true,key:u.n+':m:'+i}}
function gapChoices(u,i){const a=u.gaps[i][1];const pool=[...new Set(u.gaps.map(g=>g[1][0]))].filter(x=>!a.some(y=>norm(y)===norm(x)));return shuffle([a[0],...pick(pool,3)])}
function qGapBank(u,i){const[q,a]=u.gaps[i];return{kind:'choice',inst:'Bo\'sh joyga mosini tanlang',prompt:blankHTML(q),opts:gapChoices(u,i),ans:a[0],full:clean(fill(q,a[0])),chips:true,key:u.n+':g:'+i}}
function qType(u,i){const[q,a]=u.gaps[i];return{kind:'type',inst:'Bo\'sh joyni yozing',prompt:h(q),accept:a,ans:a[0],full:clean(fill(q,a[0])),key:u.n+':g:'+i}}
function qOrder(u,i){const s=u.ord[i];const w=s.split(' ');let sh,t=0;do sh=shuffle(w);while(sh.join(' ')===s&&++t<12);
 return{kind:'order',inst:'So\'zlardan gap tuzing',words:sh,ans:s,full:s,key:u.n+':o:'+i}}
function qWord(u,i,mode){const[en,uz,ex]=u.W[i];const others=pick(range(u.W.length).filter(k=>k!==i),3);const k=u.n+':w:'+i;
 if(mode==='uz')return{kind:'choice',inst:'Bu so\'z nimani anglatadi?',prompt:`<span class="big-word">${h(en)}<button type="button" class="speak sm" data-say="${h(en)}" aria-label="Tinglash">${I.speaker}</button></span>`,say:en,auto:true,opts:shuffle([uz,...others.map(o=>u.W[o][1])]),ans:uz,full:ex,key:k};
 if(mode==='listen'&&TTS)return{kind:'choice',inst:'Tinglang va so\'zni tanlang',say:en,auto:true,opts:shuffle([en,...others.map(o=>u.W[o][0])]),ans:en,full:ex,key:k};
 if(mode==='type'&&!/[\/.]/.test(en))return{kind:'type',inst:'Inglizchasini yozing',prompt:`<span lang="uz">${h(uz)}</span> = ___`,accept:[en],ans:en,full:ex,key:k};
 return{kind:'choice',inst:'Inglizchasini tanlang',prompt:`<span class="big-word" lang="uz">${h(uz)}</span>`,opts:shuffle([en,...others.map(o=>u.W[o][0])]),ans:en,full:ex,key:k}}
function qSpot(u,i){const[q,o]=u.mc[i];const wrong=o[1+Math.floor(RNG()*2)];const[pre,post]=q.split('___');const toks=[];
 const push=(t,bad)=>t.split(' ').filter(Boolean).forEach(w=>toks.push([w,bad]));push(pre,false);push(wrong,true);push(post,false);
 return{kind:'spot',inst:'Xatoni toping: noto\'g\'ri so\'zni bosing',toks,ans:`${wrong} → ${o[0]}`,full:fill(q,o[0]),key:u.n+':m:'+i}}
function qDict(u,i){if(!TTS)return qOrder(u,i);const s=u.ord[i];return{kind:'type',dict:true,inst:'Tinglang va gapni yozing',say:s,auto:true,prompt:'___',accept:[s],ans:s,full:s,key:u.n+':o:'+i}}
function qPairs(u){const ids=pick(range(u.W.length),5);return{kind:'pairs',inst:'Juftlarini toping',pairs:ids.map(i=>[u.W[i][0],u.W[i][1]]),ans:'',full:''}}
function fromKey(k){ // a missed question comes back in its easiest recognisable form
const[n,t,i]=k.split(':');const u=U(+n);if(!u)return null;const j=+i;
 if(SRC[t]&&u[SRC[t]][j])return qMC(u,j,t);if(t==='y'&&u.tg[j])return qTestGap(u,j);if(t==='g'&&u.gaps[j])return qGapBank(u,j);if(t==='o'&&u.ord[j])return qOrder(u,j);if(t==='w'&&u.W&&u.W[j])return qWord(u,j,'uz');return null}

const LEVELS=[null,{name:'Tanishuv',desc:'Variant tanlash va gap tuzish. Isinish uchun.'},{name:'Mashq',desc:'Tinglab tanlash, so\'z banki va aralash savollar.'},{name:'Usta',desc:'Javobni o\'zingiz yozasiz. Eng qiyin daraja.'}];
function unitQuestions(u,L){const mA=range(u.mc.length),g=range(u.gaps.length),o=range(u.ord.length),v=u.k==='v',w=v?range(u.W.length):[];let qs=[];
 if(L===1){qs=[...pick(mA,5).map(i=>qMC(u,i)),...pick(o,2).map(i=>qOrder(u,i))];
  qs.push(...(v?[...pick(w,3).map(i=>qWord(u,i,'uz')),qPairs(u)]:pick(g,3).map(i=>qGapBank(u,i))))}
 else if(L===2){const m=shuffle(mA);qs=[...m.slice(0,3).map(i=>qMC(u,i)),...m.slice(3,5).map(i=>qListen(u,i)),qSpot(u,m[5]),...pick(g,3).map(i=>qGapBank(u,i)),...pick(o,2).map(i=>qOrder(u,i))];
  if(v)qs.push(...pick(w,2).map(i=>qWord(u,i,'en')),qWord(u,any(w),'listen'),qPairs(u))}
 else{const m=pick(mA,4),oo=pick(o,3);qs=[...pick(g,4).map(i=>qType(u,i)),...m.slice(0,2).map(i=>qMC(u,i)),...oo.slice(0,2).map(i=>qOrder(u,i)),qListen(u,m[2]),qSpot(u,m[3]),qDict(u,oo[2])];
  if(v)qs.push(...pick(w,3).map(i=>qWord(u,i,'type')))}
 const first=qs.shift();return[first,...shuffle(qs)]}

/* ---------- journey structure ---------- */
const legUnits=i=>[3*i+1,3*i+2,3*i+3];
const legOf=n=>Math.floor((n-1)/3);
function nextStop(){if(AS)return null;for(let i=0;i<14;i++){for(const n of legUnits(i)){if(!crowns(n))return{t:'u',n};if(!(n in S.tests))return{t:'test',n}}if(!S.boss[i])return{t:'boss',i};if(S.scenes[i]==null)return{t:'scene',i};if(i===6&&!(S.exam[1]>=70))return{t:'exam',k:1}}
 if(!(S.exam[2]>=70))return{t:'exam',k:2};const n=UNITS.find(u=>crowns(u.n)<3);return n?{t:'u',n:n.n}:null}
const stopHref=s=>!s?(AS?'#':'#me'):s.t==='u'?`#play-u-${s.n}-${Math.min(3,crowns(s.n)+1)}`:s.t==='test'?`#test-u-${s.n}`:s.t==='boss'?`#boss-${s.i}`:s.t==='scene'?`#scene-${s.i}`:`#exam-${s.k}`;
const stopLabel=s=>!s?'Hammasi tugadi!':s.t==='u'?`Unit ${s.n}: ${U(s.n).t}`:s.t==='test'?`Unit ${s.n} testi · 20 savol`:s.t==='boss'?`Review ${s.i+1}: ${CITIES[s.i].name} darvozasi`:s.t==='scene'?`Sahna: ${SCENES[s.i].title}`:`Progress Test ${s.k}`;

/* ---------- screens ---------- */
let CUR={act:{},key:null},SES=null;
const topbar=()=>{const L=levelOf(S.xp),st=streak();return`<header class="bar"><a class="logo" href="#" aria-label="Destination A2, xarita"><span class="lg">Destination </span><b>A2</b></a><div class="chips">
<span class="chip streak ${st?'':'dim'}" title="Kunlik seriya${S.freeze?` · ${S.freeze} ta muzlatgich`:''}">${I.flame}${st}${S.freeze?`<i class="fz">${I.snow}${S.freeze}</i>`:''}</span><span class="chip xp" title="Jami XP">${I.gem}${S.xp}</span><a class="chip lvl" href="#me" title="Profil">Lv ${L}</a></div></header>`};
function greet(){const hr=new Date().getHours();const hi=hr<12?'Xayrli tong!':hr<18?'Salom!':'Xayrli kech!';const st=streak();
 if(!S.stats.sessions)return`${hi} Men Laylak, Buxorodan. Birga sayohat qilamizmi?<small>Hi! I'm Laylak. Let's travel and learn English.</small>`;
 if(todayXP()>=S.goal)return`${hi} Bugungi maqsad bajarildi. Qoyil!<small>Yana bir oz mashq qilsangiz, rekord bo'ladi.</small>`;
 return`${hi} ${st?`Seriyangiz: ${st} kun. Uzmang!`:'Bugun yangi seriya boshlaymiz!'}<small>Maqsadgacha ${S.goal-todayXP()} XP qoldi.</small>`}
function ring(v,max){const r=26,c=2*Math.PI*r,p=Math.min(1,v/max);return`<svg class="ring" viewBox="0 0 64 64" aria-hidden="true"><circle class="trk" cx="32" cy="32" r="${r}"/><circle class="val" cx="32" cy="32" r="${r}" stroke-dasharray="${c}" stroke-dashoffset="${c*(1-p)}"/></svg>`}
const crownRow=n=>`<span class="crowns" aria-label="${n} / 3 toj">${[1,2,3].map(k=>`<span class="${k<=n?'':'off'}">${I.crown}</span>`).join('')}</span>`;
const gradeOf=p=>p>=86?[5,'a\'lo']:p>=70?[4,'yaxshi']:p>=55?[3,'qoniqarli']:[2,'qoniqarsiz'];
const gradeChip=p=>`<span class="grade g${gradeOf(p)[0]}" title="${p}%">${gradeOf(p)[0]}</span>`;
function gradeBanner(p){const[g,t]=gradeOf(p);return`<div class="banner grade-b">${gradeChip(p)}<div><b>Baho: ${g} (${t})</b><p>${p}% · o'tish chegarasi 70%</p></div></div>`}
function reviewList(log,hide){ // hide = attempts remain, so show which answers were wrong but not the right ones
 return`<section class="card answers"><h2>Javoblaringiz</h2>${hide?'<p class="note">To\'g\'ri javoblar urinishlar tugagach ko\'rsatiladi.</p>':''}<ol>${log.map(r=>`<li class="${r.ok?'ok':'bad'}"><span class="mk">${r.ok?I.check:I.cross}</span><div><p>${hide?r.q.prompt.replace('___','<span class="blank"></span>'):h(r.q.full)}</p>${r.ok?'':`<p class="yours">Sizning javobingiz: <s>${h(r.given||'—')}</s></p>`}</div></li>`).join('')}</ol></section>`}
const you=(t,o)=>`<span class="you ${o>0?'l':''}">${STORK}<span>${t}</span></span>`;

function home(){const ns=nextStop(),dk=S.daily[dayKey()],mc=mistakeCount(),off=[0,1,0,-1];
 const legs=CITIES.map((c,i)=>{
  const rows=legUnits(i).map((n,k)=>{const u=U(n),cr=crowns(n),isNext=ns&&ns.t==='u'&&ns.n===n;
   return`<li class="node-row" style="--o:${off[(i*4+k)%4]}"><a class="node ${u.k} ${cr===3?'full':''} ${isNext?'next':''}" href="#u-${n}" style="--c:${cr/3}" aria-label="Unit ${n}: ${h(u.t)}. ${cr} / 3 toj"><span class="node-in">${n}</span>${n in S.tests?`<span class="tb ${S.tests[n]>=70?'pass':'fail'}" title="Unit testi: ${S.tests[n]}%">${gradeOf(S.tests[n])[0]}</span>`:''}</a><span class="node-label">${h(u.t)}<small>${u.k==='v'?'Lug\'at':'Grammatika'}</small></span>${isNext?you('Shu yerda!',off[(i*4+k)%4]):''}</li>`}).join('');
  const bNext=ns&&ns.t==='boss'&&ns.i===i;
  const boss=`<li class="node-row" style="--o:${off[(i*4+3)%4]}"><a class="node boss ${S.boss[i]?'won':''} ${bNext?'next':''}" href="#boss-${i}" style="--c:${S.boss[i]?1:0}" aria-label="Review ${i+1}, boss jangi: ${c.name}"><span class="node-in">${S.boss[i]?I.shield:I.swords}</span></a><span class="node-label">Review ${i+1}<small>Boss jangi · ${c.name}</small></span>${bNext?you('Jang!',off[(i*4+3)%4]):''}</li>`;
  const sNext=ns&&ns.t==='scene'&&ns.i===i,sc=SCENES[i],so=-off[(i*4+3)%4];
  const scn=`<li class="node-row" style="--o:${so}"><a class="node scene ${S.scenes[i]!=null?'won':''} ${sNext?'next':''}" href="#scene-${i}" style="--c:${(S.scenes[i]||0)/3}" aria-label="Sahna: ${h(sc.title)}"><span class="node-in">${I.chat}</span></a><span class="node-label">Sahna<small>${h(sc.title)}</small></span>${sNext?you('Suhbat!',so):''}</li>`;
  let exam='';if(i===6||i===13){const k=i===6?1:2,ok=S.exam[k]>=70,eNext=ns&&ns.t==='exam'&&ns.k===k;
   exam=`<div class="city airport"><div><p class="eyebrow">Aeroport · nazorat nuqtasi</p><h2>Progress Test ${k}</h2><p>Unitlar ${k===1?'1–21':'22–42'} · 30 savol</p></div>${ok?`<span class="stamp"><small>PASSED</small><b>Gate ${k}</b></span>`:''}</div>
   <ol class="path"><li class="node-row"><a class="node exam ${ok?'won':''} ${eNext?'next':''}" href="#exam-${k}" style="--c:${ok?1:0}" aria-label="Progress Test ${k}"><span class="node-in">${I.plane}</span></a><span class="node-label">Progress Test ${k}<small>30 savol · 70% dan o'ting</small></span>${eNext?you('Uchamiz!'):''}</li></ol>`}
  return`<section class="leg" id="leg-${i}"><div class="city"><div><p class="eyebrow">${i+1}-bosqich · Unitlar ${3*i+1}–${3*i+3}</p><h2>${c.name}</h2><p>${c.uz}</p></div>${S.boss[i]?`<span class="stamp"><small>VISITED</small><b>${h(c.name.split(' ')[0])}</b></span>`:''}</div><ol class="path">${rows}${boss}${scn}</ol>${exam}</section>`}).join('');
 const due=dueKeys().length,done=CITIES.filter((_,i)=>S.boss[i]).length,tp=UNITS.filter(u=>S.tests[u.n]>=70).length,ep=[1,2].filter(k=>S.exam[k]>=70).length;
 app.innerHTML=`<div class="wrap">${topbar()}
<section class="hero">${mascot('idle',greet())}
<div class="goal">${ring(todayXP(),S.goal)}<div><b>${todayXP()} / ${S.goal} XP</b><p>Bugungi maqsad${todayXP()>=S.goal?' bajarildi':''}</p></div></div>
<a class="btn big" href="${stopHref(ns)}" id="continue">${S.stats.sessions?'Davom etish':'Sayohatni boshlash'}</a><p class="cont-sub">${h(stopLabel(ns))}</p></section>
<nav class="modes" aria-label="O'yin rejimlari">
<a class="mode daily" href="#daily">${I.cal}<b>Kunlik chaqiruv</b><span>${dk?`Bugun: ${dk.c}/10 · ${fmt(dk.t)}`:'10 savol, hammaga bir xil'}</span></a>
<a class="mode blitz" href="#blitz">${I.bolt}<b>Blitz 60 s</b><span>${S.blitz?`Rekord: ${S.blitz}`:'Qancha tez javob berasiz?'}</span></a>
<a class="mode games" href="#games">${I.cards}<b>O'yinlar</b><span>Xotira, harf jumbog'i, yashirin so'z, omon qolish</span></a>
<a class="mode fix ${mc?'':'off'}" href="#mistakes">${I.redo}<b>Takrorlash</b><span>${mc?`Bugun ${due} ta · jami ${mc} ta xato`:'Hozircha xato yo\'q'}</span></a></nav>
<div class="map-h"><h2>Sayohat xaritasi</h2><span>${done} / 14 shahar</span></div>
<p class="book" aria-label="Kitob tuzilishi"><span class="bk"><b>28</b> grammatika</span><span class="bk"><b>14</b> lug'at</span><span class="bk"><b>${tp}/42</b> unit testi</span><span class="bk"><b>${done}/14</b> review</span><span class="bk"><b>${ep}/2</b> progress test</span></p>${legs}
<a class="teach-link" href="#teacher">${I.clip}<span><b>O'qituvchi uchun</b><small>O'quvchilarga faqat tanlangan unit va vazifalarni fayl qilib bering</small></span></a>
<footer class="foot">Destination A2 kitobi unitlari asosidagi original mashqlar. Progress shu brauzerda saqlanadi.</footer></div>`;
 CUR={act:{},key:null}}

function unitView(n){const u=U(n);if(!u)return goHome();const cr=crowns(n),c=CITIES[legOf(n)],lvs=AS?[1,2,3].filter(L=>AS.parts.includes(''+L)):[1,2,3],showTest=!AS||AS.parts.includes('t');
 let learn;
 if(u.k==='g'){learn=`<div class="learn">${u.L.map((r,i)=>`<article class="rule" ${i?'hidden':''}><h3>${h(r[0])}</h3><ul>${r[1].map(l=>l.startsWith('UZ: ')?`<li class="uz"><span class="uzchip">UZ</span><span lang="uz">${l.slice(4)}</span></li>`:`<li>${l}</li>`).join('')}</ul></article>`).join('')}</div>
  ${u.L.length>1?`<div class="learn-nav"><button type="button" class="btn ghost" data-act="prev">Oldingi</button><span class="dots">${u.L.map((_,i)=>`<i class="${i?'':'on'}"></i>`).join('')}</span><button type="button" class="btn ghost" data-act="next">Keyingi</button></div>`:''}`}
 else learn=`<ul class="words">${u.W.map(w=>`<li class="word"><button type="button" class="speak sm" data-say="${h(w[0])}" aria-label="Tinglash: ${h(w[0])}">${I.speaker}</button><div><b>${h(w[0])}</b><span lang="uz">${h(w[1])}</span></div></li>`).join('')}</ul><p class="tip"><b>Tip:</b> ${h(u.tip)}</p>`;
 app.innerHTML=`<div class="wrap">${topbar()}<a class="back" href="${AS?'#':`#leg-${legOf(n)}`}">${I.back}${AS?'Topshiriqlar':'Xarita'}</a>
<header class="unit-head ${u.k}"><p class="eyebrow">Unit ${n} · ${u.k==='v'?'Lug\'at':'Grammatika'} · ${c.name}</p><h1>${h(u.t)}</h1>${crownRow(cr)}</header>
${lvs.length?`<section class="levels" aria-label="Darajalar">${lvs.map(L=>{const d=AS?S.lv[n+'-'+L]!=null:cr>=L;return`<a class="level ${d?'done':''}" href="#play-u-${n}-${L}"><span class="lv-c">${I.crown}</span><span><b>${L}-daraja: ${LEVELS[L].name}</b><span>${AS&&d?`Natija: ${S.lv[n+'-'+L]}%`:LEVELS[L].desc}</span></span><span class="go">${d?'Yana':'O\'ynash'}</span></a>`}).join('')}</section>`:''}
${showTest?`<section class="card testcard"><div class="tc-h"><div><h2>Unit ${n} testi</h2><p class="note">20 savol: 15 ta variantli, 5 ta yozma. Mashqda uchramagan savollar. Javoblar test oxirida ko'rsatiladi.</p></div>${n in S.tests?gradeChip(S.tests[n]):''}</div>
${n in S.tests?`<p class="note">Eng yaxshi natija: ${S.tests[n]}% · baho ${gradeOf(S.tests[n]).join(', ')}</p>`:''}<div class="actions"><a class="btn gold" href="#test-u-${n}">${n in S.tests?'Qayta topshirish':'Testni boshlash'}</a>${AS?'':`<a class="btn ghost" href="#print-u-${n}">Qog'oz varianti</a>`}</div></section>`:''}
<section class="card"><h2>${u.k==='g'?'Qoida':'So\'zlar'}</h2>${learn}</section>
<section class="card task"><h2>Bonus: gapiring va yozing</h2><p>${h(u.task)}</p><button type="button" class="btn ${S.tasks[n]?'ghost':'gold'}" data-act="task" ${S.tasks[n]?'disabled':''}>${S.tasks[n]?'Bajarildi':'Bajardim · +20 XP'}</button></section></div>`;
 let r=0;const show=d=>{const arts=$$('.rule');r=(r+d+arts.length)%arts.length;arts.forEach((a,i)=>a.hidden=i!==r);$$('.dots i').forEach((x,i)=>x.classList.toggle('on',i===r))};
 CUR={act:{prev:()=>show(-1),next:()=>show(1),task:b=>{if(S.tasks[n])return;S.tasks[n]=1;addXP(20);checkBadges({});save();sfx.win();toast(`${I.gem} +20 XP`);b.disabled=true;b.textContent='Bajarildi';b.classList.replace('gold','ghost')}},key:null}}

function intro(o){app.innerHTML=`<div class="wrap center intro">${mascot('idle',o.bubble)}<p class="eyebrow">${o.eyebrow}</p><h1>${o.title}</h1><p class="sub">${o.sub}</p><ul class="rules">${o.rules.map(r=>`<li>${r}</li>`).join('')}</ul>${o.extra||''}
<div class="actions"><button type="button" class="btn big" data-act="start" ${o.disabled?'disabled':''}>${o.cta||'Boshlash'}</button><a class="btn big ghost" href="${o.back||'#'}">Orqaga</a></div></div>`;
 CUR={act:{start:o.start},key:e=>{if(e.key==='Enter'&&!o.disabled&&e.target.tagName!=='A'){o.start();e.preventDefault()}}}}

/* ---------- play engine ---------- */
function startSession(cfg){
 SES=Object.assign({queue:cfg.qs?cfg.qs.slice():[],total:cfg.qs?cfg.qs.length:0,done:0,correct:0,first:0,answered:0,combo:0,maxCombo:0,xp:0,t0:Date.now(),requeued:new Set(),state:'q',sel:null},cfg);
 SES.lives=cfg.hearts||0;SES.bhp=100;SES.sureN=0;SES.sureOk=0;
 const pw=cfg.powers?`<span class="powers"><button type="button" class="pw" data-act="pw" data-p="half" title="Bitta noto'g'ri variantni olib tashlaydi">50/50 <b>${S.powers.half}</b></button>${cfg.hearts?`<button type="button" class="pw" data-act="pw" data-p="heal" title="+1 jon">${I.heart}<b>${S.powers.heal}</b></button>`:''}</span>`:'';
 app.innerHTML=`<main class="play mode-${cfg.mode}"><header class="play-top"><button type="button" class="x" data-act="quit" aria-label="Chiqish">${I.x}</button><div class="pbar" aria-hidden="true"><i></i></div>
${cfg.hearts?`<span class="hearts" aria-label="Jonlar">${I.heart}<b>${cfg.hearts}</b></span>`:''}${cfg.timer||cfg.clock?`<span class="timer">${I.clock}<b>${cfg.timer?cfg.timer:'0:00'}</b></span>`:''}</header>
${cfg.boss?`<div class="battle"><div class="dev">${DEV}<span class="dmg" aria-hidden="true"></span></div><div class="bhp"><b>${h(cfg.boss)}</b><div class="hpbar" role="progressbar" aria-label="Dev jonlari" aria-valuemin="0" aria-valuemax="100" aria-valuenow="100"><i></i></div><small>Har to'g'ri javob zarba beradi. Combo bilan kuchliroq!</small></div></div>`:''}${pw}
<div class="combo-pill" hidden></div><section class="q-area" aria-live="polite"></section><div class="play-mascot">${mascot('idle')}</div>
<footer class="play-foot"><div class="sheet"></div><div class="foot-row">${cfg.bet?`<button type="button" class="sure" data-act="sure" aria-pressed="false" title="To'g'ri bo'lsa XP ikki baravar, xato bo'lsa -5 XP">Aniq bilaman ×2</button>`:''}<button type="button" class="btn big" data-act="check" disabled>Tekshirish</button></div></footer></main>`;
 CUR={act:PLAY,key:playKey};
 if(cfg.timer){SES.left=cfg.timer;const s=SES;s.tick=setInterval(()=>{if(SES!==s)return;s.left--;const t=$('.timer');if(t){t.querySelector('b').textContent=s.left;t.classList.toggle('low',s.left<=10)}updateBar();if(s.left<=0)finish()},1000)}
 else if(cfg.clock)SES.tick=setInterval(()=>{const t=$('.timer b');if(t&&SES)t.textContent=fmt(Math.round((Date.now()-SES.t0)/1000))},1000);
 next()}
function stopSession(){if(SES&&SES.tick)clearInterval(SES.tick);SES=null}
function updateBar(){const b=$('.pbar i');if(!b||!SES)return;b.style.width=(SES.boss?SES.bhp:SES.endless?SES.correct%10*10:SES.timer?(1-SES.left/SES.timer)*100:SES.done/SES.total*100)+'%';
 const hp=$('.hpbar');if(hp){hp.querySelector('i').style.width=SES.bhp+'%';hp.setAttribute('aria-valuenow',SES.bhp)}}
function next(){if(!SES)return;if(!SES.queue.length&&SES.gen)SES.queue.push(SES.gen());const q=SES.queue.shift();if(!q)return SES.boss&&SES.bhp>0?fail():finish();
 SES.q=q;SES.state='q';SES.sel=null;SES.pairMiss=0;SES.hintLv=0;
 const sure=$('.sure');if(sure){sure.setAttribute('aria-pressed','false');sure.hidden=q.kind==='pairs'}
 const foot=$('.play-foot');foot.className='play-foot';$('.sheet').innerHTML='';const btn=$('[data-act=check]');btn.textContent=SES.silent?'Javob berish':'Tekshirish';btn.className='btn big';btn.disabled=true;btn.hidden=!!SES.instant||q.kind==='pairs';
 const area=$('.q-area');area.style.animation='none';void area.offsetWidth;area.style.animation='';
 let body='';
 if(q.say&&(!q.prompt||q.dict))body+=`<div class="listen-row"><button type="button" class="speak huge" data-say="${h(q.say)}" aria-label="Tinglash">${I.speaker}</button><button type="button" class="slow" data-say="${h(q.say)}" data-slow="1">Sekinroq</button></div>`;
 if(q.kind==='choice'){body+=(q.prompt?`<div class="prompt">${q.prompt}</div>`:'')+`<div class="opts ${q.chips?'chips':''}">${q.opts.map((o,i)=>`<button type="button" class="opt" data-act="opt" data-i="${i}"><kbd>${i+1}</kbd><span>${h(o)}</span></button>`).join('')}</div>`}
 else if(q.kind==='type'){body+=`<div class="prompt">${q.prompt.replace('___',`<input class="type-in${q.dict?' wide':''}" id="type-in" type="text" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="Javob">`)}</div>`}
 else if(q.kind==='spot'){body+=`<div class="spot">${q.toks.map((t,j)=>`<button type="button" class="stok" data-act="stok" data-j="${j}">${h(t[0])}</button>`).join(' ')}</div>`}
 else if(q.kind==='order'){body+=`<div class="ord-line" aria-label="Sizning gapingiz"></div><div class="ord-bank">${q.words.map((w,i)=>`<button type="button" class="tile" data-act="tile" data-i="${i}">${h(w)}</button>`).join('')}</div>`}
 else if(q.kind==='pairs'){const L=shuffle(range(q.pairs.length)),R=shuffle(range(q.pairs.length));SES.pairLeft=q.pairs.length;
  body+=`<div class="pairs"><div class="col">${L.map(i=>`<button type="button" class="pair" data-act="pair" data-side="en" data-k="${i}">${h(q.pairs[i][0])}</button>`).join('')}</div><div class="col" lang="uz">${R.map(i=>`<button type="button" class="pair" data-act="pair" data-side="uz" data-k="${i}">${h(q.pairs[i][1])}</button>`).join('')}</div></div>`}
 const canHint=SES.hints&&['choice','type','order'].includes(q.kind);
 area.innerHTML=`<div class="inst-row"><p class="inst">${q.inst}</p>${canHint?`<button type="button" class="hint-btn" data-act="hint">${I.bulb}Maslahat</button>`:''}</div><p class="hint-msg" role="status" hidden></p>${body}`;
 const inp=$('#type-in');if(inp){inp.addEventListener('input',()=>btn.disabled=!inp.value.trim());setTimeout(()=>inp.focus(),60)}
 if(q.auto&&q.say)setTimeout(()=>{if(SES&&SES.q===q)say(q.say)},260);
 updateBar()}
function react(mood,text){const m=$('.play-mascot');if(m)m.innerHTML=mascot(mood,text)}
function grade(ok){const s=SES;
 if(s.silent){s.answered++;s.done++;(s.log=s.log||[]).push({q:s.q,given:s.given,ok});if(ok){s.correct++;s.first++;s.xp+=5;if(isDue(s.q.key))reviewMistake(s.q.key,true)}else addMistake(s.q.key);sfx.tap();return next()} // tests: no feedback until the end
 s.answered++;const first=!s.requeued.has(s.q),q0=s.q,sureB=$('.sure'),sure=!!sureB&&!sureB.hidden&&sureB.getAttribute('aria-pressed')==='true';
 if(sure){s.sureN++;S.sure.n++;if(ok){s.sureOk++;S.sure.ok++}}
 if(ok){s.correct++;s.combo++;s.maxCombo=Math.max(s.maxCombo,s.combo);let gain=s.mode==='blitz'?5:10+Math.min(5,s.combo-1);if(q0.hinted)gain=Math.ceil(gain/2);if(sure)gain*=2;s.xp+=gain;s.done++;if(first)s.first++;
  if(s.mode==='mistakes')reviewMistake(q0.key,true);else if(first&&isDue(q0.key))reviewMistake(q0.key,true); // the in-session retry does not count as a review
  if(s.boss){const dmg=12+(s.combo>=5?8:s.combo>=3?4:0);s.bhp=Math.max(0,s.bhp-dmg);const d=$('.dev');if(d){d.classList.remove('hit');void d.offsetWidth;d.classList.add('hit');const f=$('.dmg');f.textContent='-'+dmg;f.classList.remove('show');void f.offsetWidth;f.classList.add('show')}}
  if(s.combo>0&&s.combo%5===0&&(s.powers||s.bet)){const p=s.hearts&&RNG()<.4?'heal':'half';if(S.powers[p]<3){S.powers[p]++;toast(`${p==='heal'?I.heart+' +1 jon':'50/50'} kuchi qo'lga kiritildi!`);const b=$(`.pw[data-p=${p}] b`);if(b)b.textContent=S.powers[p]}}
  if(s.combo>=3){const p=$('.combo-pill');p.hidden=false;p.innerHTML=`${I.flame} ${s.combo} ketma-ket`;p.style.animation='none';void p.offsetWidth;p.style.animation=''}
  if(s.combo===5||s.combo===10||s.combo===20){sfx.combo();toast(`${I.flame} ${s.combo} ta ketma-ket to'g'ri!`)}else sfx.ok();
  react('happy',s.combo>=5?`${s.combo} ketma-ket!`:any(PRAISE))}
 else{s.combo=0;$('.combo-pill').hidden=true;sfx.bad();if(s.mode==='mistakes')reviewMistake(q0.key,false);else addMistake(q0.key);if(sure){s.xp=Math.max(0,s.xp-5);toast('Ishonch garovi: -5 XP')}
  if(s.boss){const d=$('.dev');if(d){d.classList.remove('atk');void d.offsetWidth;d.classList.add('atk')}}
  if(s.requeue&&first){s.queue.push(s.q);s.requeued.add(s.q)}else s.done++;
  if(s.hearts){s.lives--;const hb=$('.hearts');hb.querySelector('b').textContent=s.lives;shake(hb)}
  react('sad',any(COMFORT))}
 updateBar();
 if(s.instant){s.state='wait';setTimeout(()=>{if(SES===s)next()},ok?300:900);return}
 const foot=$('.play-foot'),q=s.q,btn=$('[data-act=check]');foot.className='play-foot '+(ok?'ok':'bad');
 const full=q.full?`<p>${h(q.full)}<button type="button" class="speak sm" data-say="${h(q.full)}" aria-label="Tinglash">${I.speaker}</button></p>`:'';
 $('.sheet').innerHTML=ok?`${I.check}<div><b>${any(PRAISE)}</b>${q.kind==='order'||q.long?'':full}</div>`:`${I.cross}<div><b>To'g'ri javob:</b>${q.ans&&q.ans!==q.full?`<p class="ans">${h(q.ans)}</p>`:''}${full}</div>`;
 if(sureB)sureB.hidden=true;
 btn.hidden=false;btn.disabled=false;btn.textContent=s.hearts&&s.lives<=0?'Natijani ko\'rish':s.boss&&s.bhp<=0?'G\'alaba!':'Davom etish';btn.className='btn big '+(ok?'ok':'bad');s.state='fb';btn.focus({preventScroll:true});
 if(!ok&&q.full&&(q.kind==='order'||q.kind==='type'))setTimeout(()=>say(q.full),200)}
function check(){const s=SES,q=s.q;let ok;
 if(q.kind==='choice'){if(s.sel==null)return;ok=q.opts[s.sel]===q.ans;s.given=q.opts[s.sel];if(!s.silent)$$('.opt').forEach((b,i)=>{b.disabled=true;if(q.opts[i]===q.ans)b.classList.add('right');else if(i===s.sel)b.classList.add('wrong')})}
 else if(q.kind==='type'){const inp=$('#type-in'),v=inp.value;if(!v.trim())return;const cmp=q.dict?x=>norm(x).replace(/[.,!?;:"]/g,'').replace(/\s+/g,' ').trim():norm;ok=q.accept.some(a=>cmp(a)===cmp(v));s.given=v;inp.readOnly=true;if(!s.silent){inp.classList.add(ok?'ok':'bad');if(!ok)shake(inp)}}
 else if(q.kind==='order'){const line=$('.ord-line');if($('.ord-bank').children.length)return;s.given=[...line.children].map(t=>t.textContent).join(' ');ok=s.given===q.ans;$$('.tile').forEach(t=>t.disabled=true);if(!s.silent){line.classList.add(ok?'ok':'bad');if(!ok)shake(line)}}
 else if(q.kind==='spot'){if(s.sel==null)return;ok=q.toks[s.sel][1];s.given=q.toks[s.sel][0];$$('.stok').forEach((b,j)=>{b.disabled=true;if(q.toks[j][1])b.classList.add('err');else if(j===s.sel)b.classList.add('wrong')})}
 else return;
 grade(ok)}
const PLAY={
 opt(b){const s=SES;if(s.state!=='q'||b.disabled)return;s.sel=+b.dataset.i;$$('.opt').forEach(x=>x.classList.toggle('sel',x===b));sfx.tap();if(s.instant)return check();$('[data-act=check]').disabled=false},
 tile(b){if(SES.state!=='q')return;const line=$('.ord-line'),bank=$('.ord-bank');(b.parentElement===line?bank:line).appendChild(b);sfx.tap();$('[data-act=check]').disabled=bank.children.length>0},
 pair(b){const s=SES;if(s.state!=='q'||b.classList.contains('done'))return;const sel=$('.pair.sel');
  if(!sel||sel.dataset.side===b.dataset.side){if(sel)sel.classList.remove('sel');b.classList.add('sel');sfx.tap();if(b.dataset.side==='en')say(b.textContent);return}
  sel.classList.remove('sel');
  if(sel.dataset.k===b.dataset.k){[sel,b].forEach(x=>{x.classList.add('done');x.disabled=true});sfx.tap();if(--s.pairLeft===0)grade(s.pairMiss<=1)}
  else{s.pairMiss++;[sel,b].forEach(x=>{x.classList.add('bad');shake(x);setTimeout(()=>x.classList.remove('bad'),450)});sfx.bad()}},
 check(){if(SES.state==='q')check();else if(SES.state==='fb'){if(SES.hearts&&SES.lives<=0)return SES.endless?finish():fail();if(SES.boss&&SES.bhp<=0)return finish();next()}},
 stok(b){const s=SES;if(s.state!=='q')return;s.sel=+b.dataset.j;$$('.stok').forEach(x=>x.classList.toggle('sel',x===b));sfx.tap();$('[data-act=check]').disabled=false},
 sure(b){if(SES.state!=='q')return;b.setAttribute('aria-pressed',b.getAttribute('aria-pressed')!=='true');sfx.tap()},
 hint(b){const s=SES,q=s.q;if(s.state!=='q')return;s.hintLv++;q.hinted=true;let msg='';
  if(q.kind==='choice'){if(s.hintLv===1){const w=$$('.opt').filter((x,i)=>q.opts[i]!==q.ans&&!x.disabled);const x=any(w);if(x){x.disabled=true;x.classList.add('gone')}msg='Bitta noto\'g\'ri variant olib tashlandi.'}else msg=`Javob «${h(q.ans.charAt(0))}» harfi bilan boshlanadi.`}
  else if(q.kind==='type'){const a=q.ans;msg=s.hintLv===1?`Birinchi harf: «${h(a.charAt(0))}» · ${a.replace(/ /g,'').length} ta harf`:h(a.split('').map((c,i)=>c===' '?'  ':i%2?'_':c).join(''))}
  else if(q.kind==='order'){const line=$('.ord-line'),bank=$('.ord-bank');$$('.tile',line).forEach(t=>bank.appendChild(t));q.ans.split(' ').slice(0,s.hintLv).forEach(w=>{const t=$$('.tile',bank).find(x=>x.textContent===w);if(t)line.appendChild(t)});msg=`Gapning boshi qo'yildi (${s.hintLv} ta so'z).`;$('[data-act=check]').disabled=bank.children.length>0}
  const m=$('.hint-msg');m.hidden=false;m.innerHTML=`${I.bulb} ${msg} <small>Bu savol uchun XP yarmiga kamayadi.</small>`;if(s.hintLv>=2)b.disabled=true;sfx.tap()},
 pw(b){const s=SES,p=b.dataset.p;if(s.state!=='q'||!S.powers[p])return;
  if(p==='half'){if(s.q.kind!=='choice')return toast('50/50 faqat variantli savolda ishlaydi');const w=$$('.opt').filter((x,i)=>s.q.opts[i]!==s.q.ans&&!x.disabled);if(!w.length)return;const x=any(w);x.disabled=true;x.classList.add('gone')}
  if(p==='heal'){s.lives++;const hb=$('.hearts b');if(hb)hb.textContent=s.lives}
  S.powers[p]--;$('b',b).textContent=S.powers[p];save();sfx.combo()},
 quit(){const back=SES.back||'#';const o=document.createElement('div');o.className='overlay';o.innerHTML=`<div class="dialog" role="dialog" aria-modal="true" aria-labelledby="qt">${mascot('sad')}<h2 id="qt">Chiqib ketasizmi?</h2><p>${SES.quitNote||'Bu mashg\'ulotdagi natija saqlanmaydi.'}</p><div class="actions"><button type="button" class="btn" data-act="stay">Davom etaman</button><button type="button" class="btn ghost" data-act="leave">Chiqish</button></div></div>`;$('.play').appendChild(o);$('[data-act=stay]',o).focus();
  PLAY.stay=()=>o.remove();PLAY.leave=()=>{stopSession();location.hash=back}}
};
function playKey(e){const s=SES;if(!s||$('.overlay'))return;const t=e.target;
 if(e.key==='Enter'){if(t.classList&&(t.classList.contains('speak')||t.classList.contains('slow')))return;e.preventDefault();const b=$('[data-act=check]');if(b&&!b.disabled&&!b.hidden)PLAY.check();return}
 if(t.tagName==='INPUT')return;
 if(/^[1-9]$/.test(e.key)&&s.state==='q'&&s.q.kind==='choice'){const b=$(`.opt[data-i="${+e.key-1}"]`);if(b&&!b.disabled)PLAY.opt(b)}
 if(e.key==='Backspace'&&s.state==='q'&&s.q.kind==='order'){const l=$('.ord-line').lastElementChild;if(l)PLAY.tile(l)}}

function finish(){const s=SES;if(!s)return;stopSession();const secs=Math.round((Date.now()-s.t0)/1000);
 const acc=s.requeue?Math.round(s.first*100/Math.max(1,s.total)):s.answered?Math.round(s.correct*100/s.answered):0;
 const perfect=s.requeue?s.first===s.total:s.answered>0&&s.correct===s.answered;
 const before=todayXP();const r=s.onDone?s.onDone(s,acc,secs,perfect):{};
 const gained=s.xp+(perfect&&s.total>=8?20:0)+(r.bonus||0);addXP(gained);
 const st=S.stats;st.sessions++;st.correct+=s.correct;st.answered+=s.answered;st.maxCombo=Math.max(st.maxCombo,s.maxCombo);st.secs+=secs;
 const nb=checkBadges({perfect:perfect&&s.answered>=8,combo:s.maxCombo,hour:new Date().getHours()});save();
 const goalHit=before<S.goal&&todayXP()>=S.goal;
 app.innerHTML=`<div class="wrap center result">${mascot(r.sad?'sad':'cheer',r.bubble||(perfect?'Xatosiz! Siz haqiqiy sayyohsiz!':any(PRAISE)))}
<h1>${r.title}</h1><p class="sub">${r.sub||''}</p>
<div class="stats"><div class="stat xp"><b data-count="${gained}">+0</b><span>XP</span></div><div class="stat"><b>${acc}%</b><span>Aniqlik</span></div><div class="stat"><b>${fmt(secs)}</b><span>Vaqt</span></div><div class="stat">${s.silent?`<b>${s.correct}/${s.answered}</b><span>To'g'ri javob</span>`:`<b>${s.maxCombo}</b><span>Eng uzun seriya</span>`}</div></div>
${r.extra||''}${s.sureN?`<div class="banner calib"><span class="big-n">${s.sureOk}/${s.sureN}</span><div><b>Ishonch garovi</b><p>${s.sureOk===s.sureN?'Ishonchingiz o\'rinli! Nimani bilishingizni aniq sezasiz.':'«Aniq bilaman» degan ba\'zi javoblar xato chiqdi. Garov qo\'yishdan oldin qoidani eslab oling.'}</p></div></div>`:''}${goalHit?`<div class="banner">${ring(1,1)}<div><b>Kunlik maqsad bajarildi!</b><p>${S.goal} XP · seriya: ${streak()} kun</p></div></div>`:''}
${nb.length?`<h2 style="margin-top:22px">Yangi nishon!</h2><div class="new-badges">${nb.map(badgeHTML).join('')}</div>`:''}
<div class="actions">${r.buttons||''}<a class="btn big ghost" href="#">${AS?'Topshiriqlar':'Xaritaga'}</a></div></div>`;
 const c=$('[data-count]');const tgt=+c.dataset.count;if(RM)c.textContent='+'+tgt;else{let v=0;const inc=Math.max(1,Math.ceil(tgt/30));const iv=setInterval(()=>{v=Math.min(tgt,v+inc);c.textContent='+'+v;if(v>=tgt)clearInterval(iv)},30)}
 if(!r.sad){sfx.win();if(perfect||goalHit||nb.length||r.big)confetti()}else sfx.lose();
 CUR={act:r.act||{},key:e=>{if(e.key==='Enter'&&e.target===document.body){const b=$('.result .actions .btn');if(b){b.click();e.preventDefault()}}}};window.scrollTo(0,0)}
function fail(){const s=SES;stopSession();if(s.onFail)s.onFail(s);addXP(s.xp);save();
 app.innerHTML=`<div class="wrap center result">${mascot('sad','Jonlar tugadi. Lekin har bir xato ham saboq!')}<h1>Bu safar bo'lmadi</h1><p class="sub">${s.correct} ta to'g'ri javob · +${s.xp} XP</p>
<ul class="rules"><li>Xato savollar "Xatolar" bo'limiga tushdi.</li><li>Unitlarni yana bir marta o'ynab, keyin qayta urinib ko'ring.</li></ul>
<div class="actions"><button type="button" class="btn big" data-act="retry">Qayta urinish</button><a class="btn big ghost" href="${s.back||'#'}">Orqaga</a></div></div>`;
 sfx.lose();CUR={act:{retry:()=>s.retry?s.retry():route()},key:null}}

/* ---------- modes ---------- */
function playUnit(n,L){const u=U(n);if(!u)return goHome();
 startSession({mode:'unit',qs:unitQuestions(u,L),requeue:true,hints:true,bet:true,back:'#u-'+n,onDone:(s,acc)=>{const prev=crowns(n),got=L>prev;if(got)S.crowns[n]=L;const ns=nextStop(),lk=n+'-'+L;S.lv[lk]=Math.max(S.lv[lk]??0,acc);
  const nxL=AS?[1,2,3].find(k=>k>L&&AS.parts.includes(''+k)):L+1;
  const buttons=AS?(nxL?`<a class="btn big" href="#play-u-${n}-${nxL}">Keyingi: ${nxL}-daraja</a>`:AS.parts.includes('t')&&!(n in S.tests)?`<a class="btn big" href="#test-u-${n}">Unit ${n} testi</a>`:''):L<3?`<a class="btn big" href="#play-u-${n}-${L+1}">Keyingi: ${L+1}-daraja</a>${L===1?`<a class="btn big ghost" href="${stopHref(ns)}">Keyingi bekat</a>`:''}`:`<a class="btn big" href="${stopHref(ns)}">Keyingi bekat</a>`;
  return{title:`${L}-daraja tugadi!`,sub:`Unit ${n}: ${h(u.t)}`,extra:got?`<div class="banner">${crownRow(L)}<div><b>Yangi toj!</b><p>Unit ${n}: ${L} / 3 toj</p></div></div>`:'',buttons,big:got&&L===3}}})}
function bossQs(i){const qs=[];legUnits(i).forEach(n=>{const u=U(n),g=pick(range(u.gaps.length),2),m=pick(range(u.mc.length),2);qs.push(qMC(u,m[0]),qSpot(u,m[1]),qOrder(u,rnd(u.ord.length)),qGapBank(u,g[0]),u.k==='v'?qWord(u,rnd(u.W.length),'en'):qType(u,g[1]))});return shuffle(qs)}
function bossIntro(i){const c=CITIES[i];if(!c)return goHome();const[a,b,d]=legUnits(i);
 intro({eyebrow:`Review ${i+1} · Boss jangi`,title:`${c.name} darvozasi`,sub:`Unitlar ${a}, ${b} va ${d} takrori`,bubble:'Darvozadan o\'tish uchun bossni yenging!<small>Beat the boss to enter the city.</small>',
  rules:['Dev jonini 0 ga tushiring: har to\'g\'ri javob zarba, 3 va 5 ketma-ket javobda zarba kuchayadi','Savollar 3 ta unitdan aralash, «Xatoni top» ham bor','3 ta jon. 50/50 va +1 jon kuchlaridan foydalaning (ularni 5 ketma-ket to\'g\'ri javob uchun olasiz)','G\'alaba: shahar muhri, +50 XP va shahar sahnasi'],extra:`<p><a href="#print-r-${i+1}">Review ${i+1} ning qog'oz varianti</a></p>`,back:`#leg-${i}`,start:()=>playBoss(i)})}
function playBoss(i){const c=CITIES[i];startSession({mode:'boss',qs:bossQs(i),hearts:3,powers:true,boss:`${c.uz} devi`,back:`#leg-${i}`,retry:()=>playBoss(i),onDone:(s,acc)=>{const firstWin=!S.boss[i];S.boss[i]=Math.max(S.boss[i]||0,acc||1);
 return{bonus:firstWin?50:0,title:`Review ${i+1}: boss yengildi!`,sub:`${c.name} sizni kutib oldi`,big:true,bubble:`Welcome to ${c.name}!`,
  extra:`<div class="banner city"><span class="stamp press"><small>VISITED</small><b>${h(c.name.split(' ')[0])}</b></span><div><b>Bilasizmi? / Did you know?</b><p>${h(c.fact)}</p><button type="button" class="speak sm" data-say="${h(c.fact)}" aria-label="Tinglash">${I.speaker}</button></div></div>`,
  buttons:`<a class="btn big" href="#scene-${i}">Shahar sahnasi: ${h(SCENES[i].title)}</a>`}}})}
function examIntro(k){const from=k===1?1:22;
 intro({eyebrow:'Aeroport · nazorat nuqtasi',title:`Progress Test ${k}`,sub:`Unitlar ${from}–${from+20}`,bubble:'Pasport nazorati! Tayyormisiz?<small>Passport control. Ready?</small>',
  rules:['30 ta savol, jonlar yo\'q','Javoblar va baho test oxirida ko\'rsatiladi','70% va undan yuqori: o\'tdingiz · +100 XP va aeroport muhri'],extra:`<p><a href="#print-p-${k}">Progress Test ${k} ning qog'oz varianti</a></p>`,back:`#leg-${k===1?6:13}`,start:()=>playExam(k)})}
function playExam(k){const from=k===1?1:22;const pool=[];for(let n=from;n<from+21;n++){const u=U(n);u.test.forEach((_,i)=>pool.push([u,i,'t']));u.tx.forEach((_,i)=>pool.push([u,i,'x']))}
 startSession({mode:'exam',silent:true,qs:pick(pool,30).map(([u,i,src])=>qMC(u,i,src)),clock:true,back:`#leg-${k===1?6:13}`,onDone:(s,acc)=>{const pass=acc>=70,first=pass&&!(S.exam[k]>=70);S.exam[k]=Math.max(S.exam[k]||0,acc);
  return pass?{bonus:first?100:0,big:true,title:`Progress Test ${k}: o'tdingiz!`,sub:`${s.correct} / 30 · ${acc}%`,extra:gradeBanner(acc)+`<div class="banner"><span class="stamp press" style="color:var(--gold-deep)"><small>PASSED</small><b>Gate ${k}</b></span><div><b>Parvozga ruxsat berildi</b><p>${k===1?'Endi Parijga uchamiz!':'Siz butun A2 kursini tugatdingiz!'}</p></div></div>`+reviewList(s.log||[]),buttons:`<a class="btn big" href="${k===1?'#play-u-22-1':'#me'}">${k===1?'Parijga uchish':'Profilni ko\'rish'}</a>`}
   :{sad:true,title:`Progress Test ${k}: biroz yetmadi`,sub:`${s.correct} / 30 · ${acc}% · 70% kerak`,bubble:'Xatolarni ko\'rib chiqing va yana urining!',extra:gradeBanner(acc)+reviewList(s.log||[]),buttons:`<button type="button" class="btn big" data-act="again">Qayta topshirish</button>`,act:{again:()=>playExam(k)}}}})}
function dailyQs(){RNG=seeded('daily-'+dayKey());const qs=[];
 for(let k=0;k<10;k++){const u=any(UNITS),t=k%5;qs.push(t<2?qMC(u,rnd(u.mc.length)):t===2?qOrder(u,rnd(u.ord.length)):t===3?qGapBank(u,rnd(u.gaps.length)):u.k==='v'?qWord(u,rnd(u.W.length),'en'):qSpot(u,rnd(u.mc.length)))}
 RNG=Math.random;return qs}
function dailyIntro(){const dk=S.daily[dayKey()];
 intro({eyebrow:dayKey(),title:'Kunlik chaqiruv',sub:'Bugun hamma bir xil 10 ta savol oladi',bubble:'Sinfdoshlaringiz bilan natijani solishtiring!<small>Same questions for everyone today.</small>',
  rules:['Barcha unitlardan 10 ta savol','Vaqt hisoblanadi: tez va aniq bo\'ling','Birinchi urinish natijasi saqlanadi · +30 XP'],extra:dk?`<p class="sub">Bugungi natijangiz: ${dk.c}/10 · ${fmt(dk.t)}. Yana o'ynash mumkin, lekin natija o'zgarmaydi.</p>`:'',start:playDaily})}
function shareBox(text){return`<textarea class="share-box" readonly rows="2" aria-label="Natija matni">${h(text)}</textarea><button type="button" class="btn ghost" data-act="copy">Natijani nusxalash</button>`}
const copyAct=()=>({copy:b=>{const t=$('.share-box');const sel=()=>{t.select();b.textContent='Belgilandi, nusxalang'};try{navigator.clipboard.writeText(t.value).then(()=>{b.textContent='Nusxalandi!'},sel)}catch(e){sel()}}});
function playDaily(){startSession({mode:'daily',qs:dailyQs(),clock:true,bet:true,back:'#',onDone:(s,acc,secs)=>{const d=dayKey(),first=!S.daily[d];if(first)S.daily[d]={c:s.correct,t:secs};
 const txt=`Destination A2 · Kunlik chaqiruv ${d}: ${s.correct}/10, ${fmt(secs)}`;
 return{bonus:first?30:0,title:`${s.correct} / 10`,sub:first?'Bugungi natija saqlandi':'Mashq uchun o\'yin (natija o\'zgarmadi)',extra:`<div class="card" style="text-align:left"><h2>Sinfdoshlarga yuboring</h2>${shareBox(txt)}</div>`,act:copyAct(),buttons:''}}})}
function blitzPool(){if(AS)return asUnits();const started=UNITS.filter(u=>crowns(u.n));return started.length>=2?started:UNITS.slice(0,6)}
function blitzIntro(){intro({eyebrow:'60 soniya',title:'Blitz',sub:S.blitz?`Rekordingiz: ${S.blitz} ta to'g'ri javob`:'Birinchi rekordni o\'rnating!',bubble:'Tez bo\'ling, lekin shoshmang!<small>Fast, but careful.</small>',
 rules:['60 soniyada iloji boricha ko\'p savol','Variantni bosishingiz bilan javob tekshiriladi','Savollar siz boshlagan unitlardan olinadi','5 ketma-ket to\'g\'ri javob 50/50 kuchini beradi'],start:playBlitz})}
function playBlitz(){const pool=blitzPool();startSession({mode:'blitz',instant:true,timer:60,powers:true,back:'#',gen:()=>{const u=any(pool);return u.k==='v'&&RNG()<.4?qWord(u,rnd(u.W.length),RNG()<.5?'uz':'en'):qMC(u,rnd(u.mc.length))},
 onDone:s=>{const rec=s.correct>S.blitz;if(rec)S.blitz=s.correct;const txt=`Destination A2 · Blitz: 60 soniyada ${s.correct} ta to'g'ri javob`;
  return{title:rec?'Yangi rekord!':`${s.correct} ta to'g'ri`,sub:`${s.answered} ta savol · rekord: ${S.blitz}`,big:rec,extra:`<div class="card" style="text-align:left"><h2>Do'stlaringizni chaqiring</h2>${shareBox(txt)}</div>`,act:Object.assign(copyAct(),{again:playBlitz}),buttons:`<button type="button" class="btn big" data-act="again">Yana bir marta</button>`}}})}
function mistakesIntro(){const n=mistakeCount(),d=dueKeys().length;intro({eyebrow:'Oraliq takrorlash',title:'Xatolar ustida ishlash',sub:n?(d?`Bugun ${d} ta savol takrorlanadi · jami ${n} ta`:`Bugungi takrorlash bajarilgan · jami ${n} ta`):'Hozircha xato yo\'q. Zo\'r!',bubble:n?'Xatolar eng yaxshi ustoz!<small>Mistakes are the best teachers.</small>':'Unitlarni o\'ynang, xatolar shu yerga tushadi.',
 rules:['Xato qilgan savolingiz o\'sha kuni, keyin 1 kundan va 3 kundan so\'ng qaytadi','Uch marta to\'g\'ri topsangiz, savol ro\'yxatdan chiqadi','Maslahat va «Aniq bilaman» garovi shu yerda ham ishlaydi'],cta:d?'Boshlash':'Muddatidan oldin takrorlash',disabled:!n,start:playMistakes})}
function playMistakes(){const due=shuffle(dueKeys()),rest=Object.keys(S.mistakes).filter(k=>!isDue(k)).sort((a,b)=>S.mistakes[a].d<S.mistakes[b].d?-1:1);
 const qs=(due.length?due:rest).map(fromKey).filter(Boolean).slice(0,12);if(!qs.length)return mistakesIntro();
 startSession({mode:'mistakes',qs,hints:true,bet:true,back:'#',onDone:s=>({title:'Takrorlash yakunlandi!',sub:`${s.correct} / ${s.answered} to'g'ri · bugun qoldi: ${dueKeys().length} · jami: ${mistakeCount()}`,buttons:dueKeys().length?`<a class="btn big" href="#mistakes">Davom etish</a>`:''})})}

/* ---------- story scenes: choose-your-reply dialogues with a speaking finale ---------- */
function scene(i){const sc=SCENES[i],c=CITIES[i];if(!sc)return goHome();let li=0,firstOk=0,tries=0,left=45,tick=null;
 app.innerHTML=`<div class="wrap scene-v">${topbar()}<a class="back" href="${AS?'#':`#leg-${i}`}">${I.back}${AS?'Topshiriqlar':'Xarita'}</a>
<header class="unit-head v"><p class="eyebrow">Sahna ${i+1} · ${c.name}</p><h1>${h(sc.title)}</h1><p class="scene-intro">${h(sc.intro)}</p><span class="scene-step"></span></header>
<section class="chat" aria-live="polite"></section><section class="replies"></section></div>`;
 const chat=$('.chat'),rep=$('.replies');
 const step=()=>{$('.scene-step').textContent=`${Math.min(li+1,5)} / 5`};
 function npc(){const line=sc.lines[li][0],opts=sc.lines[li][1];const note=(line.match(/^\[([^\]]+)\]\s*/)||[])[1];const txt=line.replace(/^\[[^\]]+\]\s*/,'');
  chat.insertAdjacentHTML('beforeend',`${note?`<p class="c-note">${h(note)}</p>`:''}<div class="msg them"><span class="av" aria-hidden="true">${h(sc.who.charAt(0))}</span><div class="bub"><b>${h(sc.who)}</b><p>${h(txt)}</p></div><button type="button" class="speak sm" data-say="${h(txt)}" aria-label="Tinglash">${I.speaker}</button></div>`);
  setTimeout(()=>say(txt),200);tries=0;step();const order=shuffle(range(3));
  rep.innerHTML=`<p class="inst">Javobingizni tanlang</p><div class="opts">${order.map((k,j)=>`<button type="button" class="opt" data-act="rep" data-k="${k}"><kbd>${j+1}</kbd><span>${h(opts[k][0])}</span></button>`).join('')}</div><p class="coach" role="status" hidden></p>`;
  rep.scrollIntoView({behavior:RM?'auto':'smooth',block:'end'})}
 function choose(b){if(b.disabled)return;const opts=sc.lines[li][1],o=opts[+b.dataset.k],co=$('.coach');
  if(o[1]===1){if(!tries)firstOk++;sfx.ok();$$('.replies .opt').forEach(x=>x.disabled=true);chat.insertAdjacentHTML('beforeend',`<div class="msg me"><div class="bub"><p>${h(o[0])}</p></div></div>`);
   co.hidden=false;co.className='coach good';co.innerHTML=`${I.check} ${h(o[2])}`;li++;setTimeout(()=>li<sc.lines.length?npc():finale(),1300)}
  else{tries++;sfx.bad();b.disabled=true;b.classList.add('wrong');shake(b);co.hidden=false;co.className='coach '+(o[1]===0?'gram':'odd');co.innerHTML=`<b>${o[1]===0?'Grammatik xato':'Suhbatga mos emas'}:</b> ${h(o[2])} <small>Yana urinib ko'ring.</small>`}}
 function finale(){step();rep.innerHTML=`<section class="card turn"><h2>Sizning navbatingiz!</h2><p class="prompt-sm">${h(sc.finale)}</p><button type="button" class="speak sm" data-say="${h(sc.finale)}" aria-label="Tinglash">${I.speaker}</button>
<p class="note">45 soniya davomida ovoz chiqarib gapiring. Tayyor bo'lsangiz, taymerni boshlang.</p><div class="t45" aria-live="polite">45</div><div class="actions"><button type="button" class="btn" data-act="go">Taymerni boshlash</button><button type="button" class="btn ghost" data-act="skip">O'tkazib yuborish</button></div>
<div id="selfcheck" hidden><p class="note">O'zingizni tekshiring:</p><ul class="check">${['45 soniya deyarli to\'xtamasdan gapirdim','Bu bosqichning grammatikasidan foydalandim','Kamida 5 ta gap aytdim'].map((t,j)=>`<li><label><input type="checkbox" id="ck${i}-${j}"> ${t}</label></li>`).join('')}</ul><div class="actions"><button type="button" class="btn gold" data-act="done">Sahnani yakunlash</button></div></div></section>`;
  rep.scrollIntoView({behavior:RM?'auto':'smooth',block:'end'})}
 function selfcheck(){clearInterval(tick);$('#selfcheck').hidden=false;$$('[data-act=go],[data-act=skip]').forEach(x=>x.hidden=true)}
 function done(){clearInterval(tick);const checks=$$('#selfcheck input:checked').length,stars=firstOk>=5?3:firstOk>=4?2:firstOk>=3?1:0,xp=firstOk*10+checks*5,prev=S.scenes[i];
  S.scenes[i]=Math.max(prev||0,stars);addXP(xp);S.stats.sessions++;const nb=checkBadges({hour:new Date().getHours()});save();
  const nx=AS?'#':i===6?'#exam-1':i<13?`#play-u-${3*i+4}-1`:'#exam-2';
  app.innerHTML=`<div class="wrap center result">${mascot('cheer',stars===3?'Ajoyib suhbat! Siz haqiqiy sayyohsiz!':'Yaxshi suhbat! Yana o\'ynasangiz, yulduzlar ko\'payadi.')}<h1>Sahna yakunlandi!</h1><p class="sub">${h(sc.title)} · birinchi urinishda ${firstOk}/5 to'g'ri</p>
<p class="res-stars" aria-label="${stars} / 3 yulduz">${[1,2,3].map(k=>`<span class="${k<=stars?'':'off'}">${I.crown}</span>`).join('')}</p><div class="stats"><div class="stat xp"><b>+${xp}</b><span>XP</span></div><div class="stat"><b>${firstOk}/5</b><span>Birinchi urinish</span></div><div class="stat"><b>${checks}/3</b><span>O'z-o'zini tekshirish</span></div><div class="stat"><b>${stars}</b><span>Yulduz</span></div></div>
${nb.length?`<h2 style="margin-top:22px">Yangi nishon!</h2><div class="new-badges">${nb.map(badgeHTML).join('')}</div>`:''}<div class="actions">${AS?`<a class="btn big" href="#">Topshiriqlar</a>`:`<a class="btn big" href="${nx}">${i===6||i===13?'Aeroportga':'Keyingi shahar'}</a><a class="btn big ghost" href="#">Xaritaga</a>`}</div></div>`;
  sfx.win();if(stars===3)confetti();CUR={act:{},key:null};window.scrollTo(0,0)}
 CUR={act:{rep:choose,go:b=>{b.disabled=true;left=45;tick=setInterval(()=>{left--;const t=$('.t45');if(t)t.textContent=left;if(left<=0){sfx.combo();selfcheck()}},1000)},skip:selfcheck,done},
  key:e=>{if(/^[1-3]$/.test(e.key)){const b=$$('.replies .opt')[+e.key-1];if(b)choose(b)}}};
 npc()}

/* ---------- unit tests ---------- */
function testIntro(n){const u=U(n);if(!u)return goHome();const best=S.tests[n],left=attemptsLeft(n);
 intro({eyebrow:`Unit ${n} · ${u.k==='v'?'Lug\'at':'Grammatika'}`,title:`Unit ${n} testi`,sub:h(u.t),bubble:'Test paytida javoblar ko\'rsatilmaydi. Diqqat bilan o\'qing!<small>No hints during the test. Read carefully.</small>',
  rules:['20 ta savol: 15 ta variantli, 5 ta yozma','Mashqda uchramagan yangi savollar','Javoblar va baho test oxirida ko\'rsatiladi','70% va undan yuqori: test topshirildi · +30 XP',...(AS?[AS.att?`Urinishlar: ${left} / ${AS.att} qoldi. Boshlangan urinish hisoblanadi`:'Urinishlar cheklanmagan, o\'qituvchi birinchi urinish natijasini ham ko\'radi']:[])],
  extra:`${best!=null?`<p class="sub">Eng yaxshi natijangiz: ${best}% · baho ${gradeOf(best)[0]}</p>`:''}${AS?'':`<p><a href="#print-u-${n}">Qog'oz varianti (javoblar kaliti bilan)</a></p>`}`,back:`#u-${n}`,disabled:left===0,cta:left===0?'Urinishlar tugadi':null,start:()=>playTest(n)})}
const attemptsLeft=n=>AS&&AS.att?Math.max(0,AS.att-(S.tries[n]||0)):null;
const testQs=u=>shuffle([...u.test.map((_,i)=>qMC(u,i,'t')),...u.tx.map((_,i)=>qMC(u,i,'x')),...u.tg.map((_,i)=>qTestGap(u,i))]);
function playTest(n){const u=U(n);if(!u||attemptsLeft(n)===0)return testIntro(n);
 if(AS){S.tries[n]=(S.tries[n]||0)+1;save()} // an attempt counts once it starts
 startSession({mode:'test',silent:true,qs:testQs(u),clock:true,back:`#u-${n}`,quitNote:AS&&AS.att?'Bu urinish hisoblanadi, natija esa saqlanmaydi.':null,onDone:(s,acc)=>{const pass=acc>=70,first=pass&&!(S.tests[n]>=70);S.tests[n]=Math.max(S.tests[n]??0,acc);if(S.firstT[n]==null)S.firstT[n]=acc;const ns=nextStop(),left=attemptsLeft(n);
 const again=left!==0?`<button type="button" class="btn big" data-act="again">Qayta topshirish${left?` (${left} ta qoldi)`:''}</button>`:'';
 return{bonus:first?30:0,sad:!pass,big:pass,title:`Unit ${n} testi: ${s.correct} / ${s.total}`,sub:h(u.t),bubble:pass?'Test topshirildi! Barakalla!':'Xatolarni ko\'rib chiqing va yana urinib ko\'ring.',
  extra:gradeBanner(acc)+reviewList(s.log||[],left>0),act:{again:()=>playTest(n)},
  buttons:AS?(pass?'':again+`<a class="btn big ghost" href="#u-${n}">Mashq qilish</a>`):pass?`<a class="btn big" href="${stopHref(ns)}">Keyingi bekat</a>`:`${again}<a class="btn big ghost" href="#u-${n}">Mashq qilish</a>`}}})}

/* ---------- printable tests (same questions every time, with an answer key) ---------- */
function printItems(kind,id){RNG=seeded('print-'+kind+id);let mcs=[],gps=[],title,sub;
 if(kind==='u'){const u=U(id);mcs=[...u.test,...u.tx];gps=u.tg;title=`Unit ${id} testi`;sub=`${u.k==='v'?'Vocabulary':'Grammar'} · ${u.t}`}
 else if(kind==='r'){legUnits(id-1).forEach(n=>{const u=U(n);mcs.push(...pick(u.mc,3));gps.push(...pick(u.gaps,2))});title=`Review ${id}`;sub=`Units ${3*id-2}, ${3*id-1} and ${3*id}`}
 else{const from=id===1?1:22;const pool=[];for(let n=from;n<from+21;n++){const u=U(n);pool.push(...u.test,...u.tx)}mcs=pick(pool,30);title=`Progress Test ${id}`;sub=`Units ${from}–${from+20}`}
 mcs=shuffle(mcs).map(([q,o])=>({q,opts:shuffle(o),ans:o[0]}));gps=shuffle(gps).map(([q,a])=>({q,ans:a}));RNG=Math.random;return{title,sub,mcs,gps}}
function printView(kind,id){if((kind==='u'&&!U(id))||(kind==='r'&&!(id>=1&&id<=14))||(kind==='p'&&id!==1&&id!==2))return goHome();
 const d=printItems(kind,id),L='abc',line=q=>h(q).replace('___','<span class="pl"></span>'),total=d.mcs.length+d.gps.length;
 const back=kind==='u'?`#u-${id}`:kind==='r'?`#boss-${id-1}`:`#exam-${id}`;
 app.innerHTML=`<div class="wrap print"><div class="actions no-print"><button type="button" class="btn" data-act="print">Chop etish</button><a class="btn ghost" href="${back}">Orqaga</a></div>
<p class="note no-print">A4 varaq: birinchi sahifa o'quvchiga, oxirgisi javoblar kaliti o'qituvchiga. Tugma ishlamasa, faylni brauzerda ochib Ctrl+P ni bosing.</p>
<article class="sheet-p"><header class="sp-h"><div><p class="eyebrow">Destination A2</p><h1>${d.title}</h1><p class="sub">${h(d.sub)}</p></div><div class="sp-f"><span>Name / Ism: ________________</span><span>Class / Sinf: ________</span><span>Date / Sana: ________</span><span>Score / Ball: ______ / ${total}</span></div></header>
<h2>A. Choose the correct answer. <small>To'g'ri javobni belgilang.</small></h2><ol class="sp-q">${d.mcs.map(m=>`<li><p>${line(m.q)}</p><p class="sp-o">${m.opts.map((o,i)=>`<span>${L[i]}) ${h(o)}</span>`).join('')}</p></li>`).join('')}</ol>
${d.gps.length?`<h2>B. Complete the sentences. <small>Gaplarni to'ldiring.</small></h2><ol class="sp-q" start="${d.mcs.length+1}">${d.gps.map(g=>`<li><p>${line(g.q)}</p></li>`).join('')}</ol>`:''}
<p class="sp-grade">Baholash: 86–100% = 5 · 70–85% = 4 · 55–69% = 3 · 0–54% = 2</p></article>
<article class="sheet-p key"><h2>Answer key / Javoblar kaliti · ${d.title}</h2><ol class="sp-k">${d.mcs.map(m=>`<li>${L[m.opts.indexOf(m.ans)]}) ${h(m.ans)}</li>`).join('')}${d.gps.map(g=>`<li>${h(g.ans.join(' / '))}</li>`).join('')}</ol></article></div>`;
 CUR={act:{print:()=>{try{window.print()}catch(e){}}},key:null}}

/* ---------- word games (ideas from Destination-B1-quizes): memory, scramble, hidden word, survival ---------- */
function wordPool(){const vs=(AS?asUnits():UNITS).filter(u=>u.k==='v'),st=vs.filter(u=>crowns(u.n)),src=st.length?st:vs.slice(0,3);return src.flatMap(u=>u.W.map(w=>({en:w[0],uz:w[1],ex:w[2],n:u.n})))}
const GAMES=[['memory','Xotira','Kartalarni ochib, inglizcha so\'z va o\'zbekcha ma\'noni juftlang',I.cards],['scramble','Harf jumbog\'i','Aralash harflardan so\'zni yig\'ing',I.abc],
 ['hidden','Yashirin so\'z','O\'zbekcha ma\'nodan so\'zni harfma-harf toping, 6 ta jon',I.eye],['survival','Omon qolish','3 ta jon, vaqt yo\'q: qancha chidaysiz?',I.heart]];
const G={};
function gamesHub(){const started=UNITS.some(u=>u.k==='v'&&crowns(u.n));
 app.innerHTML=`<div class="wrap">${topbar()}<a class="back" href="#">${I.back}${AS?'Topshiriqlar':'Xarita'}</a><h1 class="page-h">O'yinlar</h1><p class="sub">${AS?'Topshiriqdagi lug\'at unitlarining so\'zlari bilan. Kamida 2 ta o\'yinni o\'ynang.':started?'Siz boshlagan lug\'at unitlaridagi so\'zlar bilan.':'Hozircha 3, 6 va 9-unit so\'zlari. Lug\'at unitlarini o\'ynasangiz, o\'yinlar ularning so\'zlarini oladi.'}</p>
<div class="ghub">${GAMES.map(([id,t,d,ic])=>{const r=S.games[id];return`<a class="gcard g-${id}" href="#g-${id}"><span class="gic">${ic}</span><b>${t}</b><span>${d}</span><small>${r?`Rekord: ${r.best}${id==='memory'?' yulduz':''} · ${r.plays} marta`:'Hali o\'ynalmagan'}</small></a>`}).join('')}</div></div>`;
 CUR={act:{},key:null}}
function gameTop(t,d){return`${topbar()}<a class="back" href="#games">${I.back}O'yinlar</a><header class="g-head"><h1>${t}</h1><p>${d}</p></header>`}
function gameEnd(id,o){const r=S.games[id]=S.games[id]||{best:0,plays:0};r.plays++;const rec=o.score>r.best;if(rec)r.best=o.score;addXP(o.xp);S.stats.sessions++;const nb=checkBadges({hour:new Date().getHours()});save();
 app.innerHTML=`<div class="wrap center result">${mascot('cheer',rec?'Yangi rekord!':any(PRAISE))}<h1>${o.title}</h1><p class="sub">${o.sub||''}</p>
<div class="stats"><div class="stat xp"><b>+${o.xp}</b><span>XP</span></div><div class="stat"><b>${o.score}</b><span>${o.unit||'Natija'}</span></div><div class="stat"><b>${r.best}</b><span>Rekord</span></div><div class="stat"><b>${r.plays}</b><span>O'yinlar soni</span></div></div>
${o.extra||''}${nb.length?`<h2 style="margin-top:22px">Yangi nishon!</h2><div class="new-badges">${nb.map(badgeHTML).join('')}</div>`:''}
<div class="actions"><button type="button" class="btn big" data-act="again">Yana o'ynash</button><a class="btn big ghost" href="#games">Boshqa o'yin</a></div></div>`;
 sfx.win();if(rec)confetti();CUR={act:{again:o.again},key:null};window.scrollTo(0,0)}

function gameMemory(){const pool=pick(wordPool().filter(w=>w.uz.length<=30),6),cards=shuffle(pool.flatMap((w,i)=>[{i,t:w.en,en:1},{i,t:w.uz,en:0}]));let open=[],moves=0,found=0,lock=false;
 app.innerHTML=`<div class="wrap game">${gameTop('Xotira','Kartani oching, so\'ng uning juftini toping: inglizcha so\'z va o\'zbekcha ma\'no.')}
<p class="g-stat"><span>Urinishlar: <b id="mv">0</b></span><span>Topildi: <b id="fd">0</b> / 6</span></p>
<div class="mem">${cards.map((c,k)=>`<button type="button" class="mcard" data-act="flip" data-k="${k}" data-p="${c.i}" aria-label="Yopiq karta ${k+1}"><span class="mc-in"><span class="mc-f" aria-hidden="true">?</span><span class="mc-b ${c.en?'en':'uz'}" ${c.en?'':'lang="uz"'}>${h(c.t)}</span></span></button>`).join('')}</div></div>`;
 CUR={act:{flip:b=>{if(lock||b.classList.contains('open'))return;const c=cards[+b.dataset.k];b.classList.add('open');b.setAttribute('aria-label',c.t);if(c.en)say(c.t);else sfx.tap();open.push([b,c]);if(open.length<2)return;
  moves++;$('#mv').textContent=moves;const[[b1,c1],[b2,c2]]=open;open=[];
  if(c1.i===c2.i){[b1,b2].forEach(x=>{x.classList.add('done');x.disabled=true});found++;$('#fd').textContent=found;sfx.ok();
   if(found===6){const stars=moves<=8?3:moves<=12?2:1;setTimeout(()=>gameEnd('memory',{title:'Hamma juftlar topildi!',sub:`${moves} ta urinish`,score:stars,unit:'Yulduz',xp:30+stars*10,again:gameMemory,
    extra:`<p class="res-stars" aria-label="${stars} / 3 yulduz">${[1,2,3].map(k=>`<span class="${k<=stars?'':'off'}">${I.crown}</span>`).join('')}</p>`}),600)}}
  else{lock=true;sfx.bad();setTimeout(()=>{b1.classList.remove('open');b2.classList.remove('open');b1.setAttribute('aria-label','Yopiq karta');b2.setAttribute('aria-label','Yopiq karta');lock=false},900)}}},key:null}}

function gameScramble(){const words=pick(wordPool().filter(w=>/^[a-z]{3,11}$/i.test(w.en)),8);let wi=0,score=0,hints=0,built=[];
 app.innerHTML=`<div class="wrap game">${gameTop('Harf jumbog\'i','O\'zbekcha ma\'noga qarab, harflardan inglizcha so\'zni yig\'ing.')}<p class="g-stat"><span>So'z: <b id="wi">1</b> / ${words.length}</span><span>Ball: <b id="sc">0</b></span></p><section class="g-area"></section></div>`;
 function show(){const w=words[wi],a=w.en.toLowerCase().split('');let l,t=0;do l=shuffle(a);while(l.join('')===a.join('')&&++t<12);built=[];hints=0;G.word=w.en.toLowerCase();
  $('.g-area').innerHTML=`<p class="clue" lang="uz">${h(w.uz)}</p><div class="slots">${a.map(()=>'<span class="slot"></span>').join('')}</div>
<div class="letters">${l.map((c,k)=>`<button type="button" class="ltr" data-act="ltr" data-k="${k}">${c}</button>`).join('')}</div>
<div class="actions"><button type="button" class="btn ghost" data-act="undo">O'chirish</button><button type="button" class="btn ghost" data-act="ghint">${I.bulb} Harf ochish</button><button type="button" class="btn ghost" data-act="skip">O'tkazish</button></div>`;
  $('#wi').textContent=wi+1}
 function paint(){$$('.slot').forEach((x,i)=>{x.textContent=built[i]?built[i].c:'';x.classList.toggle('fixed',!!(built[i]&&built[i].fixed))})}
 function place(b){if(b.disabled)return;built.push({c:b.textContent,b});b.disabled=true;sfx.tap();paint();if(built.length===G.word.length)judge()}
 function judge(){const w=built.map(x=>x.c).join('');if(w===G.word){const pts=Math.max(2,10-3*hints);score+=pts;$('#sc').textContent=score;sfx.ok();say(G.word);$('.slots').classList.add('ok');setTimeout(nextW,800)}
  else{sfx.bad();shake($('.slots'));setTimeout(()=>{built.filter(x=>!x.fixed).forEach(x=>x.b.disabled=false);built=built.filter(x=>x.fixed);paint()},500)}}
 function nextW(){wi++;wi<words.length?show():gameEnd('scramble',{title:'Jumboq yechildi!',sub:`${words.length} ta so'z`,score,unit:'Ball',xp:Math.round(score/2)+10,again:gameScramble})}
 CUR={act:{ltr:place,undo:()=>{const x=built[built.length-1];if(!x||x.fixed)return;built.pop();x.b.disabled=false;paint()},
  ghint:()=>{built.filter(x=>!x.fixed).forEach(x=>x.b.disabled=false);built=built.filter(x=>x.fixed);const need=G.word[built.length];if(need==null)return;const b=$$('.ltr').find(x=>!x.disabled&&x.textContent===need);if(!b)return;hints++;built.push({c:need,b,fixed:true});b.disabled=true;paint();if(built.length===G.word.length)judge()},
  skip:()=>{sfx.bad();$$('.slot').forEach((x,i)=>x.textContent=G.word[i]);setTimeout(nextW,900)}},
  key:e=>{if(/^[a-z]$/i.test(e.key)){const b=$$('.ltr').find(x=>!x.disabled&&x.textContent===e.key.toLowerCase());if(b)place(b)}else if(e.key==='Backspace'){CUR.act.undo();e.preventDefault()}}};
 show()}

function gameHidden(){const words=pick(wordPool().filter(w=>/^[a-z]+( [a-z]+)?$/i.test(w.en)&&w.en.length<=14),5);let wi=0,score=0,lives=6,got=new Set(),over=false;
 app.innerHTML=`<div class="wrap game">${gameTop('Yashirin so\'z','Ma\'noga qarab harflarni tanlang. Xato harf bitta jonni oladi.')}<p class="g-stat"><span>So'z: <b id="wi">1</b> / ${words.length}</span><span>Ball: <b id="sc">0</b></span><span class="lives" aria-label="Jonlar"></span></p><section class="g-area"></section></div>`;
 function show(){const w=words[wi];lives=6;got=new Set();over=false;G.word=w.en.toLowerCase();
  $('.g-area').innerHTML=`<p class="clue" lang="uz">${h(w.uz)}</p><div class="hidden-w" aria-live="polite"></div><div class="kbd">${'abcdefghijklmnopqrstuvwxyz'.split('').map(c=>`<button type="button" class="key" data-act="key" data-c="${c}">${c}</button>`).join('')}</div><div class="actions" id="hnext" hidden><button type="button" class="btn big" data-act="nextw">Keyingi so'z</button></div>`;
  $('#wi').textContent=wi+1;paint()}
 function paint(){$('.hidden-w').innerHTML=G.word.split('').map(c=>c===' '?'<span class="gap"></span>':`<span class="hl ${got.has(c)||over?'on':''}">${got.has(c)||over?c:''}</span>`).join('');$('.lives').innerHTML=`${I.heart}<b>${lives}</b>`}
 function guess(c){if(over)return;const b=$(`.key[data-c="${c}"]`);if(!b||b.disabled)return;b.disabled=true;
  if(G.word.includes(c)){got.add(c);b.classList.add('hit');sfx.tap();if(G.word.replace(/ /g,'').split('').every(x=>got.has(x))){over=true;score+=lives*5;$('#sc').textContent=score;sfx.ok();say(G.word);end(true)}}
  else{lives--;b.classList.add('miss');sfx.bad();shake($('.lives'));if(lives<=0){over=true;end(false)}}paint()}
 function end(won){$$('.key').forEach(k=>k.disabled=true);$('#hnext').hidden=false;const ex=words[wi].ex;$('.g-area').insertAdjacentHTML('beforeend',`<p class="g-ex ${won?'ok':'bad'}">${won?'Topdingiz!':'Jonlar tugadi.'} <i>${h(ex)}</i></p>`);$('[data-act=nextw]').focus()}
 CUR={act:{key:b=>guess(b.dataset.c),nextw:()=>{wi++;wi<words.length?show():gameEnd('hidden',{title:'Yashirin so\'zlar ochildi!',sub:`${words.length} ta so'z`,score,unit:'Ball',xp:Math.round(score/3)+10,again:gameHidden})}},
  key:e=>{if(/^[a-z]$/i.test(e.key))guess(e.key.toLowerCase());else if(e.key==='Enter'&&over&&!$('#hnext').hidden){CUR.act.nextw();e.preventDefault()}}};
 show()}

function survivalIntro(){intro({eyebrow:'O\'yin',title:'Omon qolish',sub:S.games.survival?`Rekordingiz: ${S.games.survival.best} ta to'g'ri javob`:'Birinchi rekordni o\'rnating!',bubble:'Vaqt yo\'q, shoshmang. Faqat xato qilmang!<small>No timer. Just don\'t make mistakes.</small>',
 rules:['Savollar tugamaydi: siz boshlagan unitlardan aralash','3 ta jon: uchinchi xatoda o\'yin tugaydi','50/50 va +1 jon kuchlari ishlaydi'],back:'#games',start:playSurvival})}
function playSurvival(){const pool=blitzPool();startSession({mode:'survival',endless:true,hearts:3,powers:true,back:'#games',
 gen:()=>{const u=any(pool),r=RNG();return u.k==='v'&&r<.35?qWord(u,rnd(u.W.length),RNG()<.5?'uz':'en'):r<.6?qSpot(u,rnd(u.mc.length)):qMC(u,rnd(u.mc.length))},
 onDone:s=>{const g=S.games.survival=S.games.survival||{best:0,plays:0};g.plays++;const rec=s.correct>g.best;if(rec)g.best=s.correct;const txt=`Destination A2 · Omon qolish: ${s.correct} ta to'g'ri javob`;
  return{title:rec?'Yangi rekord!':`${s.correct} ta to'g'ri javob`,sub:`Rekord: ${g.best}`,big:rec,extra:`<div class="card" style="text-align:left"><h2>Do'stlaringizni chaqiring</h2>${shareBox(txt)}</div>`,act:Object.assign(copyAct(),{again:playSurvival}),buttons:`<button type="button" class="btn big" data-act="again">Yana bir marta</button><a class="btn big ghost" href="#games">Boshqa o'yin</a>`}}})}

/* ---------- badges ---------- */
const BADGES=[
 ['first','1','Birinchi parvoz','Birinchi mashg\'ulot',()=>S.stats.sessions>=1],
 ['perfect','100','Benuqson','Xatosiz mashg\'ulot',c=>c.perfect],
 ['combo10','x10','Olov','10 ta ketma-ket to\'g\'ri',c=>c.combo>=10],
 ['streak3','3d','3 kunlik seriya','3 kun ketma-ket',()=>streak()>=3],
 ['streak7','7d','Bir hafta','7 kun ketma-ket',()=>streak()>=7],
 ['boss','B','Darvoza','Birinchi bossni yengish',()=>Object.keys(S.boss).length>=1],
 ['silk','UZ','Ipak yo\'li','O\'zbekistonning 5 shahri',()=>[0,1,2,3,4].every(i=>S.boss[i])],
 ['exam1','G1','Aeroport 1','1-imtihondan o\'tish',()=>S.exam[1]>=70],
 ['exam2','G2','Aeroport 2','2-imtihondan o\'tish',()=>S.exam[2]>=70],
 ['blitz20','60','Chaqmoq','Blitzda 20+ to\'g\'ri',()=>S.blitz>=20],
 ['fixer','Fix','Xatodan saboq','10 ta xatoni tuzatish',()=>S.fixed>=10],
 ['words','W','So\'z ustasi','14 lug\'at unitida toj',()=>UNITS.filter(u=>u.k==='v').every(u=>crowns(u.n))],
 ['xp1000','1K','1000 XP','Jami 1000 XP',()=>S.xp>=1000],
 ['night','21','Tungi boyqush','21:00 dan keyin mashq',c=>c.hour>=21],
 ['early','7','Erta qush','08:00 gacha mashq',c=>c.hour<8],
 ['grand','42','Katta sayohat','42 unitning hammasida toj',()=>UNITS.every(u=>crowns(u.n))],
 ['test1','T','Birinchi test','Unit testini topshirish',()=>Object.values(S.tests).some(p=>p>=70)],
 ['test42','42T','Test ustasi','42 ta unit testini topshirish',()=>UNITS.every(u=>S.tests[u.n]>=70)],
 ['story','5S','Hikoyachi','5 ta shahar sahnasini tugatish',()=>Object.keys(S.scenes).length>=5],
 ['sure10','×2','O\'zini biladi','«Aniq bilaman» bilan 10 ta to\'g\'ri javob',()=>S.sure.ok>=10],
 ['arcade','4G','O\'yinchi','4 ta o\'yinning hammasini o\'ynash',()=>GAMES.every(g=>S.games[g[0]])],
 ['survive15','15','Chidamli','Omon qolishda 15+ to\'g\'ri',()=>(S.games.survival||{}).best>=15]];
function checkBadges(ctx){const got=[];if(AS)return got;BADGES.forEach(b=>{if(!S.badges[b[0]]&&b[4](ctx||{})===true){S.badges[b[0]]=dayKey();got.push(b)}});return got}
const badgeHTML=b=>`<div class="badge ${S.badges[b[0]]?'':'locked'}"><span class="medal">${b[1]}</span><b>${b[2]}</b><span class="desc">${b[3]}</span></div>`;

/* ---------- profile ---------- */
function profile(){const L=levelOf(S.xp),a=lvStart(L),b=lvStart(L+1),st=S.stats;const acc=st.answered?Math.round(st.correct*100/st.answered):0;
 const allCrowns=UNITS.reduce((t,u)=>t+crowns(u.n),0),bosses=Object.keys(S.boss).length,tp=UNITS.filter(u=>S.tests[u.n]>=70).length,ep=[1,2].filter(k=>S.exam[k]>=70).length;
 const theme=document.documentElement.dataset.theme||'';
 app.innerHTML=`<div class="wrap">${topbar()}<a class="back" href="#">${I.back}Xarita</a>
<section class="card profile">${mascot('cheer')}<div style="flex:1;min-width:200px"><p class="eyebrow">Daraja ${L}</p><h1>${rankOf(L)}</h1><div class="lvbar"><i style="width:${(S.xp-a)*100/(b-a)}%"></i></div><p class="note">Keyingi darajagacha ${b-S.xp} XP</p></div></section>
<section class="card"><h2>Statistika</h2><div class="grid-stats">
<div class="stat xp"><b>${S.xp}</b><span>Jami XP</span></div><div class="stat"><b>${streak()}</b><span>Kunlik seriya</span></div><div class="stat"><b>${st.sessions}</b><span>Mashg'ulotlar</span></div>
<div class="stat"><b>${acc}%</b><span>Aniqlik</span></div><div class="stat"><b>${allCrowns}/126</b><span>Tojlar</span></div><div class="stat"><b>${tp}/42</b><span>Unit testlari</span></div>
<div class="stat"><b>${bosses}/14</b><span>Review</span></div><div class="stat"><b>${ep}/2</b><span>Progress test</span></div><div class="stat"><b>${S.blitz}</b><span>Blitz rekordi</span></div></div>
<p class="note">${I.snow} Seriya muzlatgichi: <b>${S.freeze} / 2</b>. Kunlik maqsadni har 5 marta bajarganingizda bittasini olasiz; bir kun o'tkazib yuborsangiz, u seriyangizni saqlab qoladi.${S.frozen.length?` Ishlatilgan: ${S.frozen.length} marta.`:''}</p></section>
<section class="card"><h2>Qiyin mavzular</h2>${(()=>{const top=Object.entries(S.errs).filter(e=>e[1]>0).sort((a,b)=>b[1]-a[1]).slice(0,3);return top.length?`<ol class="weak">${top.map(([n,c])=>`<li><div><b>Unit ${n}: ${h(U(+n).t)}</b><span>${c} ta xato</span></div><a class="btn ghost" href="#u-${n}">Mashq qilish</a></li>`).join('')}</ol><p class="note">Xatolar ko'p bo'lgan unitlar. Ularni qayta o'ynang yoki «Takrorlash»dan foydalaning.</p>`:'<p class="note">Hali ma\'lumot yo\'q. Xato qilgan savollaringizdan bu yerda qiyin mavzular aniqlanadi.</p>'})()}</section>
<section class="card"><h2>Nishonlar · ${Object.keys(S.badges).length}/${BADGES.length}</h2><div class="badges">${BADGES.map(badgeHTML).join('')}</div></section>
<section class="card"><h2>Sozlamalar</h2>
<div class="setting"><b>Kunlik maqsad</b><span class="seg">${[20,50,100].map(g=>`<button type="button" data-act="goal" data-g="${g}" aria-pressed="${S.goal===g}">${g} XP</button>`).join('')}</span></div>
<div class="setting"><b>Ovoz effektlari</b><span class="seg"><button type="button" data-act="sound" data-v="1" aria-pressed="${S.sound}">Yoqilgan</button><button type="button" data-act="sound" data-v="0" aria-pressed="${!S.sound}">O'chiq</button></span></div>
<div class="setting"><b>Ko'rinish</b><span class="seg"><button type="button" data-act="theme" data-v="" aria-pressed="${!theme}">Tizim</button><button type="button" data-act="theme" data-v="light" aria-pressed="${theme==='light'}">Yorug'</button><button type="button" data-act="theme" data-v="dark" aria-pressed="${theme==='dark'}">Qorong'i</button></span></div></section>
<section class="card"><h2>O'qituvchi bo'limi</h2><p class="note">O'quvchilarga faqat tanlangan unitlar, testlar va o'yinlardan iborat alohida fayl yarating va ularning natijalarini tekshiring.</p><a class="btn ghost" href="#teacher">Topshiriq yaratish</a></section>
<section class="card"><h2>Boshqa qurilmaga ko'chirish</h2><p class="note">Progress faqat shu brauzerda saqlanadi. Kodni olib, boshqa qurilmada shu maydonga qo'ying va "Kodni kiritish"ni bosing.</p>
<label class="sr" for="code">Progress kodi</label><textarea class="code" id="code" placeholder="Progress kodi"></textarea><div class="actions"><button type="button" class="btn ghost" data-act="export">Kodni olish</button><button type="button" class="btn ghost" data-act="import">Kodni kiritish</button></div><p class="note" id="code-msg" role="status"></p></section>
<section class="card"><h2>Boshidan boshlash</h2><p class="note">Barcha progress, XP va nishonlar o'chiriladi.</p><button type="button" class="btn bad" data-act="reset">Progressni o'chirish</button></section></div>`;
 const msg=t=>{$('#code-msg').textContent=t};
 CUR={act:{goal:b=>{S.goal=+b.dataset.g;save();profile()},sound:b=>{S.sound=b.dataset.v==='1';save();profile();sfx.ok()},
  theme:b=>{S.theme=b.dataset.v||null;if(S.theme)document.documentElement.dataset.theme=S.theme;else delete document.documentElement.dataset.theme;save();profile()},
  export:()=>{const c=btoa(unescape(encodeURIComponent(JSON.stringify(S))));const t=$('#code');t.value=c;t.select();try{navigator.clipboard.writeText(c).then(()=>msg('Kod nusxalandi.'),()=>msg('Kod belgilandi, nusxalang.'))}catch(e){msg('Kod belgilandi, nusxalang.')}},
  import:()=>{try{const o=JSON.parse(decodeURIComponent(escape(atob($('#code').value.trim()))));if(!o||typeof o!=='object'||typeof o.xp!=='number')throw 0;S=load(o);save();msg('Progress tiklandi.');setTimeout(profile,700)}catch(e){msg('Kod noto\'g\'ri. Uni boshidan oxirigacha to\'liq nusxalang.')}},
  reset:b=>{if(b.dataset.sure){S=FRESH();save();location.hash='';route();toast('Progress o\'chirildi')}else{b.dataset.sure=1;b.textContent='Rostdan ham o\'chirasizmi? Yana bosing'}}},key:null}}

/* ---------- assignments: the teacher picks units and tasks, the student gets a file with only those ---------- */
// The result text ends with a code: a hash of the lines plus the assignment's secret. It catches an edited
// result text; it cannot stop a student who edits the browser's storage, so it is a check, not a lock.
const HDR='Destination A2 · Topshiriq natijasi';
const PARTS=[['1','1-daraja · Tanishuv','Variant tanlash va gap tuzish',1],['2','2-daraja · Mashq','Tinglash, xatoni topish, so\'z banki',1],['3','3-daraja · Usta','Javobni o\'zi yozadi, diktant',0],
 ['t','Unit testi','20 savol, 5 baholik baho',1],['r','Review jangi','Tanlangan unitlar aralash, boss jangi',0],['s','Suhbat sahnasi','Shahar dialogi va 45 soniya gapirish',0],['g','So\'z o\'yinlari','Xotira, jumboq, yashirin so\'z · lug\'at uniti kerak',0]];
function goHome(){return AS?asHome():home()}
const asUnits=()=>AS.units.map(U).filter(Boolean);
const legsOf=a=>[...new Set(a.units.map(legOf))];
const hasVocab=a=>a.units.some(n=>U(n)&&U(n).k==='v');
const unitRange=us=>{const o=[];us.slice().sort((a,b)=>a-b).forEach(n=>{const l=o[o.length-1];if(l&&l[1]===n-1)l[1]=n;else o.push([n,n])});return o.map(([a,b])=>a===b?a:a+'–'+b).join(', ')};
const dueTxt=d=>d?d.split('-').reverse().join('.'):'';
function taskDefs(a){const t=[],p=x=>a.parts.includes(x);
 a.units.forEach(n=>{['1','2','3'].forEach(L=>{if(p(L))t.push({k:'l',n,L:+L,label:`Unit ${n} · ${L}-daraja`,href:`#play-u-${n}-${L}`})});if(p('t'))t.push({k:'t',n,label:`Unit ${n} testi`,href:`#test-u-${n}`})});
 if(p('r'))t.push({k:'r',label:'Review jangi',href:'#review'});
 if(p('s'))legsOf(a).forEach(i=>{if(SCENES[i])t.push({k:'s',i,label:`Sahna: ${SCENES[i].title}`,href:`#scene-${i}`})});
 if(p('g')&&hasVocab(a))t.push({k:'g',label:'So\'z o\'yinlari',href:'#games'});
 return t}
function taskState(d){ // null = not done yet; s = a percentage that counts toward the average
 if(d.k==='l'){const v=S.lv[d.n+'-'+d.L];return v==null?null:{s:v,txt:v+'%'}}
 if(d.k==='t'){const v=S.tests[d.n];if(v==null)return null;const f=S.firstT[d.n],tr=S.tries[d.n]||0;return{s:v,txt:`${v}% (baho ${gradeOf(v)[0]})${f!=null&&f!==v?` · 1-urinish ${f}%`:''}${tr?` · ${tr} urinish`:''}`}}
 if(d.k==='r')return S.rev==null?null:{s:S.rev,txt:`${S.rev}% · dev yengildi`};
 if(d.k==='s'){const v=S.scenes[d.i];return v==null?null:{txt:`${v}/3 yulduz`}}
 const pl=GAMES.filter(g=>S.games[g[0]]);return pl.length<2?null:{txt:pl.map(g=>`${g[1]} ${S.games[g[0]].best}`).join(', ')}}
function pendingTxt(d){if(d.k==='t'&&S.tries[d.n])return`tugatilmagan · ${S.tries[d.n]} urinish`;if(d.k==='r'&&S.revFail)return`dev yengilmadi · ${S.revFail} urinish`;
 if(d.k==='g'){const k=GAMES.filter(g=>S.games[g[0]]).length;if(k)return`${k}/2 o'yin`}return'bajarilmagan'}
function sign(lines,sec){const t=lines.map(l=>l.trim()).join('\n').normalize('NFC')+'\n'+sec;let a=2166136261,b=5381;
 for(let i=0;i<t.length;i++){const c=t.charCodeAt(i);a=Math.imul(a^c,16777619);b=(Math.imul(b,33)^c)>>>0}
 const f=x=>(x>>>0).toString(36).toUpperCase().padStart(7,'0');return f(a)+'-'+f(b)}
function asReport(){const rows=taskDefs(AS).map(d=>[d,taskState(d)]),done=rows.filter(r=>r[1]).length,sc=rows.map(r=>r[1]&&r[1].s).filter(v=>v!=null),avg=sc.length?Math.round(sc.reduce((x,y)=>x+y,0)/sc.length):null,d=new Date();
 const body=[`«${AS.title}» · ID ${AS.id}`,`O'quvchi: ${S.name}`,...rows.map(([t,st])=>`${st?'✓':'✗'} ${t.label}: ${st?st.txt:pendingTxt(t)}`),`Bajarildi: ${done}/${rows.length}${avg!=null?` · o'rtacha ${avg}%`:''}`,`Vaqt: ${dayKey(d)} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`];
 return{text:[HDR,...body,'Kod: '+sign(body,AS.secret)].join('\n'),done,total:rows.length,rows}}

function asHome(){const r=asReport(),byU={},late=AS.due&&dayKey()>AS.due;r.rows.forEach(x=>{if(x[0].n)(byU[x[0].n]=byU[x[0].n]||[]).push(x)});const other=r.rows.filter(x=>!x[0].n);
 const row=([d,st])=>{const out=d.k==='t'&&!st&&attemptsLeft(d.n)===0;return`<li><a class="trow ${st?'done':''}" href="${d.href}"><span class="tk">${st?I.check:out?I.cross:'<i></i>'}</span><span class="tl"><b>${h(d.k==='l'?`${d.L}-daraja: ${LEVELS[d.L].name}`:d.k==='t'?'Unit testi':d.label)}</b><small>${h(st?st.txt:pendingTxt(d))}</small></span><span class="go">${st||out?'Ko\'rish':'Boshlash'}</span></a></li>`};
 app.innerHTML=`<div class="wrap">${topbar()}
${PREVIEW?`<div class="banner pv"><div><b>Oldindan ko'rish</b><p>O'quvchi faylni ochganda shunday ko'radi. Bu yerdagi natijalar chiqqaningizda o'chiriladi.</p></div><button type="button" class="btn ghost" data-act="endpv">O'qituvchi sahifasiga</button></div>`:''}
<header class="as-head"><p class="eyebrow">Topshiriq · Destination A2</p><h1>${h(AS.title)}</h1>${AS.note?`<p class="as-note">${h(AS.note)}</p>`:''}${AS.due?`<p class="due ${late?'late':''}">${I.cal}Muddat: ${dueTxt(AS.due)}${late?' · o\'tib ketgan':''}</p>`:''}</header>
${S.name?`<section class="card as-prog">${ring(r.done,r.total||1)}<div><b>${r.done} / ${r.total} vazifa bajarildi</b><p>${h(S.name)} · <button type="button" class="linkish" data-act="rename">ismni o'zgartirish</button></p></div></section>
${Object.keys(byU).map(n=>{const u=U(+n);return`<section class="card as-unit"><div class="au-h"><div><p class="eyebrow">Unit ${n} · ${u.k==='v'?'Lug\'at':'Grammatika'}</p><h2>${h(u.t)}</h2></div><a class="btn ghost" href="#u-${n}">${u.k==='v'?'So\'zlar':'Qoida'}</a></div><ul class="tasks">${byU[n].map(row).join('')}</ul></section>`}).join('')}
${other.length?`<section class="card"><h2>Yakuniy vazifalar</h2><ul class="tasks">${other.map(row).join('')}</ul></section>`:''}
${mistakeCount()?`<section class="card"><h2>Xatolar ustida ishlash</h2><p class="note">Ixtiyoriy: xato qilgan savollaringiz qaytadi (jami ${mistakeCount()} ta).</p><a class="btn ghost" href="#mistakes">Takrorlash</a></section>`:''}
<section class="card send"><h2>Natijani o'qituvchiga yuborish</h2><p class="note">${r.done<r.total?`Yana ${r.total-r.done} ta vazifa qoldi. Istalgan payt yuborish mumkin, lekin hammasini bajarib yuborgan yaxshi.`:'Hamma vazifa bajarildi! Matnni nusxalab, o\'qituvchingizga Telegram yoki SMS orqali yuboring.'}</p>
<textarea class="share-box" readonly rows="${r.rows.length+10}" aria-label="Natija matni">${h(r.text)}</textarea><button type="button" class="btn ${r.done===r.total?'gold':'ghost'}" data-act="copy">Natijani nusxalash</button><p class="note">Matnni o'zgartirmang: oxiridagi kod natija haqiqiyligini tasdiqlaydi.</p></section>`
:`<section class="card"><h2>Ismingizni yozing</h2><p class="note">Natija o'qituvchingizga shu ism bilan boradi.</p><form class="name-f" id="name-f"><label class="sr" for="as-name">Familiya va ism</label><input class="text-in" id="as-name" maxlength="40" autocomplete="name" placeholder="Familiya Ism"><button class="btn" type="submit">Boshlash</button></form>
<p class="note">Topshiriqda: ${r.total} ta vazifa, unitlar ${unitRange(AS.units)}.</p></section>`}
<footer class="foot">Destination A2 · o'qituvchingiz tayyorlagan topshiriq. Natijalar shu brauzerda saqlanadi.</footer></div>`;
 const f=$('#name-f');if(f)f.addEventListener('submit',e=>{e.preventDefault();const v=$('#as-name').value.replace(/\s+/g,' ').trim();if(v.length<2){shake($('#as-name'));return}S.name=v;save();sfx.ok();asHome()});
 CUR={act:Object.assign(copyAct(),{rename:()=>{const old=S.name;S.name='';save();asHome();$('#as-name').value=old;$('#as-name').focus()},
  endpv:()=>{try{sessionStorage.removeItem('destA2.preview');localStorage.removeItem(KEY)}catch(e){}location.hash='#teacher';location.reload()}}),key:null}}

function mixQs(us,n){const make=[u=>qMC(u,rnd(u.mc.length)),u=>qSpot(u,rnd(u.mc.length)),u=>qOrder(u,rnd(u.ord.length)),u=>qGapBank(u,rnd(u.gaps.length)),u=>u.k==='v'?qWord(u,rnd(u.W.length),'en'):qType(u,rnd(u.gaps.length))];
 const qs=[],seen=new Set();for(let t=0;qs.length<n&&t<n*8;t++){const u=us[t%us.length],q=make[Math.floor(t/us.length)%5](u);if(!seen.has(q.key)){seen.add(q.key);qs.push(q)}}return shuffle(qs)}
function reviewIntro(){intro({eyebrow:'Topshiriq · Review',title:'Review jangi',sub:`Unitlar ${unitRange(AS.units)} aralash`,bubble:'Devni yenging: hamma unitlardan aralash savollar!<small>Beat the giant with mixed questions.</small>',
 rules:['Har to\'g\'ri javob devga zarba beradi, ketma-ket javoblar kuchliroq uradi','3 ta jon, 50/50 va +1 jon kuchlari bor','Dev yengilganda natija topshiriqqa yoziladi'],extra:S.rev!=null?`<p class="sub">Eng yaxshi natija: ${S.rev}%</p>`:'',back:'#',start:playReview})}
function playReview(){startSession({mode:'boss',qs:mixQs(asUnits(),Math.min(24,Math.max(16,AS.units.length*5))),hearts:3,powers:true,boss:'Takror devi',back:'#',retry:playReview,onFail:()=>{S.revFail++},
 onDone:(s,acc)=>{S.rev=Math.max(S.rev??0,acc);return{title:'Review: dev yengildi!',sub:`${s.correct} ta to'g'ri javob · ${acc}%`,big:true,buttons:''}}})}

function asRoute(hs){let m;const has=n=>AS.units.includes(n),p=x=>AS.parts.includes(x);
 if(!S.name)return asHome();
 if((m=hs.match(/^u-(\d+)$/))&&has(+m[1]))return unitView(+m[1]);
 if((m=hs.match(/^play-u-(\d+)-([123])$/))&&has(+m[1])&&p(m[2]))return playUnit(+m[1],+m[2]);
 if((m=hs.match(/^test-u-(\d+)$/))&&has(+m[1])&&p('t'))return testIntro(+m[1]);
 if(hs==='review'&&p('r'))return reviewIntro();
 if((m=hs.match(/^scene-(\d+)$/))&&p('s')&&legsOf(AS).includes(+m[1])&&SCENES[+m[1]])return scene(+m[1]);
 if(p('g')&&hasVocab(AS)){if(hs==='games')return gamesHub();if(hs==='g-memory')return gameMemory();if(hs==='g-scramble')return gameScramble();if(hs==='g-hidden')return gameHidden();if(hs==='g-survival')return survivalIntro()}
 if(hs==='mistakes')return mistakesIntro();
 asHome()}

/* The teacher's file: this page's own CSS and JS, only the chosen units, and the assignment config. */
function assignFile(a){const css=[...document.querySelectorAll('style')].map(x=>x.textContent).find(t=>t.includes('--lapis'));
 const js=[...document.scripts].map(x=>x.textContent).find(t=>t.includes('function assignFile'));if(!css||!js)throw new Error('source');
 const legs=legsOf(a),j=o=>JSON.stringify(o).replace(/</g,'\\u003c');
 const data={units:a.units.map(U),cities:CITIES,scenes:SCENES.map((sc,i)=>a.parts.includes('s')&&legs.includes(i)?sc:null)};
 const cfg={v:1,id:a.id,title:a.title,note:a.note,due:a.due,units:a.units,parts:a.parts,att:a.att,secret:a.secret};
 return`<!doctype html><html lang="uz"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>${h(a.title)} · Destination A2</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@400;600;700;800&display=swap">
<style>${css}</style>
</head><body><div id="app"><noscript><p style="padding:24px">Bu topshiriq uchun JavaScript kerak.</p></noscript></div>
<script id="a2-data" type="application/json">${j(data)}<\/script>
<script id="a2-assign" type="application/json">${j(cfg)}<\/script>
<script>${js}<\/script></body></html>`}
// Inside the claude.ai viewer a page may not start downloads itself; the `downloads` capability asks the viewer instead.
async function download(name,text){const dls=window.claude&&window.claude.use?await window.claude.use('downloads').catch(()=>null):null;
 if(dls){try{await dls.save({filename:name,data:text});return true}catch(e){return false}}
 const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type:'text/html;charset=utf-8'}));a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},4000);return true}
const slug=t=>t.toLowerCase().replace(/[ʻʼ'’`‘]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,40)||'topshiriq';
const rid=n=>Array.from(crypto.getRandomValues(new Uint8Array(n)),b=>'abcdefghijkmnpqrstuvwxyz23456789'[b%32]).join('');
const fileName=a=>`Topshiriq-${slug(a.title)}-${a.id}.html`;

function verifyResults(txt){const blocks=[];let cur=null;
 txt.split(/\r?\n/).map(l=>l.trim()).filter(Boolean).forEach(l=>{if(l.includes(HDR)){cur={lines:[]};blocks.push(cur)}else if(cur&&cur.code==null){const m=l.match(/^Kod:\s*([A-Z0-9-]+)/i);if(m)cur.code=m[1].toUpperCase();else cur.lines.push(l)}});
 return blocks.map(b=>{const id=((b.lines[0]||'').match(/ID ([a-z0-9]+)$/)||[])[1],a=id&&S.assigns[id],get=p=>(b.lines.find(l=>l.startsWith(p))||'').slice(p.length).trim();
  return{id:id||'?',a,name:get('O\'quvchi:')||'—',sum:get('Bajarildi:'),time:get('Vaqt:'),tasks:b.lines.filter(l=>/^[✓✗]/.test(l)),st:!a?'unk':b.code&&b.code===sign(b.lines,a.secret)?'ok':'bad'}})}
const VST={ok:'✓ Haqiqiy',bad:'✗ O\'zgartirilgan',unk:'? Noma\'lum'};
function verifyHTML(res){if(!res.length)return`<p class="note">Natija topilmadi. Matnda «${HDR}» qatori bo'lishi kerak.</p>`;const groups={};res.forEach(r=>(groups[r.id]=groups[r.id]||[]).push(r));
 return Object.entries(groups).map(([id,rs])=>{const a=S.assigns[id],ok=rs.filter(r=>r.st==='ok').length;return`<div class="vgroup"><h3>${a?h(a.title):'Noma\'lum topshiriq'} <small>ID ${h(id)} · ${rs.length} ta natija · ${ok} ta haqiqiy</small></h3>${a?'':'<p class="note">Bu topshiriq shu brauzerda yaratilmagan, shuning uchun kodni tekshirib bo\'lmaydi. Topshiriqni yaratgan qurilmada tekshiring.</p>'}
<div class="vtable-w"><table class="vtable"><thead><tr><th>O'quvchi</th><th>Bajarildi</th><th>Yuborilgan</th><th>Holat</th></tr></thead><tbody>${rs.sort((x,y)=>x.name.localeCompare(y.name)).map(r=>`<tr><td><details><summary>${h(r.name)}</summary><ul>${r.tasks.map(t=>`<li>${h(t)}</li>`).join('')}</ul></details></td><td>${h(r.sum)}</td><td>${h(r.time)}</td><td><span class="vst ${r.st}">${VST[r.st]}</span></td></tr>`).join('')}</tbody></table></div></div>`}).join('')
 +`<div class="actions"><button type="button" class="btn ghost" data-act="tsv">Jadvalni nusxalash (Excel uchun)</button></div><textarea class="share-box" id="tsv" rows="4" readonly hidden aria-label="Jadval"></textarea>`}

function teacher(msgText){const saved=Object.values(S.assigns).sort((a,b)=>b.made-a.made);let att=2,res=[];
 app.innerHTML=`<div class="wrap teacher">${topbar()}<a class="back" href="#">${I.back}Xarita</a>
<p class="eyebrow" style="margin-top:8px">O'qituvchi bo'limi</p><h1 class="page-h">Topshiriq yaratish</h1><p class="sub">O'quvchiga butun o'yinni emas, faqat siz tanlagan unit va vazifalarni bering.</p>
<ol class="how"><li><b>1. Tanlang</b>unitlar, vazifalar, muddat</li><li><b>2. Yuboring</b>tayyor HTML faylni Telegram orqali</li><li><b>3. Tekshiring</b>o'quvchi natija matnini qaytaradi, kod uni tasdiqlaydi</li></ol>
<section class="card"><h2>Unitlar</h2><div class="legs-pick">${CITIES.map((c,i)=>`<fieldset class="lp"><legend>${i+1}. ${h(c.name)}<button type="button" class="mini" data-act="legall" data-i="${i}">hammasi</button></legend>${legUnits(i).map(n=>{const u=U(n);return`<label class="ck"><input type="checkbox" name="u" value="${n}"><span><b>${n}.</b> ${h(u.t)} <i class="kd ${u.k}">${u.k==='v'?'lug\'at':'grammatika'}</i></span></label>`}).join('')}</fieldset>`).join('')}</div></section>
<section class="card"><h2>Vazifalar</h2><div class="parts">${PARTS.map(p=>`<label class="ck big"><input type="checkbox" name="p" value="${p[0]}" ${p[3]?'checked':''}><span><b>${p[1]}</b><small>${p[2]}</small></span></label>`).join('')}</div>
<div class="setting"><b>Unit testiga urinishlar</b><span class="seg">${[1,2,3,0].map(v=>`<button type="button" data-act="att" data-v="${v}" aria-pressed="${v===att}">${v||'Cheklanmagan'}</button>`).join('')}</span></div>
<p class="note">Urinishlar qolganda o'quvchi to'g'ri javoblarni ko'rmaydi, faqat qaysi savolda xato qilganini ko'radi. Qoida va so'zlar sahifasi har doim ochiq.</p></section>
<section class="card"><h2>Nom va muddat</h2><label class="fl" for="as-title">Topshiriq nomi</label><input class="text-in" id="as-title" maxlength="60" value="Uy vazifasi">
<label class="fl" for="as-due">Muddat (ixtiyoriy)</label><input class="text-in" type="date" id="as-due">
<label class="fl" for="as-note">O'quvchiga izoh (ixtiyoriy)</label><textarea class="text-in" id="as-note" rows="2" maxlength="300" placeholder="Masalan: 1 va 2-darajani bajaring, keyin testni topshiring."></textarea></section>
<section class="card make"><p class="sum" id="as-sum" role="status"></p><div class="actions"><button type="button" class="btn big gold" data-act="mkfile">Faylni yaratish</button><button type="button" class="btn big ghost" data-act="preview">Oldindan ko'rish</button></div>
<p class="note" id="as-msg" role="status">${msgText||''}</p><p class="note">Fayl ichida faqat tanlangan unitlar bor: boshqa unitlar, javoblar kaliti va qog'oz variantlari yo'q. O'quvchi faylni telefonda Chrome yoki boshqa brauzer bilan ochadi, internet shart emas.</p></section>
${saved.length?`<section class="card"><h2>Yaratilgan topshiriqlar</h2><ul class="as-list">${saved.map(a=>`<li><div><b>${h(a.title)}</b><small>Unitlar ${unitRange(a.units)} · ${taskDefs(a).length} ta vazifa${a.parts.includes('t')?` · test: ${a.att?a.att+' urinish':'cheklanmagan'}`:''}${a.due?` · muddat ${dueTxt(a.due)}`:''} · ID ${a.id}</small></div><span class="actions"><button type="button" class="btn ghost" data-act="redl" data-id="${a.id}">Yana yuklab olish</button><button type="button" class="btn ghost" data-act="del" data-id="${a.id}">O'chirish</button></span></li>`).join('')}</ul></section>`:''}
<section class="card"><h2>Natijalarni tekshirish</h2><p class="note">O'quvchilar yuborgan natija matnlarini shu yerga qo'ying. Bir nechtasini birga qo'ysangiz, sinf jadvali chiqadi.</p>
<label class="sr" for="as-res">Natija matnlari</label><textarea class="code" id="as-res" rows="6" placeholder="${HDR} …"></textarea><div class="actions"><button type="button" class="btn" data-act="verify">Tekshirish</button></div><div id="as-out" aria-live="polite"></div></section></div>`;
 const msg=t=>{$('#as-msg').textContent=t};
 function readForm(quiet){const units=$$('input[name=u]:checked').map(x=>+x.value),vocab=units.some(n=>U(n).k==='v'),parts=$$('input[name=p]:checked').map(x=>x.value).filter(p=>p!=='g'||vocab);
  if(!units.length||!parts.length){if(!quiet)msg(units.length?'Kamida bitta vazifani belgilang.':'Kamida bitta unitni belgilang.');return null}
  return{title:$('#as-title').value.replace(/\s+/g,' ').trim()||'Uy vazifasi',note:$('#as-note').value.trim(),due:$('#as-due').value||'',units,parts,att}}
 const upd=()=>{const a=readForm(true),gOff=$$('input[name=p][value=g]:checked').length&&!(a&&a.parts.includes('g'));
  $('#as-sum').innerHTML=a?`<b>${a.units.length} ta unit · ${taskDefs(a).length} ta vazifa</b>${gOff?'<small>So\'z o\'yinlari uchun kamida bitta lug\'at unitini tanlang.</small>':''}`:'<b>Unit va vazifalarni tanlang</b>'};
 $('.teacher').addEventListener('change',upd);upd();
 CUR={act:{legall:b=>{const bx=$$('input',b.closest('fieldset')),on=!bx.every(x=>x.checked);bx.forEach(x=>x.checked=on);upd()},
  att:b=>{att=+b.dataset.v;$$('[data-act=att]').forEach(x=>x.setAttribute('aria-pressed',x===b))},
  mkfile:()=>{const a=readForm();if(!a)return;a.id=rid(6);a.secret=rid(12);a.made=Date.now();let html;try{html=assignFile(a)}catch(e){return msg('Faylni yaratib bo\'lmadi.')}
   S.assigns[a.id]=a;save();sfx.win();teacher(`Topshiriq yaratildi: ${fileName(a)}. Yuklab olinmasa, «Yaratilgan topshiriqlar»dagi «Yana yuklab olish»ni bosing.`);download(fileName(a),html).then(ok=>{if(!ok)msg('Fayl saqlanmadi. «Yana yuklab olish» tugmasi bilan qayta urining.')})},
  preview:()=>{const a=readForm();if(!a)return;Object.assign(a,{id:'preview',secret:'preview'});try{sessionStorage.setItem('destA2.preview',JSON.stringify(a));localStorage.removeItem('destA2.as.preview');location.hash='';location.reload()}catch(e){msg('Oldindan ko\'rish bu brauzerda ishlamadi.')}},
  redl:b=>{const a=S.assigns[b.dataset.id];if(a)download(fileName(a),assignFile(a)).then(ok=>msg(ok?`Yuklab olindi: ${fileName(a)}`:'Fayl saqlanmadi.'))},
  del:b=>{if(!b.dataset.sure){b.dataset.sure=1;b.textContent='Rostdan o\'chirasizmi?';return}delete S.assigns[b.dataset.id];save();teacher('Topshiriq o\'chirildi. Uning natijalarini endi tekshirib bo\'lmaydi.')},
  verify:()=>{res=verifyResults($('#as-res').value);$('#as-out').innerHTML=verifyHTML(res);if(res.length)sfx.tap()},
  tsv:b=>{const t=$('#tsv'),head=['O\'quvchi','Topshiriq','Bajarildi','Yuborilgan','Holat','Vazifalar'];
   t.value=[head,...res.map(r=>[r.name,r.a?r.a.title:r.id,r.sum,r.time,VST[r.st],r.tasks.join(' | ')])].map(x=>x.map(v=>String(v).replace(/\t/g,' ')).join('\t')).join('\n');t.hidden=false;
   const sel=()=>{t.select();b.textContent='Belgilandi, nusxalang'};try{navigator.clipboard.writeText(t.value).then(()=>{b.textContent='Nusxalandi! Excelga qo\'ying'},sel)}catch(e){sel()}}},key:null}}

/* ---------- router ---------- */
function route(){stopSession();$('.overlay')?.remove();const hs=location.hash.slice(1);let m;window.scrollTo(0,0);
 if(AS)return asRoute(hs);
 if(hs==='teacher')return teacher();
 if(m=hs.match(/^u-(\d+)$/))return unitView(+m[1]);
 if(m=hs.match(/^play-u-(\d+)-([123])$/))return playUnit(+m[1],+m[2]);
 if(m=hs.match(/^boss-(\d+)$/))return bossIntro(+m[1]);
 if(m=hs.match(/^exam-([12])$/))return examIntro(+m[1]);
 if(m=hs.match(/^test-u-(\d+)$/))return testIntro(+m[1]);
 if(m=hs.match(/^scene-(\d+)$/))return scene(+m[1]);
 if(hs==='games')return gamesHub();if(hs==='g-memory')return gameMemory();if(hs==='g-scramble')return gameScramble();if(hs==='g-hidden')return gameHidden();if(hs==='g-survival')return survivalIntro();
 if(m=hs.match(/^print-([urp])-(\d+)$/))return printView(m[1],+m[2]);
 if(hs==='daily')return dailyIntro();if(hs==='blitz')return blitzIntro();if(hs==='mistakes')return mistakesIntro();if(hs==='me')return profile();
 home();if(m=hs.match(/^leg-(\d+)$/)){const el=$('#leg-'+m[1]);if(el)el.scrollIntoView()}}
addEventListener('hashchange',route);
document.addEventListener('click',e=>{const a=e.target.closest('a[href^="#"]');if(a&&(a.getAttribute('href')===location.hash||(a.getAttribute('href')==='#'&&!location.hash))){e.preventDefault();route();return} // same-hash links still navigate
 const b=e.target.closest('[data-say],[data-act]');if(!b||b.disabled)return;
 if(b.dataset.say!==undefined){e.preventDefault();return say(b.dataset.say,!!b.dataset.slow)}
 const f=CUR.act&&CUR.act[b.dataset.act];if(f){e.preventDefault();f(b)}});
document.addEventListener('keydown',e=>{if(e.altKey||e.ctrlKey||e.metaKey)return;if(CUR.key)CUR.key(e)});
window.__a2={get q(){return SES&&SES.q},get state(){return S},get session(){return SES},game:G,applyFreeze};
applyFreeze();route();
})();
"""


if __name__ == "__main__":
    validate()
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.html"):
        old.unlink()
    (OUT / "index.html").write_text(page(), encoding="utf-8")
    print(f"built {OUT / 'index.html'}: {len(UNITS)} units, {len(CITIES)} cities")

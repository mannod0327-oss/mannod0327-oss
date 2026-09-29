"""Build the Destination A2 practice game into ./html/index.html: one self-contained page (inline CSS, JS and data)
that works offline and from file://.

The book content (42 units, in units_a/b/c.py) is turned into short game sessions: a journey map of 14 cities,
three crown levels per unit, a boss battle after every three units, two airport exams, a daily challenge,
a 60-second blitz and a mistakes review. Progress is kept in the browser's localStorage.
Run: py build.py"""
import json, random, pathlib
from units_a import UNITS_A
from units_b import UNITS_B
from units_c import UNITS_C

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


def gaps(u):
    return [[q, a] for ex in u["ex"] if ex[1] == "gap" for q, a in ex[2]]


def order_sentences(u):
    """Full sentences for the word-order game: multiple-choice items with the right answer filled in,
    plus the example sentences of vocabulary units. Short, plain sentences only."""
    cands = [q.replace("___", opts[0]) for q, opts in u["ex"][0][2] + u["test"]]
    cands += [ex for _, _, ex in u.get("words", [])]
    keep = list(dict.fromkeys(s for s in cands if 4 <= len(s.split()) <= 10 and not any(c in s for c in "—→/()…")))
    random.Random(f"order-{u['n']}").shuffle(keep)
    return keep[:12]


def unit_data(u):
    d = {"n": u["n"], "t": u["title"], "k": "v" if "words" in u else "g", "task": u["task"],
         "mc": [[q, list(o)] for q, o in u["ex"][0][2] + u["test"]],  # 0-5: exercise A, 6-15: unit test
         "gaps": [[q, list(a)] for q, a in gaps(u)], "ord": order_sentences(u)}
    if "words" in u:
        d["W"] = [list(w) for w in u["words"]]
        d["tip"] = u["tip"]
    else:
        d["L"] = [[head, lines] for head, lines in u["lesson"]]
    return d


def page():
    data = {"units": [unit_data(u) for u in UNITS],
            "cities": [{"name": a, "uz": b, "fact": c} for a, b, c in CITIES]}
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f"""<!doctype html><html lang="uz"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Destination A2</title>
<meta name="description" content="Destination A2 grammatika va lug'at o'yini: 42 unit, 14 shahar, bosslar, kunlik chaqiruv.">
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
.toast{position:fixed;left:50%;top:calc(76px + env(safe-area-inset-top,0px));transform:translate(-50%,-20px);opacity:0;background:var(--ink);color:var(--bg);font:700 16px var(--f-display);padding:10px 18px;border-radius:99px;pointer-events:none;transition:opacity .25s,transform .25s;z-index:40;display:flex;gap:8px;align-items:center;max-width:calc(100% - 32px)}
.toast.show{opacity:1;transform:translate(-50%,0)}.toast svg{color:var(--flame)}
.confetti{position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:30}
footer.foot{color:var(--muted);font-size:13px;text-align:center;margin-top:36px}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""

JS = r"""
(()=>{
'use strict';
const DATA=JSON.parse(document.getElementById('a2-data').textContent);
const UNITS=DATA.units,CITIES=DATA.cities,U=n=>UNITS[n-1];
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
 back:svg('<path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
};
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
const KEY='destA2.v3';
const FRESH=()=>({xp:0,days:{},crowns:{},boss:{},exam:{},mistakes:{},fixed:0,badges:{},blitz:0,daily:{},stats:{sessions:0,correct:0,answered:0,maxCombo:0,secs:0},goal:50,sound:true,theme:null,tasks:{}});
let S=FRESH();
function load(raw){const o=Object.assign(FRESH(),raw);o.stats=Object.assign(FRESH().stats,raw.stats||{});return o}
try{const raw=JSON.parse(localStorage.getItem(KEY));if(raw&&typeof raw==='object')S=load(raw)}catch(e){}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}};
const todayXP=()=>S.days[dayKey()]||0;
function streak(){const d=new Date();let n=0;if(!(dayKey(d) in S.days))d.setDate(d.getDate()-1);while(dayKey(d) in S.days){n++;d.setDate(d.getDate()-1)}return n}
function addXP(g){const t=dayKey();S.xp+=g;S.days[t]=(S.days[t]||0)+g}
const lvStart=L=>50*(L-1)*L;
const levelOf=xp=>{let L=1;while(xp>=lvStart(L+1))L++;return L};
const RANKS=['Tourist','Traveller','Explorer','Navigator','Pilot','Captain','Globetrotter','Legend'];
const rankOf=L=>RANKS[Math.min(RANKS.length-1,Math.floor((L-1)/2))];
const crowns=n=>S.crowns[n]||0;
function addMistake(k){if(k)S.mistakes[k]=Math.min(2,(S.mistakes[k]||0)+1)}
function fixMistake(k,force){if(!k||!(k in S.mistakes))return;S.mistakes[k]-=force?9:1;if(S.mistakes[k]<=0){delete S.mistakes[k];S.fixed++}}
const mistakeCount=()=>Object.keys(S.mistakes).length;

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
function qMC(u,i){const[q,o]=u.mc[i];return{kind:'choice',inst:'To\'g\'ri variantni tanlang',prompt:blankHTML(q),opts:shuffle(o),ans:o[0],full:fill(q,o[0]),key:u.n+':m:'+i}}
function qListen(u,i){if(!TTS)return qMC(u,i);const[q,o]=u.mc[i];const s=o.map(x=>fill(q,x));
 return{kind:'choice',inst:'Tinglang va eshitgan gapni tanlang',say:s[0],auto:true,opts:shuffle(s),ans:s[0],full:s[0],long:true,key:u.n+':m:'+i}}
function gapChoices(u,i){const a=u.gaps[i][1];const pool=[...new Set(u.gaps.map(g=>g[1][0]))].filter(x=>!a.some(y=>norm(y)===norm(x)));return shuffle([a[0],...pick(pool,3)])}
function qGapBank(u,i){const[q,a]=u.gaps[i];return{kind:'choice',inst:'Bo\'sh joyga mosini tanlang',prompt:blankHTML(q),opts:gapChoices(u,i),ans:a[0],full:fill(q,a[0]),chips:true,key:u.n+':g:'+i}}
function qType(u,i){const[q,a]=u.gaps[i];return{kind:'type',inst:'Bo\'sh joyni yozing',prompt:h(q),accept:a,ans:a[0],full:fill(q,a[0]),key:u.n+':g:'+i}}
function qOrder(u,i){const s=u.ord[i];const w=s.split(' ');let sh,t=0;do sh=shuffle(w);while(sh.join(' ')===s&&++t<12);
 return{kind:'order',inst:'So\'zlardan gap tuzing',words:sh,ans:s,full:s,key:u.n+':o:'+i}}
function qWord(u,i,mode){const[en,uz,ex]=u.W[i];const others=pick(range(u.W.length).filter(k=>k!==i),3);const k=u.n+':w:'+i;
 if(mode==='uz')return{kind:'choice',inst:'Bu so\'z nimani anglatadi?',prompt:`<span class="big-word">${h(en)}<button type="button" class="speak sm" data-say="${h(en)}" aria-label="Tinglash">${I.speaker}</button></span>`,say:en,auto:true,opts:shuffle([uz,...others.map(o=>u.W[o][1])]),ans:uz,full:ex,key:k};
 if(mode==='listen'&&TTS)return{kind:'choice',inst:'Tinglang va so\'zni tanlang',say:en,auto:true,opts:shuffle([en,...others.map(o=>u.W[o][0])]),ans:en,full:ex,key:k};
 if(mode==='type'&&!/[\/.]/.test(en))return{kind:'type',inst:'Inglizchasini yozing',prompt:`<span lang="uz">${h(uz)}</span> = ___`,accept:[en],ans:en,full:ex,key:k};
 return{kind:'choice',inst:'Inglizchasini tanlang',prompt:`<span class="big-word" lang="uz">${h(uz)}</span>`,opts:shuffle([en,...others.map(o=>u.W[o][0])]),ans:en,full:ex,key:k}}
function qPairs(u){const ids=pick(range(u.W.length),5);return{kind:'pairs',inst:'Juftlarini toping',pairs:ids.map(i=>[u.W[i][0],u.W[i][1]]),ans:'',full:''}}
function fromKey(k){const[n,t,i]=k.split(':');const u=U(+n);if(!u)return null;const j=+i;
 if(t==='m'&&u.mc[j])return qMC(u,j);if(t==='g'&&u.gaps[j])return qGapBank(u,j);if(t==='o'&&u.ord[j])return qOrder(u,j);if(t==='w'&&u.W&&u.W[j])return qWord(u,j,'uz');return null}

const LEVELS=[null,{name:'Tanishuv',desc:'Variant tanlash va gap tuzish. Isinish uchun.'},{name:'Mashq',desc:'Tinglab tanlash, so\'z banki va aralash savollar.'},{name:'Usta',desc:'Javobni o\'zingiz yozasiz. Eng qiyin daraja.'}];
function unitQuestions(u,L){const mA=range(6),mT=range(u.mc.length).slice(6),mAll=range(u.mc.length),g=range(u.gaps.length),o=range(u.ord.length),v=u.k==='v',w=v?range(u.W.length):[];let qs=[];
 if(L===1){qs=[...pick(mA,4).map(i=>qMC(u,i)),...pick(mT,2).map(i=>qMC(u,i)),...pick(o,2).map(i=>qOrder(u,i))];
  qs.push(...(v?[...pick(w,3).map(i=>qWord(u,i,'uz')),qPairs(u)]:pick(g,3).map(i=>qGapBank(u,i))))}
 else if(L===2){qs=[...pick(mAll,3).map(i=>qMC(u,i)),...pick(mT,2).map(i=>qListen(u,i)),...pick(g,3).map(i=>qGapBank(u,i)),...pick(o,2).map(i=>qOrder(u,i))];
  if(v)qs.push(...pick(w,2).map(i=>qWord(u,i,'en')),qWord(u,any(w),'listen'),qPairs(u))}
 else{qs=[...pick(g,4).map(i=>qType(u,i)),...pick(mT,3).map(i=>qMC(u,i)),...pick(o,2).map(i=>qOrder(u,i)),qListen(u,any(mT))];
  if(v)qs.push(...pick(w,3).map(i=>qWord(u,i,'type')))}
 const first=qs.shift();return[first,...shuffle(qs)]}

/* ---------- journey structure ---------- */
const legUnits=i=>[3*i+1,3*i+2,3*i+3];
const legOf=n=>Math.floor((n-1)/3);
function nextStop(){for(let i=0;i<14;i++){for(const n of legUnits(i))if(!crowns(n))return{t:'u',n};if(!S.boss[i])return{t:'boss',i};if(i===6&&!(S.exam[1]>=70))return{t:'exam',k:1}}
 if(!(S.exam[2]>=70))return{t:'exam',k:2};const n=UNITS.find(u=>crowns(u.n)<3);return n?{t:'u',n:n.n}:null}
const stopHref=s=>!s?'#me':s.t==='u'?`#play-u-${s.n}-${Math.min(3,crowns(s.n)+1)}`:s.t==='boss'?`#boss-${s.i}`:`#exam-${s.k}`;
const stopLabel=s=>!s?'Hammasi tugadi!':s.t==='u'?`Unit ${s.n}: ${U(s.n).t}`:s.t==='boss'?`Boss: ${CITIES[s.i].name} darvozasi`:`Aeroport imtihoni ${s.k}`;

/* ---------- screens ---------- */
let CUR={act:{},key:null},SES=null;
const topbar=()=>{const L=levelOf(S.xp),st=streak();return`<header class="bar"><a class="logo" href="#" aria-label="Destination A2, xarita"><span class="lg">Destination </span><b>A2</b></a><div class="chips">
<span class="chip streak ${st?'':'dim'}" title="Kunlik seriya">${I.flame}${st}</span><span class="chip xp" title="Jami XP">${I.gem}${S.xp}</span><a class="chip lvl" href="#me" title="Profil">Lv ${L}</a></div></header>`};
function greet(){const hr=new Date().getHours();const hi=hr<12?'Xayrli tong!':hr<18?'Salom!':'Xayrli kech!';const st=streak();
 if(!S.stats.sessions)return`${hi} Men Laylak, Buxorodan. Birga sayohat qilamizmi?<small>Hi! I'm Laylak. Let's travel and learn English.</small>`;
 if(todayXP()>=S.goal)return`${hi} Bugungi maqsad bajarildi. Qoyil!<small>Yana bir oz mashq qilsangiz, rekord bo'ladi.</small>`;
 return`${hi} ${st?`Seriyangiz: ${st} kun. Uzmang!`:'Bugun yangi seriya boshlaymiz!'}<small>Maqsadgacha ${S.goal-todayXP()} XP qoldi.</small>`}
function ring(v,max){const r=26,c=2*Math.PI*r,p=Math.min(1,v/max);return`<svg class="ring" viewBox="0 0 64 64" aria-hidden="true"><circle class="trk" cx="32" cy="32" r="${r}"/><circle class="val" cx="32" cy="32" r="${r}" stroke-dasharray="${c}" stroke-dashoffset="${c*(1-p)}"/></svg>`}
const crownRow=n=>`<span class="crowns" aria-label="${n} / 3 toj">${[1,2,3].map(k=>`<span class="${k<=n?'':'off'}">${I.crown}</span>`).join('')}</span>`;
const you=(t,o)=>`<span class="you ${o>0?'l':''}">${STORK}<span>${t}</span></span>`;

function home(){const ns=nextStop(),dk=S.daily[dayKey()],mc=mistakeCount(),off=[0,1,0,-1];
 const legs=CITIES.map((c,i)=>{
  const rows=legUnits(i).map((n,k)=>{const u=U(n),cr=crowns(n),isNext=ns&&ns.t==='u'&&ns.n===n;
   return`<li class="node-row" style="--o:${off[(i*4+k)%4]}"><a class="node ${u.k} ${cr===3?'full':''} ${isNext?'next':''}" href="#u-${n}" style="--c:${cr/3}" aria-label="Unit ${n}: ${h(u.t)}. ${cr} / 3 toj"><span class="node-in">${n}</span></a><span class="node-label">${h(u.t)}<small>${u.k==='v'?'Lug\'at':'Grammatika'}</small></span>${isNext?you('Shu yerda!',off[(i*4+k)%4]):''}</li>`}).join('');
  const bNext=ns&&ns.t==='boss'&&ns.i===i;
  const boss=`<li class="node-row" style="--o:${off[(i*4+3)%4]}"><a class="node boss ${S.boss[i]?'won':''} ${bNext?'next':''}" href="#boss-${i}" style="--c:${S.boss[i]?1:0}" aria-label="Boss jangi: ${c.name}"><span class="node-in">${S.boss[i]?I.shield:I.swords}</span></a><span class="node-label">Boss jangi<small>${c.name} darvozasi</small></span>${bNext?you('Jang!',off[(i*4+3)%4]):''}</li>`;
  let exam='';if(i===6||i===13){const k=i===6?1:2,ok=S.exam[k]>=70,eNext=ns&&ns.t==='exam'&&ns.k===k;
   exam=`<div class="city airport"><div><p class="eyebrow">Nazorat nuqtasi</p><h2>Aeroport ${k}</h2><p>Unitlar ${k===1?'1–21':'22–42'} bo'yicha imtihon</p></div>${ok?`<span class="stamp"><small>PASSED</small><b>Gate ${k}</b></span>`:''}</div>
   <ol class="path"><li class="node-row"><a class="node exam ${ok?'won':''} ${eNext?'next':''}" href="#exam-${k}" style="--c:${ok?1:0}" aria-label="Aeroport imtihoni ${k}"><span class="node-in">${I.plane}</span></a><span class="node-label">20 savol<small>70% dan o'ting</small></span>${eNext?you('Uchamiz!'):''}</li></ol>`}
  return`<section class="leg" id="leg-${i}"><div class="city"><div><p class="eyebrow">${i+1}-bosqich · Unitlar ${3*i+1}–${3*i+3}</p><h2>${c.name}</h2><p>${c.uz}</p></div>${S.boss[i]?`<span class="stamp"><small>VISITED</small><b>${h(c.name.split(' ')[0])}</b></span>`:''}</div><ol class="path">${rows}${boss}</ol>${exam}</section>`}).join('');
 const done=CITIES.filter((_,i)=>S.boss[i]).length;
 app.innerHTML=`<div class="wrap">${topbar()}
<section class="hero">${mascot('idle',greet())}
<div class="goal">${ring(todayXP(),S.goal)}<div><b>${todayXP()} / ${S.goal} XP</b><p>Bugungi maqsad${todayXP()>=S.goal?' bajarildi':''}</p></div></div>
<a class="btn big" href="${stopHref(ns)}" id="continue">${S.stats.sessions?'Davom etish':'Sayohatni boshlash'}</a><p class="cont-sub">${h(stopLabel(ns))}</p></section>
<nav class="modes" aria-label="O'yin rejimlari">
<a class="mode daily" href="#daily">${I.cal}<b>Kunlik chaqiruv</b><span>${dk?`Bugun: ${dk.c}/10 · ${fmt(dk.t)}`:'10 savol, hammaga bir xil'}</span></a>
<a class="mode blitz" href="#blitz">${I.bolt}<b>Blitz 60 s</b><span>${S.blitz?`Rekord: ${S.blitz}`:'Qancha tez javob berasiz?'}</span></a>
<a class="mode fix ${mc?'':'off'}" href="#mistakes">${I.redo}<b>Xatolar</b><span>${mc?`${mc} ta savol sizni kutyapti`:'Hozircha xato yo\'q'}</span></a></nav>
<div class="map-h"><h2>Sayohat xaritasi</h2><span>${done} / 14 shahar</span></div>${legs}
<footer class="foot">Destination A2 kitobi unitlari asosidagi original mashqlar. Progress shu brauzerda saqlanadi.</footer></div>`;
 CUR={act:{},key:null}}

function unitView(n){const u=U(n);if(!u)return home();const cr=crowns(n),c=CITIES[legOf(n)];
 let learn;
 if(u.k==='g'){learn=`<div class="learn">${u.L.map((r,i)=>`<article class="rule" ${i?'hidden':''}><h3>${h(r[0])}</h3><ul>${r[1].map(l=>l.startsWith('UZ: ')?`<li class="uz"><span class="uzchip">UZ</span><span lang="uz">${l.slice(4)}</span></li>`:`<li>${l}</li>`).join('')}</ul></article>`).join('')}</div>
  ${u.L.length>1?`<div class="learn-nav"><button type="button" class="btn ghost" data-act="prev">Oldingi</button><span class="dots">${u.L.map((_,i)=>`<i class="${i?'':'on'}"></i>`).join('')}</span><button type="button" class="btn ghost" data-act="next">Keyingi</button></div>`:''}`}
 else learn=`<ul class="words">${u.W.map(w=>`<li class="word"><button type="button" class="speak sm" data-say="${h(w[0])}" aria-label="Tinglash: ${h(w[0])}">${I.speaker}</button><div><b>${h(w[0])}</b><span lang="uz">${h(w[1])}</span></div></li>`).join('')}</ul><p class="tip"><b>Tip:</b> ${h(u.tip)}</p>`;
 app.innerHTML=`<div class="wrap">${topbar()}<a class="back" href="#leg-${legOf(n)}">${I.back}Xarita</a>
<header class="unit-head ${u.k}"><p class="eyebrow">Unit ${n} · ${u.k==='v'?'Lug\'at':'Grammatika'} · ${c.name}</p><h1>${h(u.t)}</h1>${crownRow(cr)}</header>
<section class="levels" aria-label="Darajalar">${[1,2,3].map(L=>`<a class="level ${cr>=L?'done':''}" href="#play-u-${n}-${L}"><span class="lv-c">${I.crown}</span><span><b>${L}-daraja: ${LEVELS[L].name}</b><span>${LEVELS[L].desc}</span></span><span class="go">${cr>=L?'Yana':'O\'ynash'}</span></a>`).join('')}</section>
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
 SES.lives=cfg.hearts||0;
 app.innerHTML=`<main class="play mode-${cfg.mode}"><header class="play-top"><button type="button" class="x" data-act="quit" aria-label="Chiqish">${I.x}</button><div class="pbar" aria-hidden="true"><i></i></div>
${cfg.hearts?`<span class="hearts" aria-label="Jonlar">${I.heart}<b>${cfg.hearts}</b></span>`:''}${cfg.timer||cfg.clock?`<span class="timer">${I.clock}<b>${cfg.timer?cfg.timer:'0:00'}</b></span>`:''}</header>
<div class="combo-pill" hidden></div><section class="q-area" aria-live="polite"></section><div class="play-mascot">${mascot('idle')}</div>
<footer class="play-foot"><div class="sheet"></div><button type="button" class="btn big" data-act="check" disabled>Tekshirish</button></footer></main>`;
 CUR={act:PLAY,key:playKey};
 if(cfg.timer){SES.left=cfg.timer;const s=SES;s.tick=setInterval(()=>{if(SES!==s)return;s.left--;const t=$('.timer');if(t){t.querySelector('b').textContent=s.left;t.classList.toggle('low',s.left<=10)}updateBar();if(s.left<=0)finish()},1000)}
 else if(cfg.clock)SES.tick=setInterval(()=>{const t=$('.timer b');if(t&&SES)t.textContent=fmt(Math.round((Date.now()-SES.t0)/1000))},1000);
 next()}
function stopSession(){if(SES&&SES.tick)clearInterval(SES.tick);SES=null}
function updateBar(){const b=$('.pbar i');if(!b||!SES)return;b.style.width=(SES.timer?(1-SES.left/SES.timer):SES.done/SES.total)*100+'%'}
function next(){if(!SES)return;if(!SES.queue.length&&SES.gen)SES.queue.push(SES.gen());const q=SES.queue.shift();if(!q)return finish();
 SES.q=q;SES.state='q';SES.sel=null;SES.pairMiss=0;
 const foot=$('.play-foot');foot.className='play-foot';$('.sheet').innerHTML='';const btn=$('[data-act=check]');btn.textContent='Tekshirish';btn.className='btn big';btn.disabled=true;btn.hidden=!!SES.instant||q.kind==='pairs';
 const area=$('.q-area');area.style.animation='none';void area.offsetWidth;area.style.animation='';
 let body='';
 if(q.say&&!q.prompt)body+=`<div class="listen-row"><button type="button" class="speak huge" data-say="${h(q.say)}" aria-label="Tinglash">${I.speaker}</button><button type="button" class="slow" data-say="${h(q.say)}" data-slow="1">Sekinroq</button></div>`;
 if(q.kind==='choice'){body+=(q.prompt?`<div class="prompt">${q.prompt}</div>`:'')+`<div class="opts ${q.chips?'chips':''}">${q.opts.map((o,i)=>`<button type="button" class="opt" data-act="opt" data-i="${i}"><kbd>${i+1}</kbd><span>${h(o)}</span></button>`).join('')}</div>`}
 else if(q.kind==='type'){body+=`<div class="prompt">${q.prompt.replace('___','<input class="type-in" id="type-in" type="text" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="Javob">')}</div>`}
 else if(q.kind==='order'){body+=`<div class="ord-line" aria-label="Sizning gapingiz"></div><div class="ord-bank">${q.words.map((w,i)=>`<button type="button" class="tile" data-act="tile" data-i="${i}">${h(w)}</button>`).join('')}</div>`}
 else if(q.kind==='pairs'){const L=shuffle(range(q.pairs.length)),R=shuffle(range(q.pairs.length));SES.pairLeft=q.pairs.length;
  body+=`<div class="pairs"><div class="col">${L.map(i=>`<button type="button" class="pair" data-act="pair" data-side="en" data-k="${i}">${h(q.pairs[i][0])}</button>`).join('')}</div><div class="col" lang="uz">${R.map(i=>`<button type="button" class="pair" data-act="pair" data-side="uz" data-k="${i}">${h(q.pairs[i][1])}</button>`).join('')}</div></div>`}
 area.innerHTML=`<p class="inst">${q.inst}</p>${body}`;
 const inp=$('#type-in');if(inp){inp.addEventListener('input',()=>btn.disabled=!inp.value.trim());setTimeout(()=>inp.focus(),60)}
 if(q.auto&&q.say)setTimeout(()=>{if(SES&&SES.q===q)say(q.say)},260);
 updateBar()}
function react(mood,text){const m=$('.play-mascot');if(m)m.innerHTML=mascot(mood,text)}
function grade(ok){const s=SES;s.answered++;const first=!s.requeued.has(s.q);
 if(ok){s.correct++;s.combo++;s.maxCombo=Math.max(s.maxCombo,s.combo);s.xp+=s.mode==='blitz'?5:10+Math.min(5,s.combo-1);s.done++;if(first)s.first++;if(first||s.mode==='mistakes')fixMistake(s.q.key,s.mode==='mistakes'); // the in-session retry does not clear a mistake
  if(s.combo>=3){const p=$('.combo-pill');p.hidden=false;p.innerHTML=`${I.flame} ${s.combo} ketma-ket`;p.style.animation='none';void p.offsetWidth;p.style.animation=''}
  if(s.combo===5||s.combo===10||s.combo===20){sfx.combo();toast(`${I.flame} ${s.combo} ta ketma-ket to'g'ri!`)}else sfx.ok();
  react('happy',s.combo>=5?`${s.combo} ketma-ket!`:any(PRAISE))}
 else{s.combo=0;$('.combo-pill').hidden=true;sfx.bad();if(s.mode!=='mistakes')addMistake(s.q.key);
  if(s.requeue&&first){s.queue.push(s.q);s.requeued.add(s.q)}else s.done++;
  if(s.hearts){s.lives--;const hb=$('.hearts');hb.querySelector('b').textContent=s.lives;shake(hb)}
  react('sad',any(COMFORT))}
 updateBar();
 if(s.instant){s.state='wait';setTimeout(()=>{if(SES===s)next()},ok?300:900);return}
 const foot=$('.play-foot'),q=s.q,btn=$('[data-act=check]');foot.className='play-foot '+(ok?'ok':'bad');
 const full=q.full?`<p>${h(q.full)}<button type="button" class="speak sm" data-say="${h(q.full)}" aria-label="Tinglash">${I.speaker}</button></p>`:'';
 $('.sheet').innerHTML=ok?`${I.check}<div><b>${any(PRAISE)}</b>${q.kind==='order'||q.long?'':full}</div>`:`${I.cross}<div><b>To'g'ri javob:</b>${q.ans&&q.ans!==q.full?`<p class="ans">${h(q.ans)}</p>`:''}${full}</div>`;
 btn.hidden=false;btn.disabled=false;btn.textContent=s.hearts&&s.lives<=0?'Natijani ko\'rish':'Davom etish';btn.className='btn big '+(ok?'ok':'bad');s.state='fb';btn.focus({preventScroll:true});
 if(!ok&&q.full&&(q.kind==='order'||q.kind==='type'))setTimeout(()=>say(q.full),200)}
function check(){const s=SES,q=s.q;let ok;
 if(q.kind==='choice'){if(s.sel==null)return;ok=q.opts[s.sel]===q.ans;$$('.opt').forEach((b,i)=>{b.disabled=true;if(q.opts[i]===q.ans)b.classList.add('right');else if(i===s.sel)b.classList.add('wrong')})}
 else if(q.kind==='type'){const inp=$('#type-in'),v=inp.value;if(!v.trim())return;ok=q.accept.some(a=>norm(a)===norm(v));inp.readOnly=true;inp.classList.add(ok?'ok':'bad');if(!ok)shake(inp)}
 else if(q.kind==='order'){const line=$('.ord-line');if($('.ord-bank').children.length)return;ok=[...line.children].map(t=>t.textContent).join(' ')===q.ans;line.classList.add(ok?'ok':'bad');$$('.tile').forEach(t=>t.disabled=true);if(!ok)shake(line)}
 else return;
 grade(ok)}
const PLAY={
 opt(b){const s=SES;if(s.state!=='q')return;s.sel=+b.dataset.i;$$('.opt').forEach(x=>x.classList.toggle('sel',x===b));sfx.tap();if(s.instant)return check();$('[data-act=check]').disabled=false},
 tile(b){if(SES.state!=='q')return;const line=$('.ord-line'),bank=$('.ord-bank');(b.parentElement===line?bank:line).appendChild(b);sfx.tap();$('[data-act=check]').disabled=bank.children.length>0},
 pair(b){const s=SES;if(s.state!=='q'||b.classList.contains('done'))return;const sel=$('.pair.sel');
  if(!sel||sel.dataset.side===b.dataset.side){if(sel)sel.classList.remove('sel');b.classList.add('sel');sfx.tap();if(b.dataset.side==='en')say(b.textContent);return}
  sel.classList.remove('sel');
  if(sel.dataset.k===b.dataset.k){[sel,b].forEach(x=>{x.classList.add('done');x.disabled=true});sfx.tap();if(--s.pairLeft===0)grade(s.pairMiss<=1)}
  else{s.pairMiss++;[sel,b].forEach(x=>{x.classList.add('bad');shake(x);setTimeout(()=>x.classList.remove('bad'),450)});sfx.bad()}},
 check(){if(SES.state==='q')check();else if(SES.state==='fb'){if(SES.hearts&&SES.lives<=0)return fail();next()}},
 quit(){const back=SES.back||'#';const o=document.createElement('div');o.className='overlay';o.innerHTML=`<div class="dialog" role="dialog" aria-modal="true" aria-labelledby="qt">${mascot('sad')}<h2 id="qt">Chiqib ketasizmi?</h2><p>Bu mashg'ulotdagi natija saqlanmaydi.</p><div class="actions"><button type="button" class="btn" data-act="stay">Davom etaman</button><button type="button" class="btn ghost" data-act="leave">Chiqish</button></div></div>`;$('.play').appendChild(o);$('[data-act=stay]',o).focus();
  PLAY.stay=()=>o.remove();PLAY.leave=()=>{stopSession();location.hash=back}}
};
function playKey(e){const s=SES;if(!s||$('.overlay'))return;const t=e.target;
 if(e.key==='Enter'){if(t.classList&&(t.classList.contains('speak')||t.classList.contains('slow')))return;e.preventDefault();const b=$('[data-act=check]');if(b&&!b.disabled&&!b.hidden)PLAY.check();return}
 if(t.tagName==='INPUT')return;
 if(/^[1-9]$/.test(e.key)&&s.state==='q'&&s.q.kind==='choice'){const b=$(`.opt[data-i="${+e.key-1}"]`);if(b)PLAY.opt(b)}
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
<div class="stats"><div class="stat xp"><b data-count="${gained}">+0</b><span>XP</span></div><div class="stat"><b>${acc}%</b><span>Aniqlik</span></div><div class="stat"><b>${fmt(secs)}</b><span>Vaqt</span></div><div class="stat"><b>${s.maxCombo}</b><span>Eng uzun seriya</span></div></div>
${r.extra||''}${goalHit?`<div class="banner">${ring(1,1)}<div><b>Kunlik maqsad bajarildi!</b><p>${S.goal} XP · seriya: ${streak()} kun</p></div></div>`:''}
${nb.length?`<h2 style="margin-top:22px">Yangi nishon!</h2><div class="new-badges">${nb.map(badgeHTML).join('')}</div>`:''}
<div class="actions">${r.buttons||''}<a class="btn big ghost" href="#">Xaritaga</a></div></div>`;
 const c=$('[data-count]');const tgt=+c.dataset.count;if(RM)c.textContent='+'+tgt;else{let v=0;const inc=Math.max(1,Math.ceil(tgt/30));const iv=setInterval(()=>{v=Math.min(tgt,v+inc);c.textContent='+'+v;if(v>=tgt)clearInterval(iv)},30)}
 if(!r.sad){sfx.win();if(perfect||goalHit||nb.length||r.big)confetti()}else sfx.lose();
 CUR={act:r.act||{},key:e=>{if(e.key==='Enter'&&e.target===document.body){const b=$('.result .actions .btn');if(b){b.click();e.preventDefault()}}}};window.scrollTo(0,0)}
function fail(){const s=SES;stopSession();addXP(s.xp);save();
 app.innerHTML=`<div class="wrap center result">${mascot('sad','Jonlar tugadi. Lekin har bir xato ham saboq!')}<h1>Bu safar bo'lmadi</h1><p class="sub">${s.correct} ta to'g'ri javob · +${s.xp} XP</p>
<ul class="rules"><li>Xato savollar "Xatolar" bo'limiga tushdi.</li><li>Unitlarni yana bir marta o'ynab, keyin qayta urinib ko'ring.</li></ul>
<div class="actions"><button type="button" class="btn big" data-act="retry">Qayta urinish</button><a class="btn big ghost" href="${s.back||'#'}">Orqaga</a></div></div>`;
 sfx.lose();CUR={act:{retry:()=>s.retry?s.retry():route()},key:null}}

/* ---------- modes ---------- */
function playUnit(n,L){const u=U(n);if(!u)return home();
 startSession({mode:'unit',qs:unitQuestions(u,L),requeue:true,back:'#u-'+n,onDone:()=>{const prev=crowns(n),got=L>prev;if(got)S.crowns[n]=L;const ns=nextStop();
  const buttons=L<3?`<a class="btn big" href="#play-u-${n}-${L+1}">Keyingi: ${L+1}-daraja</a>${L===1?`<a class="btn big ghost" href="${stopHref(ns)}">Keyingi bekat</a>`:''}`:`<a class="btn big" href="${stopHref(ns)}">Keyingi bekat</a>`;
  return{title:`${L}-daraja tugadi!`,sub:`Unit ${n}: ${h(u.t)}`,extra:got?`<div class="banner">${crownRow(L)}<div><b>Yangi toj!</b><p>Unit ${n}: ${L} / 3 toj</p></div></div>`:'',buttons,big:got&&L===3}}})}
function bossQs(i){const qs=[];legUnits(i).forEach(n=>{const u=U(n);qs.push(...pick(range(u.mc.length),2).map(k=>qMC(u,k)),qOrder(u,rnd(u.ord.length)),u.k==='v'?qWord(u,rnd(u.W.length),'en'):qGapBank(u,rnd(u.gaps.length)))});return shuffle(qs)}
function bossIntro(i){const c=CITIES[i];if(!c)return home();const[a,b,d]=legUnits(i);
 intro({eyebrow:`${i+1}-bosqich · Boss jangi`,title:`${c.name} darvozasi`,sub:`Unitlar ${a}, ${b} va ${d} aralash`,bubble:'Darvozadan o\'tish uchun bossni yenging!<small>Beat the boss to enter the city.</small>',
  rules:['12 ta aralash savol','3 ta jon: har xato bitta jonni oladi','G\'alaba: shahar muhri va +50 XP'],back:`#leg-${i}`,start:()=>playBoss(i)})}
function playBoss(i){const c=CITIES[i];startSession({mode:'boss',qs:bossQs(i),hearts:3,back:`#leg-${i}`,retry:()=>playBoss(i),onDone:(s,acc)=>{const firstWin=!S.boss[i];S.boss[i]=Math.max(S.boss[i]||0,acc||1);
 const nx=i===6?'#exam-1':i<13?`#play-u-${3*i+4}-1`:'#exam-2';
 return{bonus:firstWin?50:0,title:'Boss yengildi!',sub:`${c.name} sizni kutib oldi`,big:true,bubble:`Welcome to ${c.name}!`,
  extra:`<div class="banner city"><span class="stamp press"><small>VISITED</small><b>${h(c.name.split(' ')[0])}</b></span><div><b>Bilasizmi? / Did you know?</b><p>${h(c.fact)}</p><button type="button" class="speak sm" data-say="${h(c.fact)}" aria-label="Tinglash">${I.speaker}</button></div></div>`,
  buttons:`<a class="btn big" href="${nx}">${i===6||i===13?'Aeroportga':'Keyingi shahar'}</a>`}}})}
function examIntro(k){const from=k===1?1:22;
 intro({eyebrow:'Nazorat nuqtasi',title:`Aeroport ${k}`,sub:`Unitlar ${from}–${from+20} bo'yicha imtihon`,bubble:'Pasport nazorati! Tayyormisiz?<small>Passport control. Ready?</small>',
  rules:['20 ta savol, jonlar yo\'q','70% va undan yuqori: o\'tdingiz','O\'tsangiz: +100 XP va aeroport muhri'],back:`#leg-${k===1?6:13}`,start:()=>playExam(k)})}
function playExam(k){const from=k===1?1:22;const pool=[];for(let n=from;n<from+21;n++){const u=U(n);for(let i=6;i<u.mc.length;i++)pool.push([u,i])}
 startSession({mode:'exam',qs:pick(pool,20).map(([u,i])=>qMC(u,i)),clock:true,back:`#leg-${k===1?6:13}`,onDone:(s,acc)=>{const pass=acc>=70,first=pass&&!(S.exam[k]>=70);S.exam[k]=Math.max(S.exam[k]||0,acc);
  return pass?{bonus:first?100:0,big:true,title:'Imtihondan o\'tdingiz!',sub:`${s.correct} / 20 · ${acc}%`,extra:`<div class="banner"><span class="stamp press" style="color:var(--gold-deep)"><small>PASSED</small><b>Gate ${k}</b></span><div><b>Parvozga ruxsat berildi</b><p>${k===1?'Endi Parijga uchamiz!':'Siz butun A2 kursini tugatdingiz!'}</p></div></div>`,buttons:`<a class="btn big" href="${k===1?'#play-u-22-1':'#me'}">${k===1?'Parijga uchish':'Profilni ko\'rish'}</a>`}
   :{sad:true,title:'Biroz yetmadi',sub:`${s.correct} / 20 · ${acc}% · 70% kerak`,bubble:'Xatolarni ko\'rib chiqing va yana urining!',buttons:`<button type="button" class="btn big" data-act="again">Qayta topshirish</button>`,act:{again:()=>playExam(k)}}}})}
function dailyQs(){RNG=seeded('daily-'+dayKey());const qs=[];
 for(let k=0;k<10;k++){const u=any(UNITS),t=k%5;qs.push(t<2?qMC(u,rnd(u.mc.length)):t===2?qOrder(u,rnd(u.ord.length)):t===3?qGapBank(u,rnd(u.gaps.length)):u.k==='v'?qWord(u,rnd(u.W.length),'en'):qMC(u,rnd(u.mc.length)))}
 RNG=Math.random;return qs}
function dailyIntro(){const dk=S.daily[dayKey()];
 intro({eyebrow:dayKey(),title:'Kunlik chaqiruv',sub:'Bugun hamma bir xil 10 ta savol oladi',bubble:'Sinfdoshlaringiz bilan natijani solishtiring!<small>Same questions for everyone today.</small>',
  rules:['Barcha unitlardan 10 ta savol','Vaqt hisoblanadi: tez va aniq bo\'ling','Birinchi urinish natijasi saqlanadi · +30 XP'],extra:dk?`<p class="sub">Bugungi natijangiz: ${dk.c}/10 · ${fmt(dk.t)}. Yana o'ynash mumkin, lekin natija o'zgarmaydi.</p>`:'',start:playDaily})}
function shareBox(text){return`<textarea class="share-box" readonly rows="2" aria-label="Natija matni">${h(text)}</textarea><button type="button" class="btn ghost" data-act="copy">Natijani nusxalash</button>`}
const copyAct=()=>({copy:b=>{const t=$('.share-box');const sel=()=>{t.select();b.textContent='Belgilandi, nusxalang'};try{navigator.clipboard.writeText(t.value).then(()=>{b.textContent='Nusxalandi!'},sel)}catch(e){sel()}}});
function playDaily(){startSession({mode:'daily',qs:dailyQs(),clock:true,back:'#',onDone:(s,acc,secs)=>{const d=dayKey(),first=!S.daily[d];if(first)S.daily[d]={c:s.correct,t:secs};
 const txt=`Destination A2 · Kunlik chaqiruv ${d}: ${s.correct}/10, ${fmt(secs)}`;
 return{bonus:first?30:0,title:`${s.correct} / 10`,sub:first?'Bugungi natija saqlandi':'Mashq uchun o\'yin (natija o\'zgarmadi)',extra:`<div class="card" style="text-align:left"><h2>Sinfdoshlarga yuboring</h2>${shareBox(txt)}</div>`,act:copyAct(),buttons:''}}})}
function blitzPool(){const started=UNITS.filter(u=>crowns(u.n));return started.length>=2?started:UNITS.slice(0,6)}
function blitzIntro(){intro({eyebrow:'60 soniya',title:'Blitz',sub:S.blitz?`Rekordingiz: ${S.blitz} ta to'g'ri javob`:'Birinchi rekordni o\'rnating!',bubble:'Tez bo\'ling, lekin shoshmang!<small>Fast, but careful.</small>',
 rules:['60 soniyada iloji boricha ko\'p savol','Variantni bosishingiz bilan javob tekshiriladi','Savollar siz boshlagan unitlardan olinadi'],start:playBlitz})}
function playBlitz(){const pool=blitzPool();startSession({mode:'blitz',instant:true,timer:60,back:'#',gen:()=>{const u=any(pool);return u.k==='v'&&RNG()<.4?qWord(u,rnd(u.W.length),RNG()<.5?'uz':'en'):qMC(u,rnd(u.mc.length))},
 onDone:s=>{const rec=s.correct>S.blitz;if(rec)S.blitz=s.correct;const txt=`Destination A2 · Blitz: 60 soniyada ${s.correct} ta to'g'ri javob`;
  return{title:rec?'Yangi rekord!':`${s.correct} ta to'g'ri`,sub:`${s.answered} ta savol · rekord: ${S.blitz}`,big:rec,extra:`<div class="card" style="text-align:left"><h2>Do'stlaringizni chaqiring</h2>${shareBox(txt)}</div>`,act:Object.assign(copyAct(),{again:playBlitz}),buttons:`<button type="button" class="btn big" data-act="again">Yana bir marta</button>`}}})}
function mistakesIntro(){const n=mistakeCount();intro({eyebrow:'Takrorlash',title:'Xatolar ustida ishlash',sub:n?`${n} ta savol sizni kutyapti`:'Hozircha xato yo\'q. Zo\'r!',bubble:n?'Xatolar eng yaxshi ustoz!<small>Mistakes are the best teachers.</small>':'Unitlarni o\'ynang, xatolar shu yerga tushadi.',
 rules:['Oldin xato qilgan savollaringiz qaytadi (12 tagacha)','To\'g\'ri javob bersangiz, savol ro\'yxatdan chiqadi','Har bir to\'g\'ri javob uchun XP'],disabled:!n,start:playMistakes})}
function playMistakes(){const qs=shuffle(Object.keys(S.mistakes)).map(fromKey).filter(Boolean).slice(0,12);if(!qs.length)return mistakesIntro();
 startSession({mode:'mistakes',qs,back:'#',onDone:s=>({title:'Xatolar tuzatildi!',sub:`${s.correct} / ${s.answered} to'g'ri · qoldi: ${mistakeCount()}`,buttons:mistakeCount()?`<a class="btn big" href="#mistakes">Davom etish</a>`:''})})}

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
 ['grand','42','Katta sayohat','42 unitning hammasida toj',()=>UNITS.every(u=>crowns(u.n))]];
function checkBadges(ctx){const got=[];BADGES.forEach(b=>{if(!S.badges[b[0]]&&b[4](ctx||{})===true){S.badges[b[0]]=dayKey();got.push(b)}});return got}
const badgeHTML=b=>`<div class="badge ${S.badges[b[0]]?'':'locked'}"><span class="medal">${b[1]}</span><b>${b[2]}</b><span class="desc">${b[3]}</span></div>`;

/* ---------- profile ---------- */
function profile(){const L=levelOf(S.xp),a=lvStart(L),b=lvStart(L+1),st=S.stats;const acc=st.answered?Math.round(st.correct*100/st.answered):0;
 const allCrowns=UNITS.reduce((t,u)=>t+crowns(u.n),0),bosses=Object.keys(S.boss).length;
 const theme=document.documentElement.dataset.theme||'';
 app.innerHTML=`<div class="wrap">${topbar()}<a class="back" href="#">${I.back}Xarita</a>
<section class="card profile">${mascot('cheer')}<div style="flex:1;min-width:200px"><p class="eyebrow">Daraja ${L}</p><h1>${rankOf(L)}</h1><div class="lvbar"><i style="width:${(S.xp-a)*100/(b-a)}%"></i></div><p class="note">Keyingi darajagacha ${b-S.xp} XP</p></div></section>
<section class="card"><h2>Statistika</h2><div class="grid-stats">
<div class="stat xp"><b>${S.xp}</b><span>Jami XP</span></div><div class="stat"><b>${streak()}</b><span>Kunlik seriya</span></div><div class="stat"><b>${st.sessions}</b><span>Mashg'ulotlar</span></div>
<div class="stat"><b>${acc}%</b><span>Aniqlik</span></div><div class="stat"><b>${allCrowns}/126</b><span>Tojlar</span></div><div class="stat"><b>${bosses}/14</b><span>Shaharlar</span></div></div></section>
<section class="card"><h2>Nishonlar · ${Object.keys(S.badges).length}/${BADGES.length}</h2><div class="badges">${BADGES.map(badgeHTML).join('')}</div></section>
<section class="card"><h2>Sozlamalar</h2>
<div class="setting"><b>Kunlik maqsad</b><span class="seg">${[20,50,100].map(g=>`<button type="button" data-act="goal" data-g="${g}" aria-pressed="${S.goal===g}">${g} XP</button>`).join('')}</span></div>
<div class="setting"><b>Ovoz effektlari</b><span class="seg"><button type="button" data-act="sound" data-v="1" aria-pressed="${S.sound}">Yoqilgan</button><button type="button" data-act="sound" data-v="0" aria-pressed="${!S.sound}">O'chiq</button></span></div>
<div class="setting"><b>Ko'rinish</b><span class="seg"><button type="button" data-act="theme" data-v="" aria-pressed="${!theme}">Tizim</button><button type="button" data-act="theme" data-v="light" aria-pressed="${theme==='light'}">Yorug'</button><button type="button" data-act="theme" data-v="dark" aria-pressed="${theme==='dark'}">Qorong'i</button></span></div></section>
<section class="card"><h2>Boshqa qurilmaga ko'chirish</h2><p class="note">Progress faqat shu brauzerda saqlanadi. Kodni olib, boshqa qurilmada shu maydonga qo'ying va "Kodni kiritish"ni bosing.</p>
<label class="sr" for="code">Progress kodi</label><textarea class="code" id="code" placeholder="Progress kodi"></textarea><div class="actions"><button type="button" class="btn ghost" data-act="export">Kodni olish</button><button type="button" class="btn ghost" data-act="import">Kodni kiritish</button></div><p class="note" id="code-msg" role="status"></p></section>
<section class="card"><h2>Boshidan boshlash</h2><p class="note">Barcha progress, XP va nishonlar o'chiriladi.</p><button type="button" class="btn bad" data-act="reset">Progressni o'chirish</button></section></div>`;
 const msg=t=>{$('#code-msg').textContent=t};
 CUR={act:{goal:b=>{S.goal=+b.dataset.g;save();profile()},sound:b=>{S.sound=b.dataset.v==='1';save();profile();sfx.ok()},
  theme:b=>{S.theme=b.dataset.v||null;if(S.theme)document.documentElement.dataset.theme=S.theme;else delete document.documentElement.dataset.theme;save();profile()},
  export:()=>{const c=btoa(unescape(encodeURIComponent(JSON.stringify(S))));const t=$('#code');t.value=c;t.select();try{navigator.clipboard.writeText(c).then(()=>msg('Kod nusxalandi.'),()=>msg('Kod belgilandi, nusxalang.'))}catch(e){msg('Kod belgilandi, nusxalang.')}},
  import:()=>{try{const o=JSON.parse(decodeURIComponent(escape(atob($('#code').value.trim()))));if(!o||typeof o!=='object'||typeof o.xp!=='number')throw 0;S=load(o);save();msg('Progress tiklandi.');setTimeout(profile,700)}catch(e){msg('Kod noto\'g\'ri. Uni boshidan oxirigacha to\'liq nusxalang.')}},
  reset:b=>{if(b.dataset.sure){S=FRESH();save();location.hash='';route();toast('Progress o\'chirildi')}else{b.dataset.sure=1;b.textContent='Rostdan ham o\'chirasizmi? Yana bosing'}}},key:null}}

/* ---------- router ---------- */
function route(){stopSession();$('.overlay')?.remove();const hs=location.hash.slice(1);let m;window.scrollTo(0,0);
 if(m=hs.match(/^u-(\d+)$/))return unitView(+m[1]);
 if(m=hs.match(/^play-u-(\d+)-([123])$/))return playUnit(+m[1],+m[2]);
 if(m=hs.match(/^boss-(\d+)$/))return bossIntro(+m[1]);
 if(m=hs.match(/^exam-([12])$/))return examIntro(+m[1]);
 if(hs==='daily')return dailyIntro();if(hs==='blitz')return blitzIntro();if(hs==='mistakes')return mistakesIntro();if(hs==='me')return profile();
 home();if(m=hs.match(/^leg-(\d+)$/)){const el=$('#leg-'+m[1]);if(el)el.scrollIntoView()}}
addEventListener('hashchange',route);
document.addEventListener('click',e=>{const b=e.target.closest('[data-say],[data-act]');if(!b||b.disabled)return;
 if(b.dataset.say!==undefined){e.preventDefault();return say(b.dataset.say,!!b.dataset.slow)}
 const f=CUR.act&&CUR.act[b.dataset.act];if(f){e.preventDefault();f(b)}});
document.addEventListener('keydown',e=>{if(e.altKey||e.ctrlKey||e.metaKey)return;if(CUR.key)CUR.key(e)});
window.__a2={get q(){return SES&&SES.q},get state(){return S},get session(){return SES}};
route();
})();
"""


if __name__ == "__main__":
    validate()
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.html"):
        old.unlink()
    (OUT / "index.html").write_text(page(), encoding="utf-8")
    print(f"built {OUT / 'index.html'}: {len(UNITS)} units, {len(CITIES)} cities")

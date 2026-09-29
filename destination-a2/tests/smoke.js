// End-to-end smoke test for the game: plays every mode in a real browser and checks the saved progress.
// Run after `python build.py`:  node tests/smoke.js   (needs the `playwright` npm package)
const path = require('path');
const assert = require('assert');
const { chromium } = require('playwright');

const URL = 'file://' + path.resolve(__dirname, '..', 'html', 'index.html');
const state = page => page.evaluate(() => JSON.parse(JSON.stringify(window.__a2.state)));

// Answer the question on screen, right or wrong, the way a learner would (click / type / tap tiles).
async function answer(page, right = true) {
  const q = await page.evaluate(() => { const q = window.__a2.q; return q && { kind: q.kind, ans: q.ans, opts: q.opts, accept: q.accept, words: q.words, pairs: q.pairs, toks: q.toks, dict: q.dict }; });
  if (!q) return false;
  const mode = await page.evaluate(() => ({ instant: !!window.__a2.session.instant, silent: !!window.__a2.session.silent }));
  const instant = mode.instant;
  if (q.kind === 'choice') {
    const i = right ? q.opts.indexOf(q.ans) : q.opts.findIndex(o => o !== q.ans);
    await page.click(`.opt[data-i="${i}"]`);
  } else if (q.kind === 'type') {
    await page.fill('#type-in', right ? q.accept[0] : 'zzz');
  } else if (q.kind === 'order') {
    const want = right ? q.ans.split(' ') : q.words.slice().reverse();
    for (const w of want) {
      const i = await page.locator('.ord-bank .tile').evaluateAll((els, w) => els.findIndex(e => e.textContent === w), w);
      await page.locator('.ord-bank .tile').nth(i).click();
    }
  } else if (q.kind === 'spot') {
    const j = q.toks.findIndex(t => right ? t[1] : !t[1]);
    await page.click(`.stok[data-j="${j}"]`);
  } else if (q.kind === 'pairs') {
    for (let k = 0; k < q.pairs.length; k++) {
      await page.click(`.pair[data-side=en][data-k="${k}"]`);
      await page.click(`.pair[data-side=uz][data-k="${k}"]`);
    }
  }
  if (instant) { await page.waitForTimeout(right ? 380 : 980); return true; }
  if (mode.silent) { // tests: no feedback, straight to the next question
    const before = await page.evaluate(() => window.__a2.session && window.__a2.session.answered);
    await page.click('[data-act=check]');
    await page.waitForFunction(b => !window.__a2.session || window.__a2.session.answered > b, before);
    assert.equal(await page.locator('.play-foot.ok, .play-foot.bad').count(), 0, 'no feedback during a test');
    return true;
  }
  if (q.kind !== 'pairs') await page.click('[data-act=check]');
  await page.waitForSelector('.play-foot.ok, .play-foot.bad');
  if (right) assert.ok(await page.locator('.play-foot.ok').count(), q.kind + ' accepted: ' + q.ans);
  await page.click('[data-act=check]');
  return true;
}

async function playToEnd(page, wrongFirst = 0) {
  for (let n = 0; n < 60; n++) {
    if (await page.locator('.result').count()) return;
    await answer(page, n >= wrongFirst);
  }
  throw new Error('session did not end');
}

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  await ctx.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort()); // offline case: fallback fonts
  const errors = [];
  const page = await ctx.newPage();
  page.on('pageerror', e => errors.push(e.message));

  // First visit: greeting, continue button goes to Unit 1 level 1
  await page.goto(URL);
  assert.match(await page.textContent('.bubble'), /Laylak/);
  assert.equal(await page.getAttribute('#continue', 'href'), '#play-u-1-1');
  assert.equal(await page.locator('.node').count(), 42 + 14 + 14 + 2, '42 units, 14 reviews, 14 scenes, 2 progress tests on the map');

  // Unit 1 level 1, all right: a crown, XP, a first badge
  await page.click('#continue');
  await page.waitForSelector('.q-area .inst');
  assert.equal(await page.locator('.play-foot [data-act=check]').isDisabled(), true, 'check waits for an answer');
  await playToEnd(page);
  let s = await state(page);
  assert.equal(s.crowns[1], 1);
  assert.ok(s.xp >= 100, 'xp for 10 answers plus perfect bonus: ' + s.xp);
  assert.ok(s.badges.first && s.badges.perfect, 'first and perfect badges');
  assert.match(await page.textContent('.result h1'), /1-daraja tugadi/);

  // The next stop after a first crown is the unit test: 20 questions, no feedback until the end
  await page.goto(URL);
  assert.equal(await page.getAttribute('#continue', 'href'), '#test-u-1');
  assert.match(await page.textContent('.book'), /28 grammatika.*14 lug'at.*0\/42 unit testi.*0\/14 review.*0\/2 progress test/);
  await page.click('#continue');
  await page.click('[data-act=start]');
  assert.equal(await page.evaluate(() => window.__a2.session.total), 20);
  const kinds = await page.evaluate(() => [window.__a2.q, ...window.__a2.session.queue].map(q => q.kind + ':' + q.key.split(':')[1]).sort().join(','));
  assert.equal((kinds.match(/type:y/g) || []).length, 5, '5 write-in items');
  assert.ok(!/:m|:g|:o|:w/.test(kinds), 'unit test uses test-only items: ' + kinds);
  await playToEnd(page, 3);
  s = await state(page);
  assert.equal(s.tests[1], 85, '17 / 20 = 85%');
  assert.match(await page.textContent('.grade-b'), /Baho: 4/);
  assert.equal(await page.locator('.answers li').count(), 20);
  assert.equal(await page.locator('.answers li.bad').count(), 3);
  // a failed attempt: grade 2, retry button
  await page.goto(URL + '#test-u-2');
  await page.click('[data-act=start]');
  await playToEnd(page, 20);
  assert.equal((await state(page)).tests[2], 0);
  assert.match(await page.textContent('.grade-b'), /Baho: 2/);
  assert.ok(await page.locator('[data-act=again]').count());
  await page.goto(URL);
  assert.equal(await page.locator('.tb.pass').count(), 1);
  assert.equal(await page.locator('.tb.fail').count(), 1);

  // Printable sheets: same questions every time, answer key included
  for (const [hash, mc, gap] of [['#print-u-5', 15, 5], ['#print-r-3', 9, 6], ['#print-p-2', 30, 0]]) {
    await page.goto(URL + hash);
    assert.equal(await page.locator('.sheet-p:not(.key) .sp-q li').count(), mc + gap, hash);
    assert.equal(await page.locator('.sheet-p:not(.key) .sp-o').count(), mc, hash);
    assert.equal(await page.locator('.sp-k li').count(), mc + gap, hash + ' key');
    const first = await page.textContent('.sheet-p');
    await page.goto(URL);
    await page.goto(URL + hash);
    assert.equal(await page.textContent('.sheet-p'), first, hash + ' is stable');
  }

  // Vocabulary unit level 2 (pairs, word questions, listening)
  await page.goto(URL + '#play-u-3-2');
  await page.waitForSelector('.q-area .inst');
  await playToEnd(page);
  assert.equal((await state(page)).crowns[3], 2);

  // Level 3 with two wrong answers: they come back at the end, and land in the mistakes list
  await page.goto(URL + '#play-u-5-3');
  await page.waitForSelector('.q-area .inst');
  const answeredBefore = (await state(page)).stats.answered;
  const total = await page.evaluate(() => window.__a2.session.total);
  await playToEnd(page, 2);
  s = await state(page);
  assert.equal(s.crowns[5], 3);
  assert.equal(s.stats.answered - answeredBefore, total + 2, 'wrong answers were asked again');
  assert.ok(Object.keys(s.mistakes).length >= 1, 'mistakes saved');

  // Mistakes review clears them
  // Spaced review: a right answer moves a mistake to 1 day later, then 3 days, then clears it
  const dueNow = () => page.evaluate(() => { const t = new Date(); const d = t.getFullYear() + '-' + String(t.getMonth() + 1).padStart(2, '0') + '-' + String(t.getDate()).padStart(2, '0'); return Object.values(window.__a2.state.mistakes).filter(m => m.d <= d).length; });
  const total0 = Object.keys((await state(page)).mistakes).length;
  for (let round = 0; round < 5 && await dueNow(); round++) { await page.goto(URL + '#me'); await page.goto(URL + '#mistakes'); await page.click('[data-act=start]'); await playToEnd(page); }
  s = await state(page);
  assert.equal(await dueNow(), 0, 'nothing due after the review');
  await page.click('.result .btn.ghost[href="#"]');
  await page.waitForSelector('.hero');
  assert.equal(Object.keys(s.mistakes).length, total0, 'reviewed mistakes stay for later days');
  assert.ok(Object.values(s.mistakes).every(m => m.b === 1), 'each moved one box');
  for (const round of [1, 2]) { // time travel: make them due again twice
    await page.evaluate(() => { for (const m of Object.values(window.__a2.state.mistakes)) m.d = '2000-01-01'; });
    while (await dueNow()) { await page.goto(URL + '#me'); await page.goto(URL + '#mistakes'); await page.evaluate(() => { for (const m of Object.values(window.__a2.state.mistakes)) m.d = '2000-01-01'; }); await page.click('[data-act=start]'); await playToEnd(page); }
  }
  assert.equal(Object.keys((await state(page)).mistakes).length, 0, 'three right reviews clear a mistake');

  // Boss: three wrong answers end the battle, then a clean win stamps the city
  await page.goto(URL + '#boss-0');
  await page.click('[data-act=start]');
  for (let i = 0; i < 3; i++) await answer(page, false);
  await page.waitForSelector('text=Bu safar bo\'lmadi');
  await page.click('[data-act=retry]');
  await page.waitForSelector('.hearts');
  assert.equal(await page.evaluate(() => window.__a2.session.bhp), 100);
  await answer(page, true);
  assert.ok(await page.evaluate(() => window.__a2.session.bhp) < 100, 'a right answer hits the boss');
  await playToEnd(page);
  s = await state(page);
  assert.ok(s.boss[0], 'boss beaten');
  assert.ok(s.stats.answered > 0);
  assert.match(await page.textContent('.banner.city'), /Tashkent/);
  assert.match(await page.textContent('.result h1'), /Review 1/);

  // Hint ladder and confidence bet on a practice level
  await page.goto(URL + '#play-u-8-1');
  await page.waitForSelector('.q-area .inst');
  for (let k = 0; k < 20; k++) { // find a multiple-choice question
    if (await page.evaluate(() => window.__a2.q.kind) === 'choice') break;
    await answer(page, true);
  }
  await page.click('[data-act=hint]');
  assert.equal(await page.locator('.opt.gone').count(), 1, 'first hint removes a wrong option');
  await page.click('[data-act=hint]');
  assert.match(await page.textContent('.hint-msg'), /harfi bilan boshlanadi/);
  assert.ok(await page.locator('[data-act=hint]').isDisabled());
  await page.click('[data-act=sure]');
  assert.equal(await page.getAttribute('[data-act=sure]', 'aria-pressed'), 'true');
  const sureBefore = (await state(page)).sure.ok;
  await answer(page, true);
  assert.equal((await state(page)).sure.ok, sureBefore + 1, 'bet counted');
  await playToEnd(page);
  assert.match(await page.textContent('.banner.calib'), /Ishonch garovi/);

  // Story scene: a wrong reply gets coaching and a retry, then the speaking finale
  await page.goto(URL + '#scene-0');
  const lines = await page.evaluate(() => JSON.parse(document.getElementById('a2-data').textContent).scenes[0].lines);
  for (let li = 0; li < 5; li++) {
    await page.waitForFunction(n => document.querySelectorAll('.msg.them').length === n, li + 1);
    if (li === 0) {
      const bad = lines[0][1].findIndex(o => o[1] === 0);
      await page.click(`.replies .opt[data-k="${bad}"]`);
      assert.match(await page.textContent('.coach'), /Grammatik xato/);
    }
    await page.click(`.replies .opt[data-k="${lines[li][1].findIndex(o => o[1] === 1)}"]`);
  }
  await page.waitForSelector('.t45');
  await page.click('[data-act=skip]');
  await page.check('#ck0-0'); await page.check('#ck0-1');
  await page.click('[data-act=done]');
  assert.equal((await state(page)).scenes[0], 2, '4/5 first-try replies = 2 stars');
  assert.match(await page.textContent('.result'), /Sahna yakunlandi/);

  // Progress test: 30 questions, no feedback until the end
  await page.goto(URL + '#exam-1');
  await page.click('[data-act=start]');
  assert.equal(await page.evaluate(() => window.__a2.session.total), 30);
  await playToEnd(page);
  assert.equal((await state(page)).exam[1], 100);
  assert.equal(await page.locator('.answers li').count(), 30);

  // Daily challenge: same questions for everyone today, result saved once
  await page.goto(URL + '#daily');
  await page.click('[data-act=start]');
  const q1 = await page.evaluate(() => [window.__a2.q, ...window.__a2.session.queue].map(q => q.ans).join('|'));
  await playToEnd(page, 1);
  s = await state(page);
  const today = Object.keys(s.daily)[0];
  assert.equal(s.daily[today].c, 9);
  assert.match(await page.inputValue('.share-box'), /9\/10/);
  const other = await ctx.newPage();
  await other.goto(URL + '#daily');
  await other.click('[data-act=start]');
  const q2 = await other.evaluate(() => [window.__a2.q, ...window.__a2.session.queue].map(q => q.ans).join('|'));
  assert.equal(q2, q1, 'daily questions are the same in another tab');
  await other.close();

  // Blitz: instant answers, 60 second timer (fast-forwarded), record saved
  await page.clock.install();
  await page.goto(URL + '#blitz');
  await page.click('[data-act=start]');
  for (let i = 0; i < 6; i++) { await answer(page, true); await page.clock.runFor(400); }
  await page.clock.runFor(61000);
  await page.waitForSelector('.result');
  assert.ok((await state(page)).blitz >= 5, 'blitz record');

  // Quit dialog keeps you in the session or leaves it
  await page.goto(URL + '#play-u-2-1');
  await page.click('[data-act=quit]');
  await page.click('[data-act=stay]');
  assert.equal(await page.locator('.overlay').count(), 0);
  await page.click('[data-act=quit]');
  await page.click('[data-act=leave]');
  await page.waitForSelector('.unit-head');

  // Unit screen: lesson cards and bonus task
  await page.goto(URL + '#u-1');
  await page.click('[data-act=next]');
  assert.equal(await page.locator('.rule:not([hidden])').count(), 1);
  const xpBefore = (await state(page)).xp;
  await page.click('[data-act=task]');
  assert.equal((await state(page)).xp, xpBefore + 20);

  // Home reflects progress
  await page.goto(URL);
  assert.equal(await page.locator('.node.boss.won').count(), 1, 'boss node won');
  assert.match(await page.textContent('.map-h span'), /1 \/ 14/);

  // Profile: badges, settings, export and import, reset
  await page.goto(URL + '#me');
  assert.ok(await page.locator('.badge:not(.locked)').count() >= 5);
  assert.match(await page.textContent('.grid-stats'), /1\/42\s*Unit testlari/);
  await page.click('[data-act=theme][data-v=dark]');
  assert.equal(await page.getAttribute('html', 'data-theme'), 'dark');
  await page.click('[data-act=export]');
  const code = await page.inputValue('#code');
  await page.click('[data-act=reset]');
  await page.click('[data-act=reset]');
  assert.equal((await state(page)).xp, 0, 'reset');
  await page.goto(URL + '#me');
  await page.fill('#code', code);
  await page.click('[data-act=import]');
  assert.ok((await state(page)).xp > 0, 'import restores progress');

  // Word games: memory, scramble, hidden word, survival
  await page.goto(URL + '#games');
  assert.equal(await page.locator('.gcard').count(), 4);
  await page.goto(URL + '#g-memory');
  for (let pair = 0; pair < 6; pair++) {
    const ks = await page.locator(`.mcard[data-p="${pair}"]`).evaluateAll(els => els.map(e => e.dataset.k));
    await page.click(`.mcard[data-k="${ks[0]}"]`); await page.click(`.mcard[data-k="${ks[1]}"]`);
  }
  await page.waitForSelector('.result');
  assert.equal((await state(page)).games.memory.best, 3, '6 moves = 3 stars');
  await page.goto(URL + '#g-scramble');
  for (let w = 0; w < 8; w++) {
    const word = await page.evaluate(() => window.__a2.game.word);
    for (const c of word) await page.keyboard.press(c);
    if (w < 7) await page.waitForFunction(x => window.__a2.game.word !== x, word);
  }
  await page.waitForSelector('.result');
  assert.equal((await state(page)).games.scramble.best, 80, '8 words x 10 points');
  await page.goto(URL + '#g-hidden');
  for (let w = 0; w < 5; w++) {
    const word = await page.evaluate(() => window.__a2.game.word);
    await page.keyboard.press('q'.repeat(word.includes('q') ? 0 : 1) || 'z');
    for (const c of new Set(word.replace(/ /g, ''))) await page.keyboard.press(c);
    await page.waitForSelector('#hnext:not([hidden])');
    await page.keyboard.press('Enter');
  }
  await page.waitForSelector('.result');
  assert.ok((await state(page)).games.hidden.best >= 5 * 25, 'one miss per word leaves 5 lives');
  await page.goto(URL + '#g-survival');
  await page.click('[data-act=start]');
  await answer(page, true); await answer(page, true);
  for (let i = 0; i < 3; i++) await answer(page, false);
  await page.waitForSelector('.result');
  assert.equal((await state(page)).games.survival.best, 2);

  // Streak freeze fills one missed day
  await page.evaluate(() => { const S = window.__a2.state, d = new Date(); d.setDate(d.getDate() - 2); const k = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
    S.days = { [k]: 60 }; S.freeze = 1; localStorage.setItem('destA2.v3', JSON.stringify(S)); });
  await page.goto(URL + '#me'); await page.goto(URL); await page.reload();
  s = await state(page);
  assert.equal(s.freeze, 0, 'freeze used');
  assert.equal(Object.keys(s.days).length, 2, 'yesterday filled');
  assert.match(await page.textContent('.chip.streak'), /2/);

  // Phone width: no sideways scrolling on any screen
  const phone = await ctx.newPage();
  phone.on('pageerror', e => errors.push(e.message));
  await phone.setViewportSize({ width: 360, height: 740 });
  for (const hash of ['', '#u-16', '#u-3', '#play-u-16-3', '#play-u-3-1', '#boss-4', '#blitz', '#daily', '#mistakes', '#me', '#exam-2', '#test-u-7', '#print-u-12', '#print-p-1', '#scene-5', '#play-u-9-3', '#games', '#g-memory', '#g-scramble', '#g-hidden']) {
    await phone.goto(URL + hash);
    await phone.waitForTimeout(100);
    const [sw, w] = await phone.evaluate(() => [document.documentElement.scrollWidth, innerWidth]);
    assert.ok(sw <= w, `${hash || 'home'} scrolls sideways on a phone (${sw} > ${w})`);
  }
  assert.deepEqual(errors, [], 'no page errors');
  await browser.close();
  console.log('smoke test passed: all modes played');
})().catch(e => { console.error(e); process.exit(1); });

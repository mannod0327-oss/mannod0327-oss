// End-to-end smoke test for the game: plays every mode in a real browser and checks the saved progress.
// Run after `python build.py`:  node tests/smoke.js   (needs the `playwright` npm package)
const path = require('path');
const assert = require('assert');
const { chromium } = require('playwright');

const URL = 'file://' + path.resolve(__dirname, '..', 'html', 'index.html');
const state = page => page.evaluate(() => JSON.parse(JSON.stringify(window.__a2.state)));

// Answer the question on screen, right or wrong, the way a learner would (click / type / tap tiles).
async function answer(page, right = true) {
  const q = await page.evaluate(() => { const q = window.__a2.q; return q && { kind: q.kind, ans: q.ans, opts: q.opts, accept: q.accept, words: q.words, pairs: q.pairs }; });
  if (!q) return false;
  const instant = await page.evaluate(() => !!window.__a2.session.instant);
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
  } else if (q.kind === 'pairs') {
    for (let k = 0; k < q.pairs.length; k++) {
      await page.click(`.pair[data-side=en][data-k="${k}"]`);
      await page.click(`.pair[data-side=uz][data-k="${k}"]`);
    }
  }
  if (instant) { await page.waitForTimeout(right ? 380 : 980); return true; }
  if (q.kind !== 'pairs') await page.click('[data-act=check]');
  await page.waitForSelector('.play-foot.ok, .play-foot.bad');
  if (q.kind === 'order' && right) assert.ok(await page.locator('.play-foot.ok').count(), 'order accepted: ' + q.ans);
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
  assert.equal(await page.locator('.node').count(), 42 + 14 + 2, '42 units, 14 bosses, 2 exams on the map');

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
  await page.goto(URL + '#mistakes');
  await page.click('[data-act=start]');
  await playToEnd(page);
  assert.equal(Object.keys((await state(page)).mistakes).length, 0, 'mistakes fixed');

  // Boss: three wrong answers end the battle, then a clean win stamps the city
  await page.goto(URL + '#boss-0');
  await page.click('[data-act=start]');
  for (let i = 0; i < 3; i++) await answer(page, false);
  await page.waitForSelector('text=Bu safar bo\'lmadi');
  await page.click('[data-act=retry]');
  await page.waitForSelector('.hearts');
  await playToEnd(page);
  s = await state(page);
  assert.ok(s.boss[0], 'boss beaten');
  assert.match(await page.textContent('.banner.city'), /Tashkent/);

  // Airport exam
  await page.goto(URL + '#exam-1');
  await page.click('[data-act=start]');
  await playToEnd(page);
  assert.ok((await state(page)).exam[1] >= 70);

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
  assert.ok(await page.locator('.badge:not(.locked)').count() >= 4);
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

  // Phone width: no sideways scrolling on any screen
  const phone = await ctx.newPage();
  phone.on('pageerror', e => errors.push(e.message));
  await phone.setViewportSize({ width: 360, height: 740 });
  for (const hash of ['', '#u-16', '#u-3', '#play-u-16-3', '#play-u-3-1', '#boss-4', '#blitz', '#daily', '#mistakes', '#me', '#exam-2']) {
    await phone.goto(URL + hash);
    await phone.waitForTimeout(100);
    const [sw, w] = await phone.evaluate(() => [document.documentElement.scrollWidth, innerWidth]);
    assert.ok(sw <= w, `${hash || 'home'} scrolls sideways on a phone (${sw} > ${w})`);
  }
  assert.deepEqual(errors, [], 'no page errors');
  await browser.close();
  console.log('smoke test passed: all modes played');
})().catch(e => { console.error(e); process.exit(1); });

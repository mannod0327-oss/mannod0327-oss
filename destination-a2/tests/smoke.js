// End-to-end smoke test for the built site: plays every kind of exercise and game in a real browser.
// Run after `python build.py`:  node tests/smoke.js   (needs the `playwright` npm package)
const path = require('path');
const fs = require('fs');
const assert = require('assert');
const { chromium } = require('playwright');

const DIR = path.resolve(__dirname, '..', 'html');
const url = f => 'file://' + path.join(DIR, f);
const store = page => page.evaluate(() => JSON.parse(localStorage.getItem('destA2.v1') || '{}'));

async function answerTest(page, sel) {
  const n = await page.locator(`${sel} li.q`).count();
  await page.click(`${sel} .step-count`); // move focus out of any text box so the number keys reach the test
  for (let i = 0; i < n; i++) {
    const k = await page.locator(`${sel} li.q.cur input`).evaluateAll(els => els.findIndex(e => e.value === '1'));
    await page.keyboard.press(String(k + 1));
    await page.waitForTimeout(450);
  }
  await page.click(`${sel} [data-act=finish]`);
}

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  // Test the offline case: web fonts blocked, so layouts must hold with fallback fonts
  await ctx.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
  const errors = [];
  ctx.on('page', p => p.on('pageerror', e => errors.push(p.url() + ': ' + e.message)));
  const page = await ctx.newPage();
  page.on('pageerror', e => errors.push(page.url() + ': ' + e.message));

  // Grammar unit: instant multiple choice, gap fill with Enter, test stepper, word order, task
  await page.goto(url('unit-01.html'));
  for (const li of await page.locator('#ex1 li.q').all()) await li.locator('input[value="1"]').check();
  assert.equal(await page.locator('#ex1 li.q.ok').count(), 6, 'exercise A all correct');
  assert.equal((await page.textContent('#ex1 .live')).trim(), '6 / 6');
  assert.match(await page.textContent('#ex1 .blank'), /plays/, 'blank filled with the answer');

  for (const inp of await page.locator('#ex2 input[type=text]').all()) {
    await inp.fill(JSON.parse(await inp.getAttribute('data-a'))[0]);
    await inp.press('Enter');
  }
  assert.equal(await page.locator('#ex2 li.q.ok').count(), 6, 'exercise B all correct');
  await page.fill('#ex3 li.q >> nth=0 >> input', 'wrong');
  await page.click('#ex3 [data-act=check]');
  assert.equal(await page.locator('#ex3 li.q.bad').count(), 6, 'exercise C unanswered/wrong marked');
  assert.match(await page.textContent('#ex3 .fix'), /Answer:/);
  await page.click('#ex3 [data-act=reset]');
  assert.equal(await page.locator('#ex3 li.q.bad').count(), 0, 'reset clears marks');

  assert.ok(await page.locator('#test').evaluate(e => e.classList.contains('stepping')), 'test starts one question at a time');
  assert.equal(await page.locator('#test li.q:visible').count(), 1);
  await answerTest(page, '#test');
  await page.waitForSelector('#test .result .stamp.big:not(.empty)');
  assert.match(await page.textContent('#test .res-score'), /10 \/ 10/);

  const sents = JSON.parse(await page.getAttribute('#order', 'data-s'));
  for (const s of sents) {
    for (const w of s.split(' ')) {
      const i = await page.locator('#order .ord-bank .tile').evaluateAll((els, w) => els.findIndex(e => e.textContent === w), w);
      await page.locator('#order .ord-bank .tile').nth(i).click();
    }
    assert.ok(await page.locator('#order .ord-line.ok').count(), 'sentence accepted: ' + s);
    await page.click('#order [data-ord=next]');
  }
  assert.match(await page.textContent('#order .mini-result'), /5 \/ 5/);

  await page.fill('#task textarea', 'There is a big park in my town.');
  assert.match(await page.textContent('#task .wc'), /8 words/);
  await page.click('#task [data-act=done]');

  let s = await store(page);
  const u1 = s.p['unit-01.html'];
  assert.deepEqual([u1.ex1.ok, u1.ex2.ok, u1.test.ok, u1.order.ok, u1.task.ok], [6, 6, 10, 5, 1], 'progress saved');
  assert.ok(s.xp >= 270, 'xp counted');
  assert.equal(s.drafts['unit-01.html'], 'There is a big park in my town.');
  assert.equal(await page.locator('.route a.done').count(), 6, 'route stations ticked');

  // Replaying must not farm XP
  const xp = s.xp;
  await page.click('#test [data-act=reset]');
  await answerTest(page, '#test');
  assert.equal((await store(page)).xp, xp, 'no extra XP for a repeat score');

  // Unanswered test warns first
  await page.click('#test [data-act=reset]');
  await page.click('#test [data-act=finish]');
  assert.match(await page.textContent('#test .score'), /10 questions are not answered/);

  // Vocabulary unit: flashcards and match
  await page.goto(url('unit-03.html'));
  const words = JSON.parse(await page.getAttribute('#words', 'data-w'));
  await page.click('#words .flash');
  assert.ok(await page.locator('#words .flash.flipped').count(), 'card flips');
  for (let i = 0; i < words.length; i++) await page.click('#words [data-fc=know]');
  assert.match(await page.textContent('#words [data-panel=cards]'), /whole deck/);
  await page.click('#words [data-tab=match]');
  await page.click('#words [data-m=start]');
  for (let r = 0; r < Math.ceil(words.length / 5); r++) {
    const ks = await page.locator('#words .m-item[data-side=en]').evaluateAll(els => els.map(e => e.dataset.k));
    for (const k of ks) {
      await page.click(`#words .m-item[data-side=en][data-k="${k}"]`);
      await page.click(`#words .m-item[data-side=uz][data-k="${k}"]`);
    }
    await page.waitForTimeout(450);
  }
  assert.match(await page.textContent('#words [data-panel=match] .mini-result'), /No mistakes/);
  assert.equal((await store(page)).p['unit-03.html'].match.ok, words.length);

  // Review: part 1 stepper + part 2 gaps
  await page.goto(url('review-01.html'));
  await answerTest(page, '#p1');
  await page.waitForSelector('#p1 .result');
  for (const inp of await page.locator('#p2 input[type=text]').all()) await inp.fill(JSON.parse(await inp.getAttribute('data-a'))[0]);
  await page.click('#p2 [data-act=check]');
  assert.equal(await page.locator('#p2 li.q.bad').count(), 0);

  // Index: passport, stamps, filters, search, continue link
  await page.goto(url('index.html'));
  assert.equal(await page.textContent('#st-stamps'), '2');
  assert.equal(await page.textContent('#st-total'), '58');
  assert.equal(await page.locator('.tk.stamped').count(), 2);
  assert.match(await page.textContent('#continue'), /Continue: Unit 4/);
  await page.click('.chip-f[data-f=v]');
  assert.equal(await page.locator('.tk:visible').count(), 14, '14 vocabulary units');
  await page.click('.chip-f[data-f=all]');
  await page.fill('#q', 'past simple');
  assert.equal(await page.locator('.tk:visible').count(), 2);
  await page.fill('#q', 'zzzz');
  assert.ok(await page.locator('#empty').isVisible());
  await page.click('[data-act=theme]');
  assert.ok(['dark', 'light'].includes(await page.getAttribute('html', 'data-theme')));

  // Every page: no script errors, no sideways scroll on a phone
  const phone = await ctx.newPage();
  await phone.setViewportSize({ width: 375, height: 800 });
  for (const f of fs.readdirSync(DIR).filter(f => f.endsWith('.html'))) {
    await phone.goto(url(f));
    const [sw, w, wide] = await phone.evaluate(() => [document.documentElement.scrollWidth, innerWidth,
      [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > innerWidth + 1).slice(0, 5)
        .map(e => e.tagName.toLowerCase() + '.' + e.className)]);
    assert.ok(sw <= w, `${f} scrolls sideways on a phone (${sw} > ${w}): ${wide.join(', ')}`);
  }
  assert.deepEqual(errors, [], 'no page errors');
  await browser.close();
  console.log('smoke test passed: 59 pages checked');
})().catch(e => { console.error(e); process.exit(1); });

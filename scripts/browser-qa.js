async (page) => {
  const base = 'http://127.0.0.1:8765/portfolio-dist/';
  const pages = ['index.html', 'ventilation/index.html', 'furniture/index.html',
    'furniture/services.html', 'furniture/portfolio.html', 'furniture/contacts.html',
    'autoservice/index.html'];
  const errors = [];
  const results = [];
  const checks = [];
  const check = (condition, message) => {
    checks.push({ message, passed: Boolean(condition) });
    if (!condition) errors.push(message);
  };
  page.on('pageerror', (error) => errors.push(`JS: ${error.message}`));
  page.on('console', (message) => {
    if (message.type() === 'error') errors.push(`Console: ${message.text()}`);
  });
  page.on('response', (response) => {
    if (response.status() >= 400) errors.push(`HTTP ${response.status()}: ${response.url()}`);
  });
  page.on('request', (request) => {
    if (!request.url().startsWith('http://127.0.0.1:8765/')) errors.push(`External request: ${request.url()}`);
    if (request.method() !== 'GET') errors.push(`Unexpected request method: ${request.method()}`);
  });

  for (const name of pages) {
    for (const width of [360, 390, 768, 1440]) {
      await page.setViewportSize({ width, height: 1000 });
      const response = await page.goto(base + name);
      for (const image of await page.locator('img:visible').all()) {
        await image.scrollIntoViewIfNeeded();
        await image.evaluate((element) => element.decode());
      }
      await page.evaluate(() => window.scrollTo(0, 0));
      const state = await page.evaluate(() => ({
        overflow: document.documentElement.scrollWidth > innerWidth + 1,
        broken: [...document.images].filter((image) => !image.complete || image.naturalWidth === 0).map((image) => image.src),
        h1: document.querySelector('h1').getBoundingClientRect().width,
        forms: document.querySelectorAll('form,input,textarea').length,
        notice: document.querySelector('.demo-notice').getBoundingClientRect(),
        storage: localStorage.length + sessionStorage.length,
      }));
      check(response.status() === 200, `${name}/${width}: HTTP 200`);
      check(!state.overflow, `${name}/${width}: no horizontal overflow`);
      check(state.broken.length === 0, `${name}/${width}: images loaded`);
      check(state.h1 > 100 && state.forms === 0, `${name}/${width}: styled page, no data fields`);
      check(state.storage === 0, `${name}/${width}: no browser storage`);
      check(state.notice.y >= 0, `${name}/${width}: notice visible`);

      const menu = page.locator('[data-menu-toggle]');
      if (await menu.count()) {
        check(await menu.isVisible() === (width < 761), `${name}/${width}: correct menu mode`);
        if (width < 761) {
          await menu.click();
          check(await menu.getAttribute('aria-expanded') === 'true' && await page.locator('#navigation').isVisible(), `${name}/${width}: menu opens`);
          await page.keyboard.press('Escape');
          check(await menu.getAttribute('aria-expanded') === 'false' && await menu.evaluate((element) => document.activeElement === element), `${name}/${width}: Escape closes menu and restores focus`);
          await menu.click();
          await page.locator('#navigation a').first().click();
          check(await menu.getAttribute('aria-expanded') === 'false', `${name}/${width}: navigation dismisses menu`);
          await page.goto(base + name);
        }
      }
      if (width === 390 || width === 1440) {
        await page.screenshot({ path: `qa/screenshots/${name.replaceAll('/', '-').replace('.html', '')}-${width}.png`, fullPage: true });
      }
      results.push({ page: name, width, ...state });
    }
  }

  await page.setViewportSize({ width: 390, height: 900 });
  for (const name of pages.filter((name) => name !== 'index.html')) {
    await page.goto(base + name);
    const buttons = page.locator('[data-demo]');
    for (let i = 0; i < await buttons.count(); i += 1) {
      const button = buttons.nth(i);
      if (!await button.isVisible()) continue;
      await button.click();
      check(await page.locator('#demo-dialog').evaluate((dialog) => dialog.open), `${name}/CTA-${i}: opens modal`);
      check((await page.locator('#demo-dialog').innerText()).includes('Это демонстрационный сайт, заявки не отправляются'), `${name}/CTA-${i}: disclaimer`);
      await page.keyboard.press('Tab');
      check(await page.evaluate(() => document.querySelector('#demo-dialog').contains(document.activeElement)), `${name}/CTA-${i}: focus stays inside`);
      await page.keyboard.press('Escape');
      check(!await page.locator('#demo-dialog').evaluate((dialog) => dialog.open) && await button.evaluate((element) => document.activeElement === element), `${name}/CTA-${i}: Escape and focus return`);
    }
    const questions = page.locator('details');
    for (let i = 0; i < await questions.count(); i += 1) {
      await questions.nth(i).locator('summary').click();
      check(await questions.nth(i).evaluate((detail) => detail.open), `${name}/FAQ-${i}: opens`);
    }
  }

  await page.goto(base + 'furniture/portfolio.html');
  const galleryButtons = page.locator('[data-gallery]');
  for (let i = 0; i < await galleryButtons.count(); i += 1) {
    await galleryButtons.nth(i).click();
    check(await page.locator('[data-gallery-position]').innerText() === `${i + 1} из 4`, `gallery/${i}: correct item`);
    await page.locator('[data-next]').click();
    check(await page.locator('[data-gallery-position]').innerText() === `${(i + 1) % 4 + 1} из 4`, `gallery/${i}: next and wrap`);
    await page.keyboard.press('ArrowLeft');
    check(await page.locator('[data-gallery-position]').innerText() === `${i + 1} из 4`, `gallery/${i}: keyboard previous`);
    await page.locator('#gallery-dialog [data-close]').click();
    check(await galleryButtons.nth(i).evaluate((element) => document.activeElement === element), `gallery/${i}: close restores focus`);
  }

  await page.goto(base + 'autoservice/');
  for (const [category, count] of [['wheels', 5], ['maintenance', 1], ['all', 6]]) {
    await page.locator(`[data-filter="${category}"]`).click();
    check(await page.locator('[data-category]:visible').count() === count, `picker/${category}: ${count} results`);
    check(await page.locator(`[data-filter="${category}"]`).getAttribute('aria-pressed') === 'true', `picker/${category}: selected state`);
  }
  await page.emulateMedia({ reducedMotion: 'reduce' });
  check(await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior === 'auto'), 'reduced motion: no smooth scrolling');
  await page.emulateMedia({ reducedMotion: 'no-preference' });

  // Check enlarged text independently from the four normal viewports.
  for (const name of pages) {
    await page.goto(base + name);
    await page.addStyleTag({ content: 'html { font-size: 200%; }' });
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), `${name}: 200% text no horizontal overflow`);
  }
  return { matrix: results, checks, errors, checkCount: checks.length, passed: errors.length === 0 };
}

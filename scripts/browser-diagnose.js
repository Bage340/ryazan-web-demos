async (page) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto('http://127.0.0.1:8765/portfolio-dist/ventilation/');
  await page.locator('[data-demo]').first().click();
  const before = await page.evaluate(() => ({ tag: document.activeElement.tagName, text: document.activeElement.textContent, open: document.querySelector('dialog').open }));
  await page.keyboard.press('Tab');
  const after = await page.evaluate(() => ({ tag: document.activeElement.tagName, dialogContains: document.querySelector('dialog').contains(document.activeElement) }));
  await page.keyboard.press('Escape');
  const overflow = [];
  for (const name of ['index.html', 'ventilation/', 'furniture/', 'furniture/portfolio.html', 'autoservice/']) {
    await page.goto('http://127.0.0.1:8765/portfolio-dist/' + name);
    await page.addStyleTag({ content: 'html { font-size: 200%; }' });
    overflow.push({ page: name, elements: await page.evaluate(() => [...document.querySelectorAll('body *')].filter((e) => e.getBoundingClientRect().right > innerWidth + 1 && e.getBoundingClientRect().width > 0).map((e) => ({ tag: e.tagName, class: e.className, right: e.getBoundingClientRect().right, width: e.getBoundingClientRect().width })).slice(0, 15)) });
  }
  return { before, after, overflow };
}

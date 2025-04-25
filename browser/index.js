import { chromium } from 'playwright';
import fs from 'node:fs';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await browser.newPage();

  await page.goto(process.env.SPIDER_PAGE_URL);
  await page.waitForLoadState();
  const content = await page.content();

  try {
    const url = new URL(process.env.SPIDER_PAGE_URL);
    const fileName = url.hostname.replace(/\./g, '_') + url.pathname.replace(/\/$/, '').replace(/\//g, '_') + '.html';
    fs.writeFileSync(`/tmp/${fileName}`, content);
    console.log(`/tmp/${fileName}`);
  } catch (err) {
    console.error(err);
  } finally {
    await context.close();
    await browser.close();
    process.exit(0);
  }
})();
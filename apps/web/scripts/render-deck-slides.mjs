import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

import { chromium } from "playwright";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const workspaceRoot = path.resolve(__dirname, "..", "..", "..");
const deckPath = path.join(workspaceRoot, "pitch", "deck.html");
const slidesDir = path.join(workspaceRoot, "pitch", "assets", "slides");

async function main() {
  await mkdir(slidesDir, { recursive: true });

  const browser = await chromium.launch({
    channel: "chrome",
    headless: true,
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
  });

  const page = await context.newPage();
  await page.goto(pathToFileURL(deckPath).href, { waitUntil: "networkidle" });
  await page.evaluate(async () => {
    if ("fonts" in document) {
      await document.fonts.ready;
    }
  });

  const slides = page.locator(".slide");
  const slideCount = await slides.count();
  if (!slideCount) {
    throw new Error("No .slide elements found in pitch/deck.html");
  }

  const outputs = [];
  for (let index = 0; index < slideCount; index += 1) {
    const outputPath = path.join(slidesDir, `slide-${index + 1}.png`);
    await slides.nth(index).screenshot({ path: outputPath });
    outputs.push(outputPath);
  }

  await context.close();
  await browser.close();

  console.log(JSON.stringify({ slideCount, outputs }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

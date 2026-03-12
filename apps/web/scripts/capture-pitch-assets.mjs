import { cp, mkdir, rename, rm } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "playwright";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const workspaceRoot = path.resolve(__dirname, "..", "..", "..");
const pitchAssetsDir = path.join(workspaceRoot, "pitch", "assets");
const tempVideoDir = path.join(workspaceRoot, ".tmp", "pitch-video");
const studioUrl = process.env.STUDIO_URL ?? "http://127.0.0.1:3000";

const output = {
  preview: path.join(pitchAssetsDir, "preview.png"),
  landing: path.join(pitchAssetsDir, "full-landing-page.png"),
  run: path.join(pitchAssetsDir, "full-run-page.png"),
  runFocus: path.join(pitchAssetsDir, "run-focus.png"),
  video: path.join(pitchAssetsDir, "demo-walkthrough.webm"),
};

async function ensureDirectories() {
  await mkdir(pitchAssetsDir, { recursive: true });
  await rm(tempVideoDir, { recursive: true, force: true });
  await mkdir(tempVideoDir, { recursive: true });
}

async function scrollShowcase(page) {
  const positions = [0, 780, 1640, 2480, 3320];
  for (const position of positions) {
    await page.evaluate((top) => {
      window.scrollTo({ top, behavior: "smooth" });
    }, position);
    await page.waitForTimeout(900);
  }
  await page.evaluate(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
  await page.waitForTimeout(900);
}

async function main() {
  await ensureDirectories();

  const browser = await chromium.launch({
    channel: "chrome",
    headless: true,
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 960 },
    recordVideo: {
      dir: tempVideoDir,
      size: { width: 1440, height: 960 },
    },
  });

  const page = await context.newPage();

  await page.goto(studioUrl, { waitUntil: "networkidle" });
  await page.waitForTimeout(1200);
  await page.screenshot({ path: output.preview });
  await page.screenshot({ path: output.landing, fullPage: true });

  const recommendedButton = page.getByTestId("load-demo-recommended");
  await recommendedButton.waitFor();
  await recommendedButton.click();

  await page.getByTestId("run-output").waitFor({ timeout: 15000 });
  await page.waitForTimeout(1200);
  await page.getByTestId("run-output").scrollIntoViewIfNeeded();
  await page.waitForTimeout(800);
  await page.screenshot({ path: output.runFocus });
  await page.screenshot({ path: output.run, fullPage: true });
  await scrollShowcase(page);

  const video = page.video();
  await context.close();
  await browser.close();

  if (!video) {
    throw new Error("Playwright did not return a video handle.");
  }

  const recordedVideoPath = await video.path();
  await rm(output.video, { force: true });
  try {
    await rename(recordedVideoPath, output.video);
  } catch {
    await cp(recordedVideoPath, output.video);
  }

  console.log(JSON.stringify(output, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

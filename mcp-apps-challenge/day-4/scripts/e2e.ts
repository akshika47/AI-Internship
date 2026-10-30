// End-to-end check in a real browser, on a copy of the job board: open the test page, send Claude's suggestions,
// click Apply and Skip, Undo, then "I'm done". Checks the CSV and the model panels. Saves screenshots to docs/.
//
// It needs Playwright, which isn't installed by `npm install` (it's big). Either:
//   npm install --no-save playwright-core && npx playwright-core install chromium
// or point PLAYWRIGHT_CORE at a playwright-core you already have:
//   PLAYWRIGHT_CORE=/path/to/node_modules/playwright-core/index.mjs npm run test:e2e
import fs from "node:fs";
import type { Server } from "node:http";
import type { AddressInfo } from "node:net";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { startTestPage } from "../host/serve.js";
import { loadApp, ROOT, startMcpServer } from "../src/server.js";

// playwright-core is optional, so it has no types here.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Playwright = { chromium: { launch(options?: { executablePath?: string }): Promise<any> } };

async function loadPlaywright(): Promise<Playwright> {
  const where = process.env.PLAYWRIGHT_CORE;
  try {
    return where ? await import(pathToFileURL(where).href) : await import("playwright-core" as string);
  } catch {
    console.error(
      "Playwright isn't available. Run: npm install --no-save playwright-core && npx playwright-core install chromium\n" +
        "or set PLAYWRIGHT_CORE to the path of playwright-core/index.mjs.",
    );
    process.exit(1);
  }
}

let failures = 0;
function check(ok: boolean, what: string, got?: unknown) {
  console.log(`  ${ok ? "✓" : "✗"} ${what}${ok ? "" : `  (got: ${JSON.stringify(got)})`}`);
  if (!ok) failures++;
}

const BRIGHTPATH = "Operations & AI Associate, Brightpath Logistics";
const LEDGERLY = "AI Product Analyst, Ledgerly";

const { chromium } = await loadPlaywright();
// CHROMIUM_PATH: use a Chrome or Chromium you already have instead of downloading one.
const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});

try {
  for (const width of [1280, 420]) {
    console.log(`\nAt ${width}px wide`);
    // A fresh copy of the job board each time, so the examples in the repo never change.
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "board-e2e-"));
    fs.cpSync(path.join(ROOT, "examples/job-board"), dir, { recursive: true });
    const csv = () => fs.readFileSync(path.join(dir, "applications.csv"), "utf-8");
    const source = loadApp(dir);
    // Use the usual ports so the screenshots match what you see; if npm start is running, take any free ones.
    const mcp: Server = await startMcpServer(source, 3001).catch(() => startMcpServer(source, 0));
    const mcpUrl = `http://localhost:${(mcp.address() as AddressInfo).port}/mcp`;
    const testPage = await startTestPage({ mcpUrl }).catch(() => startTestPage({ mcpUrl, port: 0, sandboxPort: 0 }));

    const page = await browser.newPage({ viewport: { width, height: 900 } });
    const outside: string[] = [];
    const errors: string[] = [];
    page.on("request", (r: { url(): string }) => { if (!new URL(r.url()).hostname.match(/^(localhost|127\.0\.0\.1|\[::1\])$/) && !r.url().startsWith("data:") && !r.url().startsWith("about:")) outside.push(r.url()); });
    page.on("pageerror", (e: Error) => errors.push(e.message));
    const panel = async (id: string, has: string) => {
      await page.waitForFunction(([i, t]: string[]) => document.getElementById(i)?.textContent?.includes(t), [id, has], { timeout: 5000 }).catch(() => {});
      return page.locator(`#${id}`).innerText();
    };

    try {
      await page.goto(testPage.url);
      await page.locator("#tool option").first().waitFor({ state: "attached" });
      const options = await page.locator("#tool option").allTextContents();
      check(options.join() === "list_items,add_items,review_items (has a view)", "the model sees list_items, add_items and review_items", options);
      check((await page.locator("#hidden-tools").textContent())?.includes("set_status") ?? false, "set_status is listed as app-only");

      await page.locator("#tool").selectOption("review_items");
      check((await page.locator("#input").inputValue()).includes("Apply: 9/10"), "the input is prefilled with the sample suggestions");
      await page.getByRole("button", { name: "Call tool" }).click();
      const view = page.frameLocator("#frame-box iframe").frameLocator("iframe"); // test page -> sandbox -> view
      await view.locator(".item").first().waitFor();
      check((await view.locator(".item").count()) === 6, "the board has 6 cards", await view.locator(".item").count());
      check((await view.locator(".lede").innerText()) === "6 to review · 0 apply · 0 skip", "the counts start at 6 to review");
      const first = view.locator(".item").first();
      check((await first.locator(".suggestion").innerText()).includes("Apply: 9/10"), "Claude's suggestion is on the card");

      await first.getByRole("button", { name: "Apply" }).click();
      check((await panel("context", "Apply (1)")).includes(`Apply (1): ${BRIGHTPATH}.`), "Apply tells the model", await page.locator("#context").innerText());
      check(csv().includes("Hybrid in Leeds.,approved"), "Apply writes approved to the CSV");

      await view.locator(".item", { hasText: LEDGERLY }).getByRole("button", { name: "Skip" }).click();
      check((await panel("context", "Skip (1)")).includes(`Skip (1): ${LEDGERLY}.`), "Skip tells the model");
      check((await view.locator(".lede").innerText()) === "4 to review · 1 apply · 1 skip", "the counts follow", await view.locator(".lede").innerText());

      await view.locator(".item", { hasText: LEDGERLY }).getByRole("button", { name: "Undo" }).click();
      check((await panel("context", "Skip (0)")).includes("Skip (0): none."), "Undo puts it back to review");
      check(csv().includes("fintech.,\n") || csv().includes("in fintech.,\n"), "Undo clears the cell in the CSV", csv());

      await view.getByRole("button", { name: "I'm done: tell Claude" }).click();
      check((await panel("message", "finished")).includes(`I chose "Apply" for: ${BRIGHTPATH}.`), "I'm done sends a chat message", await page.locator("#message").innerText());
      check(fs.existsSync(path.join(dir, "applications.csv.bak")), "the original CSV was backed up");

      await page.waitForTimeout(500); // let the iframe settle at its final height
      const file = `docs/test-page-${width}.png`;
      await page.screenshot({ path: file, fullPage: true });
      console.log(`  saved ${file}`);

      check(outside.length === 0, "nothing was loaded from outside localhost", outside);
      check(errors.length === 0, "no errors in the page", errors);
    } finally {
      await page.close();
      mcp.close();
      testPage.servers.forEach((s) => s.close());
      fs.rmSync(dir, { recursive: true, force: true });
    }
  }
} finally {
  await browser.close();
}

console.log(failures ? `\n${failures} check(s) failed` : "\nAll checks passed");
process.exit(failures ? 1 : 0);

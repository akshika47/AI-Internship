// End-to-end check in a real browser: open the test page, call the tool, click "Show the reasons",
// and check that the model panel updates. Saves screenshots to docs/.
//
// It needs Playwright, which isn't installed by `npm install` (it's big). Either:
//   npm install --no-save playwright-core && npx playwright-core install chromium
// or point PLAYWRIGHT_CORE at a playwright-core you already have:
//   PLAYWRIGHT_CORE=/path/to/node_modules/playwright-core/index.mjs npm run test:e2e
import type { Server } from "node:http";
import type { AddressInfo } from "node:net";
import { pathToFileURL } from "node:url";
import { startTestPage } from "../host/serve.js";
import { startMcpServer } from "../src/server.js";

// playwright-core is optional, so it has no types here.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Playwright = { chromium: { launch(): Promise<any> } };

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

const SUMMARY =
  "Lighting had 92 returns in 2026-Q3 out of 318 items sold (28.9%). Aurora Glass Pendant had the most: 77 of 96 sold (80.2%).";
const CONTEXT = "User looked at return reasons for Aurora Glass Pendant (Lighting, 2026-Q3): damaged 74, wrong size 3.";

const { chromium } = await loadPlaywright();
// Use the usual ports so the screenshots match what you see; if npm start is running, take any free ones.
const mcp: Server = await startMcpServer(3001).catch(() => startMcpServer(0));
const mcpUrl = `http://localhost:${(mcp.address() as AddressInfo).port}/mcp`;
const testPage = await startTestPage({ mcpUrl }).catch(() => startTestPage({ mcpUrl, port: 0, sandboxPort: 0 }));
const browser = await chromium.launch();

try {
  for (const width of [1280, 420]) {
    console.log(`\nAt ${width}px wide`);
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    const outside: string[] = [];
    const errors: string[] = [];
    page.on("request", (r: { url(): string }) => { if (!new URL(r.url()).hostname.match(/^(localhost|127\.0\.0\.1|\[::1\])$/) && !r.url().startsWith("data:") && !r.url().startsWith("about:")) outside.push(r.url()); });
    page.on("pageerror", (e: Error) => errors.push(e.message));

    await page.goto(testPage.url);
    await page.locator("#tool option").first().waitFor({ state: "attached" });
    const options = await page.locator("#tool option").allTextContents();
    check(options.length === 1 && options[0].startsWith("returns_chart"), "the model sees returns_chart only", options);
    check((await page.locator("#hidden-tools").textContent())?.includes("return_reasons") ?? false, "return_reasons is listed as app-only");

    await page.getByRole("button", { name: "Call tool" }).click();
    const view = page.frameLocator("#frame-box iframe").frameLocator("iframe"); // test page -> sandbox -> view
    await view.locator(".row").first().waitFor();
    check((await view.locator(".row").count()) === 6, "the chart has 6 bars", await view.locator(".row").count());
    const top = await view.locator(".row.top").innerText();
    check(top.includes("Aurora Glass Pendant") && top.includes("77 of 96"), "the biggest bar is the Aurora Glass Pendant, highlighted", top);
    check((await view.locator("h1").innerText()) === "92 returns", "the title says 92 returns");
    check((await page.locator("#content").innerText()) === SUMMARY, "the model panel shows the summary sentence");

    await view.getByRole("button", { name: "Show the reasons for Aurora Glass Pendant" }).click();
    await view.locator("#reasons li").first().waitFor();
    const reasons = await view.locator("#reasons li").allInnerTexts();
    check(reasons.length === 2 && /damaged\s+74 of 77/.test(reasons[0]), "the reasons show: damaged 74 of 77", reasons);
    await page.waitForFunction((t: string) => document.getElementById("context")?.textContent === t, CONTEXT, { timeout: 5000 }).catch(() => {});
    check((await page.locator("#context").innerText()) === CONTEXT, "the model panel shows the view's update", await page.locator("#context").innerText());

    // Let the iframe settle at its final height, then take the screenshot.
    await page.waitForTimeout(500);
    const file = `docs/test-page-${width}.png`;
    await page.screenshot({ path: file, fullPage: true });
    console.log(`  saved ${file}`);

    if (width === 1280) {
      // Pick another bar: the button and the model context follow it.
      await view.locator(".row", { hasText: "Brass Desk Lamp" }).click();
      await view.getByRole("button", { name: "Show the reasons for Brass Desk Lamp" }).click();
      await page.waitForFunction(() => document.getElementById("context")?.textContent?.includes("Brass Desk Lamp"), null, { timeout: 5000 }).catch(() => {});
      check((await page.locator("#context").innerText()).startsWith("User looked at return reasons for Brass Desk Lamp"), "picking another bar updates the context");
    }

    check(outside.length === 0, "nothing was loaded from outside localhost", outside);
    check(errors.length === 0, "no errors in the page", errors);
    await page.close();
  }
} finally {
  await browser.close();
  mcp.close();
  testPage.servers.forEach((s) => s.close());
}

console.log(failures ? `\n${failures} check(s) failed` : "\nAll checks passed");
process.exit(failures ? 1 : 0);

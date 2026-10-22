// Loads your API key from the .env file, wherever it sits above this script.
//
// It does what Python's load_dotenv(find_dotenv()) does: start in the folder of the
// script that calls it, look for a .env there, then in the folder above, and so on.
// So the .env in the claude-agent-sdk-challenge folder is found from any day's folder.
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import dotenv from "dotenv";

// The nearest .env at or above `folder`, or undefined if there isn't one.
function findDotenv(folder: string): string | undefined {
  const candidate = join(folder, ".env");
  if (existsSync(candidate)) return candidate;
  const parent = dirname(folder);
  if (parent === folder) return undefined; // reached the top of the disk
  return findDotenv(parent);
}

// Call it as loadEnv(import.meta.url): import.meta.url is the address of your own script.
export function loadEnv(scriptUrl: string): void {
  const path = findDotenv(dirname(fileURLToPath(scriptUrl)));
  if (path === undefined) return; // no .env: the key may already be set in your terminal
  dotenv.config({ path, quiet: true }); // never replaces a key you've already set
}

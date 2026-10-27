// Builds the test page into dist/host/. (sandbox.html is served as it is, so it isn't built.)
import { defineConfig } from "vite";

export default defineConfig({
  build: { outDir: "../dist/host", emptyOutDir: true, target: "es2022" },
  logLevel: "warn",
});

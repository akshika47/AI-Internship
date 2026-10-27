// Builds the view into ONE HTML file (JS and CSS inlined): dist/view/index.html. The MCP server serves that file.
import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

export default defineConfig({
  plugins: [viteSingleFile()],
  build: { outDir: "../dist/view", emptyOutDir: true },
  logLevel: "warn",
});

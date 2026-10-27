// Wrangler bundles these files as plain strings (see "rules" in wrangler.jsonc).
declare module "*.csv" {
  const text: string;
  export default text;
}
declare module "*.html" {
  const text: string;
  export default text;
}

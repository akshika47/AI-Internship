import { Callout, DemoHeader, Panel } from "@/components/ui";

export function Demo6WrapUp() {
  return (
    <div>
      <DemoHeader
        kicker="Section 5"
        title="Wrap-up"
        blurb="Tonight's sections map directly to Assignment 1 pass criteria."
      />

      <Panel title="Section → Assignment criteria">
        <table className="w-full text-left text-[15px]">
          <thead>
            <tr className="border-b border-[var(--line)]">
              <th className="py-2 pr-4">Section</th>
              <th className="py-2">Criterion</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-[var(--line)]">
              <td className="py-3 pr-4">1 — stop_reason + max_tokens</td>
              <td className="py-3">Handle max_tokens explicitly in your agent loop</td>
            </tr>
            <tr className="border-b border-[var(--line)]">
              <td className="py-3 pr-4">2 — tool loop by hand</td>
              <td className="py-3">Branch on stop_reason, not iteration count</td>
            </tr>
            <tr className="border-b border-[var(--line)]">
              <td className="py-3 pr-4">2 — structured tool errors</td>
              <td className="py-3">Return structured errors from tools</td>
            </tr>
            <tr className="border-b border-[var(--line)]">
              <td className="py-3 pr-4">3 — schema + validation + retry</td>
              <td className="py-3">Validate extracted data; retry with error feedback</td>
            </tr>
            <tr>
              <td className="py-3 pr-4">4 — prompt caching</td>
              <td className="py-3">Demonstrate cache write then cache read</td>
            </tr>
          </tbody>
        </table>
      </Panel>

      <div className="mt-6 space-y-4">
        <Callout tone="accent">
          Notebook code lives in <code className="mono">week1_demo.ipynb</code> for
          under-the-hood SDK teaching. This UI is optimized for projection and live
          audience readability.
        </Callout>
        <Callout>
          Starter repo:{" "}
          <span className="mono text-brand-violet">
            github.com/example/claude-architect-bootcamp-starter
          </span>
          <br />
          Community: <span className="mono">#claude-architect-bootcamp</span>
        </Callout>
      </div>
    </div>
  );
}

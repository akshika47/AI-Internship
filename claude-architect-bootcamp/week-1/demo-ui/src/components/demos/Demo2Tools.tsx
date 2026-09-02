"use client";

import { useState } from "react";
import {
  ApiMessage,
  Button,
  Callout,
  Claim,
  DemoHeader,
  Loading,
  Panel,
  ResponseViewer,
} from "@/components/ui";
import { formatToolResult } from "@/lib/tools";

type AgentIteration = {
  iteration: number;
  stop_reason: string;
  tool_calls?: { name: string; input: Record<string, string>; result: unknown }[];
  final_answer?: string;
};

export function Demo2Tools() {
  const [singleLoading, setSingleLoading] = useState(false);
  const [single, setSingle] = useState<ApiMessage | null>(null);
  const [agentLoading, setAgentLoading] = useState(false);
  const [trace, setTrace] = useState<AgentIteration[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function runSingle() {
    setSingleLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/tools/single", { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Request failed");
      setSingle(data.message);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setSingleLoading(false);
    }
  }

  async function runAgent() {
    setAgentLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/tools/agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message:
            "If I buy 150 shares of NVIDIA at the current price, what will it cost me in total?",
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Request failed");
      setTrace(data.trace);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setAgentLoading(false);
    }
  }

  return (
    <div>
      <DemoHeader
        kicker="Section 2"
        title="The tool calling loop, by hand"
        blurb="Claude never runs code. It asks — your runtime executes."
      />

      <Claim>
        Claim: When tools are available, Claude can respond with{" "}
        <code className="mono">stop_reason: tool_use</code> instead of text.
      </Claim>

      <Button onClick={runSingle} disabled={singleLoading || agentLoading}>
        Run single tool call — &quot;What is NVIDIA&apos;s stock price?&quot;
      </Button>

      {error ? <div className="mt-4"><Callout tone="warn">{error}</Callout></div> : null}
      {singleLoading ? <div className="mt-4"><Loading /></div> : null}
      {single ? (
        <div className="mt-6 space-y-4">
          <ResponseViewer message={single} />
          <Callout tone="accent">
            Claude never runs code. It <strong>ASKS</strong>. Your runtime executes.
          </Callout>
        </div>
      ) : null}

      <hr className="my-10 border-[var(--line)]" />

      <Claim>
        Claim: A production agent loop branches on{" "}
        <code className="mono">stop_reason</code>, not iteration count or string
        matching.
      </Claim>

      <Button
        variant="secondary"
        onClick={runAgent}
        disabled={singleLoading || agentLoading}
      >
        Run full agent loop — 150 shares of NVDA
      </Button>

      {agentLoading ? <div className="mt-4"><Loading label="Running agent loop…" /></div> : null}
      {trace ? (
        <div className="mt-6 space-y-4">
          {trace.map((step) => (
            <Panel key={step.iteration} tone={step.final_answer ? "ok" : "accent"}>
              <p className="mono text-base font-semibold text-brand-ink">
                === ITERATION {step.iteration} === stop_reason: {step.stop_reason}
              </p>
              {step.tool_calls?.map((tc, i) => (
                <p key={i} className="mt-2 text-lg text-brand-ink">
                  Claude called:{" "}
                  <code className="mono">
                    {tc.name}({JSON.stringify(tc.input)})
                  </code>{" "}
                  | returned: {formatToolResult(tc.name, tc.result)}
                </p>
              ))}
              {step.final_answer ? (
                <p className="mt-3 text-lg leading-relaxed text-brand-ink">
                  {step.final_answer}
                </p>
              ) : null}
            </Panel>
          ))}
        </div>
      ) : null}
    </div>
  );
}

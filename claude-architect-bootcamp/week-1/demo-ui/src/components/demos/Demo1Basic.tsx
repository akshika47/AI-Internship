"use client";

import { useState } from "react";
import {
  ApiMessage,
  Button,
  Callout,
  Claim,
  DemoHeader,
  Loading,
  ResponseViewer,
} from "@/components/ui";

export function Demo1Basic() {
  const [loading, setLoading] = useState<"full" | "truncated" | null>(null);
  const [full, setFull] = useState<ApiMessage | null>(null);
  const [truncated, setTruncated] = useState<ApiMessage | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run(variant: "full" | "truncated") {
    setLoading(variant);
    setError(null);
    try {
      const res = await fetch("/api/basic", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ variant }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Request failed");
      if (variant === "full") setFull(data.message);
      else setTruncated(data.message);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div>
      <DemoHeader
        kicker="Section 1"
        title="First call + reading the raw response"
        blurb="The API returns a structured object — content blocks, stop_reason, and usage. Not just text."
      />

      <Claim>
        Claim: A normal <code className="mono">messages.create</code> call returns
        content blocks, a stop reason, and token usage.
      </Claim>

      <div className="mb-6 flex flex-wrap gap-3">
        <Button onClick={() => run("full")} disabled={loading !== null}>
          Run — max_tokens=1024
        </Button>
        <Button
          variant="secondary"
          onClick={() => run("truncated")}
          disabled={loading !== null}
        >
          Run — max_tokens=50 (truncated)
        </Button>
      </div>

      {error ? <Callout tone="warn">{error}</Callout> : null}
      {loading === "full" ? <Loading /> : null}
      {full ? (
        <>
          <ResponseViewer message={full} />
          <Callout tone="ok">
            <code className="mono">content</code> is a list of blocks ·{" "}
            <code className="mono">stop_reason</code> is{" "}
            <strong>end_turn</strong> · check usage numbers
          </Callout>
        </>
      ) : null}

      {loading === "truncated" ? <Loading /> : null}
      {truncated ? (
        <>
          <div className="mt-8">
            <ResponseViewer message={truncated} />
          </div>
          <Callout tone="warn">
            In an agent loop, unhandled <code className="mono">max_tokens</code> =
            silent data corruption. Assignment pass criterion #1.
          </Callout>
        </>
      ) : null}
    </div>
  );
}

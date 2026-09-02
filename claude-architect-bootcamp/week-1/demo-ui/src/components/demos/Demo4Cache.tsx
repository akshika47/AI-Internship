"use client";

import { useState } from "react";
import {
  ApiMessage,
  Button,
  Callout,
  Claim,
  DemoHeader,
  JsonBlock,
  Loading,
  Panel,
} from "@/components/ui";

export function Demo4Cache() {
  const [loading, setLoading] = useState<"write" | "read" | "both" | null>(null);
  const [writeUsage, setWriteUsage] = useState<ApiMessage | null>(null);
  const [readUsage, setReadUsage] = useState<ApiMessage | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function runCall(call: "write" | "read") {
    const res = await fetch("/api/cache", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ call }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error ?? "Request failed");
    return data.message as ApiMessage;
  }

  async function run(call: "write" | "read" | "both") {
    setLoading(call);
    setError(null);
    try {
      if (call === "write" || call === "both") {
        const msg = await runCall("write");
        setWriteUsage(msg);
      }
      if (call === "read" || call === "both") {
        const msg = await runCall("read");
        setReadUsage(msg);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div>
      <DemoHeader
        kicker="Section 4"
        title="Prompt caching"
        blurb="Same system prompt across hundreds of agent calls — this is the economics of production agents."
      />

      <Claim>
        Claim: First call with <code className="mono">cache_control</code> writes the
        system prompt to cache — watch{" "}
        <code className="mono">cache_creation_input_tokens</code>.
      </Claim>

      <div className="mb-6 flex flex-wrap gap-3">
        <Button onClick={() => run("write")} disabled={loading !== null}>
          Call 1 — cache write
        </Button>
        <Button
          variant="secondary"
          onClick={() => run("read")}
          disabled={loading !== null}
        >
          Call 2 — cache read
        </Button>
        <Button
          variant="ghost"
          onClick={() => run("both")}
          disabled={loading !== null}
        >
          Run both in sequence
        </Button>
      </div>

      {error ? <Callout tone="warn">{error}</Callout> : null}
      {loading ? <Loading label="Calling Claude with cached system prompt…" /> : null}

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        {writeUsage ? (
          <Panel title="Call 1 — cache write" tone="accent">
            <p className="mb-3 text-base text-brand-ink">
              cache_creation_input_tokens:{" "}
              <strong>{writeUsage.usage.cache_creation_input_tokens ?? 0}</strong>
            </p>
            <JsonBlock data={writeUsage.usage} />
          </Panel>
        ) : null}
        {readUsage ? (
          <Panel title="Call 2 — cache read" tone="ok">
            <p className="mb-3 text-base text-brand-ink">
              cache_read_input_tokens:{" "}
              <strong>{readUsage.usage.cache_read_input_tokens ?? 0}</strong>
              {" · "}
              input_tokens: <strong>{readUsage.usage.input_tokens}</strong>
            </p>
            <JsonBlock data={readUsage.usage} />
          </Panel>
        ) : null}
      </div>

      {writeUsage && readUsage ? (
        <Callout tone="ok">
          Cache reads are ~90% cheaper. Same system prompt across hundreds of agent
          calls = production economics. (Exam: know it exists. Production: know it cold.)
        </Callout>
      ) : null}
    </div>
  );
}

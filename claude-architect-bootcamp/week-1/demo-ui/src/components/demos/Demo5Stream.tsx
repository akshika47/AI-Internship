"use client";

import { useState } from "react";
import {
  Button,
  Callout,
  Claim,
  DemoHeader,
  JsonBlock,
  Loading,
  Panel,
} from "@/components/ui";

export function Demo5Stream() {
  const [streaming, setStreaming] = useState(false);
  const [text, setText] = useState("");
  const [done, setDone] = useState<{
    stop_reason: string;
    usage: Record<string, number>;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setStreaming(true);
    setText("");
    setDone(null);
    setError(null);

    try {
      const res = await fetch("/api/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });

      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done: streamDone, value } = await reader.read();
        if (streamDone) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.trim()) continue;
          const event = JSON.parse(line) as
            | { type: "delta"; text: string }
            | { type: "done"; stop_reason: string; usage: Record<string, number> }
            | { type: "error"; error: string };

          if (event.type === "delta") {
            setText((prev) => prev + event.text);
          } else if (event.type === "done") {
            setDone({ stop_reason: event.stop_reason, usage: event.usage });
          } else if (event.type === "error") {
            throw new Error(event.error);
          }
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Stream failed");
    } finally {
      setStreaming(false);
    }
  }

  return (
    <div>
      <DemoHeader
        kicker="Streaming"
        title="Perceived latency — tokens as they arrive"
        blurb="Notebooks buffer output. For live streaming, use the API stream endpoint or stream_demo.py."
      />

      <Claim>
        Claim: Streaming improves perceived latency — but you still check{" "}
        <code className="mono">stop_reason</code> when the stream completes.
      </Claim>

      <Button onClick={run} disabled={streaming}>
        {streaming ? "Streaming…" : "Start stream"}
      </Button>

      {error ? <div className="mt-4"><Callout tone="warn">{error}</Callout></div> : null}
      {streaming && !text ? <div className="mt-4"><Loading label="Waiting for first token…" /></div> : null}

      {text ? (
        <Panel title="Live output">
          <p className="text-xl leading-relaxed text-brand-ink">{text}</p>
        </Panel>
      ) : null}

      {done ? (
        <div className="mt-4 space-y-4">
          <Callout tone="accent">
            --- stream complete --- · stop_reason:{" "}
            <strong>{done.stop_reason}</strong>
          </Callout>
          <JsonBlock data={done.usage} />
        </div>
      ) : null}
    </div>
  );
}

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
  ResponseViewer,
} from "@/components/ui";
import { INVOICE_TEXT, validateInvoice, type InvoiceData } from "@/lib/invoice";

function getToolInput(message: ApiMessage) {
  const block = message.content.find((b) => b.type === "tool_use");
  if (!block || block.type !== "tool_use") return null;
  return { id: block.id, input: block.input as InvoiceData, content: message.content };
}

export function Demo3Invoice() {
  const [loading, setLoading] = useState<string | null>(null);
  const [extracted, setExtracted] = useState<InvoiceData | null>(null);
  const [extractMsg, setExtractMsg] = useState<ApiMessage | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [retryData, setRetryData] = useState<InvoiceData | null>(null);
  const [toolChoiceResults, setToolChoiceResults] = useState<
    { mode: string; message: ApiMessage }[]
  >([]);
  const [error, setError] = useState<string | null>(null);

  async function extract() {
    setLoading("extract");
    setError(null);
    setValidationError(null);
    setRetryData(null);
    try {
      const res = await fetch("/api/invoice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ step: "extract" }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Request failed");
      setExtractMsg(data.message);
      const tool = getToolInput(data.message);
      if (tool) setExtracted(tool.input);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(null);
    }
  }

  function validate() {
    if (!extracted) return;
    try {
      validateInvoice(extracted);
      setValidationError(null);
    } catch (e) {
      setValidationError(e instanceof Error ? e.message : "Validation failed");
    }
  }

  async function retry() {
    if (!extractMsg || !extracted) return;
    const tool = getToolInput(extractMsg);
    if (!tool) return;

    setLoading("retry");
    setError(null);
    try {
      const res = await fetch("/api/invoice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          step: "retry",
          previous: {
            assistantContent: tool.content,
            toolUseId: tool.id,
            extracted,
          },
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Request failed");
      const retryTool = getToolInput(data.message);
      if (retryTool) setRetryData(retryTool.input);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(null);
    }
  }

  async function runToolChoice() {
    setLoading("tool_choice");
    setError(null);
    setToolChoiceResults([]);
    try {
      const modes = ["auto", "any", "forced"] as const;
      const results: { mode: string; message: ApiMessage }[] = [];
      for (const mode of modes) {
        const res = await fetch("/api/invoice", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ step: "tool_choice", mode }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error ?? "Request failed");
        results.push({ mode, message: data.message });
      }
      setToolChoiceResults(results);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div>
      <DemoHeader
        kicker="Section 3"
        title="Structured output — tool_use + JSON schema"
        blurb="A valid schema can still contain wrong data. Nullable fields stop the model inventing facts."
      />

      <Panel title="Source document">
        <pre className="whitespace-pre-wrap text-base leading-relaxed text-brand-ink">
          {INVOICE_TEXT}
        </pre>
      </Panel>

      <div className="mt-6">
        <Claim>
          Claim: Forced <code className="mono">tool_choice</code> returns
          schema-compliant JSON — including correctly null fields.
        </Claim>
        <Button onClick={extract} disabled={loading !== null}>
          Extract invoice (forced tool)
        </Button>
      </div>

      {error ? <div className="mt-4"><Callout tone="warn">{error}</Callout></div> : null}
      {loading === "extract" ? <div className="mt-4"><Loading /></div> : null}
      {extracted ? (
        <div className="mt-6 space-y-4">
          <JsonBlock data={extracted} />
          <Callout tone="accent">
            <code className="mono">purchase_order: null</code> — no PO in source, so
            the model did not invent one.
          </Callout>
        </div>
      ) : null}

      <div className="mt-8">
        <Claim>
          Claim: Schema validation catches syntax — not semantic errors like a wrong
          total.
        </Claim>
        <Button variant="secondary" onClick={validate} disabled={!extracted}>
          Validate totals
        </Button>
      </div>

      {validationError ? (
        <div className="mt-4 space-y-4">
          <Callout tone="warn">Error: {validationError}</Callout>
          <Callout tone="warn">
            The schema is <strong>VALID</strong>. The data is <strong>WRONG</strong>.
            Schemas kill syntax errors, not semantic errors.
          </Callout>
        </div>
      ) : null}

      <div className="mt-8">
        <Claim>
          Claim: Retry with error feedback flags conflicts instead of silently fixing
          numbers.
        </Claim>
        <Button
          variant="secondary"
          onClick={retry}
          disabled={!extracted || loading !== null}
        >
          Retry with validation error
        </Button>
      </div>

      {loading === "retry" ? <div className="mt-4"><Loading /></div> : null}
      {retryData ? (
        <div className="mt-4">
          <JsonBlock data={retryData} />
          <Callout tone="ok">
            Retries fix format/logic errors; they cannot conjure information absent from
            the source.
          </Callout>
        </div>
      ) : null}

      <div className="mt-8">
        <Claim>
          Claim: <code className="mono">tool_choice</code> mode controls whether Claude
          speaks, must call a tool, or must call a specific tool.
        </Claim>
        <Button
          variant="ghost"
          onClick={runToolChoice}
          disabled={loading !== null}
        >
          Compare auto / any / forced
        </Button>
      </div>

      {loading === "tool_choice" ? <div className="mt-4"><Loading /></div> : null}
      {toolChoiceResults.length > 0 ? (
        <div className="mt-4 space-y-4">
          {toolChoiceResults.map(({ mode, message }) => (
            <Panel key={mode} title={`tool_choice: ${mode}`}>
              <ResponseViewer message={message} />
            </Panel>
          ))}
          <Panel>
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-[var(--line)]">
                  <th className="py-2 pr-4">Mode</th>
                  <th className="py-2">When to use</th>
                </tr>
              </thead>
              <tbody className="text-[15px]">
                <tr className="border-b border-[var(--line)]">
                  <td className="mono py-3 pr-4">auto</td>
                  <td className="py-3">General chat — Claude decides</td>
                </tr>
                <tr className="border-b border-[var(--line)]">
                  <td className="mono py-3 pr-4">any</td>
                  <td className="py-3">Structured output every turn (audit pipelines)</td>
                </tr>
                <tr>
                  <td className="mono py-3 pr-4">tool + name</td>
                  <td className="py-3">Fixed-schema extraction / classification</td>
                </tr>
              </tbody>
            </table>
          </Panel>
        </div>
      ) : null}
    </div>
  );
}

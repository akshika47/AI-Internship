import { NextResponse } from "next/server";
import { callWithRetry, getClient, MODEL, serializeMessage } from "@/lib/anthropic";
import {
  EXTRACT_INVOICE_TOOL,
  EXTRACT_INVOICE_TOOL_V2,
  INVOICE_TEXT,
  VALIDATION_ERROR,
} from "@/lib/invoice";

type ExtractBody = { step: "extract" };
type RetryBody = {
  step: "retry";
  previous: {
    assistantContent: unknown;
    toolUseId: string;
    extracted: Record<string, unknown>;
  };
};
type ToolChoiceBody = { step: "tool_choice"; mode: "auto" | "any" | "forced" };

export async function POST(req: Request) {
  try {
    const body = (await req.json()) as ExtractBody | RetryBody | ToolChoiceBody;
    const client = getClient();

    if (body.step === "extract") {
      const message = await callWithRetry(client, {
        model: MODEL,
        max_tokens: 2048,
        tools: [EXTRACT_INVOICE_TOOL],
        tool_choice: { type: "tool", name: "extract_invoice" },
        messages: [
          {
            role: "user",
            content: `Extract all invoice fields from this document:\n\n${INVOICE_TEXT}`,
          },
        ],
      });
      return NextResponse.json({ message: serializeMessage(message) });
    }

    if (body.step === "retry") {
      const message = await callWithRetry(client, {
        model: MODEL,
        max_tokens: 2048,
        tools: [EXTRACT_INVOICE_TOOL_V2],
        tool_choice: { type: "tool", name: "extract_invoice" },
        messages: [
          {
            role: "user",
            content: `Extract all invoice fields:\n\n${INVOICE_TEXT}`,
          },
          {
            role: "assistant",
            content: body.previous.assistantContent as never,
          },
          {
            role: "user",
            content: [
              {
                type: "tool_result",
                tool_use_id: body.previous.toolUseId,
                content: JSON.stringify(body.previous.extracted),
              },
              { type: "text", text: VALIDATION_ERROR },
            ],
          },
        ],
      });
      return NextResponse.json({ message: serializeMessage(message) });
    }

    const toolChoice =
      body.mode === "auto"
        ? { type: "auto" as const }
        : body.mode === "any"
          ? { type: "any" as const }
          : { type: "tool" as const, name: "extract_invoice" };

    const message = await callWithRetry(client, {
      model: MODEL,
      max_tokens: 512,
      tools: [EXTRACT_INVOICE_TOOL],
      tool_choice: toolChoice,
      messages: [{ role: "user", content: "Thanks, that all looks right!" }],
    });

    return NextResponse.json({
      message: serializeMessage(message),
      mode: body.mode,
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Request failed";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}

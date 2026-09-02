import { NextResponse } from "next/server";
import { callWithRetry, getClient, MODEL, serializeMessage } from "@/lib/anthropic";
import { TOOLS } from "@/lib/tools";

export async function POST() {
  try {
    const client = getClient();
    const message = await callWithRetry(client, {
      model: MODEL,
      max_tokens: 1024,
      tools: TOOLS,
      messages: [{ role: "user", content: "What is NVIDIA's stock price?" }],
    });

    return NextResponse.json({ message: serializeMessage(message) });
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Request failed";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}

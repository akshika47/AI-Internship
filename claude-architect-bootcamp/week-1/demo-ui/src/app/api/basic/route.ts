import { NextResponse } from "next/server";
import { callWithRetry, getClient, MODEL, serializeMessage } from "@/lib/anthropic";

export async function POST(req: Request) {
  try {
    const { variant } = (await req.json()) as { variant?: "full" | "truncated" };
    const client = getClient();
    const max_tokens = variant === "truncated" ? 50 : 1024;

    const message = await callWithRetry(client, {
      model: MODEL,
      max_tokens,
      system: "You are a concise assistant for a financial services company.",
      messages: [
        {
          role: "user",
          content: "What is prompt caching in one paragraph?",
        },
      ],
    });

    return NextResponse.json({
      message: serializeMessage(message),
      retried: false,
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Request failed";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}

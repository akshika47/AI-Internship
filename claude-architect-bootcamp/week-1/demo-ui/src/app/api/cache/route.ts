import { NextResponse } from "next/server";
import { callWithRetry, getClient, MODEL, serializeMessage } from "@/lib/anthropic";
import { SYSTEM_PROMPT } from "@/lib/policy";

const QUESTIONS = {
  write: "A customer wants to return shoes bought 45 days ago. What do I do?",
  read: "What's the escalation threshold for refunds?",
} as const;

export async function POST(req: Request) {
  try {
    const { call } = (await req.json()) as { call: "write" | "read" };
    const client = getClient();

    const message = await callWithRetry(client, {
      model: MODEL,
      max_tokens: 512,
      system: [
        {
          type: "text",
          text: SYSTEM_PROMPT,
          cache_control: { type: "ephemeral" },
        },
      ],
      messages: [{ role: "user", content: QUESTIONS[call] }],
    });

    return NextResponse.json({
      call,
      message: serializeMessage(message),
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Request failed";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}

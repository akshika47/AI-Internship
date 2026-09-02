import { NextResponse } from "next/server";
import { runAgentLoop } from "@/lib/agent-loop";

export async function POST(req: Request) {
  try {
    const body = (await req.json()) as { message?: string };
    const message =
      body.message ??
      "If I buy 150 shares of NVIDIA at the current price, what will it cost me in total?";

    const trace = await runAgentLoop(message);
    return NextResponse.json({ trace });
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Request failed";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}

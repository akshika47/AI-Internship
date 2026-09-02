import { getClient, MODEL } from "@/lib/anthropic";

export async function POST(req: Request) {
  const { question } = (await req.json()) as { question?: string };
  const prompt =
    question?.trim() ||
    "Explain in 3 sentences why streaming improves perceived latency.";

  const client = getClient();
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      try {
        const anthropicStream = client.messages.stream({
          model: MODEL,
          max_tokens: 1024,
          messages: [{ role: "user", content: prompt }],
        });

        for await (const event of anthropicStream) {
          if (
            event.type === "content_block_delta" &&
            event.delta.type === "text_delta"
          ) {
            controller.enqueue(
              encoder.encode(
                JSON.stringify({ type: "delta", text: event.delta.text }) + "\n",
              ),
            );
          }
        }

        const message = await anthropicStream.finalMessage();
        controller.enqueue(
          encoder.encode(
            JSON.stringify({
              type: "done",
              stop_reason: message.stop_reason,
              usage: message.usage,
            }) + "\n",
          ),
        );
        controller.close();
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Stream failed";
        controller.enqueue(
          encoder.encode(JSON.stringify({ type: "error", error: msg }) + "\n"),
        );
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "application/x-ndjson",
      "Cache-Control": "no-cache",
    },
  });
}

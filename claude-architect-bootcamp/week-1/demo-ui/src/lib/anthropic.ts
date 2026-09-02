import Anthropic from "@anthropic-ai/sdk";

export const MODEL = "claude-sonnet-4-6";

export function getClient() {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new Error("ANTHROPIC_API_KEY is not set in .env.local");
  }
  return new Anthropic({ apiKey });
}

export async function callWithRetry(
  client: Anthropic,
  params: Anthropic.MessageCreateParamsNonStreaming,
) {
  try {
    return await client.messages.create(params);
  } catch (err: unknown) {
    const status =
      err && typeof err === "object" && "status" in err
        ? (err as { status?: number }).status
        : undefined;
    if (status === 429 || status === 529) {
      await new Promise((r) => setTimeout(r, 2000));
      return await client.messages.create(params);
    }
    throw err;
  }
}

export type ApiMessage = Anthropic.Message;

export function serializeMessage(message: ApiMessage) {
  return {
    id: message.id,
    type: message.type,
    role: message.role,
    model: message.model,
    stop_reason: message.stop_reason,
    content: message.content,
    usage: message.usage,
  };
}

import type Anthropic from "@anthropic-ai/sdk";
import { callWithRetry, getClient, MODEL, serializeMessage } from "@/lib/anthropic";
import { formatToolResult, runTool, TOOLS } from "@/lib/tools";

export type AgentIteration = {
  iteration: number;
  stop_reason: string;
  tool_calls?: { name: string; input: Record<string, string>; result: unknown }[];
  final_answer?: string;
};

export async function runAgentLoop(userMessage: string): Promise<AgentIteration[]> {
  const client = getClient();
  const messages: Anthropic.MessageParam[] = [
    { role: "user", content: userMessage },
  ];
  const trace: AgentIteration[] = [];
  let iteration = 0;

  while (true) {
    // ANTI-PATTERN: while i < 10 as your stop condition
    // ANTI-PATTERN: if 'done' in response.text
    iteration += 1;
    const resp = await callWithRetry(client, {
      model: MODEL,
      max_tokens: 1024,
      tools: TOOLS,
      messages,
    });

    if (resp.stop_reason === "tool_use") {
      const toolCalls: AgentIteration["tool_calls"] = [];
      const toolResults: Anthropic.ToolResultBlockParam[] = [];

      for (const block of resp.content) {
        if (block.type === "tool_use") {
          const input = block.input as Record<string, string>;
          const result = runTool(block.name, input);
          toolCalls.push({ name: block.name, input, result });
          toolResults.push({
            type: "tool_result",
            tool_use_id: block.id,
            content: JSON.stringify(result),
          });
        }
      }

      trace.push({
        iteration,
        stop_reason: resp.stop_reason,
        tool_calls: toolCalls,
      });

      messages.push({ role: "assistant", content: resp.content });
      messages.push({ role: "user", content: toolResults });
      continue;
    }

    if (resp.stop_reason === "end_turn") {
      const final_answer = resp.content
        .filter((b) => b.type === "text")
        .map((b) => (b.type === "text" ? b.text : ""))
        .join("");

      trace.push({
        iteration,
        stop_reason: resp.stop_reason,
        final_answer,
      });
      return trace;
    }

    if (resp.stop_reason === "max_tokens") {
      throw new Error("Unhandled max_tokens — silent data corruption risk");
    }

    throw new Error(`Unexpected stop_reason: ${resp.stop_reason}`);
  }
}

export { serializeMessage, formatToolResult };

import type Anthropic from "@anthropic-ai/sdk";

const MOCK_PRICES: Record<string, number> = {
  NVDA: 1284.5,
  AAPL: 243.1,
  GOOG: 201.75,
};

const SAFE_EXPR = /^[\d\s+\-*/().]+$/;

export function calculator(expression: string): number {
  const expr = expression.trim();
  if (!SAFE_EXPR.test(expr)) {
    throw new Error("Invalid characters in expression");
  }
  // Demo only — never raw eval() in production; use a vetted math parser instead.
  const result = Function(`"use strict"; return (${expr})`)() as number;
  if (typeof result !== "number" || !Number.isFinite(result)) {
    throw new Error("Invalid expression result");
  }
  return result;
}

export function getStockPrice(ticker: string) {
  const upper = ticker.toUpperCase();
  const price = MOCK_PRICES[upper];
  if (price === undefined) {
    // structured errors, not generic failures — Week 1 assignment criterion #3
    return {
      error: "Unknown ticker",
      errorCategory: "validation",
      isRetryable: false,
    };
  }
  return { ticker: upper, price_usd: price };
}

export const TOOLS: Anthropic.Tool[] = [
  {
    name: "calculator",
    description:
      "Evaluates a basic arithmetic expression. Use for any math the user asks for. Input is a single expression string like '(1420 * 3) + 275'. Supports + - * / ** and parentheses. Do not use for currency conversion or anything requiring live data.",
    input_schema: {
      type: "object",
      properties: {
        expression: {
          type: "string",
          description: "Arithmetic expression to evaluate, e.g. '23 * 41'",
        },
      },
      required: ["expression"],
    },
  },
  {
    name: "get_stock_price",
    description:
      "Returns the latest closing price in USD for a stock ticker symbol, e.g. 'NVDA', 'AAPL'. Use only when the user asks about a specific stock's price. Returns mock data in this demo.",
    input_schema: {
      type: "object",
      properties: {
        ticker: {
          type: "string",
          description: "Stock ticker symbol, uppercase, e.g. 'NVDA'",
        },
      },
      required: ["ticker"],
    },
  },
];

export function runTool(name: string, input: Record<string, string>) {
  if (name === "calculator") {
    return calculator(input.expression);
  }
  if (name === "get_stock_price") {
    return getStockPrice(input.ticker);
  }
  throw new Error(`Unknown tool: ${name}`);
}

export function formatToolResult(name: string, result: unknown): string {
  if (
    name === "get_stock_price" &&
    result &&
    typeof result === "object" &&
    "price_usd" in result
  ) {
    return String((result as { price_usd: number }).price_usd);
  }
  if (typeof result === "number") return String(result);
  return JSON.stringify(result);
}

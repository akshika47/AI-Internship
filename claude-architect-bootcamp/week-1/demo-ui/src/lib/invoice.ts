export const INVOICE_TEXT = `INVOICE #INV-2026-0847
From: Meridian Consulting Ltd
To: Apex Retail Group
Date: 12 August 2026
Line items:
- Strategy workshop facilitation: $4,500
- Market analysis report: $3,200
- Stakeholder interviews (12 sessions): $2,800
Total due: $11,300
Payment terms: Net 30. A late fee of 2% applies after the due date.`;

export const EXTRACT_INVOICE_TOOL = {
  name: "extract_invoice",
  description: "Extract structured fields from an invoice document.",
  input_schema: {
    type: "object" as const,
    properties: {
      invoice_number: { type: "string" },
      vendor: { type: "string" },
      client: { type: "string" },
      invoice_date: { type: "string", description: "ISO 8601 date" },
      line_items: {
        type: "array",
        items: {
          type: "object",
          properties: {
            description: { type: "string" },
            amount_usd: { type: "number" },
          },
          required: ["description", "amount_usd"],
        },
      },
      stated_total_usd: { type: "number" },
      payment_terms: {
        type: "string",
        enum: ["net_15", "net_30", "net_60", "due_on_receipt", "other"],
      },
      payment_terms_detail: {
        type: "string",
        description: "Required if payment_terms is 'other'",
      },
      purchase_order: {
        type: ["string", "null"],
        description: "PO number if present, null if absent — DO NOT invent one",
      },
    },
    required: [
      "invoice_number",
      "vendor",
      "client",
      "invoice_date",
      "line_items",
      "stated_total_usd",
      "payment_terms",
    ],
  },
};

export const EXTRACT_INVOICE_TOOL_V2 = {
  ...EXTRACT_INVOICE_TOOL,
  input_schema: {
    ...EXTRACT_INVOICE_TOOL.input_schema,
    properties: {
      ...EXTRACT_INVOICE_TOOL.input_schema.properties,
      calculated_total_usd: { type: "number" },
      conflict_detected: { type: "boolean" },
    },
    required: [
      ...EXTRACT_INVOICE_TOOL.input_schema.required,
      "calculated_total_usd",
      "conflict_detected",
    ],
  },
};

export type InvoiceData = {
  line_items: { description: string; amount_usd: number }[];
  stated_total_usd: number;
  [key: string]: unknown;
};

export function validateInvoice(data: InvoiceData) {
  const calculated = data.line_items.reduce((sum, item) => sum + item.amount_usd, 0);
  const stated = data.stated_total_usd;
  if (calculated !== stated) {
    throw new Error(
      `line_items sum to ${calculated} but stated_total_usd is ${stated}`,
    );
  }
  return { calculated, stated };
}

export const VALIDATION_ERROR =
  "line_items sum to 10500 but stated_total_usd is 11300 — re-extract and add calculated_total_usd and a conflict_detected flag";

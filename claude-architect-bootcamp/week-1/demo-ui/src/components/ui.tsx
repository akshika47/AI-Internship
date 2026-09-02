import { ReactNode } from "react";

export function SectionLabel({ children }: { children: ReactNode }) {
  return (
    <p className="mono mb-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-brand-violet">
      {children}
    </p>
  );
}

export function DemoHeader({
  kicker,
  title,
  blurb,
}: {
  kicker: string;
  title: string;
  blurb: string;
}) {
  return (
    <header className="mb-8 max-w-3xl">
      <SectionLabel>{kicker}</SectionLabel>
      <h1 className="font-display text-3xl font-extrabold tracking-tight text-brand-ink sm:text-4xl">
        {title}
      </h1>
      <p className="mt-3 text-lg leading-relaxed text-[var(--muted)]">{blurb}</p>
    </header>
  );
}

export function Claim({ children }: { children: ReactNode }) {
  return (
    <p className="mb-4 rounded-lg border border-brand-violet/20 bg-brand-violet-soft px-4 py-3 text-[15px] font-medium text-brand-ink">
      {children}
    </p>
  );
}

export function Panel({
  title,
  children,
  tone = "default",
}: {
  title?: string;
  children: ReactNode;
  tone?: "default" | "accent" | "warn" | "ok" | "danger";
}) {
  const tones = {
    default: "border-[var(--line)] bg-white",
    accent: "border-brand-violet/25 bg-brand-violet-soft/50",
    warn: "border-amber-200 bg-amber-50/80",
    ok: "border-emerald-200 bg-emerald-50/70",
    danger: "border-red-200 bg-red-50/70",
  };
  return (
    <div className={`rounded-2xl border p-5 sm:p-6 ${tones[tone]}`}>
      {title ? (
        <h3 className="mb-4 text-base font-semibold text-brand-ink">{title}</h3>
      ) : null}
      {children}
    </div>
  );
}

export function Button({
  children,
  onClick,
  variant = "primary",
  disabled,
}: {
  children: ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "ghost";
  disabled?: boolean;
}) {
  const styles = {
    primary:
      "bg-brand-orange text-white hover:bg-[#d85618] disabled:bg-orange-300 shadow-sm",
    secondary:
      "bg-white text-brand-ink border border-[var(--line)] hover:bg-slate-50 disabled:opacity-50",
    ghost:
      "bg-transparent text-[var(--muted)] hover:bg-white/80 disabled:opacity-50",
  };
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={`inline-flex items-center justify-center rounded-full px-5 py-2.5 text-sm font-semibold transition ${styles[variant]}`}
    >
      {children}
    </button>
  );
}

export function Callout({
  children,
  tone = "accent",
}: {
  children: ReactNode;
  tone?: "accent" | "warn" | "ok";
}) {
  const tones = {
    accent: "border-brand-violet/30 bg-brand-violet-soft text-brand-ink",
    warn: "border-amber-300 bg-amber-50 text-amber-950",
    ok: "border-emerald-300 bg-emerald-50 text-emerald-950",
  };
  return (
    <div
      className={`rounded-xl border px-4 py-3 text-[15px] leading-relaxed ${tones[tone]}`}
    >
      {children}
    </div>
  );
}

export function JsonBlock({ data }: { data: unknown }) {
  return (
    <pre className="mono max-h-[420px] overflow-auto rounded-xl bg-brand-ink p-4 text-[15px] leading-relaxed text-emerald-300">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}

export type ApiMessage = {
  stop_reason: string | null;
  content: Array<
    | { type: "text"; text: string }
    | { type: "tool_use"; id: string; name: string; input: unknown }
  >;
  usage: Record<string, number>;
};

export function ResponseViewer({ message }: { message: ApiMessage }) {
  return (
    <div className="space-y-4">
      <Panel title="Content blocks">
        {message.content.map((block, i) => (
          <div key={i} className="mb-4 last:mb-0">
            <p className="mono mb-2 text-xs font-semibold uppercase tracking-wide text-brand-violet">
              Block {i + 1} · {block.type}
            </p>
            {block.type === "text" ? (
              <p className="text-lg leading-relaxed text-brand-ink">{block.text}</p>
            ) : (
              <JsonBlock data={{ name: block.name, input: block.input }} />
            )}
          </div>
        ))}
      </Panel>

      <div className="rounded-xl border-2 border-[var(--warn)] bg-orange-50 px-5 py-4">
        <p className="text-sm font-medium text-[var(--muted)]">stop_reason</p>
        <p className="font-display text-3xl font-extrabold text-[var(--warn)]">
          {message.stop_reason ?? "null"}
        </p>
      </div>

      <Panel title="usage">
        <JsonBlock data={message.usage} />
      </Panel>
    </div>
  );
}

export function Loading({ label = "Calling Claude…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-dashed border-brand-violet/30 bg-white px-5 py-8 text-[var(--muted)]">
      <span className="h-2 w-2 animate-pulse rounded-full bg-brand-violet" />
      <span className="text-base">{label}</span>
    </div>
  );
}

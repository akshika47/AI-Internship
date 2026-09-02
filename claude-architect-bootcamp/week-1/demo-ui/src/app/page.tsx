"use client";

import { useState } from "react";
import { Demo1Basic } from "@/components/demos/Demo1Basic";
import { Demo2Tools } from "@/components/demos/Demo2Tools";
import { Demo3Invoice } from "@/components/demos/Demo3Invoice";
import { Demo4Cache } from "@/components/demos/Demo4Cache";
import { Demo5Stream } from "@/components/demos/Demo5Stream";
import { Demo6WrapUp } from "@/components/demos/Demo6WrapUp";

const DEMOS = [
  { id: "1", label: "Raw response", Component: Demo1Basic },
  { id: "2", label: "Tool calling loop", Component: Demo2Tools },
  { id: "3", label: "Structured output", Component: Demo3Invoice },
  { id: "4", label: "Prompt caching", Component: Demo4Cache },
  { id: "5", label: "Streaming", Component: Demo5Stream },
  { id: "6", label: "Wrap-up", Component: Demo6WrapUp },
] as const;

export default function Home() {
  const [active, setActive] = useState<(typeof DEMOS)[number]["id"]>("1");
  const current = DEMOS.find((d) => d.id === active) ?? DEMOS[0];
  const Active = current.Component;

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[280px_1fr]">
      <aside className="border-b border-[var(--line)] bg-white lg:sticky lg:top-0 lg:h-screen lg:border-b-0 lg:border-r">
        <div className="px-5 pb-4 pt-6">
          <p className="mono text-[11px] font-semibold uppercase tracking-[0.16em] text-brand-violet">
            Claude Architect · Week 1
          </p>
          <h1 className="font-display mt-1 text-xl font-extrabold tracking-tight text-brand-ink">
            API Beyond Chat
          </h1>
          <p className="mt-2 text-[13px] leading-snug text-[var(--muted)]">
            Live demo UI — raw Anthropic SDK, no frameworks. API key stays server-side.
          </p>
        </div>

        <nav className="px-3 pb-6" aria-label="Demos">
          <ul className="space-y-0.5">
            {DEMOS.map((d, i) => {
              const on = d.id === active;
              return (
                <li key={d.id}>
                  <button
                    type="button"
                    onClick={() => setActive(d.id)}
                    className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm transition ${
                      on
                        ? "bg-brand-violet-soft font-semibold text-brand-violet"
                        : "text-[var(--muted)] hover:bg-slate-50 hover:text-brand-ink"
                    }`}
                  >
                    <span
                      className={`mono flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-[11px] font-bold ${
                        on
                          ? "bg-brand-violet text-white"
                          : "bg-slate-100 text-slate-500"
                      }`}
                    >
                      {i + 1}
                    </span>
                    {d.label}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="hidden border-t border-[var(--line)] px-5 py-4 text-xs leading-relaxed text-[var(--muted)] lg:block">
          Run <code className="mono text-brand-ink">npm run dev</code> in{" "}
          <code className="mono text-brand-ink">demo-ui/</code>. Set{" "}
          <code className="mono text-brand-ink">ANTHROPIC_API_KEY</code> in{" "}
          <code className="mono text-brand-ink">.env.local</code>.
        </div>
      </aside>

      <main className="px-5 py-8 sm:px-10 lg:px-14 lg:py-12">
        <Active />
      </main>
    </div>
  );
}

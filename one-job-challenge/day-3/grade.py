"""Score an inbox-desk log.csv against the practice inbox answer key.

Usage: python3 grade.py answer-key.md path/to/desk/log.csv
Prints type, urgency and action scores out of 36, and lists every row whose action differs from the key.
Also accepted, as the key's notes say: "flag for Rosa" on an email whose date has passed (02, 09, 23, 24),
and "flag for Rosa" or "draft reply" for the thank-you with the car park charge (27).
"""
import csv, re, sys

key = {}
for line in open(sys.argv[1]):
    m = re.match(r"\|\s*(\d\d)\s*\|\s*`([^`]+)\.md`\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|", line)
    if m:
        key[m.group(2)] = dict(type=m.group(3).strip(), urgency=m.group(4).strip(), action=m.group(5).strip())

ALSO = {"02-open-this-wednesday": {"flag for rosa"}, "09-parking": {"flag for rosa"},
        "23-sunday-rain-forecast": {"flag for rosa"},
        "27-thank-you-family-day": {"flag for rosa", "draft reply"}}

rows = list(csv.DictReader(open(sys.argv[2], newline="")))
ids = [r["id"].strip().removesuffix(".md") for r in rows]
log = {i: r for i, r in zip(ids, rows)}
print(f"key rows {len(key)}, log rows {len(rows)}, unique ids {len(set(ids))}, missing {sorted(set(key) - set(log))}")
score = {"type": 0, "urgency": 0, "action": 0}
for k, v in sorted(key.items()):
    r = log.get(k)
    if not r:
        continue
    for f in score:
        got = r.get(f, "").strip().lower()
        ok = got == v[f].lower() or (f == "action" and got in ALSO.get(k, set()))
        score[f] += ok
        if not ok and f == "action":
            print(f"  {k}: action {r.get(f)!r} vs key {v[f]!r}")
print({f: f"{n}/{len(key)}" for f, n in score.items()})

(function () {
  const cfg = window.WEDVOW_EVENT;
  if (!cfg) {
    console.error("WEDVOW_EVENT missing — load event-config.js first.");
    return;
  }

  const $ = (id) => document.getElementById(id);
  const SESSION_KEY = "wedvow_dash_unlocked_" + (cfg.slug || "demo");

  function toast(msg) {
    const el = $("toast");
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => el.classList.remove("show"), 2600);
  }

  function bindConfig() {
    document.title = `Host dashboard · ${cfg.headline} — ${cfg.brandName || "WedVow"}`;
    $("dashTitle").textContent = `${cfg.honoreeName}'s celebration at a glance`;
    $("dashSubtitle").textContent = `${cfg.dateShort || cfg.dateLabel} · RSVPs stored in this browser only.`;
    $("eventSlug").textContent = cfg.slug;
    $("panelHeading").textContent = `${cfg.headline} — RSVPs`;
    $("pinHint").textContent = cfg.dashboardPin;
  }

  function refreshList() {
    const rows = window.WedVowStorage.getRsvps();
    const s = window.WedVowStorage.stats(rows);
    $("statResponses").textContent = s.responses;
    $("statYes").textContent = s.accepting;
    $("statGuests").textContent = s.guests;

    const list = $("guestList");
    list.replaceChildren();

    if (!rows.length) {
      const empty = document.createElement("div");
      empty.className = "guest-row";
      empty.innerHTML = "<span>No responses yet. Share the invitation and check back here.</span><span>—</span>";
      list.appendChild(empty);
      return;
    }

    rows
      .slice()
      .reverse()
      .forEach((r) => {
        const row = document.createElement("div");
        row.className = "guest-row";

        const left = document.createElement("span");
        const note = r.notes || r.dietary;
        left.innerHTML =
          `<strong>${escapeHtml(r.name)}</strong>` +
          (note ? `<div class="muted">${escapeHtml(note)}</div>` : "");

        const right = document.createElement("span");
        right.className = r.attendance === "yes" ? "status-yes" : "status-no";
        right.textContent =
          r.attendance === "yes" ? `${r.guestCount} guest(s)` : "Declined";

        row.append(left, right);
        list.appendChild(row);
      });
  }

  function escapeHtml(str) {
    return String(str)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function unlock() {
    sessionStorage.setItem(SESSION_KEY, "1");
    $("dashGate").classList.add("hidden");
    $("dashPanel").classList.remove("hidden");
    refreshList();
  }

  function initGate() {
    if (sessionStorage.getItem(SESSION_KEY) === "1") {
      unlock();
    }

    $("pinForm").addEventListener("submit", (e) => {
      e.preventDefault();
      const pin = String(new FormData(e.currentTarget).get("pin") || "").trim();
      if (pin === String(cfg.dashboardPin)) {
        $("pinError").textContent = "";
        unlock();
        toast("Dashboard unlocked");
      } else {
        $("pinError").textContent = "Incorrect PIN. Check event-config.js.";
        $("pinInput").select();
      }
    });
  }

  function initActions() {
    $("exportCsv").addEventListener("click", () => {
      const ok = window.WedVowStorage.downloadCsv(
        `${cfg.slug || "wedvow"}-rsvps.csv`
      );
      toast(ok ? "CSV downloaded" : "No responses to export yet.");
    });

    $("clearData").addEventListener("click", () => {
      if (!window.WedVowStorage.getRsvps().length) {
        toast("Nothing to clear.");
        return;
      }
      if (!confirm("Clear all demo RSVPs from this browser?")) return;
      window.WedVowStorage.clearRsvps();
      refreshList();
      toast("Demo data cleared");
    });
  }

  bindConfig();
  initGate();
  initActions();
})();

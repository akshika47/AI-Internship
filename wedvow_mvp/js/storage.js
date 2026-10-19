(function (global) {
  function storageKey() {
    return (global.WEDVOW_EVENT && global.WEDVOW_EVENT.storageKey) || "wedvow_birthday_rsvps_v1";
  }

  function getRsvps() {
    try {
      return JSON.parse(localStorage.getItem(storageKey()) || "[]");
    } catch {
      return [];
    }
  }

  function saveRsvps(rows) {
    localStorage.setItem(storageKey(), JSON.stringify(rows));
  }

  function addRsvp(row) {
    const rows = getRsvps();
    rows.push(row);
    saveRsvps(rows);
    return rows;
  }

  function clearRsvps() {
    localStorage.removeItem(storageKey());
  }

  function stats(rows) {
    const list = rows || getRsvps();
    const yes = list.filter((r) => r.attendance === "yes");
    return {
      responses: list.length,
      accepting: yes.length,
      declining: list.length - yes.length,
      guests: yes.reduce((sum, r) => sum + Number(r.guestCount || 1), 0),
    };
  }

  function toCsv(rows) {
    const list = rows || getRsvps();
    const escape = (v) => '"' + String(v ?? "").replaceAll('"', '""') + '"';
    const header = ["Name", "Attendance", "Guest count", "Notes", "Submitted at"];
    const body = list.map((r) => [
      r.name,
      r.attendance,
      r.guestCount,
      r.notes || r.dietary || "",
      r.createdAt,
    ]);
    return [header, ...body].map((row) => row.map(escape).join(",")).join("\r\n");
  }

  function downloadCsv(filename) {
    const rows = getRsvps();
    if (!rows.length) return false;
    const blob = new Blob([toCsv(rows)], { type: "text/csv;charset=utf-8;" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename || "wedvow-rsvps.csv";
    a.click();
    URL.revokeObjectURL(a.href);
    return true;
  }

  global.WedVowStorage = {
    getRsvps,
    saveRsvps,
    addRsvp,
    clearRsvps,
    stats,
    toCsv,
    downloadCsv,
  };
})(window);

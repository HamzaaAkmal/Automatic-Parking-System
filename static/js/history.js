async function loadHistory() {
  const body = document.getElementById("historyRows");
  try {
    const response = await fetch("/api/history");
    const rows = await response.json();
    body.innerHTML = rows.length ? rows.map(row => `
      <tr><td>${row.plate}</td><td>${row.entry_time}</td><td>${row.exit_time || "—"}</td>
      <td>Rs. ${row.fee.toFixed(2)}</td><td>${row.status}</td></tr>`).join("")
      : '<tr><td colspan="5">No parking visits recorded yet.</td></tr>';
  } catch {
    body.innerHTML = '<tr><td colspan="5">Could not load parking history.</td></tr>';
  }
}
loadHistory();

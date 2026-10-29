async function loadSales() {
  const [summaryResponse, salesResponse] = await Promise.all([
    fetch("/api/sales/summary"), fetch("/api/sales")
  ]);
  const summary = await summaryResponse.json();
  const sales = await salesResponse.json();
  document.getElementById("salesTotal").textContent = `Rs. ${summary.total_sales.toFixed(2)}`;
  document.getElementById("salesCount").textContent = summary.transactions;
  document.getElementById("salesRows").innerHTML = sales.length ? sales.map(sale => `
    <tr><td>${sale.reference}</td><td>${sale.created_at}</td><td>${sale.status}</td>
    <td>Rs. ${sale.total.toFixed(2)}</td></tr>`).join("")
    : '<tr><td colspan="4">No sales recorded yet.</td></tr>';
}
loadSales().catch(() => {
  document.getElementById("salesRows").innerHTML = '<tr><td colspan="4">Could not load sales.</td></tr>';
});

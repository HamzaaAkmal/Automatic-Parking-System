const products = new Map();
const cart = new Map();
const productSelect = document.getElementById("productSelect");
const cartRows = document.getElementById("cartRows");
const checkoutBtn = document.getElementById("checkoutBtn");

function renderCart() {
  const rows = [...cart.values()];
  cartRows.innerHTML = rows.length ? rows.map(item => `
    <tr><td>${item.name}</td><td>${item.quantity}</td><td>Rs. ${item.price.toFixed(2)}</td>
    <td>Rs. ${(item.price * item.quantity).toFixed(2)}</td></tr>`).join("")
    : '<tr><td colspan="4">No items yet</td></tr>';
  const total = rows.reduce((sum, item) => sum + item.price * item.quantity, 0);
  document.getElementById("cartTotal").textContent = `Rs. ${total.toFixed(2)}`;
  checkoutBtn.disabled = rows.length === 0;
}

async function loadProducts() {
  const response = await fetch("/api/products");
  const items = await response.json();
  items.forEach(item => products.set(item.id, item));
  productSelect.innerHTML = items.map(item =>
    `<option value="${item.id}">${item.name} · Rs. ${item.price.toFixed(2)} · ${item.stock} in stock</option>`
  ).join("");
  if (!items.length) productSelect.innerHTML = '<option value="">No products available</option>';
}

document.getElementById("addItemForm").addEventListener("submit", event => {
  event.preventDefault();
  const item = products.get(Number(productSelect.value));
  const quantity = Number(document.getElementById("quantity").value);
  if (!item || quantity < 1) return;
  const next = (cart.get(item.id)?.quantity || 0) + quantity;
  if (next > item.stock) {
    document.getElementById("posMessage").textContent = `Only ${item.stock} ${item.name} in stock.`;
    return;
  }
  cart.set(item.id, { ...item, quantity: next });
  document.getElementById("posMessage").textContent = "";
  renderCart();
});

checkoutBtn.addEventListener("click", async () => {
  checkoutBtn.disabled = true;
  const response = await fetch("/api/sales", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ payment_method: document.getElementById("paymentMethod").value,
      items: [...cart.values()].map(item => ({ product_id: item.id, quantity: item.quantity })) })
  });
  const result = await response.json();
  if (!response.ok) {
    document.getElementById("posMessage").textContent = result.error || "Sale could not be completed.";
    checkoutBtn.disabled = false;
    return;
  }
  cart.clear();
  renderCart();
  await loadProducts();
  document.getElementById("posMessage").textContent = `Sale ${result.reference} recorded · Rs. ${result.total.toFixed(2)}`;
});

loadProducts().catch(() => {
  productSelect.innerHTML = '<option value="">Could not load products</option>';
  document.getElementById("posMessage").textContent = "Refresh this page to try again.";
});

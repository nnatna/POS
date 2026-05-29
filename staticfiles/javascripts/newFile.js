const { orderItems, renderOrderSidebar } = require("./include");

// ── 1. ADD TO CART ──────────────────────────────────────────
document.addEventListener("click", function (e) {
    const btn = e.target.closest(".add-to-cart");
    if (!btn) return;

    const id = btn.dataset.id;
    const name = btn.dataset.name;
    const price = parseFloat(btn.dataset.price);

    if (orderItems[id]) {
        orderItems[id].quantity += 1;
    } else {
        orderItems[id] = { name, price, quantity: 1 };
    }

    renderOrderSidebar();
});

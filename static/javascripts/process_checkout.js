let cart = [];
window.cart = cart;

// ១. ចាប់យក Event ពេល User ចុចប៊ូតុង Add to Cart (+)
document.addEventListener('click', function(e) {
    if (e.target.closest('.add-to-cart')) {
        const btn = e.target.closest('.add-to-cart');
        const product = {
            id: btn.dataset.id,
            name: btn.dataset.name,
            price: parseFloat(btn.dataset.price),
            discount: parseFloat(btn.dataset.discount) || 0,
            image: btn.dataset.image,
            qty: 1
        };

        addToCart(product);
    }
});

// ២. Function បន្ថែមទំនិញចូលក្នុង Array
function addToCart(product) {
    const existingItem = cart.find(item => item.id === product.id);
    if (existingItem) {
        existingItem.qty += 1;
    } else {
        cart.push(product);
    }
    renderCart();
}

// ៣. Function បង្ហាញទំនិញលើ UI Sidebar
function renderCart() {
    const container = document.getElementById('order-items');
    const subtotalDisplay = document.getElementById('cart-total');
    const discountDisplay = document.getElementById('discount-value');
    const totalItemsDisplay = document.getElementById('total-items-value');
    const totalDisplay = document.getElementById('total-value');

    if (!container || !subtotalDisplay || !discountDisplay || !totalItemsDisplay || !totalDisplay) {
        return;
    }

    if (cart.length === 0) {
        container.innerHTML = '<p class="text-muted text-center mt-3 small">No items yet</p>';
        subtotalDisplay.innerText = '$0.00';
        discountDisplay.innerText = '$0.00';
        totalDisplay.innerText = '$0.00';
        totalItemsDisplay.innerText = '0';
        updateModalSummary();
        return;
    }

    container.innerHTML = '';
    let subtotal = 0;
    let productDiscountTotal = 0;
    let totalQty = 0;

    cart.forEach((item, index) => {
        const itemTotal = item.price * item.qty;
        const itemDiscountPercent = Number(item.discount) || 0;
        const itemDiscount = itemTotal * itemDiscountPercent / 100;
        const itemNetTotal = itemTotal - itemDiscount;
        subtotal += itemTotal;
        productDiscountTotal += itemDiscount;
        totalQty += item.qty;

        container.innerHTML += `
            <div class="d-flex align-items-center mb-3 shadow-sm p-2 rounded border-start border-warning border-4">
                ${item.image 
                    ? `<img src="${item.image}" class="rounded me-2" style="width: 45px; height: 45px; object-fit: cover;">`
                    : `<div class="bg-secondary text-white d-flex align-items-center justify-content-center rounded me-2" style="width: 45px; height: 45px;">
                           <i class="fa-solid fa-image"></i>
                       </div>`
                }
            <div style="flex:1; min-width:0;">
                    <div class="fw-semibold small text-truncate">${item.name}</div>
                    <div class="text-danger fw-medium small">
                        $${itemNetTotal.toFixed(2)}
                        ${itemDiscountPercent > 0 ? `<span class="text-muted">(${itemDiscountPercent.toFixed(2)}% off)</span>` : ''}
                    </div>
                </div>
                <div class="d-flex justify-content-end align-items-center gap-1 ms-2">
                    <button class="cart-decrease-btn btn btn-sm bg-light shadow-sm rounded-circle"
                            type="button"
                            data-qty-index="${index}">
                                <i class="fa-solid fa-minus"></i>
                            </button>
                    <span class="px-1 fw-bold">${item.qty}</span>
                    <button class="cart-increase-btn btn btn-sm bg-light shadow-sm rounded-circle"
                            type="button"
                            data-qty-index="${index}">
                                <i class="fa-solid fa-plus"></i>
                            </button>
                    <button class="cart-remove-btn btn btn-sm btn-outline-danger rounded-circle"
                            type="button"
                            data-remove-index="${index}">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });

    subtotalDisplay.innerText = `$${subtotal.toFixed(2)}`;
    discountDisplay.innerText = productDiscountTotal > 0 ? `-$${productDiscountTotal.toFixed(2)}` : '$0.00';
    totalDisplay.innerText = `$${(subtotal - productDiscountTotal).toFixed(2)}`;
    totalItemsDisplay.innerText = totalQty;
    updateModalSummary();
}

function removeItem(index) {
    if (cart[index].qty > 1) {
        cart[index].qty -= 1;
    } else {
        cart.splice(index, 1);
    }
    renderCart();
}

function increaseQty(index) {
    if (!cart[index]) {
        return;
    }
    cart[index].qty += 1;
    renderCart();
}

function decreaseQty(index) {
    if (!cart[index]) {
        return;
    }
    if (cart[index].qty > 1) {
        cart[index].qty -= 1;
    } else {
        cart.splice(index, 1);
    }
    renderCart();
}

document.addEventListener('click', function(e) {
    const removeBtn = e.target.closest('.cart-remove-btn');
    if (!removeBtn) {
        return;
    }

    const index = Number(removeBtn.dataset.removeIndex);
    if (Number.isNaN(index)) {
        return;
    }

    removeItem(index);
});

document.addEventListener('click', function(e) {
    const increaseBtn = e.target.closest('.cart-increase-btn');
    if (!increaseBtn) {
        return;
    }

    const index = Number(increaseBtn.dataset.qtyIndex);
    if (Number.isNaN(index)) {
        return;
    }

    increaseQty(index);
});

document.addEventListener('click', function(e) {
    const decreaseBtn = e.target.closest('.cart-decrease-btn');
    if (!decreaseBtn) {
        return;
    }

    const index = Number(decreaseBtn.dataset.qtyIndex);
    if (Number.isNaN(index)) {
        return;
    }

    decreaseQty(index);
});

const checkoutBtn = document.getElementById('checkout-btn');
if (checkoutBtn) {
    checkoutBtn.addEventListener('click', function() {
        updateModalSummary();
    });
}

const checkoutDiscount = document.getElementById('checkout-discount');
if (checkoutDiscount) {
    checkoutDiscount.addEventListener('input', function() {
        updateModalSummary();
    });
}

const confirmCheckoutBtn = document.getElementById('confirm-checkout-btn');
if (confirmCheckoutBtn) {
    confirmCheckoutBtn.addEventListener('click', function() {
        if (!Array.isArray(cart) || cart.length === 0) {
            alert('Cart is empty!');
            return;
        }

        const selectedPayment = document.querySelector('input[name="payment"]:checked');
        const discountInput = document.getElementById('checkout-discount');
        if (!selectedPayment || !discountInput) {
            alert('Payment details are incomplete.');
            return;
        }

        const itemsForBackend = cart.map(item => ({
            id: item.id,
            quantity: item.qty
        }));

        fetch('/checkout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    items: itemsForBackend,
                    discount: discountInput.value,
                    payment_method: selectedPayment.id
                })
            })
            .then(res => res.json())
            .then(result => {
                if (result.message === 'Sale created successfully.') {
                    alert('Saved successfully! Invoice number: ' + result.order_number);
                    window.location.reload();
                } else {
                    alert('Error: ' + (result.error || 'Checkout failed.'));
                }
            });
    });
}

function updateModalSummary() {
    const checkoutSubtotalEl = document.getElementById('checkout-subtotal');
    const checkoutDiscountAmountEl = document.getElementById('checkout-discount-amount');
    const checkoutItemEl = document.getElementById('checkout-item');
    const checkoutTotalEl = document.getElementById('checkout-total');
    const discountValueEl = document.getElementById('discount-value');
    const totalValueEl = document.getElementById('total-value');
    const discountInput = document.getElementById('checkout-discount');

    if (!checkoutSubtotalEl || !checkoutDiscountAmountEl || !checkoutItemEl || !checkoutTotalEl || !discountValueEl || !totalValueEl || !discountInput) {
        return;
    }

    const subtotal = cart.reduce((sum, item) => sum + (Number(item.price) || 0) * item.qty, 0);
    const totalItems = cart.reduce((sum, item) => sum + (Number(item.qty) || 0), 0);
    const productDiscountAmount = cart.reduce((sum, item) => {
        const itemSubtotal = (Number(item.price) || 0) * item.qty;
        return sum + itemSubtotal * ((Number(item.discount) || 0) / 100);
    }, 0);
    const afterProductDiscount = subtotal - productDiscountAmount;
    const checkoutDiscountPercent = parseFloat(discountInput.value) || 0;
    const checkoutDiscountAmount = (afterProductDiscount * checkoutDiscountPercent) / 100;
    const totalDiscountAmount = productDiscountAmount + checkoutDiscountAmount;
    const finalTotal = afterProductDiscount - checkoutDiscountAmount;

    checkoutSubtotalEl.innerText = `$${subtotal.toFixed(2)}`;
    checkoutDiscountAmountEl.innerText = totalDiscountAmount > 0 ? `-$${totalDiscountAmount.toFixed(2)}` : '-$0.00';
    checkoutItemEl.innerText = totalItems;
    checkoutTotalEl.innerText = `$${finalTotal.toFixed(2)}`;
    discountValueEl.innerText = totalDiscountAmount > 0 ? `-$${totalDiscountAmount.toFixed(2)}` : '$0.00';
    totalValueEl.innerText = `$${finalTotal.toFixed(2)}`;
}

function getCsrfToken() {
    const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}

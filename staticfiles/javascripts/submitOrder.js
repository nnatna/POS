function submitOrder() {
    if (!Array.isArray(window.cart) || window.cart.length === 0) return alert("Please select products first!");
    const totalValueEl = document.getElementById('total-value');
    if (!totalValueEl) return;

    fetch('/process_checkout/', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken()
            },
            body: JSON.stringify({
                items: window.cart,
                total_price: totalValueEl.innerText.replace('$', '')
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                alert("Save successfully!");
                window.location.reload();
            }
        });
}

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

function updateModalSummary() {
    const cartTotalEl = document.getElementById('cart-total');
    const checkoutSubtotalEl = document.getElementById('checkout-subtotal');
    const checkoutDiscountAmountEl = document.getElementById('checkout-discount-amount');
    const checkoutTotalEl = document.getElementById('checkout-total');
    const discountValueEl = document.getElementById('discount-value');
    const totalValueEl = document.getElementById('total-value');
    const discountInput = document.getElementById('checkout-discount');

    if (!cartTotalEl || !checkoutSubtotalEl || !checkoutDiscountAmountEl || !checkoutTotalEl || !discountValueEl || !totalValueEl || !discountInput) {
        return;
    }

    let subtotalStr = cartTotalEl.innerText.replace('$', '');
    let subtotal = parseFloat(subtotalStr);

    let discountPercent = parseFloat(discountInput.value) || 0;

    let discountAmount = (subtotal * discountPercent) / 100;
    let finalTotal = subtotal - discountAmount;

    checkoutSubtotalEl.innerText = `$${subtotal.toFixed(2)}`;
    checkoutDiscountAmountEl.innerText = `-$${discountAmount.toFixed(2)}`;
    checkoutTotalEl.innerText = `$${finalTotal.toFixed(2)}`;

    discountValueEl.innerText = `-$${discountAmount.toFixed(2)}`;
    totalValueEl.innerText = `$${finalTotal.toFixed(2)}`;
}


const confirmCheckoutBtn = document.getElementById('confirm-checkout-btn');
if (confirmCheckoutBtn) {
    confirmCheckoutBtn.addEventListener('click', function() {
        if (!Array.isArray(window.cart) || window.cart.length === 0) return alert("Cart is empty!");

        const selectedPayment = document.querySelector('input[name="payment"]:checked');
        const discountInput = document.getElementById('checkout-discount');
        if (!selectedPayment || !discountInput) {
            return alert("Payment details are incomplete.");
        }

        let paymentMethod = selectedPayment.id;
        let discountPercent = discountInput.value;

        const itemsForBackend = window.cart.map(item => ({
            id: item.id,
            quantity: item.qty
        }));

        fetch('/checkout/', {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken()
                },
                body: JSON.stringify({
                    items: itemsForBackend,
                    discount: discountPercent,
                    payment_method: paymentMethod
                })
            })
            .then(res => res.json())
            .then(result => {
                if (result.message === 'Sale created successfully.') {
                    alert("Saved successfully! Invoice number: " + result.order_number);
                    window.location.reload();
                } else {
                    alert("Error: " + result.error);
                }
            });
    });
}

function getCsrfToken() {
    const cookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}
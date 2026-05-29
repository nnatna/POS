function selectOrder(element, status, price, orderId) {
    const url = new URL(window.location.href);
    const isAlreadySelected = element.classList.contains('bg-warning') && url.searchParams.get('orders') === String(orderId);

    if (isAlreadySelected) {
        url.searchParams.delete('orders');
        window.location.href = url.toString();
        return;
    }

    const allCards = document.querySelectorAll('.order-card');
    allCards.forEach(card => {
        card.classList.remove('bg-warning', 'text-dark');
        card.classList.add('bg-light', 'text-dark');
        const statusLabel = card.querySelector('.status-text');
        if (statusLabel.innerText === 'Unpaid') {
            statusLabel.className = 'status-text text-warning fw-medium';
        } else {
            statusLabel.className = 'status-text text-success fw-medium';
        }
        card.querySelector('.info-text').classList.add('text-muted');
        card.querySelector('.info-text').classList.remove('opacity-75');
    });
    element.classList.remove('bg-light', 'text-dark');
    element.classList.add('bg-warning', 'text-dark');

    const activeStatus = element.querySelector('.status-text');
    activeStatus.className = 'status-text opacity-75';

    const activeInfo = element.querySelector('.info-text');
    activeInfo.classList.remove('text-muted');
    activeInfo.classList.add('opacity-75');

    if (orderId) {
        url.searchParams.set('orders', orderId);
        window.location.href = url.toString();
    }
}

function filterSalesOrderCards() {
    const salesPage = document.querySelector('.sales-page');
    const salesSearchInput = document.querySelector('.top-navbar form[action*="/sales"] .search-input');
    const salesOrderList = salesPage ? salesPage.querySelector('#product-list') : null;

    if (!salesSearchInput || !salesOrderList) {
        return;
    }

    const query = salesSearchInput.value.trim().toLowerCase();
    const orderCards = salesOrderList.querySelectorAll('.order-card');
    const serverEmptyState = salesOrderList.querySelector('.col-12.p-4.text-muted.text-center');
    const liveEmptyState = document.getElementById('sales-order-live-empty');
    let visibleCount = 0;

    orderCards.forEach((card) => {
        const orderSearchText = `${card.dataset.orderSearch || ''} ${card.innerText || ''}`.toLowerCase();
        const isMatch = !query || orderSearchText.includes(query);

        card.classList.toggle('d-none', !isMatch);
        if (isMatch) {
            visibleCount += 1;
        }
    });

    if (serverEmptyState) {
        serverEmptyState.classList.toggle('d-none', visibleCount > 0 || !!query);
    }

    if (liveEmptyState) {
        liveEmptyState.classList.toggle('d-none', visibleCount > 0 || !query);
    }
    return { salesSearchInput };
}

function initSalesLiveSearch() {
    const result = filterSalesOrderCards();
    if (!result || !result.salesSearchInput) {
        return;
    }

    result.salesSearchInput.addEventListener('input', filterSalesOrderCards);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSalesLiveSearch);
} else {
    initSalesLiveSearch();
}

function printInvoice() {
    const invoiceTemplate = document.getElementById('invoice-print-template');
    if (!invoiceTemplate) {
        alert('Please select an order to print.');
        return;
    }

    const printWindow = window.open('', '_blank', 'width=900,height=700');
    if (!printWindow) {
        alert('Unable to open print window.');
        return;
    }

    printWindow.document.open();
    printWindow.document.write(`
        <html>
            <head>
                <title>Invoice</title>
                <style>
                    body { margin: 0; background: #fff; }
                    @media print { body { margin: 0; } }
                </style>
            </head>
            <body>${invoiceTemplate.innerHTML}</body>
        </html>
    `);
    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
}

const printInvoiceBtn = document.getElementById('print-invoice-btn');
if (printInvoiceBtn) {
    printInvoiceBtn.addEventListener('click', printInvoice);
}

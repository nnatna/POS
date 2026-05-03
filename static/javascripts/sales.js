function selectOrder(element, status, price, orderId) {
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
        const url = new URL(window.location.href);
        url.searchParams.set('orders', orderId);
        window.location.href = url.toString();
    }
}
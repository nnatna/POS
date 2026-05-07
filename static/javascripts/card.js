const homeSearchInput = document.querySelector('form[action*="/home/"] .search-input');
const productCardList = document.getElementById('product-list');
const productPageSearchInput = document.querySelector('form[action*="/products/"] .search-input');
const productTableBody = document.getElementById('product-table-body');
const brandPageSearchInput = document.querySelector('form[action*="/brands/"] .search-input');
const brandList = document.getElementById('brand-list');
const categoryPageSearchInput = document.querySelector('form[action*="/category/"] .search-input');
const categoryList = document.getElementById('category-list');

function filterHomeProductCards() {
    if (!homeSearchInput || !productCardList) {
        return;
    }

    const query = homeSearchInput.value.trim().toLowerCase();
    const productCards = productCardList.querySelectorAll('.product-item');
    const serverEmptyState = productCardList.querySelector('.col-12.p-4.text-muted');
    const liveEmptyState = document.getElementById('product-search-empty');
    let visibleCount = 0;

    productCards.forEach((card) => {
        const productName = (card.dataset.productName || '').toLowerCase();
        const isMatch = !query || productName.includes(query);

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
}

function filterProductTableRows() {
    if (!productPageSearchInput || !productTableBody) {
        return;
    }

    const query = productPageSearchInput.value.trim().toLowerCase();
    const productRows = productTableBody.querySelectorAll('.product-table-row');
    const serverEmptyState = document.getElementById('product-table-server-empty');
    const liveEmptyState = document.getElementById('product-table-live-empty');
    let visibleCount = 0;

    productRows.forEach((row) => {
        const productName = (row.dataset.productName || '').toLowerCase();
        const isMatch = !query || productName.includes(query);

        row.classList.toggle('d-none', !isMatch);
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
}

if (homeSearchInput && productCardList) {
    homeSearchInput.addEventListener('input', filterHomeProductCards);
    filterHomeProductCards();
}

if (productPageSearchInput && productTableBody) {
    productPageSearchInput.addEventListener('input', filterProductTableRows);
    filterProductTableRows();
}

function filterSimpleCards(searchInput, list, itemSelector, dataKey, serverEmptyId, liveEmptyId) {
    if (!searchInput || !list) {
        return;
    }

    const query = searchInput.value.trim().toLowerCase();
    const items = list.querySelectorAll(itemSelector);
    const serverEmptyState = document.getElementById(serverEmptyId);
    const liveEmptyState = document.getElementById(liveEmptyId);
    let visibleCount = 0;

    items.forEach((item) => {
        const text = (item.dataset[dataKey] || '').toLowerCase();
        const isMatch = !query || text.includes(query);

        item.classList.toggle('d-none', !isMatch);
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
}

if (brandPageSearchInput && brandList) {
    const handler = () => filterSimpleCards(brandPageSearchInput, brandList, '.brand-item', 'brandName', 'brand-server-empty', 'brand-live-empty');
    brandPageSearchInput.addEventListener('input', handler);
    handler();
}

if (categoryPageSearchInput && categoryList) {
    const handler = () => filterSimpleCards(categoryPageSearchInput, categoryList, '.category-item', 'categoryName', 'category-server-empty', 'category-live-empty');
    categoryPageSearchInput.addEventListener('input', handler);
    handler();
}

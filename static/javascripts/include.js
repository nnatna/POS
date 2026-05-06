function scrollCategories(distance) {
    const container = document.getElementById('categoryScroll');
    if (!container) {
        return;
    }

    container.scrollBy({
        left: distance,
        behavior: 'smooth'
    });
}

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

document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname.replace(/\/+$/, "") || "/";
    const links = document.querySelectorAll("#sidebarNav .nav-link");

    links.forEach((link) => {
        const linkPath = new URL(link.href, window.location.origin).pathname.replace(/\/+$/, "") || "/";
        link.classList.toggle("active", linkPath === currentPath);
    });
});

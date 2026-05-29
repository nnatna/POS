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

const container = document.getElementById('categoryScroll');
const btnLeft = document.getElementById('btnLeft');
const btnRight = document.getElementById('btnRight');

function updateButtonVisibility() {
    if (!container || !btnLeft || !btnRight) {
        return;
    }

    if (container.scrollLeft > 5) {
        btnLeft.style.display = 'block';
    } else {
        btnLeft.style.display = 'none';
    }

    const maxScroll = container.scrollWidth - container.clientWidth;
    if (container.scrollLeft >= maxScroll - 5) {
        btnRight.style.display = 'none';
    } else {
        btnRight.style.display = 'block';
    }
}

if (container) {
    container.addEventListener('scroll', updateButtonVisibility);
}

window.addEventListener('load', updateButtonVisibility);

window.addEventListener('resize', updateButtonVisibility);
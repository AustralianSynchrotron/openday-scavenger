// Store map and marker elements
var map = document.getElementById("map-public");
var markers = document.querySelectorAll('[data-marker]');

// Adjust marker positions according to div size
let positionMarkers = () => {
    markers.forEach(function (m) {
        if (map.getBoundingClientRect().width > 799) {
            m.style.top = `${m.dataset.top}px`;
            m.style.left = `${m.dataset.left}px`;
        } else {
            var height_ratio = m.dataset.top / 642.86 * map.getBoundingClientRect().height;
            var width_ratio = m.dataset.left / 800 * map.getBoundingClientRect().width;

            m.style.top = `${height_ratio}px`;
            m.style.left = `${width_ratio}px`;
        }
    });
}

// Debounce browser resize listener
let debounce = (callback, delay) => {
    let myTimeout;
    return () => {
        clearTimeout(myTimeout);
        myTimeout = setTimeout(() => {
            callback()
        }, delay);
    };
};

let doDebounce = debounce(() => positionMarkers(), 10)
window.addEventListener('resize', () => doDebounce());

// Check markers after initial page load
document.addEventListener('DOMContentLoaded', function () {
    positionMarkers();
}, false);
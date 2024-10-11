// Store marker locations
var markerLocations = [];

// Add listener to btns
document.getElementById("map-btn-copy").addEventListener("click", copyMarkerArray);
document.getElementById("map-btn-clear").addEventListener("click", clearMarkerArray);

// Add listener to map
const map = document.getElementById("map-editor");
map.addEventListener("click", newMarker);

// Marker co-ord array display text
const array_title = document.getElementById("map-array-title");
const array_display = document.getElementById("map-array");

// Update array display string
function updateArrayDisplay() {
    array_display.textContent = JSON.stringify(markerLocations);

    // Don't display array if there's no location selected
    if (markerLocations.length < 1) array_display.textContent = "No location selected";
}

// Add co-ord to markers array & display
function newMarker(e) {
    // Return if user clicked on existing marker
    if (e.target.id.startsWith("map-marker-")) return;

    // Create new marker
    var rect = e.target.getBoundingClientRect();
    var m = document.createElement("img");
    m.addEventListener("click", removeMarker);
    m_top = Math.ceil(e.clientY - rect.top - 22);
    m_left = Math.ceil(e.clientX - rect.left - 14);

    m.id = `map-marker-${markerLocations.length}`;
    m.classList.add("map-marker");
    m.src = "/static/images/map/map_marker.svg";
    m.style.top = `${m_top}px`;
    m.style.left = `${m_left}px`;
    map.appendChild(m);

    // Add marker to array list
    markerLocations.push({
        top: m_top,
        left: m_left,
    })

    updateArrayDisplay();
}

// Remove co-ord when existing marker is clicked
function removeMarker(e) {
    var marker = e.target;

    // Update display array list
    markerLocations = markerLocations.filter(m => !(`${m.top}px` == marker.style.top && `${m.left}px` == marker.style.left));
    marker.remove();

    updateArrayDisplay();
}

// Clear all markers from map
function clearMarkerArray(e) {
    // Remove the markers from html
    var markers = document.querySelectorAll('.map-marker');
    markers.forEach(m => m.remove());

    // Remove the markers from stored array
    markerLocations = [];
    updateArrayDisplay();
}

// Copy marker array to clipboard
function copyMarkerArray(e) {
    navigator.clipboard.writeText(`${JSON.stringify(markerLocations)}`);
    e.target.innerText = "Copied to clipboard!";
    e.target.classList.add("btn-info");

    myTimeout = setTimeout(function(){
        e.target.innerText = "Copy Array String to Clipboard";
        e.target.classList.remove("btn-info");
    }, 2000);
}
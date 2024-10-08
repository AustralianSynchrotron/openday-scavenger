// Store marker locations
var markerLocations = [];

// Add listener to copy btn
document.getElementById("map-btn").addEventListener("click", copyMarkerArray);

// Add listener to map
const map = document.getElementById("map-editor");
map.addEventListener("click", newMarker);

// Marker co-ord array display text
const array_title = document.getElementById("map-array-title");
const array_display = document.getElementById("map-array");

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
    markerLocations.push(`top: ${m_top}px; left: ${m_left}px;`);

    // Display array list
    if (markerLocations.length > 0) array_title.style.visibility = "visible";
    array_display.textContent = markerLocations;
}

// Remove co-ord when existing marker is clicked
function removeMarker(e) {
    var m = e.target;
    m.remove();
    markerLocations = markerLocations.filter(e => e !== `top: ${m.style.top}; left: ${m.style.left};`);

    // Update display array list
    if (markerLocations.length < 1) array_title.style.visibility = "hidden";
    array_display.textContent = markerLocations;
}

// Copy marker array to clipboard
function copyMarkerArray(e) {
    navigator.clipboard.writeText(`${markerLocations.toString()}`);
    e.target.innerText = "Copied to clipboard!";
    e.target.classList.add("btn-info");

    myTimeout = setTimeout(function(){
        e.target.innerText = "Copy List to Clipboard";
        e.target.classList.remove("btn-info");
    }, 2000);
}
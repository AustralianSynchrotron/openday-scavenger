// When the page loads, add an event listener to the periodic table
// When the user clicks on an element, set the answer input to the element's symbol
// document.addEventListener("DOMContentLoaded", function () {
//   const periodicTable = document.querySelector(".periodic-table");
//   const answerInput = document.getElementById("answer");

//   periodicTable.addEventListener("click", function (event) {
//     const clickedElement = event.target.closest(".element");

//     if (!clickedElement || !clickedElement.classList.contains("option")) {
//       return;
//     }

//     if (clickedElement) {
//       const elementSymbol =
//         clickedElement.querySelector(".element-symbol").textContent;
//       answerInput.value = elementSymbol;
//     }
//   });
// });

function formatCategory(category) {
  return category.replace(/([A-Z])/g, " $1").trim();
}

const fetchElementLookup = async () => {
  try {
    const response = await fetch(
      "/puzzles/periodic/static/data/element_lookup.json"
    );
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching element lookup data:", error);
    return {};
  }
};

document.addEventListener("DOMContentLoaded", async function () {
  // Fetch element_lookup data
  const element_lookup = await fetchElementLookup();

  const popup = document.getElementById("element-popup");
  const closeBtn = popup.querySelector(".close");

  closeBtn.onclick = function () {
    popup.style.display = "none";
  };

  window.onclick = function (event) {
    if (event.target == popup) {
      popup.style.display = "none";
    }
  };

  const elements = document.querySelectorAll(".element");
  elements.forEach((element) => {
    element.addEventListener("click", function () {
      const symbol = this.getAttribute("data-symbol");
      const elementData = element_lookup[symbol];

      document.getElementById("element-name").textContent = elementData.name;
      document.getElementById("element-symbol").textContent =
        elementData.symbol;
      document.getElementById("element-number").textContent =
        elementData.number;
      document.getElementById("element-mass").textContent =
        elementData.atomic_mass;
      document.getElementById("element-category").textContent = formatCategory(
        elementData.category
      );
      document.getElementById("element-density").textContent =
        elementData.density;
      document.getElementById("element-melting-point").textContent =
        elementData.melting_point;
      document.getElementById("element-boiling-point").textContent =
        elementData.boiling_point;
      document.getElementById("element-configuration").textContent =
        elementData.configuration;
      document.getElementById("element-radioactive").textContent =
        elementData.radioactive ? "Yes" : "No";
      document.getElementById("element-discoverer").textContent =
        elementData.discovered_by || "Unknown";
      document.getElementById("element-discovery-year").textContent =
        elementData.discovery || "Unknown";

      // Fade in the popup
      popup.style.display = "block";
      popup.style.transition = "opacity 0.3s ease-in-out";
      popup.style.opacity = "0";
      setTimeout(() => {
        popup.style.opacity = "1";
      }, 10);
    });
  });
});

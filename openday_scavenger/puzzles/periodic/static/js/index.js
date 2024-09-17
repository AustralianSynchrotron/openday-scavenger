// When the page loads, add an event listener to the periodic table
// When the user clicks on an element, set the answer input to the element's symbol
document.addEventListener("DOMContentLoaded", function () {
  const periodicTable = document.querySelector(".periodic-table");
  const answerInput = document.getElementById("answer");

  periodicTable.addEventListener("click", function (event) {
    const clickedElement = event.target.closest(".element");

    if (!clickedElement || !clickedElement.classList.contains("option")) {
      return;
    }

    if (clickedElement) {
      const elementSymbol =
        clickedElement.querySelector(".element-symbol").textContent;
      answerInput.value = elementSymbol;
    }
  });
});

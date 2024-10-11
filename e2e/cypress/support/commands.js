// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//

import "cypress-file-upload";

Cypress.Commands.add("adminVisit", (url) => {
  cy.visit(url, {
    auth: {
      username: "admin",
      password: "admin",
    },
  });
});

Cypress.Commands.add("adminSeedPuzzleData", () => {
  cy.intercept("POST", "/admin/puzzles/upload-json").as("uploadRequest");

  cy.adminVisit("/admin/puzzles");
  cy.contains(".btn", "Upload JSON").click();
  cy.get("form#upload-json-form").should("be.visible").as("uploadForm");
  cy.get('input#json-file[type="file"]').as("fileInput");
  cy.get("@fileInput").attachFile("puzzle_seed_data.json");
  cy.get("@uploadForm").submit();
  cy.wait("@uploadRequest").its("response.statusCode").should("eq", 200);
});

Cypress.Commands.add("adminStartSession", () => {
  cy.adminVisit("/admin/visitors/pool/");
  cy.get("input#number_of_entries").type("1");
  cy.get("button#create-button").click();
  cy.get("#visitor-pool-table table tbody tr:first-child").within(() => {
    cy.get("td:first-child").then((cell) => {
      Cypress.env("VisitorUid", cell.text());
    });
    cy.get("td:nth-child(2) a").click();
  });

  cy.contains(".container", "Scan puzzle lock to unlock the puzzle!");
});

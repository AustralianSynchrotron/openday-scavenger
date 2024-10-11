describe("template spec", () => {
  before(() => {
    cy.adminSeedPuzzleData();
    cy.adminStartSession();
  });

  describe("for a single session", () => {
    it("the demo puzzle should accept incorrect and correct answers", () => {
      cy.visit("/puzzles/demo/");

      // Incorrect
      cy.contains("h1", "Demo Puzzle");
      cy.get("input#answer").type("Fhqwhgads");
      cy.get("form").submit();
      cy.contains("h1", "Oh no!").should("be.visible");
      cy.contains("a", "Try This Puzzle Again!").click();

      // Correct
      cy.get("input#answer").type("3{enter}");
      cy.contains("h1", "100% Complete").should("be.visible");
    });

    it("puzzle responses should be recorded in the admin section", () => {
      // Filter by UID
      const visitorUid = Cypress.env("VisitorUid");

      cy.adminVisit("/admin/responses/");
      cy.get("input#visitor_uid").type(visitorUid);

      cy.get("#response-table table tbody").within(() => {
        cy.get("tr").should("have.length", 2);
        cy.contains("tr", "No").within(() => {
          cy.get("td").eq(0).should("contain.text", "demo");
          cy.get("td").eq(2).should("contain.text", "Fhqwhgads");
        });
        cy.contains("tr", "Yes").within(() => {
          cy.get("td").eq(0).should("contain.text", "demo");
          cy.get("td").eq(2).should("contain.text", "3");
        });
      });

      cy.get("input#visitor_uid").clear();

      // Filter by Name

      cy.get("input#visitor_uid").type("demo");

      cy.get("#response-table table tbody").within(() => {
        cy.get("tr").should("have.length", 2);
        cy.contains("tr", "No").within(() => {
          cy.get("td").eq(0).should("contain.text", "demo");
          cy.get("td").eq(2).should("contain.text", "Fhqwhgads");
        });
        cy.contains("tr", "Yes").within(() => {
          cy.get("td").eq(0).should("contain.text", "demo");
          cy.get("td").eq(2).should("contain.text", "3");
        });
      });

      cy.get("input#visitor_uid").clear();
    });

    it("visitors can be checked out from the admin page", () => {
      // Filter by UID
      const visitorUid = Cypress.env("VisitorUid");

      cy.adminVisit("/admin/visitors/");
      cy.get("input#still_playing").check();

      cy.get("input#uid_filter").type(visitorUid);

      cy.get("#visitor-table table tbody").within(() => {
        cy.get("tr").should("have.length", 1);
        cy.contains("tr", visitorUid).within(() => {
          cy.get("td").eq(1).should("not.be.empty");
          cy.get("td").eq(2).should("be.empty");
          cy.get("td").eq(4).should("contain.text", "Playing");
        });

        cy.contains("button", "Checkout").click();
      });

      // TODO: Should the filter clear when checkout is pressed?
      cy.get("input#uid_filter").type(visitorUid);

      cy.get("#visitor-table table tbody tr").should("not.exist");

      cy.get("input#still_playing").uncheck();

      cy.get("#visitor-table table tbody").within(() => {
        cy.get("tr").should("have.length", 1);
        cy.contains("tr", visitorUid).within(() => {
          cy.get("td").eq(1).should("not.be.empty");
          cy.get("td").eq(2).should("not.be.empty");
          cy.get("td").eq(4).should("contain.text", "Finished");
        });
      });
    });
  });
});

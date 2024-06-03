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
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })

/**
 * useful commands for selecting elements
 * reference: https://docs.cypress.io/guides/references/best-practices#Selecting-Elements
 */

Cypress.Commands.add('getBySel', (selector, ...args) => {
  return cy.get(`[data-test=${selector}]`, ...args);
});

Cypress.Commands.add('clickBySel', (selector, ...args) => {
  cy.get(`[data-test=${selector}]`, ...args).click();
  cy.wait(500);
});

Cypress.Commands.add('getBySelLike', (selector, ...args) => {
  return cy.get(`[data-test*=${selector}]`, ...args);
});

Cypress.Commands.add('checkSessionStorage', (key, val) => {
  cy.window().its('sessionStorage').invoke({ timeout: 5000 }, 'getItem', key).should('eq', val);
});

Cypress.Commands.add('checkSessionStorageObj', (storageKey, objKey, val) => {
  cy.window()
    .its('sessionStorage')
    .invoke({ timeout: 5000 }, 'getItem', storageKey)
    .then((item) => {
      const temp = JSON.parse(item);
      cy.wrap(temp).its(objKey).should('eq', val);
    });
});

Cypress.Commands.add('checkSessionStorageSubString', (key, val) => {
  cy.window()
    .its('sessionStorage')
    .invoke({ timeout: 5000 }, 'getItem', key)
    .should('contain', val);
});

Cypress.Commands.add('removeSessionStorage', (key) => {
  cy.window().its('sessionStorage').invoke({ timeout: 5000 }, 'removeItem', key);
});

// if exists then do something
Cypress.Commands.add('existsThenClick', (selector) => {
  cy.get('body').then(($body) => {
    if ($body.find(`[data-test*=${selector}]`).length > 0) {
      cy.getBySel(selector).click();
    }
  });
});

Cypress.Commands.add('uploadModel', () => {
  cy.visit('model');
  cy.contains('.v-btn', 'Upload New Model').click();
  cy.get('[data-test=model-upload-nickname]').type("SimpleCNN");
  cy.get('[data-test=model-upload-classname]').type("SimpleCNN");
  cy.get('[data-test=model-upload-codefile]').selectFile('cypress/testdata/SimpleCNN.py', { force: true });
  cy.get('[data-test=model-upload-submit-button]').click();
  cy.get('[data-test=model-upload-submit-button]').should('not.visible');
})

Cypress.Commands.add('setCurrentModel', () => {
  // This sets the first model as current.
  // Make sure model is cleaned up properly and uploadModel is called before using this
  cy.visit('model');
  cy.get('tr:nth-child(1)').find('td').eq(10).within(() => {
    cy.get('[data-test=train-model-set-model-as-current]').click({ force: true });
  })
})
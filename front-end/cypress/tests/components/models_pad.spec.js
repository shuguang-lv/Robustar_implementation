describe('The Model Training Page', () => {
  function deleteAllModels() {
    const selector = '[data-test=train-model-delete-model]'
    cy.get('body').then(($body) => {
    if ($body.find(selector).length > 0) {
      // Element exists, click it
      cy.get(selector).each(($el, index, $list) => {
        cy.get(selector).first().click();
        cy.get('[data-test=train-model-delete-model-confirm]').click();
        cy.get('[data-test=train-model-delete-model-confirm]').should('not.visible');
        cy.log(`Clicked element ${index + 1}`);
        // Call the function again to check if the element still exists
      })
    } else {
      // Element no longer exists, exit the function
      cy.log('All buttons clicked, no more buttons found');
    }
  });
  }

  before(() => {
    cy.visit('model');
    cy.wait(1000);
    deleteAllModels();
    cy.wait(1000);
  })

  beforeEach(() => {
    cy.visit('model');
    cy.wait(1000);
    cy.uploadModel()
    cy.wait(1000);
  });

  afterEach(() => {
    cy.wait(1000);
    deleteAllModels();
    cy.wait(1000);
  })
  it('can upload model', () => {
    cy.get('[data-test=train-model-delete-model]').should('have.length', 1);
  })

  it('can have current model after selecting', () => {
    cy.get('tr:nth-child(1)').find('td').eq(10).within(() => {
      cy.get('[data-test=train-model-edit-model]').click({ force: true });
    })
      cy.getBySel('train-model-set-current-model').click();
      cy.get('[data-test=train-model-edit-model-cancel]').click()
      cy.get('[data-test=train-model-edit-model-cancel]').should('not.visible')
      cy.getBySel('train-model-current-model-create-time').should('not.be.empty');
      cy.getBySel('train-model-current-model-achitecture').should('not.be.empty');

  });

  it('can go to the train page after having current model', () => {
    cy.get('tr:nth-child(1)').find('td').eq(10).within(() => {
      cy.get('[data-test=train-model-edit-model]').click({ force: true });
    });
    cy.get('[data-test=train-model-set-current-model]').click();
    cy.get('[data-test=train-model-edit-model-cancel]').click();
    cy.get('[data-test=train-model-edit-model-cancel]').should('not.visible')
    cy.get('[data-test=train-model-train-model-button]').click();
    cy.url().should('contains', 'train');
  });

  it('can edit model', () => {
    cy.get('tr:nth-child(1)').find('td').eq(10).within(() => {
      cy.get('[data-test=train-model-edit-model]').click({ force: true });
    });

    cy.get('[data-test=train-model-edit-model-description]').clear().type("test123");
    cy.get('[data-test=train-model-edit-model-cancel]').click();
    cy.get('[data-test=train-model-edit-model-cancel]').should('not.visible')

    cy.get('tr:nth-child(1)').find('td').eq(10).within(() => {
      cy.get('[data-test=train-model-edit-model]').click({ force: true });
    });
    cy.get('[data-test=train-model-edit-model-description]').invoke('val').should('not.contain', 'test123');
    cy.get('tr:nth-child(1)').find('td').eq(10).within(() => {
      cy.get('[data-test=train-model-edit-model]').click({ force: true });
    });

    cy.get('[data-test=train-model-edit-model-description]').clear().type("test");
    cy.get('[data-test=train-model-edit-model-confirm]').click();
    cy.wait(1000)
    cy.get('tr:nth-child(1)').find('td').eq(10).within(() => {
      cy.get('[data-test=train-model-edit-model]').click({ force: true });
    });
    cy.get('[data-test=train-model-edit-model-description]').invoke('val').should('contain', 'test');
    cy.get('[data-test=train-model-edit-model-cancel]').click();
    cy.get('[data-test=train-model-edit-model-cancel]').should('not.visible');
  });

  it('can duplicate model', () => {
    cy.get('tr:nth-child(1)').find('td').eq(10).within(() => {
      cy.get('[data-test=train-model-duplicate-model]').click();
      cy.wait(1000);
    });
    cy.get('[data-test=train-model-duplicate-model]').should('have.length', 2);
  });


  it('can edit model name', () => {
    cy.get('tr:nth-child(1)').find('td').eq(10).within(() => {
      cy.get('[data-test=train-model-edit-model]').click({ force: true });
    });

    cy.get('[data-test=train-model-edit-model-name]').clear().type("test");
    cy.get('[data-test=train-model-edit-model-confirm]').click();
    cy.wait(1000)

    cy.get('[data-test=train-model-edit-model-name]').invoke('val').should('contain', 'test');
  });
});
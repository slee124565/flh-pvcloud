'use strict';

describe('Controller: UsersiteCtrl', function () {

  // load the controller's module
  beforeEach(module('pvcApp'));

  var UsersiteCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    UsersiteCtrl = $controller('UsersiteCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(UsersiteCtrl.awesomeThings.length).toBe(3);
  });
});

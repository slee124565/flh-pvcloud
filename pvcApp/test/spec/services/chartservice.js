'use strict';

describe('Service: ChartService', function () {

  // load the service's module
  beforeEach(module('pvcApp'));

  // instantiate service
  var ChartService;
  beforeEach(inject(function (_ChartService_) {
    ChartService = _ChartService_;
  }));

  it('should do something', function () {
    expect(!!ChartService).toBe(true);
  });

});

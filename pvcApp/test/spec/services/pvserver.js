'use strict';

describe('Service: pvServer', function () {

  // load the service's module
  beforeEach(module('pvcApp'));

  // instantiate service
  var pvServer;
  beforeEach(inject(function (_pvServer_) {
    pvServer = _pvServer_;
  }));

  it('should do something', function () {
    expect(!!pvServer).toBe(true);
  });

});

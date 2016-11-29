'use strict';

/**
 * @ngdoc service
 * @name pvcApp.PVServer
 * @description
 * # PVServer
 * Service in the pvcApp.
 */
angular.module('pvcApp')
  .constant('apiBaseURL', 'http://localhost:8000/')
  .service('PVServer', [ '$resource','apiBaseURL', function ($resource, apiBaseURL) {
    // AngularJS will instantiate a singleton by calling "new" on this function
	return $resource( apiBaseURL + 'uapp/api/:serial');
  }]);

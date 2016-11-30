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
  .service('PVServer', [ '$http','apiBaseURL', function ($http, apiBaseURL) {
    // AngularJS will instantiate a singleton by calling "new" on this function
	  this.getPVSMeta = function(serial) {
		return $http.get( apiBaseURL + 'uapp/api/' + serial);
	  };
  }]);

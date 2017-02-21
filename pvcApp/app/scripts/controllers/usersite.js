'use strict';

/**
 * @ngdoc function
 * @name pvcApp.controller:UsersiteCtrl
 * @description
 * # UsersiteCtrl
 * Controller of the pvcApp
 */
angular.module('pvcApp')
  .controller('UsersiteCtrl', ['$scope','$window', '$stateParams', 'PVServer','ChartService',
  function ($scope,$window,$stateParams,PVServer,ChartService) {
	//console.log('param serial: ' + $stateParams.serial);
	PVServer.getPVSMeta($stateParams.serial).then(
			function(response) {
				$scope.site = response.data;
				$scope.site.title = '太陽能發電系統';
				$scope.site.header = '再生能源 – 太陽能即時發電狀況';
				ChartService.makeHourlyChart($scope.site.amchart_hourly_data);
				//ChartService.makeDailyChart($scope.site.amchart_daily_data);
				//ChartService.makeMonthlyChart($scope.site.amchart_monthly_data);
				},
			function(response){
				console.log('http error' + response.status + " " + response.statusText);
				});
	$scope.makeHourlyChart = function() {
		ChartService.makeHourlyChart($scope.site.amchart_hourly_data);
	};
	
	$scope.makeDailyChart = function() {
		ChartService.makeDailyChart($scope.site.amchart_daily_data);
	};
	
	$scope.makeMonthlyChart = function () {
		ChartService.makeMonthlyChart($scope.site.amchart_monthly_data);
	};
  }]);

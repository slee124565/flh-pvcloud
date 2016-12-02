'use strict';

/**
 * @ngdoc service
 * @name pvcApp.ChartService
 * @description
 * # ChartService
 * Service in the pvcApp.
 */
angular.module('pvcApp')
  .service('ChartService', ['$window', function ($window) {
    // AngularJS will instantiate a singleton by calling "new" on this function
	  this.makeChart = function(chartData, chartType) {
		  if (chartType == 1)
			  return this.makeHourlyChart(chartData);
		  else if (chartType == 2)
			  return this.makeDailyChart(chartData);
		  else
			  return this.makeMonthlyChart(chartData);
	  };
	  
	  this.makeHourlyChart = function(chartData) {
		  console.log('makeHourlyChart');
		  $window.AmCharts.makeChart('amchart1', {
			  type: 'serial',
			  addClassNames: true,
			  theme: 'light',
			  legend: {
			          equalWidths: false,
			          useGraphSettings: true,
			          valueAlign: 'left',
			          valueWidth: 120
			      },
			  balloon: {
			          adjustBorderColor: false,
			          horizontalPadding: 10,
			          verticalPadding: 8,
			          color: '#ffffff'
			      },
			  balloonDateFormat : 'JJ:NN',

			  dataProvider: chartData,
			  valueAxes: [{
			          id: 'energyAxis',           
			          axisAlpha: 0,
			          gridAlpha:0,
			          position: 'left',
			          title: 'Hourly Energy(Wh)',
			          stackType: 'regular', 
			      }],
			  startDuration: 1,
			  graphs: [{
			          //alphaField: 'alpha',
			          balloonText: '<span style="font-size:12px;">[[title]] in [[category]]<br><span style="font-size:20px;">[[value]]</span> [[additional]]</span>',
			          fillAlphas: 0.6,
			          lineAlpha: 0.4,
			          //type: 'column',
			          title: 'PVI(1)',
			          valueField: '1',
			          valueAxis: 'energyAxis',
			          dashLengthField: 'dashLengthColumn',
			          type: 'smoothedLine',
			      },{
			          alphaField: 'alpha',
			          balloonText: '<span style="font-size:12px;">[[title]] in [[category]]<br><span style="font-size:20px;">[[value]]</span> [[additional]]</span>',
			          fillAlphas: 0.6,
			          lineAlpha: 0.4,
			          //type: 'column',
			          title: 'PVI(2)',
			          valueField: '2',
			          valueAxis: 'energyAxis',
			          dashLengthField: 'dashLengthColumn',
			          type: 'smoothedLine',
			      }],
			  chartCursor: {
			          cursorAlpha: 0,
			          zoomable: false,
			          categoryBalloonDateFormat: 'JJ:NN',
			      },
			  dataDateFormat: 'YYYY-MM-DD JJ:NN:SS',
			  categoryField: 'date',
			  categoryAxis: {
			      dateFormats: [{
			          period:'hh', 
			          format:'JJ:NN'
			      }, {
			          period: 'JJ', 
			          format: 'JJ:NN'
			      }, {
			          period: 'DD',
			          format: 'MMM DD'
			      }, {
			          period: 'WW',
			          format: 'MMM DD'
			      }, {
			          period: 'MM',
			          format: 'MMM'
			      }, {
			          period: 'YYYY',
			          format: 'YYYY'
			      }],
				      parseDates: true,
				      minPeriod : 'hh',
				      gridPosition: 'start',
				      axisAlpha: 0,
				      tickLength: 0
			      },
			  'export': {
				      enabled: true
			      },
			  panEventsEnabled: false,
		  });
	  };
	  
	  this.makeDailyChart = function() {
		  console.log('makeDailyChart');
		  
	  };
	  
	  this.makeMonthlyChart = function() {
		  console.log('makeMonthlyChart');
		  
	  };
}]);

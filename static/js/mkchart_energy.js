
function make_eng_chart_hourly(containerID, chartData) {
	  var chartGraphs = [];
	  for (var key in chartData[chartData.length-1]) {
		  if (key != 'date') {
			  chartGraphs.push({
		          //alphaField: 'alpha',
		          balloonText: '<span style="font-size:12px;">[[title]] in [[category]]<br><span style="font-size:20px;">[[value]]</span> [[additional]]</span>',
		          fillAlphas: 0.6,
		          lineAlpha: 0.4,
		          //type: 'column',
		          title: 'PVI(' + key + ')',
		          valueField: key,
		          valueAxis: 'energyAxis',
		          dashLengthField: 'dashLengthColumn',
		          type: 'smoothedLine',
		      });
		  }
	  }

	  var chart = AmCharts.makeChart(containerID, {
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
		  graphs: chartGraphs,
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
		  panEventsEnabled: false,
	  });
	
} 
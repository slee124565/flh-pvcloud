


var chart_daily = AmCharts.makeChart("pvs_chart_en_daily_total", {
  "type": "serial",
  "addClassNames": true,
  "theme": "light",
    "legend": {
        "equalWidths": false,
        "useGraphSettings": true,
        "valueAlign": "left",
        "valueWidth": 120
    },
  "balloon": {
    "adjustBorderColor": false,
    "horizontalPadding": 10,
    "verticalPadding": 8,
    "color": "#ffffff"
  },

  "dataProvider": pvs_data_en_daily,
  /*
  "dataLoader": {
    //"url": 'http://'+location.host+'/pvi/query/H5/daily/energy/',
    "url": 'http://'+location.host+'/appeng/amchart/',
    //"url": mytest(),
  },*/
  "valueAxes": [{
    "id": "energyAxis",           
    "axisAlpha": 0,
     "gridAlpha":0,
    "position": "left",
     "title": "Energy(Wh)",},
    /*{
    "id": "visibility",           
    "axisAlpha": 0,
     "gridAlpha":0,
    "position": "right",
     "title": "Visibility",
     
    },*/
    ],
  "startDuration": 1,
  "graphs": [{
    "alphaField": "alpha",
    "balloonText": "<span style='font-size:12px;'>[[title]] in [[category]]:<br><span style='font-size:20px;'>[[value]]</span> [[additional]]</span>",
    "fillAlphas": 1,
    "type": "column",
     "title": "Energy",
    "valueField": "energy",
     "valueAxis": "energyAxis",
    "dashLengthField": "dashLengthColumn"
  }, /*{
    "id": "graph2",
    "balloonText": "<span style='font-size:12px;'>[[title]] in [[category]]:<br><span style='font-size:20px;'>[[value]]</span> [[additional]]</span>",
    "bullet": "round",
    "lineThickness": 3,
    "bulletSize": 7,
    "bulletBorderAlpha": 1,
    "bulletColor": "#FFFFFF",
    "useLineColorForBulletBorder": true,
    "bulletBorderThickness": 3,
    "fillAlphas": 0,
    "lineAlpha": 1,
    "title": "Visibility",
    "valueField": "visibility",
     "valueAxis": "visibilityAxis",
  }*/],
  "dataDateFormat": "YYYY-MM-DD",
  "categoryField": "date",
  "categoryAxis": {
    "dateFormats": [{
            "period": "DD",
            "format": "DD"
        }, {
            "period": "WW",
            "format": "MMM DD"
        }, {
            "period": "MM",
            "format": "MMM"
        }, {
            "period": "YYYY",
            "format": "YYYY"
        }],
    "parseDates": true,
    "gridPosition": "start",
    "axisAlpha": 0,
    "tickLength": 0
  },
  "export": {
    "enabled": true
  }
});


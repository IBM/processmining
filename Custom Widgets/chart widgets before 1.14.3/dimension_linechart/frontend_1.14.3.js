return {

  init: function (context) {
    var widget = document.getElementById(context.scope.widgetId);
    var div = document.createElement('div');
    div.id = context.scope.widgetId + '_div'; // creates a unique div id
    widget.appendChild(div);
    echarts.init(div);
  },

  update: function (data, context) {

    // get the variables from the backend
    var DIMENSION = data.DIMENSION;
    var GROUPBY = data.GROUPBY;
    var TIME_LABEL_UNIT = data.TIME_LABEL_UNIT;
    var MAX_NUMBER_OF_VALUES_DISPLAYED = data.MAX_NUMBER_OF_VALUES_DISPLAYED;
    var ACTIVITY = data.ACTIVITY;
    var TIMESCALE = data.TIMESCALE;
    var DATASET = data.DATASET;


    //compute the average leadtime 
    var aDay = 24 * 60 * 60 * 1000;
    for (var i = 0; i < DATASET.length; i++) { // avoid division by zero
      DATASET[i].leadtime_avg = [];
      for (var j = 0; j < DATASET[i].leadtime_sums.length; j++)
        if (DATASET[i].leadtime_sums[j] && DATASET[i].counters[j])
          DATASET[i].leadtime_avg.push(DATASET[i].leadtime_sums[j] / DATASET[i].counters[j] / aDay);
        else
          DATASET[i].leadtime_avg.push(0);
    }

    // compute count of cases for each value of the dimension
    for (var i = 0; i < DATASET.length; i++) {
      DATASET[i].count = DATASET[i].counters.reduce((accumulator, currentValue) => accumulator + currentValue);
    }
    // sort the dataset by count of cases, largest first
    DATASET.sort(function (a, b) {
      return b.count - a.count;
    });

    // FORMAT DATASET FOR RENDERING WITH AN AXIS OF TYPE TIME
    // when using an xasis of type 'time', the dataset is an array of array. The first value of each array is the timestamp followed by
    // all the values (one per linechart). The timestamp can be in ms, or ISO string (and other formats)
    var chartdataset = [];
    var maxchart = Math.min(50, MAX_NUMBER_OF_VALUES_DISPLAYED, DATASET.length);

    for (var i = 0; i < TIMESCALE.length; i++) {
      chartdataset.push([TIMESCALE[i]]);
      for (var j = 0; j < maxchart; j++)
        chartdataset[i].push(DATASET[j].counters[i]);
      for (var j = 0; j < maxchart; j++)
        chartdataset[i].push(DATASET[j].leadtime_avg[i]);
    }

    // Set the dimensions of the chart data
    var dimensions = ['timestamp'];
    for (var i = 0; i < maxchart; i++)
      dimensions.push(DATASET[i].value + ' #cases');

    for (var i = 0; i < maxchart; i++)
      dimensions.push(DATASET[i].value + ' days');

    // set the series for the chart
    var series = [];

    // average leadtime
    for (var i = 0; i < maxchart; i++) {
      series.push(
        {
          name: DATASET[i].value + ' days',
          tooltip: {
            valueFormatter: (value) => value.toFixed(1)
          },
          type: 'line',
          encode: {
            x: 'timestamp',
            y: DATASET[i].value + ' days',
          }
        }
      );
    }

    // volume of cases (count)
    for (var i = 0; i < maxchart; i++) {
      series.push(
        {
          name: DATASET[i].value + ' #cases',
          type: 'bar',
          stack: 'Ad',
          xAxisIndex: 1,
          yAxisIndex: 1,
          encode: {
            x: 'timestamp',
            y: DATASET[i].value + ' #cases',
          }
        }
      );
    }
    // console.log(chartdataset);
    // CHART RENDERING

    // CHART COLORS
    // we need to limit the size of colors to the size of maxchart
    var colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'];
    colors = colors.slice(0, maxchart);

    // TOOLTIP
    // OPTIONAL: refactor the tooltip entirely
    // That is useful to format the date, or to regroup the datasets (count and leadtime in the same row)
    function tooltipFormatter(params) {
      // see what params looks like in the console. It is an array, one entry per linechart. The dataset is the same in each array params[i].data
      // console.log(params);
      var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      var aDate = new Date(parseInt(params[0].axisValue));
      var tooltip;
      switch (GROUPBY) {
        case 'day': tooltip = aDate.toDateString() + '<br />'; break;
        case 'week': tooltip = 'Week ' + aDate.toDateString() + '<br />'; break;
        case 'month': tooltip = aDate.getFullYear().toString() + '-' + months[aDate.getUTCMonth()] + '<br />'; break;
        case 'year': tooltip = aDate.getFullYear().toString() + '<br />'; break;
      }
      var params_data = params[0].data;
      // data[0] is the timestamp, marker is different in each params[i]
      for (var i = 1; i < params_data.length / 2; i++)
        tooltip += params[i - 1].marker + ' ' + DATASET[i-1].value + ': ' +  params_data[i] + ' cases, ' + params_data[i].toFixed(1) + ' days <br />';
      return (tooltip);
    };

    var tooltip = {
      trigger: 'axis',
      formatter: tooltipFormatter,
      borderWidth: 1,
      borderColor: '#ccc',
      padding: 10,
      textStyle: {
        color: '#000'
      },
      // OPTIONNALY POSITION THE TOOL
      /*
      position: function (pos, params, el, elRect, size) {
        const obj = {
          top: 10
        };
        obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
        return obj;
      }*/
    };



    var option = {
      color: colors,
      dataset: {
        source: chartdataset,
        dimensions: dimensions,
      },

      axisPointer: {
        link: [
          {
            xAxisIndex: 'all'
          }
        ],
        label: {
          backgroundColor: '#777'
        }
      },

      grid: [
        {
          left: '7%',
          top: '7%',
          width: '70%',
          height: '50%'
        },
        {
          left: '7%',
          bottom: '7%',
          width: '70%',
          height: '20%'
        }
      ],

      yAxis: [
        {
          scale: true,
          name: 'avg leadtime',
          splitArea: {
            show: true
          }
        },

        {
          scale: true,
          name: '# cases',
          gridIndex: 1,
          splitNumber: 2,
          //axisLabel: { show: false },
          //axisLine: { show: false },
          //axisTick: { show: false },
          //splitLine: { show: false }
        }
      ],
      xAxis: [
        {
          type: 'time',
          boundaryGap: false,

          axisLine: { onZero: false },
          splitLine: { show: false },
          min: 'dataMin',
          max: 'dataMax',
          axisPointer: {
            z: 100
          }
        },
        {
          type: 'time',
          gridIndex: 1,
          boundaryGap: false,
          axisLine: { onZero: false },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false },
          min: 'dataMin',
          max: 'dataMax'
        }
      ],
      series: series,
      legend: {
        show: 'true',
        bottom: 'auto',
        right: 0,
        orient: 'vertical'
      },
      tooltip: tooltip
    };


    var div = document.getElementById(context.scope.widgetId + '_div');

    if (div) {
      // retrieve the chart created in init()
      var myChart = echarts.getInstanceByDom(div);
      myChart.setOption(option);
    }

  },

  resize: function (size, context) {
    var div = document.getElementById(context.scope.widgetId + '_div');

    if (div) {
      var myChart = echarts.getInstanceByDom(div);
      myChart.resize(
        {
          height: size.height,
          width: size.width
        });

    }
  }
};
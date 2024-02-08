  return {

    init: function (context) {
      var widget = document.getElementById(context.scope.widgetId);
      var div = document.createElement('div');
      div.id = context.scope.widgetId + '_div'; // creates a unique div id
      widget.appendChild(div);
      echarts.init(div);
    },

    update: function (data, context) {

      function tooltipFormatter(params) {
        // see what params looks like in the console. It is an array, one entry per linechart. The dataset is the same in each array params[i].data
        // console.log(params);
        var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        var aDate = new Date(parseInt(params[0].axisValue));
        var tooltip;
        switch (context.scope.data.GROUPBY){
          case 'day': tooltip = aDate.toDateString() + '<br />'; break;
          case 'week': tooltip = 'Week ' + aDate.toDateString() + '<br />'; break;
          case 'month': tooltip = aDate.getFullYear().toString() + '-' + months[aDate.getUTCMonth()]+ '<br />'; break;
          case 'year': tooltip = aDate.getFullYear().toString()+ '<br />'; break;
        }
        //tooltip = params[0].axisValueLabel;
        var dataset = params[0].data;
        // data[0] is the timestamp, marker is different in each params[i]
        for (var i = 1; i < dataset.length; i++)
          tooltip += params[i - 1].marker + ' ' + dataset[i].toFixed(1) + ' days <br />';
        return (tooltip);
      };

      context.scope.data = data;
      // compute leadtime average 
      var aDay = 24 * 60 * 60 * 1000;
      for (var i = 0; i < data.dataset.length; i++) { // avoid division by zero
        data.dataset[i].leadtime_avg = [];
        for (var j = 0; j < data.dataset[i].leadtime_sums.length; j++)
          if (data.dataset[i].leadtime_sums[j] && data.dataset[i].counters[j])
            data.dataset[i].leadtime_avg.push(data.dataset[i].leadtime_sums[j] / data.dataset[i].counters[j] / aDay);
          else
            data.dataset[i].leadtime_avg.push(0);
      }
      // compute sum of each value
      for (var i = 0; i < data.dataset.length; i++) {
        data.dataset[i].count = data.dataset[i].counters.reduce((accumulator, currentValue) => accumulator + currentValue);
      }
      // sort the dataset by count, largest first

      data.dataset.sort(function (a, b) {
        return b.count - a.count;
      });

      // when using an xasis of type 'time', the dataset is an array of array. The first value of each array is the timestamp followed by
      // all the values (one per linechart). The timestamp can be in ms, or ISO string (and other formats)
      var chartdata = [];
      var maxchart = Math.min(50, data.MAX_NUMBER_OF_VALUES_DISPLAYED, data.dataset.length);

      for (var i = 0; i < data.timeScale.length; i++) {
        chartdata.push([data.timeScale[i]]);
        for (var j = 0; j < maxchart; j++)
          chartdata[i].push(data.dataset[j].leadtime_avg[i]);
      }

      // setting the dimensions of the data
      var dimensions = ['timestamp'];
      for (var i = 0; i < maxchart; i++)
        dimensions.push(data.dataset[i].value);


      // setting the series for the chart
      var series = [];
      for (var i = 0; i < maxchart; i++) {
        series.push(
          {
            name: data.dataset[i].value,
            type: 'line',
            encode: {
              x: 'timestamp',
              y: data.dataset[i].value,
            }
          }
        );
      }
      //console.log(data);


      var div = document.getElementById(context.scope.widgetId + '_div');

      if (div) {
        var myChart = echarts.getInstanceByDom(div);

        var maxInterval;
        switch (data.TIME_LABEL_UNIT){
          case 'year': maxInterval = 365 * 3600 * 1000 * 24; break;
          case 'month': maxInterval = 30 * 3600 * 1000 * 24; break;
          case 'week': maxInterval = 7 * 3600 * 1000 * 24; break;
          case 'day': maxInterval = 3600 * 1000 * 24; break;
        }
        var option = {
          xAxis: {
            type: 'time',
            boundaryGap: false,
            maxInterval: maxInterval,
            axisLabel: { rotate: 50, interval: 0 },
          },
          yAxis: {
            type: 'value',
            name: 'avg leadtime (days)'
          },
          dataset: {
            source: chartdata,
            dimensions: dimensions,
          },
          series: series,
            title: {
            text: 'Avg leadtime for top ' + data.MAX_NUMBER_OF_VALUES_DISPLAYED + ' values of ' + data.DIMENSION + ' grouped by ' + data.GROUPBY,
            bottom: 10,
            left: 'center'
          },
          tooltip: {
            trigger: 'axis',
            formatter: tooltipFormatter
          },
          legend: {
            show: true,
          }
        };


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
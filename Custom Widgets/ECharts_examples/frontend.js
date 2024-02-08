return {
	init: function(context){
      
      var widget = document.getElementById(context.scope.widgetId);
      var div = document.createElement('div');
      div.id = context.scope.widgetId + '_div'; // creates a unique div id
      widget.appendChild(div);
      echarts.init(div);
	},

	update: function(data, context){
      
      var div = document.getElementById(context.scope.widgetId + '_div');
      
      if(div) {
        var myChart = echarts.getInstanceByDom(div);
        var option = {
          xAxis: {
            type: 'category',
            data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              data: [150, 230, 224, 218, 135, 147, 260],
              type: 'line'
            }
          ]
        };
        myChart.setOption(option);
      }

	},

	resize: function(size, context){
      var div = document.getElementById(context.scope.widgetId + '_div');
      
      if(div) {
        var myChart = echarts.getInstanceByDom(div);
        myChart.resize(
        {
          height: size.height,
          width: size.width
        });

      }
	}
};
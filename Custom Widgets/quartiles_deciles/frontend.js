return {

	
	init: function(context){
		var widget = document.getElementById(context.scope.widgetId);
		var div = document.createElement('div');
		div.id = context.scope.widgetId + '_div'; // creates a unique div id
		widget.appendChild(div);
		echarts.init(div);
	},

	update: function(data, context){


		const formatDuration = ms => {
			if (ms < 0) {
				ms = 0;
			}
			const time = {
			  d: Math.floor(ms / 86400000),
			  h: Math.floor(ms / 3600000) % 24,
			  m: Math.floor(ms / 60000) % 60,
			  s: Math.floor(ms / 1000) % 60,
			  ms: Math.floor(ms) % 1000
			};
			return Object.entries(time)
			  .filter(val => val[1] !== 0)
			  .map(([key, val]) => `${val} ${key}${val !== 1 ? '' : ''}`)
			  .join(', ');
		  };

        context.scope.data = data;
		// transform the displayed value if data.TYPE = 1 (duration)
		if (data.TYPE == 'DURATION'){
			// duration
			data.MIN = formatDuration(data.MIN);
			data.MAX = formatDuration(data.MAX);
			data.Q1 = formatDuration(data.Q1);
			data.MEDIAN = formatDuration(data.MEDIAN);
			data.Q3 = formatDuration(data.Q3);
			data.IQR = formatDuration(data.IQR);
			data.LOW_OUTLIER = formatDuration(data.LOW_OUTLIER);
			data.HIGH_OUTLIER = formatDuration(data.HIGH_OUTLIER);
			data.DECILE_1 = formatDuration(data.DECILE_1);
			data.DECILE_9 = formatDuration(data.DECILE_9);

		}

	},

	resize: function(size, context){
  
	}
};
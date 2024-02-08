(function(){

    function getMedianIndexes(a, b){
        // a and b are indexes in an array
        var len = b - a + 1;
        if (len % 2)
            // odd number of values
            return [a + (len - 1)/2 , a + (len + 1)/2];
        else
            // even number of values
            return [a + len/2 - 1, a + len/2];
    }

    function filterAndComputeMetrics(trace) {
        // Use this metrics variable for your own metrics (add more if needed)
        var metrics = {
            'exclude': 0,
            'value': 0,            
            'leadtime': 0
        };

        var firstevent = trace.get(0).getStartTime();
        var lastevent = firstevent;
        if (this.CUSTOMMETRIC) {
            metrics.value = API.getCustomMetricValue(this.DIMENSION, trace);
            if (metrics.value == null) {
                metrics.exclude = 1;
                return metrics;
            }
        }
        // Compute the leadtime, get the starttime of ACTIVITY, get DIMENSION value
        for (var k = 0; k < trace.size(); k++) {
            var event = trace.get(k);
            // needed to compute the leadtime
            if (event.getStartTime() < firstevent) {
                firstevent = event.getStartTime();
            }
            else if (event.getStartTime() > lastevent)
                lastevent = event.getStartTime();

            // select the start time we want to use for the trend
            // in case of DIMENSION, get the value from a specific ACTIVITY 
            // if ACTIVITY=='PROCESS' we take the starttime of the process
            if ((this.ACTIVITY == 'PROCESS') && (k==0)) {
                metrics.eventTime = event.getStartTime();
                if (this.TYPE == 'INTEGER') // get the DIMENSION value from the first event
                    metrics.value = event.getIntCustomAttributeValue(this.DIMENSION);
                else metrics.value = event.getDoubleCustomAttributeValue(this.DIMENSION);
            }
            else if (event.getEventClass() == this.ACTIVITY) {
                metrics.eventTime = event.getStartTime();
                if (this.TYPE == 'INTEGER') // get the DIMENSION value from the first event
                    metrics.value = event.getIntCustomAttributeValue(this.DIMENSION);
                else metrics.value = event.getDoubleCustomAttributeValue(this.DIMENSION);
            }
        }
        if (metrics.value == '') {
            if (this.KEEP_EMPTY_VALUES[0] == 'n') { // exclude cases with no value for DIMENSION
                metrics.exclude = 1;
            }
            else { // keep the case and replace the value with None
                metrics.value = "None";
            }
        }
        metrics.leadtime = lastevent - firstevent;
        if (metrics.eventTime == 0) metrics.exclude = 1; // ACTIVITY NOT FOUND
        return metrics;
    }

    return {
        init: function(params) {
            this.DIMENSION = params.DIMENSION;
            var typeChoices = ['DURATION','NUMERIC','INTEGER']
            if (params.TYPE.indexOf(typeChoices) < 0)
                this.TYPE =  'NUMERIC'; // default
            // if DIMENSION is a custom metric remove attr-custom-metrics from the name
            if (this.DIMENSION.contains('attr-custom-metrics')){
                this.DIMENSION = this.DIMENSION.replace('attr-custom-metrics','');
                this.CUSTOMMETRIC = 1; // custom metric
            }
            else // standard dimension
            {                
                this.DIMENSION = this.DIMENSION.replace('attr-custom-', '');
                this.CUSTOMMETRIC = 0; // standard dimension
            }
            this.ACTIVITY = params.ACTIVITY; // the activity in which we find the value of the dimension and from which we take the timestamp
            if (this.ACTIVITY == '') this.ACTIVITY = 'PROCESS';
            this.KEEP_EMPTY_VALUES = params.KEEP_EMPTY_VALUES; // "yes"=keep cases when value=='', "no"= exclude these cases
            if (this.KEEP_EMPTY_VALUES == '') this.KEEP_EMPTY_VALUES= 'no';
            else if (this.KEEP_EMPTY_VALUES[0] == 'y') this.KEEP_EMPTY_VALUES = 'yes';
            else this.KEEP_EMPTY_VALUES = 'no';
            this.dataset = [];
        },
    
        update: function(trace) {
    
            if(trace.getDiscarded == 1) {
                return;
            }

            var metrics = filterAndComputeMetrics(trace);
            if (metrics.exclude) return;

            this.dataset.push(metrics.value);
            return;
        },
        
        finalize: function(output) {
            var n = this.dataset.length;
            output.LEN = n;
            // sort the array
            this.dataset.sort(function(a, b){ return a - b});

            output.MIN = this.dataset[0];
            output.MAX = this.dataset[n - 1];

            // Median
            // For sets with an odd number of members, n is odd:
            // Median = value of the ((n+1)/2)th item in the sorted set
            // For sets with an even number of members, n is even:
            // Median = value of the [(n/2)th item + (n/2 + 1)th item] / 2 in the sorted set
            // If the size of the data set is odd, do not include the median when finding the first and third quartiles.

            n = this.dataset.length;
            if (n % 2){ 
                //odd number of data
                //odd: 0 1 2 q1=3 4 5 6 m=7 8 9 10 q3=11 12 13 14 
                //odd: 0 1 2 avg(3, 4) 5 6 7 m=8 9 10 11 avg(12, 13) 14 15 16
                var m = (n-1)/2;
                output.MEDIAN = this.dataset[m];
                // exclude the median to compute Q1 and Q3
                var r = getMedianIndexes(0, m-1);
                output.Q1 = (this.dataset[r[0]] + this.dataset[r[1]]) / 2;
                r = getMedianIndexes(m+1, n);
                output.Q3 = (this.dataset[r[0]] + this.dataset[r[1]]) / 2;
            }
            else{
                // m = 5
                // even: 0 1 avg(2, 3) 4 avg(5, 6) 7 avg(8, 9) 10 11 
                // even: 0 1 2 q1=3 4 5 avg(6, 7) 8 9 q3=10 11 12 13
                var m = n/2 - 1;
                output.MEDIAN = (this.dataset[m] + this.dataset[m+1]) / 2;
                var r = getMedianIndexes(0, m);
                output.Q1 = (this.dataset[r[0]] + this.dataset[r[1]]) / 2;
                r = getMedianIndexes(m+1, n);
                output.Q3 = (this.dataset[r[0]] + this.dataset[r[1]]) / 2;
            }

            output.IQR = output.Q3 - output.Q1;
            output.LOW_OUTLIER = output.Q1 - 1.5*output.IQR;
            output.HIGH_OUTLIER = output.Q3 + 1.5*output.IQR;
            output.DECILE_1 = this.dataset[Math.floor(output.LEN / 10)];
            output.DECILE_9 = this.dataset[Math.floor(output.LEN * 9/10)]
            output.DIMENSION = this.DIMENSION;
            output.TYPE = this.TYPE;
            output.CUSTOMMETRIC =  this.CUSTOMMETRIC;
            output.ACTIVITY = this.ACTIVITY;
        }
    };})();


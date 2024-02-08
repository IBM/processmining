(function () {

    function filterAndComputeMetrics(trace) {
        // Use this metrics variable for your own metrics (add more if needed)
        var metrics = {
            'exclude': 0,
            'value': 0,
            'eventTime': 0,
            'leadtime': 0
        };
        var firstevent = trace.get(0).getStartTime();
        var lastevent = firstevent;
        for (var k = 0; k < trace.size(); k++) {
            var event = trace.get(k);
            if (event.getStartTime() < firstevent) {
                firstevent = event.getStartTime();
            }
            else if (event.getStartTime() > lastevent)
                lastevent = event.getStartTime();

            if (event.getEventClass() == ACTIVITY) { // don't break if found, we need parse all the events for the leadtime
                metrics.value = event.getStringCustomAttributeValue(DIMENSION);
                if (metrics.value == '') {
                    if (KEEP_EMPTY_VALUES[0] == 'n') { // exclude cases with no value for DIMENSION
                        metrics.exclude = 1;
                    }
                    else { // keep the case and replace the value with None
                        metrics.value = "None";
                    }
                }
                metrics.eventTime = event.getStartTime();
            }
        }
        metrics.leadtime = lastevent - firstevent;
        //metrics.leadtime = trace.get(trace.size() - 1).getStartTime() - trace.get(0).getStartTime();
        if (metrics.eventTime == 0) metrics.exclude = 1; // ACTIVITY NOT FOUND
        return metrics;
    }

    return {
        init: function (params) {
            var groupByChoices = ['day', 'week', 'month', 'year'];

            DIMENSION = params.DIMENSION.replace('attr-custom-', '');

            ACTIVITY = params.ACTIVITY; // the activity in which we find the value of the dimension
            KEEP_EMPTY_VALUES = params.KEEP_EMPTY_VALUES; // "yes"=keep cases when value=='', "no"= exclude these cases

            MAX_NUMBER_OF_VALUES_DISPLAYED = params.MAX_NUMBER_OF_VALUES_DISPLAYED; // show top N values (max is hardcoded at 50)
            if (MAX_NUMBER_OF_VALUES_DISPLAYED == '')
                MAX_NUMBER_OF_VALUES_DISPLAYED = 50;
            else
                MAX_NUMBER_OF_VALUES_DISPLAYED = Math.min(50, Number(MAX_NUMBER_OF_VALUES_DISPLAYED));

            dataset = [];
        },

        update: function (trace) {

            if (trace.getDiscarded == 1) {
                return;
            }

            var metrics = filterAndComputeMetrics(trace);
            if (metrics.exclude)
                return;

            if (dataset.length == 0) { // first case
                dataset.push({
                    'value': metrics.value,
                    'case_count': 1,
                    'leadtime_sum': metrics.leadtime
                });
                return;
            }

            // search the index of 'value' in the dataset array
            var valueindex = -1;
            for (var k = 0; k < dataset.length; k++) {
                if (dataset[k].value == metrics.value) {
                    valueindex = k;
                    dataset[k].case_count += 1;
                    dataset[k].leadtime_sum += metrics.leadtime;
                    break;
                }
            }
            if (valueindex < 0) {// value not yet added; add it to dataset
                dataset.push({
                    'value': metrics.value,
                    'case_count': 1,
                    'leadtime_sum': metrics.leadtime
                });
            }
        },

        finalize: function (output) {
            output.DIMENSION = DIMENSION;
            output.MAX_NUMBER_OF_VALUES_DISPLAYED = MAX_NUMBER_OF_VALUES_DISPLAYED;
            output.ACTIVITY = ACTIVITY;
            output.dataset = dataset;
        }
    };
})();


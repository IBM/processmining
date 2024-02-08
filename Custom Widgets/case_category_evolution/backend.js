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
        if (CUSTOM_METRIC) {
            metrics.value = API.getCustomMetricValue(CUSTOM_METRIC, trace);
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
            if (ACTIVITY == 'PROCESS' && k==0) {
                metrics.eventTime = event.getStartTime();
                if (DIMENSION) // get the DIMENSION value from the first event
                    metrics.value = event.getStringCustomAttributeValue(DIMENSION);
            }
            else if (event.getEventClass() == ACTIVITY) {
                metrics.eventTime = event.getStartTime();
                if (DIMENSION) // get the DIMENSION value from this event
                    metrics.value = event.getStringCustomAttributeValue(DIMENSION);
            }
        }
        if (metrics.value == '') {
            if (KEEP_EMPTY_VALUES[0] == 'n') { // exclude cases with no value for DIMENSION
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

    function computeScale(groupBy, aDate) {
        // Update timeScale array, and push new counters to each dataset value

        var newtimeScale = [];
        var appendCounters = [];
        aDate.setHours(0, 0, 0, 0);
        switch (groupBy) {
            case "week": aDate.setDate(aDate.getDate() - aDate.getDay()); break;
            case "month": aDate.setMonth(aDate.getMonth(), 1); break;
            case "year": aDate.setFullYear(aDate.getFullYear(), 0, 1); break;
        }
        var eventTime = aDate.getTime();

        if (timeScale.length == 0) { // first event
            timeScale.push(eventTime);
        }
        else if (eventTime < timeScale[0]) { // create new dates array and concat it with previous, until earliestTimePrevious
            aDate.setTime(eventTime);
            while (aDate.getTime() < timeScale[0]) {
                newtimeScale.push(aDate.getTime());
                switch (groupBy) {
                    case "day": aDate.setDate(aDate.getDate() + 1); break;
                    case "week": aDate.setDate(aDate.getDate() + 7); break;
                    case "month": aDate.setMonth(aDate.getMonth() + 1); break;
                    case "year": aDate.setFullYear(aDate.getFullYear() + 1); break;
                }
                appendCounters.push(0);
            }
            timeScale = newtimeScale.concat(timeScale);
            for (k = 0; k < dataset.length; k++) {
                dataset[k].counters = appendCounters.concat(dataset[k].counters);
                dataset[k].leadtime_sums = appendCounters.concat(dataset[k].leadtime_sums);
            }
        }
        else if (eventTime > timeScale[timeScale.length - 1]) { // last time was the latest, eventTime is later: add days
            aDate.setTime(timeScale[timeScale.length - 1]);
            while (aDate.getTime() < eventTime) {
                switch (groupBy) {
                    case "day": aDate.setDate(aDate.getDate() + 1); break;
                    case "week": aDate.setDate(aDate.getDate() + 7); break;
                    case "month": aDate.setMonth(aDate.getMonth() + 1); break;
                    case "year": aDate.setFullYear(aDate.getFullYear() + 1); break;
                }
                timeScale.push(aDate.getTime());
                for (k = 0; k < dataset.length; k++) {
                    dataset[k].counters.push(0); // add 0 for each new date, to each counter array
                    dataset[k].leadtime_sums.push(0); // add 0 for each new date, to each counter array
                }
            }
        }
        return eventTime;
    }

    return {
        init: function (params) {
            var groupByChoices = ['day', 'week', 'month', 'year'];
            CUSTOM_METRIC = 0;
            DIMENSION = 0;
            // Is the selected dimension a standard dimension or a custom metric? Check the name
            if (params.DIMENSION.indexOf('attr-custom-metrics') >= 0)
                CUSTOM_METRIC = params.DIMENSION.replace('attr-custom-metrics', '');
            else if (params.DIMENSION.indexOf('attr-custom-') >= 0)
                DIMENSION = params.DIMENSION.replace('attr-custom-', '');

            // Which date to use: PROCESS or ACTIVITY_NAME
            // Which time to use: STARTTIME, ENDTIME
            GROUPBY = params.GROUPBY;
            EVENT_TIME = params.EVENT_TIME; // can be 'STARTTIME' or 'ENDTIME'
            var groupByIndex = groupByChoices.indexOf(GROUPBY);
            if (groupByIndex < 0){
                GROUPBY = 'month';
                groupByIndex = groupByChoices.indexOf(GROUPBY);
            }
            TIME_LABEL_UNIT = params.TIME_LABEL_UNIT;
            var time_label_unit_index = groupByChoices.indexOf(TIME_LABEL_UNIT);
            if (time_label_unit_index < 0){
                TIME_LABEL_UNIT = 'month';
                time_label_unit_index = groupByChoices.indexOf(TIME_LABEL_UNIT);
            } 
            if (time_label_unit_index < groupByIndex)
                TIME_LABEL_UNIT = groupByChoices[groupByIndex]

            ACTIVITY = params.ACTIVITY; // the activity in which we find the value of the dimension and from which we take the timestamp
            if (ACTIVITY == '') ACTIVITY = 'PROCESS';

            KEEP_EMPTY_VALUES = params.KEEP_EMPTY_VALUES; // "yes"=keep cases when value=='', "no"= exclude these cases
            if (KEEP_EMPTY_VALUES == '') KEEP_EMPTY_VALUES= 'no';
            else if (KEEP_EMPTY_VALUES[0] == 'y') KEEP_EMPTY_VALUES = 'yes';
            else KEEP_EMPTY_VALUES = 'no';

            MAX_NUMBER_OF_VALUES_DISPLAYED = params.MAX_NUMBER_OF_VALUES_DISPLAYED; // show top N values (max is hardcoded at 50)
            if (MAX_NUMBER_OF_VALUES_DISPLAYED == '')
                MAX_NUMBER_OF_VALUES_DISPLAYED = 50;
            else
                MAX_NUMBER_OF_VALUES_DISPLAYED = Math.min(50, Number(MAX_NUMBER_OF_VALUES_DISPLAYED));

            DISPLAY_LEGEND = params.DISPLAY_LEGEND;
            if (DISPLAY_LEGEND == '') DISPLAY_LEGEND = true;
            else if (DISPLAY_LEGEND[0] == 'n') DISPLAY_LEGEND = false;
            else DISPLAY_LEGEND = true;

            timeScale = [];
            dataset = [];
            console.log('init() ends');

        },

        update: function (trace) {

            if (trace.getDiscarded == 1) {
                return;
            }

            var metrics = filterAndComputeMetrics(trace);
            if (metrics.exclude)
                return;

            eventTime = computeScale(GROUPBY, new Date(metrics.eventTime));

            if (dataset.length == 0) { // first event
                dataset.push({
                    'value': metrics.value,
                    'counters': [1],
                    'leadtime_sums': [metrics.leadtime]
                });
                return;
            }

            // search the index of 'value' in the dataset array
            var valueindex = -1;
            for (var k = 0; k < dataset.length; k++) {
                if (dataset[k].value == metrics.value) {
                    valueindex = k;
                    break;
                }
            }
            if (valueindex < 0) {// value not yet added; add it to dataset
                valueindex = dataset.push({
                    'value': metrics.value,
                    'counters': [],
                    'leadtime_sums': []
                }) - 1;
                // update counters
                for (var ii = 0; ii < dataset[0].counters.length; ii++) {
                    dataset[valueindex].counters.push(0);
                    dataset[valueindex].leadtime_sums.push(0);
                }
            }

            // update the counters
            dataset[valueindex].counters[timeScale.indexOf(eventTime)]++;
            dataset[valueindex].leadtime_sums[timeScale.indexOf(eventTime)] += metrics.leadtime;
        },

        finalize: function (output) {
            output.DIMENSION = (DIMENSION ? DIMENSION: CUSTOM_METRIC);
            output.GROUPBY = GROUPBY;
            output.TIME_LABEL_UNIT = TIME_LABEL_UNIT;
            output.MAX_NUMBER_OF_VALUES_DISPLAYED = MAX_NUMBER_OF_VALUES_DISPLAYED;
            output.ACTIVITY = ACTIVITY;
            output.TIMESCALE = timeScale;
            output.DATASET = dataset;
            output.DISPLAY_LEGEND = DISPLAY_LEGEND;
            console.log('finalize() done');
        }
    };
})();


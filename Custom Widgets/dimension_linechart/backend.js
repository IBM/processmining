(function () {

    function filterAndComputeMetrics(trace) {
        // Use this metrics variable for your own metrics (add more if needed)
        var metrics = {
            exclude: 0,
            value: 0,
            eventTime: 0
        };
        for (var i = 0; i < trace.size(); i++) {
            var event = trace.get(i);

            if (event.getEventClass() == ACTIVITY) {
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
                break;
            }
        }
        if (metrics.eventTime == 0) metrics.exclude = 1; // ACTIVITY NOT FOUND
        return metrics;
    }

    function computeScale(groupBy, aDate) {
        // Update timesScale array, and push new counters to each dataset value

        var newTimeScale = [];
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
                newTimeScale.push(aDate.getTime());
                switch (groupBy) {
                    case "day": aDate.setDate(aDate.getDate() + 1); break;
                    case "week": aDate.setDate(aDate.getDate() + 7); break;
                    case "month": aDate.setMonth(aDate.getMonth() + 1); break;
                    case "year": aDate.setFullYear(aDate.getFullYear() + 1); break;
                }
                appendCounters.push(0);
            }
            timeScale = newTimeScale.concat(timeScale);
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
            var keepEmptyValuesChoices = ['yes', 'no'];

            DIMENSION = params.DIMENSION.replace('attr-custom-', '');
            GROUPBY = params.GROUPBY;
            if (groupByChoices.indexOf(GROUPBY) < 0)
                GROUPBY = 'month';
            TIME_LABEL_UNIT = params.TIME_LABEL_UNIT;
            if (groupByChoices.indexOf(TIME_LABEL_UNIT) < 0)
                TIME_LABEL_UNIT = 'month';

            ACTIVITY = params.ACTIVITY; // the activity in which we find the value of the dimension
            KEEP_EMPTY_VALUES = params.KEEP_EMPTY_VALUES; // "yes"=keep cases when value=='', "no"= exclude these cases
            if (keepEmptyValuesChoices.indexOf(KEEP_EMPTY_VALUES) < 0)
                KEEP_EMPTY_VALUES = 'no';

            MAX_NUMBER_OF_VALUES_DISPLAYED = params.MAX_NUMBER_OF_VALUES_DISPLAYED; // show top N values (max is hardcoded at 50)
            if (MAX_NUMBER_OF_VALUES_DISPLAYED == '')
                MAX_NUMBER_OF_VALUES_DISPLAYED = 50;
            else
                MAX_NUMBER_OF_VALUES_DISPLAYED = Math.min(50, Number(MAX_NUMBER_OF_VALUES_DISPLAYED));

            timeScale = [];
            dataset = [];
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
                    value: metrics.value,
                    counters: [1],
                    leadtime_sums: [metrics.leadtime]
                });
                return;
            }

            // search the index of 'value' in the dataset array
            var valueindex = -1;
            for (i = 0; i < dataset.length; i++) {
                if (dataset[i].value == metrics.value) {
                    valueindex = i;
                    break;
                }
            }
            if (valueindex < 0) {// value not yet added; add it to dataset
                valueindex = dataset.push({
                    value: metrics.value,
                    counters: [],
                    leadtime_sums: []
                }) - 1;
                // update counters
                for (var i = 0; i < dataset[0].counters.length; i++) {
                    dataset[valueindex].counters.push(0);
                    dataset[valueindex].leadtime_sums.push(0);
                }

            }
            // update the counters
            dataset[valueindex].counters[timeScale.indexOf(eventTime)]++;
            dataset[valueindex].leadtime_sums[timeScale.indexOf(eventTime)] += metrics.leadtime;
        },

        finalize: function (output) {
            output.DIMENSION = DIMENSION;
            output.GROUPBY = GROUPBY;
            output.TIME_LABEL_UNIT = TIME_LABEL_UNIT;
            output.MAX_NUMBER_OF_VALUES_DISPLAYED = MAX_NUMBER_OF_VALUES_DISPLAYED;
            output.ACTIVITY = ACTIVITY;
            output.timeScale = timeScale;
            output.dataset = dataset;
        }
    };
})();
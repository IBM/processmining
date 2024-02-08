
// TESTING THE WIDGET WITH FAKE DATA (not from the process)
function filterAndComputeMetrics_emulate(trace) {
    var values = ['a', 'b', 'c', 'd', 'e', 'f'];
    var metrics = {
        exclude: 0,
        value: 0,
        eventTime: 0
    };
    // emulate event.getStartTime()
    datePeriod.fromTime = new Date(datePeriod.fromDate).getTime();
    datePeriod.duration = new Date(datePeriod.toDate).getTime() - datePeriod.fromTime;
    metrics.eventTime = datePeriod.fromTime + Math.floor(Math.random() * datePeriod.duration);

    // emulate event.getStringCustomAttributeValue(DIMENSION);
    metrics.value = values[Math.floor(Math.random() * values.length)];

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
            }
        }
    }
    return eventTime;
}


function update(trace) {

    if (trace.getDiscarded == 1) {
        return;
    }

    var metrics = filterAndComputeMetrics_emulate(trace);
    if (metrics.exclude)
        return;

    eventTime = computeScale(GROUPBY, new Date(metrics.eventTime));

    if (dataset.length == 0) { // first event
        dataset.push({ 'value': metrics.value, 'counters': [1] });
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
        valueindex = dataset.push({value: metrics.value, counters: [] }) - 1;
        // update counters
        for (var i = 0; i < dataset[0].counters.length; i++)
            dataset[valueindex].counters.push(0);
    }
    // update the counters
    dataset[valueindex].counters[timeScale.indexOf(eventTime)]++;
}

// GLOBAL VARIABLES
var timeScale = [];
var dataset = [];
var GROUPBY = 'month';
var trace = {getDiscarded: 0 };

// period of dates to generate random start_times
var datePeriod = { fromDate: "2020-01-01", toDate: "2022-01-01" };
var numberOfCases = 1000;


// EMULATE the call to update() by process mining for all the cases
for (i = 0; i < numberOfCases; i++) {
    update(trace);
}

// CHECK that we compute correctly this.times and this.dataset
var nbevents = 0;
for (var k = 0; k < dataset.length; k++) {
    console.log(dataset[k].value);
    console.log(dataset[k].counters);
    for (var kk = 0; kk < timeScale.length; kk++)
        nbevents += dataset[k].counters[kk];
}
console.log("Number of events: " + nbevents);
console.log("timeScale :" + timeScale);


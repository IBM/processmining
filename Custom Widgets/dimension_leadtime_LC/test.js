console.log('start');
var this_times = [];
var this_dataset = [];
var startimes = [1709859600000, 1729123200000, 1673053200000, 1682035200000, 1710464400000, 1656979200000, 1666656000000, 1713571200000, 1716163200000, 1707613200000, 1670115600000, 1712534400000, 1732064400000, 1732669200000, 1698364800000, 1657065600000, 1689379200000, 1661472000000, 1660953600000, 1725148800000, 1727827200000, 1726963200000, 1692230400000, 1661817600000, 1690416000000, 1681603200000, 1671152400000, 1664496000000, 1702515600000, 1706317200000, 1675126800000, 1708650000000, 1727222400000, 1720742400000, 1730595600000, 1733619600000, 1707699600000, 1727136000000, 1733965200000, 1675818000000, 1715644800000, 1679360400000, 1723334400000, 1706230800000, 1662681600000, 1700528400000, 1656892800000, 1709427600000, 1724371200000, 1677373200000, 1717027200000, 1717372800000, 1722988800000, 1680739200000, 1716076800000, 1661472000000, 1688688000000, 1686873600000, 1730077200000, 1695081600000, 1672880400000, 1721779200000, 1684108800000, 1685318400000, 1699405200000, 1691539200000, 1715990400000, 1690416000000, 1672102800000, 1713484800000, 1704502800000, 1665446400000, 1722038400000, 1679706000000, 1724889600000, 1673312400000, 1658188800000, 1718409600000, 1686614400000, 1726963200000, 1661904000000, 1683244800000, 1711155600000, 1701565200000, 1719360000000, 1710982800000, 1664150400000, 1700182800000, 1682208000000, 1709514000000, 1693094400000, 1733014800000, 1728000000000, 1686873600000, 1719273600000, 1691452800000, 1694995200000, 1661212800000, 1711760400000, 1689811200000];
var values = ['a', 'b', 'c', 'd', 'e', 'f'];
var leadtimes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];


function filterAndComputeMetrics(trace) {
    // Compute number of shipnodekey involved
    // Use this metrics variable for your own metrics (add more if needed)
    var metrics = {
        'exclude': 0,
        'value': 0,
        'eventTime': 0,
        'leadtime': 0
    };

    metrics['eventTime'] = startimes[Math.floor(Math.random() * startimes.length)];
    metrics['value'] = values[Math.floor(Math.random() * values.length)];
    metrics['leadtime'] = leadtimes[Math.floor(Math.random() * leadtimes.length)];

    if (metrics['eventTime'] == 0) metrics['exclude'] = 1;
    return metrics;
}

function computeScale(groupBy, aDate) {
    // Update this_times array, and push new counters to each dataset value

    var newTimes = [];
    var appendCounters = [];
    aDate.setHours(0, 0, 0, 0);
    switch (groupBy) {
        case "week": aDate.setDate(aDate.getDate() - aDate.getDay()); break;
        case "month": aDate.setMonth(aDate.getMonth(), 1); break;
        case "year": aDate.setFullYear(aDate.getFullYear(), 0, 1); break;
    }
    var eventTime = aDate.getTime();

    if (this_times.length == 0) { // first event
        this_times.push(eventTime);
    }
    else if (eventTime < this_times[0]) { // create new dates array and concat it with previous, until earliestTimePrevious
        aDate.setTime(eventTime);
        while (aDate.getTime() < this_times[0]) {
            newTimes.push(aDate.getTime());
            switch (groupBy) {
                case "day": aDate.setDate(aDate.getDate() + 1); break;
                case "week": aDate.setDate(aDate.getDate() + 7); break;
                case "month": aDate.setMonth(aDate.getMonth() + 1); break;
                case "year": aDate.setFullYear(aDate.getFullYear() + 1); break;
            }
            appendCounters.push(0);
        }
        this_times = newTimes.concat(this_times);
        for (k = 0; k < this_dataset.length; k++) {
            this_dataset[k]['counters'] = appendCounters.concat(this_dataset[k]['counters']);
            this_dataset[k]['leadtime_sums'] = appendCounters.concat(this_dataset[k]['leadtime_sums']);
        }
    }
    else if (eventTime > this_times[this_times.length - 1]) { // last time was the latest, eventTime is later: add days
        aDate.setTime(this_times[this_times.length - 1]);
        while (aDate.getTime() < eventTime) {
            switch (groupBy) {
                case "day": aDate.setDate(aDate.getDate() + 1); break;
                case "week": aDate.setDate(aDate.getDate() + 7); break;
                case "month": aDate.setMonth(aDate.getMonth() + 1); break;
                case "year": aDate.setFullYear(aDate.getFullYear() + 1); break;
            }
            this_times.push(aDate.getTime());
            for (k = 0; k < this_dataset.length; k++) {
                this_dataset[k]['counters'].push(0); // add 0 for each new date, to each counter array
                this_dataset[k]['leadtime_sums'].push(0); // add 0 for each new date, to each counter array
            }
        }
    }
    return eventTime;
}

function trace(totalevents) {
    for (var i = 0; i < totalevents; i++) {

        var metrics = filterAndComputeMetrics(0);
        if (metrics['exclude'])
            continue;

        eventTime = computeScale(GROUPBY, new Date(metrics['eventTime']));
        if (this_dataset.length == 0) { // first event
            this_dataset.push({
                'value': metrics['value'],
                'counters': [1],
                'leadtime_sums': [metrics['leadtime']]
            });
            continue;
        }

        // search the index of 'value' in the this_dataset array
        var valueindex = -1;
        for (var k = 0; k < this_dataset.length; k++) {
            if (this_dataset[k]["value"] == metrics['value']) {
                valueindex = k;
                break;
            }
        }
        if (valueindex < 0) {// value not yet added; add it to this_dataset
            valueindex = this_dataset.push({
                'value': metrics['value'],
                'counters': [],
                'leadtime_sums': []
            }) - 1;
            // update counters
            for (var ii = 0; ii < this_dataset[0]['counters'].length; ii++) {
                this_dataset[valueindex]['counters'].push(0);
                this_dataset[valueindex]['leadtime_sums'].push(0);
            }
        }

        // update the counters
        this_dataset[valueindex]["counters"][this_times.indexOf(eventTime)]++;
        this_dataset[valueindex]["leadtime_sums"][this_times.indexOf(eventTime)] += metrics['leadtime'];

    }
}

var GROUPBY = "month";
trace(100);

var nbevents = 0;
for (var k = 0; k < this_dataset.length; k++) {
    console.log(this_dataset[k]['value']);
    console.log(this_dataset[k]['counters']);
    console.log(this_dataset[k]['leadtime_sums']);
    for (var kk = 0; kk < this_times.length; kk++)
        nbevents += this_dataset[k]['counters'][kk];
}
console.log(nbevents);
console.log(this_times);
console.log("end");

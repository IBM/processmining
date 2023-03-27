(function () {

    // TESTING THE WIDGET WITH FAKE DATA (not from the process)
    function filterAndComputeMetrics_test(trace) {
        var startimes = [1709859600000, 1729123200000, 1673053200000, 1682035200000, 1710464400000, 1656979200000, 1666656000000, 1713571200000, 1716163200000, 1707613200000, 1670115600000, 1712534400000, 1732064400000, 1732669200000, 1698364800000, 1657065600000, 1689379200000, 1661472000000, 1660953600000, 1725148800000, 1727827200000, 1726963200000, 1692230400000, 1661817600000, 1690416000000, 1681603200000, 1671152400000, 1664496000000, 1702515600000, 1706317200000, 1675126800000, 1708650000000, 1727222400000, 1720742400000, 1730595600000, 1733619600000, 1707699600000, 1727136000000, 1733965200000, 1675818000000, 1715644800000, 1679360400000, 1723334400000, 1706230800000, 1662681600000, 1700528400000, 1656892800000, 1709427600000, 1724371200000, 1677373200000, 1717027200000, 1717372800000, 1722988800000, 1680739200000, 1716076800000, 1661472000000, 1688688000000, 1686873600000, 1730077200000, 1695081600000, 1672880400000, 1721779200000, 1684108800000, 1685318400000, 1699405200000, 1691539200000, 1715990400000, 1690416000000, 1672102800000, 1713484800000, 1704502800000, 1665446400000, 1722038400000, 1679706000000, 1724889600000, 1673312400000, 1658188800000, 1718409600000, 1686614400000, 1726963200000, 1661904000000, 1683244800000, 1711155600000, 1701565200000, 1719360000000, 1710982800000, 1664150400000, 1700182800000, 1682208000000, 1709514000000, 1693094400000, 1733014800000, 1728000000000, 1686873600000, 1719273600000, 1691452800000, 1694995200000, 1661212800000, 1711760400000, 1689811200000];
        var values = ['a', 'b', 'c', 'd', 'e', 'f'];
        var metrics = {
            'exclude': 0,
            'value': 0,
            'eventTime': 0
        };
        metrics['eventTime'] = startimes[Math.floor(Math.random() * startimes.length)];
        metrics['value'] = values[Math.floor(Math.random() * values.length)];
        if (metrics['eventTime'] == 0) metrics['exclude'] = 1;
        return metrics;
    }


    function filterAndComputeMetrics(trace) {
        // Use this metrics variable for your own metrics (add more if needed)
        var metrics = {
            'exclude': 0,
            'value': 0,
            'eventTime': 0
        };
        for (var k = 0; k < trace.size(); k++) {
            var event = trace.get(k);
            
            if (event.getEventClass() == this.ACTIVITY) {
                metrics['value'] = event.getStringCustomAttributeValue(this.DIMENSION);
                if (metrics['value'] == '') {
                    if (this.KEEP_EMPTY_VALUES[0] == 'n') { // exclude cases with no value for DIMENSION
                        metrics['exclude'] = 1;
                    }
                    else { // keep the case and replace the value with None
                        metrics['value'] = "None";
                    }
                }
                metrics['eventTime'] = event.getStartTime();
                break;
            }
        }
        if (metrics['eventTime'] == 0) metrics['exclude'] = 1; // this.ACTIVITY NOT FOUND
        return metrics;
    }

    function computeScale(groupBy, aDate) {
        // Update this.times array, and push new counters to each dataset value

        var newTimes = [];
        var appendCounters = [];
        aDate.setHours(0, 0, 0, 0);
        switch (groupBy) {
            case "week": aDate.setDate(aDate.getDate() - aDate.getDay()); break;
            case "month": aDate.setMonth(aDate.getMonth(), 1); break;
            case "year": aDate.setFullYear(aDate.getFullYear(), 0, 1); break;
        }
        var eventTime = aDate.getTime();

        if (this.times.length == 0) { // first event
            this.times.push(eventTime);
        }
        else if (eventTime < this.times[0]) { // create new dates array and concat it with previous, until earliestTimePrevious
            aDate.setTime(eventTime);
            while (aDate.getTime() < this.times[0]) {
                newTimes.push(aDate.getTime());
                switch (groupBy) {
                    case "day": aDate.setDate(aDate.getDate() + 1); break;
                    case "week": aDate.setDate(aDate.getDate() + 7); break;
                    case "month": aDate.setMonth(aDate.getMonth() + 1); break;
                    case "year": aDate.setFullYear(aDate.getFullYear() + 1); break;
                }
                appendCounters.push(0);
            }
            this.times = newTimes.concat(this.times);
            for (k = 0; k < this.dataset.length; k++) {
                this.dataset[k]['counters'] = appendCounters.concat(this.dataset[k]['counters']);
            }
        }
        else if (eventTime > this.times[this.times.length - 1]) { // last time was the latest, eventTime is later: add days
            aDate.setTime(this.times[this.times.length - 1]);
            while (aDate.getTime() < eventTime) {
                switch (groupBy) {
                    case "day": aDate.setDate(aDate.getDate() + 1); break;
                    case "week": aDate.setDate(aDate.getDate() + 7); break;
                    case "month": aDate.setMonth(aDate.getMonth() + 1); break;
                    case "year": aDate.setFullYear(aDate.getFullYear() + 1); break;
                }
                this.times.push(aDate.getTime());
                for (k = 0; k < dataset.length; k++) {
                    this.dataset[k]['counters'].push(0); // add 0 for each new date, to each counter array
                }
            }
        }
        return eventTime;
    }


    return {
        init: function (params) {
            var groupByChoices = ['day', 'week', 'month', 'year'];

            this.DIMENSION = params.DIMENSION.replace('attr-custom-', '');
            this.GROUPBY = params.GROUPBY;
            if (groupByChoices.indexOf(this.GROUPBY) < 0)
                this.GROUPBY = 'month';
            this.TIME_LABEL_UNIT = params.TIME_LABEL_UNIT;
            if (groupByChoices.indexOf(this.TIME_LABEL_UNIT) < 0)
                this.TIME_LABEL_UNIT = 'month';

            this.ACTIVITY = params.ACTIVITY; // the activity in which we find the value of the dimension
            this.KEEP_EMPTY_VALUES = params.KEEP_EMPTY_VALUES; // "yes"=keep cases when value=='', "no"= exclude these cases

            this.MAX_NUMBER_OF_VALUES_DISPLAYED = params.MAX_NUMBER_OF_VALUES_DISPLAYED; // show top N values (max is hardcoded at 50)
            if (this.MAX_NUMBER_OF_VALUES_DISPLAYED == '')
                this.MAX_NUMBER_OF_VALUES_DISPLAYED = 50;
            else
                this.MAX_NUMBER_OF_VALUES_DISPLAYED = Math.min(50, Number(this.MAX_NUMBER_OF_VALUES_DISPLAYED));

            this.times = [];
            this.dataset = [];
        },

        update: function (trace) {
            if (trace.getDiscarded == 1) {
                return;
            }

            var metrics = filterAndComputeMetrics(trace);
            if (metrics['exclude'])
                return;

            eventTime = computeScale(this.GROUPBY, new Date(metrics['eventTime']));

            if (this.dataset.length == 0) { // first event
                this.dataset.push({ 'value': metrics['value'], 'counters': [1] });
                return;
            }

            // search the index of 'value' in the dataset array
            var valueindex = -1;
            for (var k = 0; k < this.dataset.length; k++) {
                if (this.dataset[k]['value'] == metrics['value']) {
                    valueindex = k;
                    break;
                }
            }
            if (valueindex < 0) {// value not yet added; add it to dataset
                valueindex = this.dataset.push({ 'value': metrics['value'], 'counters': [] }) - 1;
                // update counters
                for (var ii = 0; ii < this.dataset[0]['counters'].length; ii++)
                    this.dataset[valueindex]['counters'].push(0);
            }
            // update the counters
            this.dataset[valueindex]["counters"][this.times.indexOf(eventTime)]++;
        },

        finalize: function (output) {
            output['DIMENSION'] = this.DIMENSION;
            output['GROUPBY'] = this.GROUPBY;
            output['TIME_LABEL_UNIT'] = this.TIME_LABEL_UNIT;
            output['MAX_NUMBER_OF_VALUES_DISPLAYED'] = this.MAX_NUMBER_OF_VALUES_DISPLAYED;
            output['ACTIVITY'] = this.ACTIVITY;
            output['times'] = this.times;
            output['dataset'] = this.dataset;
        }
    };
})();
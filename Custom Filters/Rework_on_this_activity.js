// Filter cases that include at least one of the activities below
// This is a logical OR. It can't be done with the UI

var testedActivities = ['activity1', 'activity2'];
var counters = [];

var filter = {
    keepTrace: function (trace) {
        testedActivities.forEach(element=> counters.push(0));
        for (var k = 0; k < trace.size(); k++) {
            var event = trace.get(k);
            var index = testedActivities.indexOf(event.getEventClass());
            if (index >= 0) counters[index]++;
        }
        // if an activity appears more than once in the list, that's a rework
        return counters.reduce((a,v) => (v > 1 ? true : false), false);
    }
};

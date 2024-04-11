var customMetric = {
    caseMetric: function (aCase) {
        var activities_with_selfloops = [];
        var counters = [];
        var previous_activity = '';
        for (var k = 0; k < aCase.size(); k++) {
            var activity = aCase.get(k).getEventClass();
            if (activity == previous_activity){
                var index = activities_with_selfloops.indexOf(activity);
                if (index < 0) { 
                    activities_with_selfloops.push(activity);
                    counters.push(1);
                }
            }
            else { 
                counters[index] += 1;
            }
            previous_activity = activity;
        }
        return counters.lenth;
    }
};
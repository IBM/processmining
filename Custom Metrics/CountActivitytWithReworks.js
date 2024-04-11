var customMetric = {
    caseMetric: function (aCase) {
        var nbr_activity_with_reworks = 0;
        var activities = [];
        var counters = [];
        for (var k = 0; k < aCase.size(); k++) {
            var activity = aCase.get(k).getEventClass();
            var index = activities.indexOf(activity);
            if (index < 0) { 
                activities.push(activity);
                counters.push(1);
            }
            else { 
                counters[index] += 1;
            }
        }
        for (var i = 0; i < counters.length; i++)
            if (counters[i] > 1)
                nbr_activity_with_reworks++
        return nbr_activity_with_reworks;
    }
};
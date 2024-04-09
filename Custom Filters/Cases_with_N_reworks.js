// Keep cases with N reworks on any activity.

reworkGoal = 2;

var filter = {
    keepTrace: function (trace) {
        var activities = [];
        for (var k = 0; k < trace.size(); k++) {
            var event = trace.get(k);
            var activity = event.getEventClass();
            if (previous_activity == activity) // self loop
                continue;
            else if (activities.indexOf(activity) < 0) // first occurence of activity
                activities.push(activity);
            else // activity rework, not a self loop
                return false;
            previous_activity = activity;
        }
        return true;
    }
};
(function () {

    return {
        init: function (params) {
            this.activities = [];
        },

        update: function (trace) {

            if (trace.getDiscarded == 1) {
                return;
            }
            for (var k = 0; k < trace.size(); k++) {
                var event = trace.get(k);

                // retrieve the activity object or create it
                // increment the activity counter each time it is executed

                // retrieve the next activity (including loops
                // keep the next activity
                var current_activity_name = event.getEventClass();
                /* ACTIVITIES IS A GLOBAL VARIABLE THAT HOLDS ALL THE DATA WE NEED FOR EACH ACTIVITY
                                activities = [{
                                    'activity': "activity1",
                                    'frequency': 134,
                                    next_activities: [{ 'activity': "activity2", 'count': 120, 'pathtime_sum': 123434 },
                                    { activity: "activity3", count: 120, pathtime_sum: 123434 }],
                                    previous_activities: [{ activity: "activity2", count: 120, pathtime_sum: 123434 },
                                    { activity: "activity2", count: 120, pathtime_sum: 123434 }]
                                },
                                {
                                    'activity': "activity2",
                                    'frequency': 134,
                                    next_activities: [{ 'activity': "activity2", 'count': 120, 'pathtime_sum': 123434 },
                                    { activity: "activity3", count: 120, pathtime_sum: 123434 }],
                                    previous_activities: [{ activity: "activity2", count: 120, pathtime_sum: 123434 },
                                    { activity: "activity2", count: 120, pathtime_sum: 123434 }]
                                }]
                */
                var index = -1;
                for (var i = 0; i < this.activities.length; i++) {
                    if (this.activities[i].activity == current_activity_name) {
                        index = i;
                        break;
                    }
                }
                if (index == -1) {
                    // create a new entry for the current activity
                    index = this.activities.push({activity: current_activity_name, count:0 , previous_activities: [], next_activities: []});
                    index = index - 1;
                }
                var current_activity = this.activities[index];
                current_activity.count +=1;

                // update the next activities
                var next_activity_index = -1;
                if (k < trace.size() - 1) { // this event is not the last event
                    var next_activity_name = trace.get(k + 1).getEventClass();

                    for (var j = 0; j < current_activity.next_activities.length; j++) {
                        if (current_activity.next_activities[j].activity == next_activity_name) {
                            next_activity_index = j;
                            break;
                        }
                    }

                    if (next_activity_index == -1) {
                        // create the activity
                        next_activity_index = current_activity.next_activities.push({activity: next_activity_name , count: 0, pathtime_sum: 0});
                        next_activity_index = next_activity_index - 1;
                    }
                    current_activity.next_activities[next_activity_index].count += 1;

                    current_activity.next_activities[next_activity_index].pathtime_sum += trace.get(k + 1).getStartTime() - trace.get(k).getEndTime();
                }

                // update the previous activities if current activity is not the first
                if (k > 0){
                    var previous_activity_index = -1;
                    var previous_activity_name = trace.get(k - 1).getEventClass();
                    for (var j = 0; j < current_activity.previous_activities.length; j++) {
                        if (current_activity.previous_activities[j].activity == previous_activity_name) {
                            previous_activity_index = j;
                            break;
                        }
                    }
                    if (previous_activity_index == -1) {
                        // create
                        previous_activity_index = current_activity.previous_activities.push({activity: previous_activity_name,   count: 0, pathtime_sum: 0 });
                        previous_activity_index = previous_activity_index - 1;
                    }
                    current_activity.previous_activities[previous_activity_index].count += 1;
                    current_activity.previous_activities[previous_activity_index].pathtime_sum += trace.get(k).getStartTime() - trace.get(k - 1).getEndTime();

                }
            }
        },

        finalize: function (output) {
            output.activities = this.activities;
            console.log(output.activities);
        }
    };
})();


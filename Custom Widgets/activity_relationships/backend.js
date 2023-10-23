(function () {

    return {
        init: function (params) {
            this.activities = [];
            this.workingHours = Number(params.workingHours);
        },

        update: function (trace) {

            function countWeekendDays(d0, d1, ndays){
                var nsaturdays = Math.floor( (d0.getDay()+ndays) / 7 );
                return 2*nsaturdays + (d0.getDay()==0) - (d1.getDay()==6);
            }
            function NetLeadTime(startTime, endTime, workingHours){
                // startTime = process start time in ms (double)
                // endTime = process end time in ms (double)
                // workingHours = number of working hours
                // We considere that start and end are during working hours
                // We remove non-working hours and week-ends

                var millisecondsPerDay = 24 * 60 * 60 * 1000; // Day in milliseconds
                var millisecondsPerNonWorkingHours = (24 - workingHours) * 60 * 60 * 1000;

                var d0 = new Date(startTime);
                var d1 = new Date(endTime);

                var D0 = new Date(startTime);
                D0.setHours(0);

                var D1 = new Date(endTime);
                D1.setHours(0);

                var nbCalendarDays = Math.round((D1 - D0)/millisecondsPerDay);
                var leadTimeMs = d1 - d0;
                if (nbCalendarDays == 0){ // done within a working day
                  return leadTimeMs;
                }
;
                // Remove number of non-working hours for each calendar day
                // Remove number of week-end hours - non-working hours (already removed)
                return leadTimeMs - (millisecondsPerNonWorkingHours * nbCalendarDays) - (countWeekendDays(d0, d1, nbCalendarDays) * (millisecondsPerDay-millisecondsPerNonWorkingHours));
            }   

            var events = [];

            if (trace.getDiscarded == 1) {
                return;
            }

            for (var k = 0; k < trace.size(); k++) {
                var event = trace.get(k);
                events.push({ name: event.getEventClass(), start: event.getStartTime(), end: event.getEndTime(), predecessor: 0, successor: 0 });
            }

            // Sort the events by starttime
            events.sort(function (a, b) { return a.start - b.start });

            // For each activity, the successor is an activity that starts after and end time of the current activity
            for (var i = 0; i < events.length; i++) {
                for (var j = i + 1; j < events.length; j++) {
                    if (events[i].end <= events[j].start) {
                        events[i].successor = events[j];
                        events[j].predecessor = events[i];
                        //console.log(events[i].name + ' successor is ' + events[i].successor.name);
                        break;
                    }
                }
            }
            // for all activities with no predecessor, search events with a starttime and endtime before the starttime of the event
            for (var i = events.length - 1; i > 0; i--) {
                if (events[i].predecessor)
                    break;
                for (var j = i - 1; j >= 0; j--) {
                    if (events[i].end < events[j].start) {
                        events[i].successor = events[j];
                        events[j].predecessor = events[i];
                        break;
                    }
                }
            }
            /* ACTIVITIES IS A GLOBAL VARIABLE THAT HOLDS ALL THE DATA WE NEED FOR EACH ACTIVITY
                this.activities = [{
                    'activity': "activity1",
                    'count': 134,
                    successors: [{ 'activity': "activity2", 'count': 120, 'pathtime_sum': 123434 },
                    { activity: "activity3", count: 120, pathtime_sum: 123434 }],
                    predecessors: [{ activity: "activity2", count: 120, pathtime_sum: 123434 },
                    { activity: "activity2", count: 120, pathtime_sum: 123434 }]
                },
                {
                    'activity': "activity2",
                    'count': 134,
                    successors: [{ 'activity': "activity2", 'count': 120, 'pathtime_sum': 123434 },
                    { activity: "activity3", count: 120, pathtime_sum: 123434 }],
                    predecessors: [{ activity: "activity2", count: 120, pathtime_sum: 123434 },
                    { activity: "activity2", count: 120, pathtime_sum: 123434 }]
                }]
            */
            // Update the activities global variable for all the events
            for (var i = 0; i < events.length; i++) {
                var current_event = events[i];
                var index = -1;
                for (var j = 0; j < this.activities.length; j++) {
                    if (this.activities[j].activity == current_event.name) {
                        index = j;
                        break;
                    }
                }
                if (index < 0) {
                    // create a new entry for the current event
                    index = this.activities.push({ activity: current_event.name, count: 0, predecessors: [], successors: [] }) - 1;
                }
                // update this.activities array
                var current_activity = this.activities[index];
                current_activity.count++;
                //console.log(current_activity.count);
                if (current_event.predecessor) {
                    //console.log(current_event.name + ' add predecessor ' + current_event.predecessor.name);
                    // find the predecessor activity in the predecessor list
                    var pred_index = -1;
                    for (var j = 0; j < current_activity.predecessors.length; j++) {
                        if (current_activity.predecessors[j].activity == current_event.predecessor.name) {
                            pred_index = j;
                            break;
                        }
                    }
                    if (pred_index < 0) { // create a new entry in the predecessor list
                        pred_index = current_activity.predecessors.push({ activity: current_event.predecessor.name, count: 0, pathtime_sum: 0, pathtime_avg:0 }) - 1; // we need the index not the size
                    }
                    // update the predecessor pred_index
                    current_activity.predecessors[pred_index].count += 1;
                    //just keep working hours/days
                    if (this.workingHours)
                        current_activity.predecessors[pred_index].pathtime_sum += NetLeadTime(current_event.predecessor.end, current_event.start, 8) ;
                    else
                        current_activity.predecessors[pred_index].pathtime_sum += current_event.start - current_event.predecessor.end;

                }
                //console.log(current_activity.count);
                if (current_event.successor) {
                    // find the successor activity in the successor list
                    var succ_index = -1;
                    for (var j = 0; j < current_activity.successors.length; j++) {
                        if (current_activity.successors[j].activity == current_event.successor.name) {
                            succ_index = j;
                            break;
                        }
                    }
                    if (succ_index < 0) { // create a new entry in the predecessor list
                        succ_index = current_activity.successors.push({ activity: current_event.successor.name, count: 0, pathtime_sum: 0, pathtime_avg:0  }) - 1; // we need the index not the size
                    }
                    // update the predecessor pred_index
                    current_activity.successors[succ_index].count += 1;
                    if (this.workingHours)
                        current_activity.successors[succ_index].pathtime_sum += NetLeadTime(current_event.end, current_event.successor.start, 8);   
                    else 
                        current_activity.successors[succ_index].pathtime_sum +=  current_event.successor.start - current_event.end;

                }
                //console.log(current_activity.count);
            }
        },

        finalize: function (output) {

            // sort by frequency
            this.activities.sort(function (a, b) { return b.count - a.count });
            // compute average pathtime
            for (var i = 0; i < this.activities.length; i++){
                var current_activity = this.activities[i];
                for (var j = 0; j < current_activity.predecessors.length; j++){
                    if (current_activity.predecessors[j].pathtime_sum)
                        current_activity.predecessors[j].pathtime_avg = current_activity.predecessors[j].pathtime_sum / current_activity.predecessors[j].count;
                }
                for (var j = 0; j < current_activity.successors.length; j++){
                    if (current_activity.successors[j].pathtime_sum)
                        current_activity.successors[j].pathtime_avg = current_activity.successors[j].pathtime_sum / current_activity.successors[j].count;
                }
            }
            output.activities = this.activities;
        }
    };
})();


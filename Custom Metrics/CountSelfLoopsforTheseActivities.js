var customMetric = {
	caseMetric: function(aCase) {
        var filteredActivities = ['activity1', 'activity2'];
        var previous_activity = '';
        var counters = [];
        var nbr_self_loops = 0;
        for (var i=0; i< filteredActivities.length; i++)
            counters.push(0);
		for(var k = 0 ; k < aCase.size(); k++) {
			var event = aCase.get(k);          
            var activity = event.getEventClass();
            var index = filteredActivities.indexOf(activity);
            if (index > 0){ // one of the activities searched
                if (activity == previous_activity) // self loop
                    counters[index]++;
            }
            previous_activity = activity;
        }
        for (var i=0; i< counters.length; i++)
            nbr_self_loops += counters[i]; 
		return nbr_self_loops;
	}
};

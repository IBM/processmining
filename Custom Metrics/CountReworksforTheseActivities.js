var customMetric = {
	caseMetric: function(aCase) {
        var filteredActivities = ['activity1', 'activity2'];
        var counters = [];
        var nbr_reworks = 0;
        for (var i=0; i< filteredActivities.length; i++)
            counters.push(0);
		for(var k = 0 ; k < aCase.size(); k++) {
			var event = aCase.get(k);          
            var activity = event.getEventClass();
            var index = filteredActivities.indexOf(activity);
            if (index > 0){ // one of the activities searched
                counters[index]++;
            }
        }
        for (var i=0; i< counters.length; i++)
            nbr_reworks += counters[i]; 
		return nbr_reworks;
	}
};

var customMetric = {
	caseMetric: function(aCase) {
        var filteredActivities = ['BO Service Closure', 'activity2'];
        var counters = [];
        var nbr_reworks = 0;
        for (var i=0; i< filteredActivities.length; i++)
            counters.push(0);
		for(var k = 0 ; k < aCase.size(); k++) {
            var index = filteredActivities.indexOf(aCase.get(k).getEventClass());
            if (index >= 0) // one of the activities searched
                counters[index]++;
        }
        for (var j=0; j< counters.length; j++)
            if (counters[j] > 1)
                nbr_reworks += counters[j]; 
		return nbr_reworks;
	}
};
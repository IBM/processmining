var customMetric = {
	caseMetric: function(aCase) {
        var previous_activity = '';
        var nbr_self_loops = 0;

		for(var k = 0 ; k < aCase.size(); k++) {
            var activity = aCase.get(k).getEventClass();
            if (previous_activity == activity) // self loop
                nbr_self_loops++;
            previous_activity = activity;
        }
		return nbr_self_loops;
	}
};
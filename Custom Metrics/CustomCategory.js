// This metric determines a category for each case, based on a combination of characteristics
// The metric is then used in filters and widgets
// You can adapt this metric to your project by changing the activity names and the column names
// Or by changing the logic
// This example can work as is in Bank Account Closure project
var column1 = 'CLOSURE_REASON';
var column2 = 'CLOSURE_TYPE';
var activity1 = 'BO Service Closure';
var activity2 = 'Network Adjustment Requested';
var column1Value = '1 - Client lost';
var column2Value = 'Client Recess';

var customMetric = {
    caseMetric: function(aCase) {

        var act1RunNumber = 0;
        var act1EndTime = 0;
        var act2StartTime = 0;
        var act1_act2_pathTime = 0;
        var pathTimeThreshold1 = 7*24*3600*1000; // 1 day in millisec
        var pathTimeThreshold2 = 10*24*3600*1000; // 1 day in millisec

        if ((aCase.get(0).getStringCustomAttributeValue(column1) != column1Value) || (aCase.get(0).getStringCustomAttributeValue(column2) != column2Value))
            return "NA";

        for (var k=0; k<aCase.size(); k++){
            if (aCase.get(k).getEventClass() == activity1){
                if (act1RunNumber == 0) // We compute path time from the first occurence of activity1 to the end-time of the first occurence of activity2
                    act1EndTime = aCase.get(k).getEndTime();
                act1RunNumber += 1; // update the number of execution of activity1
            } 
            if (aCase.get(k).getEventClass() == activity2) // can succeed immediately or not immediately
                act2StartTime = aCase.get(k).getStartTime();
        }

        if (act1EndTime && act2StartTime){ // the case went through the 2 activities
            act1_act2_pathTime = act2StartTime - act1EndTime;

            if ((act1_act2_pathTime > pathTimeThreshold2) && (act1RunNumber > 1))
                return "long waiting time + rework";

            if ((act1_act2_pathTime > pathTimeThreshold2) && (act1RunNumber == 1))
                return "long waiting time no rework";
            
            if ((act1_act2_pathTime > pathTimeThreshold1) && (act1_act2_pathTime < pathTimeThreshold2) && (act1RunNumber == 1))
                return "medium waiting time no rework";

            if ((act1_act2_pathTime > pathTimeThreshold1) && (act1RunNumber > 1))
                return "medium waiting time + rework";

            if ((act1_act2_pathTime < pathTimeThreshold1) && (act1RunNumber > 1))
                return "short waiting time + rework";

            if ((act1_act2_pathTime < pathTimeThreshold1) && (act1RunNumber == 1))
                return "short waiting time no rework";
        }
        return "NA";
	}
};

// COPY UNTIL HERE
// This metrics associate an SLA (double value) to each case, based on a case attribute.

// AUTHORS: LORENZO LUCCHI, PATRICK MEGARD

//COPY FROM HERE
// Variables
var fieldName = 'RISK_LEVEL'; // You can change the name of the column

// You can replace the keys (1, 2, 3, 4) by strings ('High', 'Medium', 'Low')
// and the value for each key: number of hours per priority level
var SLA_hours_per_priority = {
    1: 3,
    2: 8,
    3: 10,
    4: 20
};

// Custom metric

var customMetric = {
    caseMetric: function(aCase) {
    // We assume that the priority attribute is in the last event of the case. Adjust if needed
    var event = aCase.get(aCase.size()-1);
    var priority = 0;
    try {
        // if the cell is empty we'll get an error, hence the 'try/catch'
        // Keep the line that match the type of the field
        // priority = event.getStringCustomAttributeValue(fieldName);
        priority = event.getIntCustomAttributeValue(fieldName);
        // priority = event.getDoubleCustomAttributeValue(fieldName);
    }
    catch(e){
        // when the value is empty
    }
    return SLA_hours_per_priority[priority]*3600000;
	}
};

// COPY UNTIL HERE

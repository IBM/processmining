// Netleadtime computes the leadtime of a case, and removes the off-office hours and week-ends. 
// The function assumes that the processes start and end during working-hours.
// AUTHOR: Patrick Megard (patrick.megard@fr.ibm.com)
// Feb 3, 2023

// Custom Metric code starts here
// COPY FROM THE LINE BELOW


// Parameter: workingHoursNumber, number of working hours per day. 
var workingHoursNumber = 8

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
    var millisecondsPerNonWorkingHours = (24-workingHours) * 60 * 60 * 1000;
    var d0 = new Date(startTime);
    var d1 = new Date(endTime);
    var D0 = new Date(d0);
    D0.setHours(0);
    var D1 = new Date(d1);
    D1.setHours(0);
    var nbCalendarDays = Math.round((D1 - D0)/millisecondsPerDay);
    var leadTimeMs = d1 - d0;
    if (nbCalendarDays == 0){ // done within a working day
      return leadTimeMs;
    }
    // Remove number of non-working hours for each calendar day
    // Remove number of week-end hours - non-working hours (already removed)
    return leadTimeMs - (millisecondsPerNonWorkingHours * nbCalendarDays) - (countWeekendDays(d0, d1, nbCalendarDays) * (millisecondsPerDay-millisecondsPerNonWorkingHours));
}

// This is for multi-event logs where the latest activity of a case is not always the last one.
// It works also for flat processes. 
var customMetric = {
	caseMetric: function(aCase) {
      var startTime = Number.MAX_VALUE;
      var endTime = 0;
      for(var k = 0 ; k < aCase.size(); k++) {
			var event = aCase.get(k);
        	if (event.getStartTime() < startTime){
              startTime = event.getStartTime();
            }
        	if(event.getEndTime() > endTime){
              endTime = event.getEndTime();
            }
		}
        
    return (NetLeadTime(startTime, endTime, workingHoursNumber));
	}
};

// if you are not using multi-level process, you can use this version that will be faster
//var customMetric = {
//	caseMetric: function(aCase) {
//        return (NetLeadTime(aCase.get(0).getStartTime(), aCase.get(aCase.size() -1).getEndTime(), workingHoursNumber));
//	}
//};

// COPY UNTIL THE LINE ABOVE
// Custom Metric code stops here


// This section is for testing the code within a javascript development environment

let startTime = "2023-02-01T17:00:00";
let endTime = "2023-02-02T09:01:01";
startTime = "2017-07-21T00:00:00";
endTime = "2019-02-21T00:01:01";
//startTime = "2019-02-25T11:56:29";
//endTime = "2019-02-25T15:54:59"

let d0 = new Date(startTime);
let d1 = new Date(endTime)
let D0 = new Date(startTime);
D0.setHours(0);
let D1 = new Date(endTime);
let millisecondsPerDay = 24 * 60 * 60 * 1000;
D1.setHours(0);
let nbCalendarDays = Math.round((D1 - D0)/millisecondsPerDay);

console.log(d0)
console.log(d1)
console.log("days: %s", nbCalendarDays)
console.log("week ends:%s", countWeekendDays(d0,d1, nbCalendarDays))
console.log("leadtime: %s", d1-d0)
console.log("net leadtime: %s", NetLeadTime(d0,d1, 8))
console.log("difference: %s", d1-d0-NetLeadTime(d0,d1, 8))

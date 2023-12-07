// Returns the number of working days to complete a case
// Remove week ends
// Remove holidays provided as an array of dates (strings)

// Custom Metric code starts here
// COPY FROM THE LINE BELOW


function countWeekendDays(d0, d1, ndays){
  var nsaturdays = Math.floor( (d0.getDay()+ndays) / 7 );
  return 2*nsaturdays + (d0.getDay()==0) - (d1.getDay()==6);
}

function excludeWeekendFromVacations(vacations){
  var vacationWorkingDates = [];
  for (var i=0; i<vacations.length; i++){
    var d = new Date(vacations[i]);
    if (d.getDay()!=0 && d.getDay() != 6) // not a weekend
       vacationWorkingDates.push(new Date(vacations[i]));
  }
  return vacationWorkingDates;
}

function countWorkingDays(startTime, endTime, vacations){
  var millisecondsPerDay = 24 * 60 * 60 * 1000; // Day in milliseconds
  var startDate = new Date(startTime);
  var endDate = new Date(endTime);
  if (startDate.getDate() == endDate.getDate())
    return 1; // case completed within a day
  startDate.setHours(0,0);
  endDate.setHours(0,0)
  var ndays = (endDate - startDate)/millisecondsPerDay + 1;
  // remove weekends
  ndays -= countWeekendDays(startDate, endDate, ndays);
  // remove vacation days that are not saturday or sunday
  var vacationsWithoutWeekends = excludeWeekendFromVacations(vacations);
  for (var i=0; i < vacationsWithoutWeekends.length; i++){
    if (startDate < vacationsWithoutWeekends[i] && endDate > vacationsWithoutWeekends[i])
      ndays--;
  }
  return ndays;
}

var vacationDays = ["2023-01-01","2023-05-01", "2023-05-08", "2023-07-14", "2023-08-15","2023-11-1", "2023-11-11","2023-12-25"];

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
        
    return (countWorkingDays(startTime, endTime, vacationDays));
	}
};

// COPY UNTIL THE LINE ABOVE
// Custom Metric code stops here


// This section is for testing the code within a javascript development environment

let startTime = "2023-12-22T10:00:00";
let endTime = "2023-12-26T20:01:00";
let millisecondsPerDay = 24 * 60 * 60 * 1000;

var vacationsWithoutWeekends = excludeWeekendFromVacations(vacationDays);
console.log(vacationsWithoutWeekends);
console.log(countWorkingDays(startTime, endTime, vacationsWithoutWeekends));


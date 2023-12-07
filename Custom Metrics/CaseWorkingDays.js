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
  var vacationsWithoutWeekends = [];
  for (var i=0; i<vacations.length;i++){
    
    if (vacations[i].getDay()>0 && vacations[i].getDay()<6)
    	vacationsWithoutWeekends.push(vacations[i]);
  } 
  return vacationsWithoutWeekends;
}

function countWorkingDays(startTime, endTime, vacations){
  var millisecondsPerDay = 24 * 60 * 60 * 1000; // Day in milliseconds
  var startDate = new Date(startTime);
  var endDate = new Date(endTime);
  if (startDate.getDate() == endDate.getDate())
    return 1; // case completed within a day
  
  startDate.setUTCHours(0,0,0,0);
  endDate.setUTCHours(0,0,0,0);
  var ndays = (endDate - startDate)/millisecondsPerDay + 1;
  
  // remove weekends
  ndays -= countWeekendDays(startDate, endDate, ndays);
  
  // remove vacation days that are not saturday or sunday
  var vacationsWithoutWeekends = excludeWeekendFromVacations(vacations);
  
  for (var j=0; j < vacationsWithoutWeekends.length; j++){
    if (startDate < vacationsWithoutWeekends[j] && endDate > vacationsWithoutWeekends[j])
      ndays--;
  }
  
  
  return ndays;
}



// This is for multi-event logs where the latest activity of a case is not always the last one.
// It works also for flat processes. 
var customMetric = {
	caseMetric: function(aCase){
      // Ideally we would just set the dates as strings like "2023-1-1", but the JS server does not allow
      //the creation of dates through string.    
      var vacationDays = [new Date(2023,1,1), new Date(2023,5,1), new Date(2023,7,14), new Date(2023,8,15),
                         new Date(2023,11,1), new Date(2023,11,11), new Date(2023,12,25)];
                         
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

startTime = "2018-11-02T15:03:56";
console.log(new Date(startTime));
startTimeMs = 1541171036000; //1541171036000
console.log(new Date(startTimeMs));

endTime = "2018-11-05T16:36:39";
endTimeMs = 1541435799000; //1541435799000
console.log(new Date(endTime));
console.log(new Date(endTimeMs));

d0 = new Date(startTime);
d1 = new Date(endTime);
console.log(d1-d0);

d0.setHours(0,0,0,0);// 1541404800000
console.log(d0);
console.log(d0.getTime()); //1541142000000
console.log("diff" + ((d0.getTime() - 1541142000000)/(60*60*1000)))


d1.setHours(0,0,0,0);// 1541142000000
console.log(d1.getTime());
console.log(d1-d0);
console.log((d1-d0)/millisecondsPerDay + 1)

var vacationsWithoutWeekends = excludeWeekendFromVacations(vacationDays);
console.log(vacationsWithoutWeekends);
console.log(new Date(startTime));
console.log(new Date(endTime));
console.log(countWorkingDays(startTime, endTime, vacationsWithoutWeekends));


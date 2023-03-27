// One of these activities started between date1Min and dateMax
// Adapt this list to your process
var activityList = [
    'Purch Order Line Quantity Changed', 
    'Purch Order Line Price Changed', 
    'Purch Order Line Payment Terms Changed', 
    'Purch Order Line Price Unit Changed', 
    'Purch Order Line Info Records Changed', 
    'Purch Order Supplier Changed', 
    'Purch Order Line Account Category Changed'
];
var dateMin = "2023-01-31 00:00:00";
var dateMax = "2023-02-06 00:00:00"; //dateMax could be today

//

var dateMin_ms = new Date(dateMin);
var dateMax_ms = new Date(dateMax);

var filter = {
    keepTrace: function(trace) {
        for(var k = 0 ; k < trace.size(); k++) {
            var event = trace.get(k);
            if (activityList.indexOf(event.getEventClass())>0 && 
                (event.getStartTime()>dateMin_ms) &&
                (event.getStartTime()<dateMax_ms)) 
                return true;
        }
        return false;
    }
};

// TESTING
console.log(dateMin_ms)
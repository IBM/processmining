
// One of these activities started more than X working days ago
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
var delay = 5; // days

//
var today = new Date().getTime();
var delay_ms = delay*24*60*1000;

var filter = {
    keepTrace: function(trace) {
        for(var k = 0 ; k < trace.size(); k++) {
            var event = trace.get(k);
            if (activityList.indexOf(event.getEventClass())>0 && ((today - event.getStartTime()) > delay_ms)) 
                return true;
        }
        return false;
    }
};
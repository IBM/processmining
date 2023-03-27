// Filter cases that include at least one of the activities below
// This is a logical OR. It can't be done with the UI

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


var filter = {
    keepTrace: function(trace) {
        for(var k = 0 ; k < trace.size(); k++) {
            var event = trace.get(k);
            if (activityList.indexOf(event.getEventClass())>0)
                return true;
        }
        return false;
    }
};


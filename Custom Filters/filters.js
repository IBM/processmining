var X = 30; //how many days you want to consider?
var act = 'Order Information';

var today = new Date().getTime();
var mondayOffset = new Date().getDay()-1;
if (mondayOffset==-1)
mondayOffset = 6;
mondayOffset = mondayOffset-7;
var msback = (X-mondayOffset)*24*60*60*1000;

var filter = {
keepTrace: function(trace) {
     for(var k = 0 ; k < trace.size(); k++) {
var event = trace.get(k);
    	if (event.getEventClass() == act && event.getStartTime() > (today - msback))
return true;
      	}
    return false;
    }
};


var delay = 30; // days

// Keep cases that had an event since the last 30 days (delay)
var today = new Date().getTime();
var delay_ms = delay*24*3600*1000;

var filter = {
    keepTrace: function(trace) {
        lastEvent = trace.get(trace.size()-1);
        if (today - lastEvent.getStartTime() <= delay_ms)
            return true;
        return false;
    }
};
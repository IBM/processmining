//Keep cases where the first activity is one of those inserted in activities

var activities = ['Requisition Created', 'Order Item Created'];

var filter = {
    keepTrace: function (trace) {
        start_activity = trace.get(0).getEventClass();
        if (activities.indexOf(start_activity) > -1)
            return true;
        else return false;
    }
};
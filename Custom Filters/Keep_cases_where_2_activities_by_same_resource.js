// Keep the case if the 2 specified activities are performed by the same resource.

var act1 = 'Request created';
var act2 = 'Request completed with account closure';

var filter = {
    keepTrace: function (trace) {
        var res1 = '';
        var res2 = '';
        for (var k = 0; k < trace.size(); k++) {
            var event = trace.get(k);
            var activity = event.getEventClass();
            if (activity == act1 && event.getResource() != '') {
                res1 = event.getResource();
            }
            if (activity == act2  &&
                event.getResource() != '') {
                res2 = event.getResource();
                if (res1 == res2)
                    return true;
            }
        }
        return false;
    }
};
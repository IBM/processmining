    var list1 = ['Activity1'];
    var list2 = ['Activity2'];

    var customMetric = {
        caseMetric: function (aCase) {
            var dt1 = 0;
            var dt2 = 0;
            for (var k = 0; k < aCase.size(); k++) {
                var event1 = aCase.get(k);
                if (list1.indexOf(event1.getEventClass()) > -1) {
                    dt1 = event1.getStartTime();
                    if (k + 1 < aCase.size()) {
                        var event2 = aCase.get(k + 1);
                        if (list2.indexOf(event2.getEventClass()) > -1) {
                            dt2 = event2.getStartTime();
                            return ((dt2 - dt1)/(24*60*60*1000));
                        }
                    }
                }
            }
            return -1;
        }
    };



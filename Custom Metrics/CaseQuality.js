// This metrics associate a quality value (0-100) to each case, which would typically decrease if deviations occur.
//
// In the provided example, the quality decreases by 7 every time an event which includes the word ‘Change’ occurs.
// AUTHOR: LORENZO LUCCHI

// COPY FROM HERE

// VARIABLES
var wordToMatch = 'Change';
// FUNCTION

var customMetric = {
    caseMetric: function (aCase) {
        var quality = 100;
        var changes = 0;
        for (var k = 0; k < aCase.size(); k++) {
            var event = aCase.get(k);
            var activity = event.getEventClass();
            if (activity.indexOf(wordToMatch) > -1) changes++;
        }
        quality -= changes * 7;
        return quality < 0 ? 0 : quality;
    }
};

// COPY UNTIL HERE
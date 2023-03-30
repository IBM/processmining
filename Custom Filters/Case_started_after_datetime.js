// Keep the cases started after the specified datetime.

// Parameters
var compareDate = '2022-12-17T03:24:00';

// Function
var compareTime = new Date(compareDate).getTime();
var filter = {
    keepTrace: function (trace) {

        if (trace.get(0).getStartTime() >= compareTime)
            return true;
        else
            return false;
    }
};
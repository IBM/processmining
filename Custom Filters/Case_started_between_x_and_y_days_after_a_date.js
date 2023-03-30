//Keep the cases started between X and Y days after the specified datetime custom field.
//The custom field’s value is detected on the first event of the case.
//Note: X is the lower bound, Y is the upper.


days_X = 30;
days_Y = 60;
var DIMENSION_WITH_DATE = 'INVOICE_DATE';


days_X_ms = days_X * 24 * 60 * 60 * 1000;
days_Y_ms = days_Y * 24 * 60 * 60 * 1000;
DIMENSION_WITH_DATE = 'attr-custom-' + DIMENSION_WITH_DATE;

var filter = {
    keepTrace: function (trace) {
        if (trace.get(0).getStartTime() - trace.get(0).getLongAttributeValue(DIMENSION_WITH_DATE) >= days_X_ms &&
            trace.get(0).getStartTime() - trace.get(0).getLongAttributeValue(DIMENSION_WITH_DATE) < days_Y_ms)
            return true;
        else
            return false;
    }
};

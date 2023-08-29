(function () {
    return {
        init: function (params) {
            
        },

        update: function (trace) {

            if (trace.getDiscarded == 1) {
                return;
            }
        },

        finalize: function (output) {
        }
    };
})();


(function () {
    return {
        init: function (params) {
            canvasName = params.canvasName;
        },

        update: function (trace) {

            if (trace.getDiscarded == 1) {
                return;
            }
        },

        finalize: function (output) {
            output.canvasName = canvasName;
        }
    };
})();


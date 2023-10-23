return {
    init: function (context) {

    },

    update: function (data, context) {

        const formatDuration = ms => {
            if (ms < 0) ms = -ms;
            const time = {
              day: Math.floor(ms / 86400000),
              hour: Math.floor(ms / 3600000) % 24,
              minute: Math.floor(ms / 60000) % 60,
              second: Math.floor(ms / 1000) % 60,
              millisecond: Math.floor(ms) % 1000
            };
            if (time.day == 0)
                if (time.hour == 0)
                    if (time.minute == 0)
                        if (time.second == 0)
                            if (time.millisecond == 0) return (0);
                            else return (time.second +'.'+time.millisecond+ ' s');
                        else
                            return (time.second +'.'+time.millisecond+ ' s');
                    else return (time.minute + ' m ' + time.second + ' s');
                else return (time.hour + ' h ' + time.minute + ' m');
            else return (time.day + ' d ' + time.hour + ' h ' + time.minute + ' m');
          };
        
        function createTableFromObjects(data, text) {
            const table = document.createElement('table');
            var headerRow = document.createElement('tr');

            // Create table header row
            var headerCell = document.createElement('th');
            headerCell.textContent = text;
            headerRow.appendChild(headerCell);
            headerCell = document.createElement('th');
            headerCell.textContent = 'Frequency';

            headerRow.appendChild(headerCell);
            headerCell = document.createElement('th');
            headerCell.textContent = 'Avg Pathtime';

            headerRow.appendChild(headerCell);

            table.appendChild(headerRow);

            // Create table data rows
            for (const obj of data) {
                var dataRow = document.createElement('tr');
                dataRow.classList.add("table-row");
                var dataCell = document.createElement('td');
                dataCell.textContent = obj.activity;
                dataRow.appendChild(dataCell);
                dataCell = document.createElement('td');
                dataCell.textContent = obj.count;
                dataRow.appendChild(dataCell);
                dataCell = document.createElement('td');
                dataCell.textContent = formatDuration(obj.pathtime_avg);
                dataRow.appendChild(dataCell);
                table.appendChild(dataRow);
            }

            return table;
        };

        context.scope.data = data;

        var widget = document.getElementById(context.scope.widgetId);
        var widget_first_div = widget.getElementsByTagName('div')[0];
        var tableContainer;
        var table;
        var row;
        var cell;

        for (var i = 0; i < data.activities.length; i++) {
            var current_activity = data.activities[i];
            tableContainer = document.createElement('div');
            tableContainer.id = 'div_' + i;
            tableContainer.classList.add('table-wrapper');
            widget_first_div.appendChild(tableContainer);
            table = document.createElement('table');
            row = document.createElement('tr');
            table.appendChild(row);
            cell = document.createElement('th');
            cell.classList.add("table-headings");
            cell.textContent = current_activity.activity;
            row.appendChild(cell);
            cell = document.createElement('th');
            cell.classList.add("table-headings");
            cell.textContent = 'Frequency: '+current_activity.count;
            row.appendChild(cell);

            tableContainer.appendChild(table);
            // table for next activities of each activity
            if (current_activity.predecessors.length > 0) {
                var predecessors = current_activity.predecessors;
                predecessors = predecessors.sort((a, b) => {
                   return b.count - a.count;
                });
                
                table = createTableFromObjects(predecessors,'Predecessors');
                tableContainer.appendChild(table);
                tableContainer.appendChild(document.createElement('p'));
            }
            if (current_activity.successors.length > 0) {
                var successors = current_activity.successors;
                successors = successors.sort((a, b) => {
                    return b.count - a.count;
                  });
                table = createTableFromObjects(successors, 'Successors');
                tableContainer.appendChild(table);

            }
        }


    },

    resize: function (size, context) {

    }
};
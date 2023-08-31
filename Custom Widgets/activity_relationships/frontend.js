return {
    init: function (context) {

    },

    update: function (data, context) {


        function createTableFromObjects(data) {
            const table = document.createElement('table');
            const headerRow = document.createElement('tr');

            // Create table header row
            const keys = Object.keys(data[0]);
            for (const key of keys) {
                const headerCell = document.createElement('th');
                headerCell.textContent = key;
                headerRow.appendChild(headerCell);
            }
            table.appendChild(headerRow);

            // Create table data rows
            for (const obj of data) {
                const dataRow = document.createElement('tr');
                for (const key of keys) {
                    const dataCell = document.createElement('td');
                    dataCell.textContent = obj[key];
                    dataRow.appendChild(dataCell);
                }
                table.appendChild(dataRow);
            }
            return table;
        }


        context.scope.data = data;
        
        for (var i = 0; i < data.activities.length; i++) {
            // table for next activities of each activity
            var current_activity = data.activities[i];
            if (current_activity.next_activities.length > 0){


                var table = createTableFromObjects(current_activity.previous_activities);
                tableContainer = document.getElementById('table-container');
                tableContainer.appendChild(document.createTextNode("Previous activities of "));
                tableContainer.appendChild(document.createTextNode(data.activities[i].activity));
                tableContainer.appendChild(table);

                table = createTableFromObjects(current_activity.next_activities);
                tableContainer = document.getElementById('table-container');
                tableContainer.appendChild(document.createTextNode(""));
                tableContainer.appendChild(document.createTextNode("Next activities of "));
                tableContainer.appendChild(document.createTextNode(data.activities[i].activity));
                tableContainer.appendChild(table);


            }
        }

    },

    resize: function (size, context) {

    }
};
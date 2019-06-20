// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#raspTable').DataTable({
        pagingType: "full_numbers",
        order: [[0, "asc"]],
        responsive: {
            details: true
        },
        // Disable sorting for the Tags and Actions columns.
        columnDefs: [{
            targets: [11, 12],
            searchable: false,
            orderable: false,
        }],
        initComplete: function () {
            this.api().columns([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).every(function () {
                var column = this;
                var select = $('<select><option value=""></option></select>')
                    .appendTo($(column.footer()).empty())
                    .on('change', function () {
                        var val = $.fn.dataTable.util.escapeRegex(
                            $(this).val()
                        );

                        column
                            .search(val ? '^' + val + '$' : '', true, false)
                            .draw();
                    });

                column.data().unique().sort().each(function (d, j) {
                    select.append('<option value="' + d + '">' + d + '</option>')
                });
            });
        },
    });
    $('#xelonTable').DataTable({
        responsive: {
            details: true
        },
        // Disable sorting for the Tags and Actions columns.
        columnDefs: [{
            targets: [15, 16],
            searchable: false,
            orderable: false,
        }],
        initComplete: function () {
            this.api().columns([0, 1, 2, 3, 4, 5, 6]).every(function () {
                var column = this;
                var select = $('<select><option value=""></option></select>')
                    .appendTo($(column.footer()).empty())
                    .on('change', function () {
                        var val = $.fn.dataTable.util.escapeRegex(
                            $(this).val()
                        );

                        column
                            .search(val ? '^' + val + '$' : '', true, false)
                            .draw();
                    });

                column.data().unique().sort().each(function (d, j) {
                    select.append('<option value="' + d + '">' + d + '</option>')
                });
            });
        },
    });
    $('#corvetTable').DataTable({
        pagingType: "full_numbers",
        order: [[0, "asc"]],
    });
});

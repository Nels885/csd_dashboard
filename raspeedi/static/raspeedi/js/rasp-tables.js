// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#raspTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: [[2, "asc"]],
        // Disable sorting for the Tags and Actions columns.
        columnDefs: [{
            targets: [0, 1],
            searchable: false,
            orderable: false,
        }],
        initComplete: function () {
            this.api().columns([2, 3, 4, 5, 6, 7]).every(function () {
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

    $('#unlockTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order:  []
    });

    $('#unlockDeleteTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: [],
        // Disable sorting for the Tags and Actions columns.
        columnDefs: [{
            targets: 0,
            searchable: false,
            orderable: false,
        }],
    });
});

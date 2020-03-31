// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#repairTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: [[2, "asc"]],
        // Disable sorting for the Tags and Actions columns.
        columnDefs: [{
            targets: 0,
            searchable: false,
            orderable: false,
        }],
    });

    $('#batchTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: [[0, "asc"]],
    });

    $('#ecuModelTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: [[0, "asc"]],
    });
});

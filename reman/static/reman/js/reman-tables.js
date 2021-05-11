// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#repairTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: [[2, "asc"]],
        // Disable sorting for the Tags and Actions columns.
        columnDefs: [{
            targets: [0, 1],
            searchable: false,
            orderable: false,
        }],
    });

    $('#batchTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: [],
        columnDefs: [{
            targets: [0, 1],
            searchable: false,
            orderable: false,
        }],
    });

    $('#baseRefTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: [[0, "asc"]],
    });

    $('#outTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: [[0, "asc"]],
    });
});

// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#prodTable').DataTable({
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
});

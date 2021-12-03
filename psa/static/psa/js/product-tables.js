// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#prodTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: [[1, "asc"]],
        // Disable sorting for the Tags and Actions columns.
        columnDefs: [{
            targets: 0,
            searchable: false,
            orderable: false,
        }],
    });
});

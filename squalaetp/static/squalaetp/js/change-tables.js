$(document).ready(function () {
    $('#changeTable').DataTable({
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

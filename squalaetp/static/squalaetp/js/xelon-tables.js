$(document).ready(function () {
    $('#xelonTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: [],
        // Disable sorting for the Tags and Actions columns.
        columnDefs: [{
            targets: [0, 1],
            searchable: false,
            orderable: false,
        }],
    });
});

// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#defaultTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: [[1, "asc"]],
        columnDefs: [{
            targets: 0,
            searchable: false,
            orderable: false,
        }],
    });
});

// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#defaultTable').DataTable({
        pagingType: "full_numbers",
        lengthMenu: [[25, 50, 100], [25, 50, 100]],
        scrollX: true,
        order: [[1, "asc"]],
        columnDefs: [{
            targets: 0,
            searchable: false,
            orderable: false,
        }],
    });
});

// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#softTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: [[1, "asc"]],
        columnDefs: [{
            targets: 0,
            searchable: false,
            orderable: false,
        }],
        dom: 'Bfrtip',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ],
    });
});

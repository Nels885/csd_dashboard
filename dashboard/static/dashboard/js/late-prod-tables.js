// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#lateProdTable').DataTable({
        paging: false,
        scrollX: true,
        // order: [[4, "desc"]],
        dom: 'Bfrtip',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ],
    });
    $('#lateProdNewTable').DataTable({
        paging: false,
        order: false,
        scrollX: true,
        dom: 'Bfrtip',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ],
        columnDefs: [
            {
                targets: "_all",
                orderable: false,
            },
            {
                targets: 0,
                searchable: false,
            }
        ],
    });
    $('#tronikTable').DataTable({
        paging: false,
        order: false,
        scrollX: true,
        dom: 'Bfrtip',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print',
        ],
        columnDefs: [
            {
                targets: "_all",
                orderable: false,
            },
            {
                targets: 0,
                searchable: false,
            }
        ],
    });
});

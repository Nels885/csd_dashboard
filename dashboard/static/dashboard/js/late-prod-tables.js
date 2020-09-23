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
});

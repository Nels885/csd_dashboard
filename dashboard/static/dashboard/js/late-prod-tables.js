// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#lateProdTable').DataTable({
        paging: false,
        order: false,
        scrollX: true,
        dom: 'Bfrtip',
        language: {
            searchPanes: {
                collapse: {0: 'Search Options', _: 'Search Options (%d)'}
            }
        },
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print',
            {
                extend: 'searchPanes',
                config: {
                    columns: [3, 7, 8, 9]
                }
            }
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
    $('#adminTable').DataTable({
        paging: false,
        order: false,
        scrollX: true,
        dom: 'Bfrtip',
        language: {
            searchPanes: {
                collapse: {0: 'Search Options', _: 'Search Options (%d)'}
            }
        },
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print',
            {
                extend: 'searchPanes',
                config: {
                    columns: [3, 7, 8]
                }
            }
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

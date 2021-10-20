// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#softTable').DataTable({
        paging: false,
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

    $('#thermalActiveTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        columnDefs: [{
            targets: 0,
            searchable: false,
            orderable: false,
        }],
        order: [[3, "desc"]],
    });

    $('#thermalTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: []
    });

    $('#tagXelonTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: []
    });

    $('#suptechTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: [],
        columnDefs: [{
            targets: 0,
            searchable: false,
            orderable: false,
        }],
        language: {
            searchPanes: {
                collapse: {0: 'Search Options', _: 'Search Options (%d)'}
            }
        },
        buttons: [{
            extend: 'searchPanes',
            config: {
                columns: [3, 5, 6]
            }
        }],
        dom: 'Bfrtip'
    });
});

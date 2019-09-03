// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#corvetTable').DataTable({
        pagingType: "full_numbers",
        order: [[0, "asc"]],
        columnDefs: [{
            targets: 7,
            searchable: false,
            orderable: false,
        }],
    });

    $('#softTable').DataTable({
        pagingType: "full_numbers",
        order: [[0, "asc"]],
        columnDefs: [{
            targets: 6,
            searchable: false,
            orderable: false,
        }],
        dom: 'Bfrtip',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ],
    });

    $('#unlockTable').DataTable({
        pagingType: "full_numbers",
        order: [[2, "desc"]],
    });
});

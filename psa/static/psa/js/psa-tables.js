// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#prodTable').DataTable({
        pagingType: "full_numbers",
        lengthMenu: [[25, 50, 100], [25, 50, 100]],
        scrollX: true,
        order: [[1, "asc"]],
        // Disable sorting for the Tags and Actions columns.
        columnDefs: [{
            targets: 0,
            searchable: false,
            orderable: false,
        }],
    });

    $('#dtcTable').DataTable({
        pagingType: "full_numbers",
        lengthMenu: [[25, 50, 100], [25, 50, 100]],
        processing: true,
        serverSide: true,
        scrollX: true,
        order: [[1, 'asc']],
        ajax: {
            url: URL_AJAX,
            type: "GET",
        },
        columns: [
            {
                sortable: false,
                render: function (data, type, full, meta) {
                    let url = '#';
                    return '<a  href="' + url + '" type="button" title="Detail" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></a>'
                },
            },
            {data: "code"},
            {data: "description"},
            {data: "type"},
            {data: "characterization"},
            {data: "location"},
            {data: "ecu_type"},
        ],
        columnDefs: [{
            targets: 0,
            searchable: false,
            orderable: false,
        }],
    });
});

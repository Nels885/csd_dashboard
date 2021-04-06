$(document).ready(function () {
    let table = $('#repairTable').DataTable({
        processing: true,
        serverSide: true,
        scrollX: true,
        order: [[2, "asc"]],
        ajax: URL_AJAX,
        columns: [
            {
                data: null,
                defaultContent: BTN_EDIT,
            },
            {
                data: null,
                defaultContent: '<button title="Detail" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></button>',
            },
            {data: "identify_number"},
            {data: "batch"},
            {data: "technical_data"},
            {data: "supplier_oe"},
            {data: "hw_reference"},
            {data: "psa_barcode"},
            {data: "status"},
            {data: "quality_control"},
            {data: "closing_date"},
            {data: "modified_by"},
            {data: "modified_at"},
            {data: "created_by"},
            {data: "created_at"}
        ],
        // Disable sorting for the Tags and Actions columns.
        columnDefs: [
            {
                targets: [0, 1],
                searchable: false,
                orderable: false,
            },
        ],
    });

    let id = 0;

    $('#repairTable tbody').on('click', 'button', function () {
        let data = table.row($(this).parents('tr')).data();
        let title = $(this).attr('title');
        id = data['id'];
        if (title === 'Modification') {
            location.href = '/reman/repair/' + id + '/edit/'
        } else if (title === 'Detail') {
            // Detail button
            location.href = '/reman/repair/' + id + '/detail/'
        }
    });
});

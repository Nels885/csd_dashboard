$(document).ready(function () {
    $('#repairTable').DataTable({
        processing: true,
        serverSide: true,
        lengthMenu: [[25, 50, 100], [25, 50, 100]],
        scrollX: true,
        order: [[2, "asc"]],
        ajax: URL_AJAX,
        columns: [
            {
                sortable: false,
                render: function (data, type, full, meta) {
                    let url = '/reman/repair/' + full.id + '/edit/';
                    if (PERM && !full.checkout) {
                        return '<a href="' + url + '" title="Modification" class="btn btn-success btn-circle btn-sm"><i class="fas fa-edit"></i></a>';
                    } else {
                        return '<i class="btn btn-dark btn-circle btn-sm fas fa-edit"></i>';
                    }
                },
            },
            {
                sortable: false,
                render: function (data, type, full, meta) {
                    let url = '/reman/repair/' + full.id + '/detail/'
                    return '<a href="' + url + '" title="Detail" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></a>';
                }
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

    $('#ecuRefBaseTable').DataTable({
        processing: true,
        serverSide: true,
        scrollX: true,
        order: [[1, "asc"]],
        ajax: URL_AJAX,
        columns: [
            {
                sortable: false,
                render: function (data, type, full, meta) {
                    let url = '/reman/ecu/' + full.psa_barcode + '/edit/';
                    if (PERM) {
                        return '<a href="' + url + '" title="Modification" class="btn btn-success btn-circle btn-sm"><i class="fas fa-edit"></i></a>';
                    } else {
                        return '<i class="btn btn-dark btn-circle btn-sm fas fa-edit"></i>';
                    }
                },
            },
            {data: "reman_reference"},
            {data: "technical_data"},
            {data: "hw_reference"},
            {data: "supplier_oe"},
            {data: "psa_barcode"},
            {data: "code_produit"},
            {data: "code_emplacement"},
            {data: "cumul_dispo"}
        ],
        // Disable sorting for the Tags and Actions columns.
        columnDefs: [
            {
                targets: 0,
                searchable: false,
                orderable: false,
            },
        ],
    });
});

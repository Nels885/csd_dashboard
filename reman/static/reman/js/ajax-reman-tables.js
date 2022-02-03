$(document).ready(function () {
    $('#repairTable').DataTable({
        processing: true,
        serverSide: true,
        lengthMenu: [[25, 50, 100], [25, 50, 100]],
        scrollX: true,
        order: [[12, "desc"]],
        ajax: URL_AJAX,
        columns: [
            {
                sortable: false,
                render: function (data, type, full, meta) {
                    let url_edit = '/reman/repair/' + full.id + '/edit/';
                    let url_detail = '/reman/repair/' + full.id + '/detail/';
                    if (PERM) {
                        return '<a href="' + url_edit + '" title="Modification" class="btn btn-success btn-circle btn-sm"><i class="fas fa-edit"></i></a> ' +
                            '<a href="' + url_detail + '" title="Detail" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></a>';
                    } else {
                        return '<i class="btn btn-dark btn-circle btn-sm fas fa-edit"></i> ' +
                            '<a href="' + url_detail + '" title="Detail" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></a>';
                    }
                },
            },
            {data: "identify_number"},
            {data: "batch"},
            {data: "customer"},
            {data: "technical_data"},
            {data: "supplier_oe"},
            {data: "hw_reference"},
            {data: "barcode"},
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
                targets: 0,
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

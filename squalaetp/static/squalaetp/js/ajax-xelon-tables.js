$(document).ready(function () {
    let table = $('#xelonTable').DataTable({
        processing: true,
        serverSide: true,
        scrollX: true,
        order: [[6, 'desc']],
        ajax: URL_AJAX,
        columns: [
            {
                sortable: false,
                render: function (data, type, full, meta) {
                    let url = '/squalaetp/' + full.id + '/detail/?select=ihm';
                    if (PERM) {
                        return '<a href="' + url + '" title="Modification" class="btn btn-success btn-circle btn-sm"><i class="fas fa-edit"></i></a>';
                    } else {
                        return '<i class="btn btn-dark btn-circle btn-sm fas fa-edit"></i>';
                    }
                }
            },
            {
                sortable: false,
                render: function (data, type, full, meta) {
                    let url = '/squalaetp/' + full.id + '/detail/';
                    return '<a  href="' + url + '" type="button" title="Detail" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></a>'
                },
            },
            {data: "numero_de_dossier"},
            {data: "vin"},
            {data: "modele_produit"},
            {data: "modele_vehicule"},
            {data: "date_retour"},
            {data: "type_de_cloture"},
            {data: "nom_technicien"},
        ],
        rowCallback: function (row, data, index) {
            if (!data['corvet'] && (data['vin'].includes('VF3') || data['vin'].includes('VF7'))) {
                $('td', row).addClass('bg-danger text-light');
            }
        },
        // Disable sorting for the Tags and Actions columns.
        columnDefs: [
            {
                targets: [0, 1],
                searchable: false,
                orderable: false,
            },
        ],
    });
});

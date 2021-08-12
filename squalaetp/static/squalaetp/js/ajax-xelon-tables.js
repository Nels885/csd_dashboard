$(document).ready(function () {
    let table = $('#xelonTable').DataTable({
        processing: true,
        serverSide: true,
        scrollX: true,
        order: [[5, 'desc']],
        ajax: URL_AJAX,
        columns: [
            {
                sortable: false,
                width:'60px',
                render: function (data, type, full, meta) {
                    let url_ihm = '/squalaetp/' + full.id + '/detail/?select=ihm';
                    let url_detail = '/squalaetp/' + full.id + '/detail/';
                    return '<a href="' + url_ihm + '" title="Modification" class="btn btn-success btn-circle btn-sm"><i class="fas fa-edit"></i></a> ' +
                        '<a  href="' + url_detail + '" type="button" title="Detail" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></a>';
                }
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
                targets: 0,
                searchable: false,
                orderable: false,
            },
        ],
    });
});

// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#xelonTable').DataTable({
        processing: true,
        serverSide: true,
        ajax: {
            url: "/api/xelon/",
            type: "GET",
        },
        columns: [
            {data: "numero_de_dossier"},
            {data: "vin"},
            {data: "modele_produit"},
            {data: "modele_vehicule"},
            {data: "date_retour"},
            {data: "type_de_cloture"},
            {data: "nom_technicien"},
            {
                data: null,
                defaultContent: '<a href="#" title="Modification" class="btn btn-success btn-circle btn-sm"><i class="fas fa-edit"></i></a>'
            },
            {
                data: null,
                defaultContent: '<a href="#" title="Detail" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></a>'
            },
        ],
        rowCallback: function (row, data, index) {
            if (data['corvet'].length === 0 && (data['vin'].includes('VF3') || data['vin'].includes('VF7'))) {
                $('td', row).addClass('bg-danger text-light');
            }
        },
        // Disable sorting for the Tags and Actions columns.
        columnDefs: [{
            targets: [7, 8],
            searchable: false,
            orderable: false,
        }],
    });

});

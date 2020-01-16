// Call the dataTables jQuery plugin
$(document).ready(function () {
    let xelon = $('#xelonTable').DataTable({
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
                defaultContent: '<a href="#" title="Edit" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></a>'
            }
        ]
    });

});

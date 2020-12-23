$(document).ready(function () {
    let table = $('#xelonTable').DataTable({
        processing: true,
        serverSide: true,
        scrollX: true,
        order: [[6, 'desc']],
        ajax: URL_AJAX,
        columns: [
            {data: null},
            {data: null},
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
            {
                defaultContent: '<button title="Modification" class="btn btn-success btn-circle btn-sm"><i class="fas fa-edit"></i></button>',
                targets: 0
            },
            {
                defaultContent: '<button title="Detail" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></button>',
                targets: 1
            }
        ],
    });

    let id = 0;

    $('#xelonTable tbody').on('click', 'button', function () {
        let data = table.row($(this).parents('tr')).data();
        let title = $(this).attr('title');
        id = data['id'];
        if (title === 'Modification') {
            location.href = '/squalaetp/' + id + '/detail/?select=ihm'
        } else if (title === 'Detail') {
            // Detail button
            location.href = '/squalaetp/' + id + '/detail/'
        }
    });
});

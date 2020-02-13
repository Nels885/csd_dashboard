let table = $('#xelonTable').DataTable({
    processing: true,
    serverSide: true,
    scrollX: true,
    order: [[6, 'desc']],
    ajax: {
        url: "/api/xelon/",
        type: "GET",
    },
    columns: [
        {
            data: null,
            defaultContent: '<button type="button" title="Modification" class="btn btn-success btn-circle btn-sm"><i class="fas fa-edit"></i></button>'
        },
        {
            data: null,
            defaultContent: '<button type="button" title="Detail" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></button>'
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
        if (data['corvet'].length === 0 && (data['vin'].includes('VF3') || data['vin'].includes('VF7'))) {
            $('td', row).addClass('bg-danger text-light');
        }
    },
    // Disable sorting for the Tags and Actions columns.
    columnDefs: [{
        targets: [0, 1],
        searchable: false,
        orderable: false,
    }],
});

let id = 0;

$('#xelonTable tbody').on('click', 'button', function () {
    let data = table.row($(this).parents('tr')).data();
    let class_name = $(this).attr('class');
    id = data['id'];
    if (class_name === 'btn btn-success btn-circle btn-sm') {
        // Edit button
        $('#xelonModalLabel').text('Modification données dossier Xelon : ' + data["numero_de_dossier"]);
        $('#id_vin').val(data["vin"]);
        $('#id_xml_data').val('');
        $('#xelonEditModal').modal();
    } else {
        // Detail button
        location.href = '/squalaetp/' + id + '/detail/'
    }
});

$('#xelonModalBody form').on('submit', function (e) {
    e.preventDefault();
    $.ajax({
        url: '/squalaetp/ajax/xelon/',
        method: 'POST',
        data: {
            file_id: id,
            vin: $('#id_vin').val(),
            xml_data: $('#id_xml_data').val(),
            btn_corvet_insert: '',
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
        },
        dataType: 'json',
        success: function (data) {
            //get your modal body by class and change its html
            document.getElementById('xelonModalBody').innerHTML = '<div class="text-center">' + data.title + '</div>';
            window.setTimeout(function () {
                window.location.reload()
            }, 2000);
        },
        error: function (data) {
            document.getElementById('xelonErrors').innerHTML = '<p class="text-danger">* Les données XML ne sont pas valide</p>';
            $('#id_xml_data').val('');
        }
    });
});
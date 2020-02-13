let table = $('#corvetTable').DataTable({
    processing: true,
    serverSide: true,
    scrollX: true,
    order: [[1, 'asc']],
    ajax: {
        url: "/api/corvet/",
        type: "GET",
    },
    columns: [
        {
            data: null,
            defaultContent: '<button type="button" title="Detail" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></button>'
        },
        {data: "vin"},
        {data: "rad_ref"},
        {data: "rad_cal"},
        {data: "nav_ref"},
        {data: "nav_cal"},
        {data: "cmm_ref"},
        {data: "cmm_cal"},
        {data: "bsi_ref"},
        {data: "bsi_cal"},
    ],
    columnDefs: [{
        targets: 0,
        searchable: false,
        orderable: false,
    }],
});

let vin = 0;

$('#corvetTable tbody').on('click', 'button', function () {
    let data = table.row($(this).parents('tr')).data();
    let class_name = $(this).attr('class');
    vin = data['vin'];
    if (class_name === 'btn btn-info btn-circle btn-sm') {
        location.href = '/squalaetp/corvet/' + vin + '/detail/'
    }
});

let table = $('#corvetTable').DataTable({
        processing: true,
        serverSide: true,
        ajax: {
            url: "/api/corvet/",
            type: "GET",
        },
        columns: [
            {data: "vin"},
            {data: "ref_radio"},
            {data: "cal_radio"},
            {data: "ref_nav"},
            {data: "cal_nav"},
            {data: "no_serie"},
            {
                data: null,
                defaultContent: '<button type="button" title="Detail" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></button>'
            },
        ],
        columnDefs: [{
            targets: 6,
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

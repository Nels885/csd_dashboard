let table = $('#corvetNewTable').DataTable({
    processing: true,
    serverSide: true,
    scrollX: true,
    order: [[1, 'asc']],
    ajax: {
        url: URL_AJAX,
        type: "GET",
    },
    columns: [
        {
            sortable: false,
            render: function (data, type, full, meta) {
                let vin = full.vin;
                let url = '/psa/corvet/' + vin + '/detail/';
                return '<a  href="' + url + '" type="button" title="Detail" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></a>'
            },
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

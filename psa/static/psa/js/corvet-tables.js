let table = $('#corvetNewTable').DataTable({
    pagingType: "full_numbers",
    lengthMenu: [[25, 50, 100], [25, 50, 100]],
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
        {data: "radio_name"},
        {data: "nav_ref"},
        {data: "nav_cal"},
        {data: "btel_name"},
        {data: "cmm_ref"},
        {data: "cmm_cal"},
        {data: "cmm_name"},
        {data: "bsi_ref"},
        {data: "bsi_cal"},
        {data: "bsi_name"},
    ],
    columnDefs: [{
        targets: 0,
        searchable: false,
        orderable: false,
    }],
});

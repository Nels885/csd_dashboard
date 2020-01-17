// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#corvetTable').DataTable({
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
                defaultContent: '<a href="#" title="Detail" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></a>'
            },
        ],
        columnDefs: [{
            targets: 6,
            searchable: false,
            orderable: false,
        }],
    });
});

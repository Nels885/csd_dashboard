// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#stockTable').DataTable({
        pagingType: "full_numbers",
        lengthMenu: [[25, 50, 100], [25, 50, 100]],
        processing: true,
        serverSide: true,
        scrollX: true,
        order: [[0, 'asc']],
        ajax: {
            url: URL_AJAX,
            type: "GET",
        },
        columns: [
            {data: "product_code"},
            {data: "code_zone"},
            {data: "code_emplacement"},
            {data: "cumul_dispo"},
            {data: "code_magasin"},
            {data: "code_site"}
        ],
    });
});

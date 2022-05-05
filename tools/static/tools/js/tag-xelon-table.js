let table = $('#tagXelonTable').DataTable({
    pagingType: "full_numbers",
    lengthMenu: [[25, 50, 100], [25, 50, 100]],
    processing: true,
    serverSide: true,
    scrollX: true,
    order: [[5, 'desc']],
    ajax: {
        url: URL_AJAX,
        type: "GET",
    },
    columns: [
        {data: "xelon"},
        {data: "calibre"},
        {data: "telecode"},
        {data: "comments"},
        {data: "created_at"},
        {data: "created_by"},
    ],
});
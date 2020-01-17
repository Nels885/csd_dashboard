// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#corvetTable').DataTable({
        pagingType: "full_numbers",
        order: [[0, "asc"]],
        columnDefs: [{
            targets: 7,
            searchable: false,
            orderable: false,
        }],
    });
});

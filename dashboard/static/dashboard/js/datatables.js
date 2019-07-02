// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#corvetTable').DataTable({
        pagingType: "full_numbers",
        order: [[0, "asc"]],
    });

    $('#softTable').DataTable({
        pagingType: "full_numbers",
        order: [[0, "asc"]],
    });
});

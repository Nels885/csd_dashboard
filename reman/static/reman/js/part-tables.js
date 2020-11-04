// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#partTable').DataTable({
        pagingType: "full_numbers",
        scrollX: true,
        order: [[0, "asc"]],
    });
});

// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#partTable').DataTable({
        pagingType: "full_numbers",
        lengthMenu: [[25, 50, 100], [25, 50, 100]],
        scrollX: true,
        order: [[0, "asc"]],
    });
});

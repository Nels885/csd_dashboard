// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

let endpoint = $("#prodPieChart").attr("data-url");
let defaultData = [];
let labels = [];
$.ajax({
    method: "GET",
    url: endpoint,
    success: function (data) {
        console.log(data);
        labels = data.labels;
        defaultData = data.default;
        // Pie Chart Product
        var ctx = document.getElementById("prodPieChart");
        var prodPieChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: defaultData,
                    backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc', '#5A5B68', '#E74A3B', '#848696', '#F6C23E'],
                    // hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf'],
                    hoverBorderColor: "rgba(234, 236, 244, 1)",
                }],
            },
            options: {
                maintainAspectRatio: false,
                tooltips: {
                    backgroundColor: "rgb(255,255,255)",
                    bodyFontColor: "#858796",
                    borderColor: '#dddfeb',
                    borderWidth: 1,
                    xPadding: 15,
                    yPadding: 15,
                    displayColors: false,
                    caretPadding: 10,
                },
                legend: {
                    display: false
                },
                cutoutPercentage: 80,
            },
        });
    },
    error: function (error_data) {
        console.log("error");
        console.log(error_data)
    }
});

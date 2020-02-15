// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito,-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

$.ajax({
    method: "GET",
    url: $("#dataCharts").attr("data-url"),
    success: function (data) {
        // console.log(data);
        let labels = data.prodLabels;
        let defaultData = data.prodDefault;
        // Pie Chart Product
        var ctx = document.getElementById("prodPieChart");
        var prodPieChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: defaultData,
                    // backgroundColor: ['#4e73df', '#1cc88a', '#E74A3B', '#848696',
                    //     '#5A5B68', '#36b9cc', '#F6C23E', '#99FF33',
                    //     '#FF7733'],
                    backgroundColor: ['#079992', '#0a3d62', '#0c2461', '#b71540',
                        '#e58e26', '#eb2f06', '#1e3799', '#3c6382',
                        '#38ada9','#78e08f', '#60a3bc', '#4a69bd'],
                    // hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf'],
                    hoverBorderColor: "rgba(234, 236, 244, 1)",
                }],
            },
            options: {
                maintainAspectRatio: false,
                // tooltips: {
                //     backgroundColor: "rgb(255,255,255)",
                //     bodyFontColor: "#858796",
                //     borderColor: '#dddfeb',
                //     borderWidth: 1,
                //     xPadding: 15,
                //     yPadding: 15,
                //     displayColors: false,
                //     caretPadding: 10,
                // },
                legend: {
                    display: true,
                    position: 'right',
                },
                cutoutPercentage: 0,
            },
        });
    },
    error: function (error_data) {
        console.log("error");
        console.log(error_data)
    }
});

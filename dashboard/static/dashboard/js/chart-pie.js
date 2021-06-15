// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.font.Family = 'Nunito,-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.color = '#858796';

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
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: defaultData,
                    backgroundColor: ['#079992', '#0a3d62', '#0c2461', '#b71540',
                        '#e58e26', '#eb2f06', '#1e3799', '#3c6382',
                        '#38ada9', '#78e08f', '#60a3bc', '#4a69bd', '#0C40FF'],
                    hoverBorderColor: "rgba(234, 236, 244, 1)",
                    borderWidth: 1
                }],
            },
            options: {
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'left',
                        labels: {
                            boxWidth: 20,
                            fontSize: 10,
                            padding: 5,
                        }
                    }
                }
            },
        });
    },
    error: function (error_data) {
        console.log("error");
        console.log(error_data)
    }
});

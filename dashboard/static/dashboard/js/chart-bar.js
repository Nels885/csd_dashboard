// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito,-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

$.ajax({
    method: "GET",
    url: $("#dataCharts").attr("data-url"),
    success: function (data) {
        // console.log(data);
        const {suptechLabels} = data;
        const {suptechValue} = data;

        // Area Chart Example
        var ctx = document.getElementById("supTechChart");
        var repairLineChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: suptechLabels,
                datasets: [
                    {
                        label: "Pourcentage délai en jours",
                        data: suptechValue,
                        backgroundColor: "#4e73df",
                        hoverBackgroundColor: "#2e59d9",
                        borderColor: "#4e73df",
                    },
                ],
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true,
                            max: 100
                        }
                    }]
                }
            }
        });
    },
    error: function (error_data) {
        console.log("error");
        console.log(error_data)
    }
});


// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.font.Family = 'Nunito,-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.color = '#858796';

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
                        label: "Demandes Suptech",
                        data: suptechValue,
                        backgroundColor: ['#4FC88B', '#F6C23E', '#E74A3B'],
                        borderWidth: 1
                    },
                ],
            },
            options: {
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Délai de traitement'
                        },
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                    },
                    y: {
                        max: 100,
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Valeur en %',
                        },
                        ticks: {
                            maxTicksLimit: 6
                        },
                        grid: {
                            color: "rgb(234, 236, 244)",
                            zeroLineColor: "rgb(234, 236, 244)",
                            drawBorder: false,
                            borderDash: [2],
                            zeroLineBorderDash: [2]
                        }
                    }
                }
            }
        });
    },
    error: function (error_data) {
        console.log("error");
        console.log(error_data)
    }
});


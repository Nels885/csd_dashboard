// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.font.Family = 'Nunito,-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.color = '#858796';

$.ajax({
    method: "GET",
    url: $("#dataCharts").attr("data-url"),
    success: function (data) {
        // console.log(data);
        const {suptechCoLabels} = data;
        const {suptechCoValue} = data;

        // Area Chart Example
        var ctx = document.getElementById("supTechCoChart");
        var repairLineChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: suptechCoLabels,
                datasets: [
                    {
                        label: "Demandes Suptech",
                        data: suptechCoValue,
                        backgroundColor: [
                            "rgba(214, 54, 33, 1)", "rgba(240, 132, 40, 1)", "rgba(0, 143, 136, 1)",
                            "rgba(78, 115, 223, 1)"
                        ],
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
                            text: 'Statut'
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


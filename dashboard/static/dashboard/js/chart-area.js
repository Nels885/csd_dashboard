// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito,-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

$.ajax({
    method: "GET",
    url: $("#dataCharts").attr("data-url"),
    success: function (data) {
        console.log(data);
        const {areaLabels} = data;
        const {prodsRepValue} = data;
        const {prodsInValue} = data;
        const {prodsExpValue} = data;
        const {prodsLateValue} = data;

        // Area Chart Example
        var ctx = document.getElementById("dealAreaChart");
        var repairLineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: areaLabels,
                datasets: [
                    {
                        data: prodsRepValue,
                        label: "Pdts en cours",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(0, 143, 136, 1)",
                        pointRadius: 3,
                        pointBackgroundColor: "rgba(78, 115, 223, 1)",
                        pointBorderColor: "rgba(0, 143, 136, 1)",
                    },
                    {
                        data: prodsInValue,
                        label: "Pdts en IN",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(78, 115, 223, 1)",
                        pointRadius: 3,
                        pointBackgroundColor: "rgba(78, 115, 223, 1)",
                        pointBorderColor: "rgba(78, 115, 223, 1)",
                    },
                    {
                        data: prodsExpValue,
                        label: "Pdts en Exp",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(240, 132, 40, 1)",
                        pointRadius: 3,
                        pointBackgroundColor: "rgba(240, 132, 40, 1)",
                        pointBorderColor: "rgba(240, 132, 40, 1)",
                    },
                    {
                        data: prodsLateValue,
                        label: "Pdts en Retard",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(214, 54, 33, 1)",
                        pointRadius: 3,
                        pointBackgroundColor: "rgba(214, 54, 33, 1)",
                        pointBorderColor: "rgba(214, 54, 33, 1)",
                    }
                ],
            },
            options: {
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        left: 10,
                        right: 25,
                        top: 25,
                        bottom: 0
                    }
                },
                scales: {
                    xAxes: [{
                        time: {
                            unit: 'date'
                        },
                        gridLines: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            maxTicksLimit: 7
                        }
                    }],
                    yAxes: [{
                        ticks: {
                            maxTicksLimit: 5,
                            padding: 10,
                        },
                        gridLines: {
                            color: "rgb(234, 236, 244)",
                            zeroLineColor: "rgb(234, 236, 244)",
                            drawBorder: false,
                            borderDash: [2],
                            zeroLineBorderDash: [2]
                        }
                    }],
                },
                legend: {
                    display: true
                },
            },
        });
    },
    error: function (error_data) {
        console.log("error");
        console.log(error_data)
    }
});


// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.font.Family = 'Nunito,-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.color = '#858796';

$.ajax({
    method: "GET",
    url: $("#dataCharts").attr("data-url"),
    success: function (data) {
        console.log(data);
        const {prodsAreaLabels} = data;
        const {prodsRepValue} = data;
        const {prodsInValue} = data;
        const {prodsExpValue} = data;
        const {prodsLateValue} = data;
        const {bgaAreaLabels} = data;
        const {bgaTotalValue} = data;
        const {bgaOneValue} = data;
        const {bgaTwoValue} = data;
        const {tcAreaLabels} = data;
        const {tcTempValue} = data;

        // Deal Area Chart
        var ctx1 = document.getElementById("dealAreaChart");
        var dealLineChart = new Chart(ctx1, {
            type: 'line',
            data: {
                labels: prodsAreaLabels,
                datasets: [
                    {
                        data: prodsRepValue,
                        label: "Pdts en cours",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(0, 143, 136, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(0, 143, 136, 1)",
                        pointBorderColor: "rgba(0, 143, 136, 1)",
                    },
                    {
                        data: prodsInValue,
                        label: "Pdts en IN",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(78, 115, 223, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(78, 115, 223, 1)",
                        pointBorderColor: "rgba(78, 115, 223, 1)",
                    },
                    {
                        data: prodsExpValue,
                        label: "Pdts en Exp",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(240, 132, 40, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(240, 132, 40, 1)",
                        pointBorderColor: "rgba(240, 132, 40, 1)",
                    },
                    {
                        data: prodsLateValue,
                        label: "Pdts en Retard",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(214, 54, 33, 1)",
                        pointRadius: 2,
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
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            maxTicksLimit: 5
                        },
                        grid: {
                            color: "rgb(234, 236, 244)",
                            zeroLineColor: "rgb(234, 236, 244)",
                            drawBorder: false,
                            borderDash: [2],
                            zeroLineBorderDash: [2]
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true
                    }
                }
            },
        });

        // BGA Duration Area Chart
        var ctx2 = document.getElementById("bgaAreaChart");
        var bgaLineChart = new Chart(ctx2, {
            type: 'line',
            data: {
                labels: bgaAreaLabels,
                datasets: [
                    {
                        data: bgaTotalValue,
                        label: "Total utilisation BGA",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(0, 143, 136, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(0, 143, 136, 1)",
                        pointBorderColor: "rgba(0, 143, 136, 1)",
                    },
                    {
                        data: bgaOneValue,
                        label: "Utilisation DES-48",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(78, 115, 223, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(78, 115, 223, 1)",
                        pointBorderColor: "rgba(78, 115, 223, 1)",
                    },
                    {
                        data: bgaTwoValue,
                        label: "Utilisation DES-51",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(240, 132, 40, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(240, 132, 40, 1)",
                        pointBorderColor: "rgba(240, 132, 40, 1)",
                    },
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
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        max: 100,
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Valeur en %',
                        },
                        ticks: {
                            maxTicksLimit: 6,
                        },
                        grid: {
                            color: "rgb(234, 236, 244)",
                            zeroLineColor: "rgb(234, 236, 244)",
                            drawBorder: false,
                            borderDash: [2],
                            zeroLineBorderDash: [2]
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true
                    }
                }
            },
        });

        // Thermal Chamber Temperature Area Chart
        var ctx3 = document.getElementById("tcAreaChart");
        var tcLineChart = new Chart(ctx3, {
            type: 'line',
            data: {
                labels: tcAreaLabels,
                datasets: [
                    {
                        data: tcTempValue,
                        label: "Température Chambre Thermique",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(0, 143, 136, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(0, 143, 136, 1)",
                        pointBorderColor: "rgba(0, 143, 136, 1)",
                    },
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
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        max: 80,
                        min: -40,
                        title: {
                            display: true,
                            text: 'Valeur en %',
                        },
                        ticks: {
                            maxTicksLimit: 10,
                        },
                        grid: {
                            color: "rgb(234, 236, 244)",
                            zeroLineColor: "rgb(234, 236, 244)",
                            drawBorder: false,
                            borderDash: [2],
                            zeroLineBorderDash: [2]
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true
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

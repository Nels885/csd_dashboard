// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.font.Family = 'Nunito,-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.color = '#858796';

const suptechOptions = {
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
        },
        datalabels: {
            display: false
        }
    }
}


$.ajax({
    method: "GET",
    url: $("#dataCharts").attr("data-url"),
    success: function (data) {
        // console.log(data);

        // Deal Area Chart
        var ctx1 = document.getElementById("dealAreaChart");
        var dealLineChart = new Chart(ctx1, {
            type: 'line',
            data: {
                labels: data['prodsAreaLabels'],
                datasets: [
                    {
                        data: data['prodsRepValue'],
                        label: "Pdts en cours",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(0, 143, 136, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(0, 143, 136, 1)",
                        pointBorderColor: "rgba(0, 143, 136, 1)",
                    },
                    {
                        data: data['prodsInValue'],
                        label: "Pdts en IN",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(78, 115, 223, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(78, 115, 223, 1)",
                        pointBorderColor: "rgba(78, 115, 223, 1)",
                    },
                    {
                        data: data['prodsExpValue'],
                        label: "Pdts en Exp",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(240, 132, 40, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(240, 132, 40, 1)",
                        pointBorderColor: "rgba(240, 132, 40, 1)",
                    },
                    {
                        data: data['prodsLateValue'],
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

        // Suptech CE Area Chart
        var ctx2 = document.getElementById("suptechCeChart");
        var suptechCeChart = new Chart(ctx2, {

            data: {
                labels: data['suptechCeLabels'],
                datasets: [
                    {
                        type: 'line',
                        data: data['twoDays'],
                        label: "1 à 2 jours (%)",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(0, 143, 136, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(0, 143, 136, 1)",
                        pointBorderColor: "rgba(0, 143, 136, 1)",
                    },
                    {
                        type: 'line',
                        data: data['twoToSixDays'],
                        label: "3 à 6 jours (%)",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(240, 132, 40, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(240, 132, 40, 1)",
                        pointBorderColor: "rgba(240, 132, 40, 1)",
                    },
                    {
                        type: 'line',
                        data: data['sixDays'],
                        label: "7 jours et plus (%)",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(214, 54, 33, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(214, 54, 33, 1)",
                        pointBorderColor: "rgba(214, 54, 33, 1)",
                    },
                    {
                        type: 'bar',
                        data: data['supNumber'],
                        label: "Total suptech",
                        backgroundColor: "rgba(78, 115, 223, 0.2)",
                        borderWidth: 1,
                        datalabels: {
                            align: 'end',
                            anchor: 'end',
                            display: true,
                            font: {
                                weight: 'bold'
                            }
                        }
                    },
                ],
            },
            options: suptechOptions,
            plugins: [ChartDataLabels]
        });

        // BGA Duration Area Chart
        var ctx3 = document.getElementById("bgaAreaChart");
        var bgaLineChart = new Chart(ctx3, {
            type: 'line',
            data: {
                labels: data['bgaAreaLabels'],
                datasets: [
                    {
                        data: data['bgaTotalValue'],
                        label: "Total utilisation BGA",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(0, 143, 136, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(0, 143, 136, 1)",
                        pointBorderColor: "rgba(0, 143, 136, 1)",
                    },
                    {
                        data: data['bgaOneValue'],
                        label: "Utilisation DES-48",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(78, 115, 223, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(78, 115, 223, 1)",
                        pointBorderColor: "rgba(78, 115, 223, 1)",
                    },
                    {
                        data: data['bgaTwoValue'],
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
        var ctx4 = document.getElementById("tcAreaChart");
        var tcLineChart = new Chart(ctx4, {
            type: 'line',
            data: {
                labels: data['tcAreaLabels'],
                datasets: [
                    {
                        data: data['tcTempValue'],
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

        // Suptech Area Chart
        var ctx5 = document.getElementById("suptechCoChart");
        var suptechCoChart = new Chart(ctx5, {
            data: {
                labels: data['suptechCoLabels'],
                datasets: [
                    {
                        type: 'line',
                        data: data['coTwoDays'],
                        label: "1 à 2 jours (%)",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(0, 143, 136, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(0, 143, 136, 1)",
                        pointBorderColor: "rgba(0, 143, 136, 1)",
                    },
                    {
                        type: 'line',
                        data: data['coTwoToSixDays'],
                        label: "3 à 6 jours (%)",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(240, 132, 40, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(240, 132, 40, 1)",
                        pointBorderColor: "rgba(240, 132, 40, 1)",
                    },
                    {
                        type: 'line',
                        data: data['coSixDays'],
                        label: "7 jours et plus (%)",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(214, 54, 33, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(214, 54, 33, 1)",
                        pointBorderColor: "rgba(214, 54, 33, 1)",
                    },
                    {
                        type: 'bar',
                        data: data['coSupNumber'],
                        label: "Total Suptech",
                        backgroundColor: "rgba(78, 115, 223, 0.2)",
                        borderWidth: 1,
                        datalabels: {
                            align: 'end',
                            anchor: 'end',
                            display: true,
                            font: {
                                weight: 'bold'
                            }
                        }
                    },
                ],
            },
            options: suptechOptions,
            plugins: [ChartDataLabels]
        });

        // Raspi Duration Area Chart
        var ctx6 = document.getElementById("raspiAreaChart");
        var raspiLineChart = new Chart(ctx6, {
            type: 'line',
            data: {
                labels: data['raspiAreaLabels'],
                datasets: [
                    {
                        data: data['raspiTotalValue'],
                        label: "Total",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(0, 143, 136, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(0, 143, 136, 1)",
                        pointBorderColor: "rgba(0, 143, 136, 1)",
                    },
                    {
                        data: data['raspiOneValue'],
                        label: "Raspeedi1",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(78, 115, 223, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(78, 115, 223, 1)",
                        pointBorderColor: "rgba(78, 115, 223, 1)",
                    },
                    {
                        data: data['raspiTwoValue'],
                        label: "Raspeedi2",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(240, 132, 40, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(240, 132, 40, 1)",
                        pointBorderColor: "rgba(240, 132, 40, 1)",
                    },
                    {
                        data: data['raspiThreeValue'],
                        label: "Raspeedi3",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(214, 54, 33, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(214, 54, 33, 1)",
                        pointBorderColor: "rgba(214, 54, 33, 1)",
                    },
                    {
                        data: data['raspiFourValue'],
                        label: "Raspeedi4",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(240, 132, 40, 1)",
                        pointRadius: 2,
                        pointBackgroundColor: "rgba(240, 132, 40, 1)",
                        pointBorderColor: "rgba(240, 132, 40, 1)",
                    },
                    {
                        data: data['raspiFiveValue'],
                        label: "Raspeedi5",
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

    },
    error: function (error_data) {
        console.log("error");
        console.log(error_data)
    }
});

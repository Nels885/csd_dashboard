async function getTemp(url) {
    $.ajax({
        url: url,
        dataType: 'json',
        success: function (data) {
            const {temp} = data;
            const thermalTemp = document.getElementById('thermal-temp');
            thermalTemp.textContent = temp;
            thermalTemp.className = "";
            if (parseInt(temp, 10) >= 40) {
                thermalTemp.classList.add('text-danger');
            } else if (parseInt(temp, 10) > 0) {
                thermalTemp.classList.add('text-warning');
            } else if (parseInt(temp, 10) <= 0) {
                thermalTemp.classList.add('text-primary');
            }
        }
    });
}

async function getTempFull(url) {
    $.ajax({
        url: url,
        dataType: 'json',
        success: function (data) {
            const {temp} = data;
            const thermalTemp = document.getElementById('thermal-temp');
            const bgThermal = document.getElementById('bg-thermal');
            thermalTemp.textContent = temp;
            thermalTemp.className = "";
            bgThermal.className = "row justify-content-center my-auto min-vh-100";
            if (parseInt(temp, 10) >= 40) {
                thermalTemp.classList.add('text-gray-200');
                bgThermal.classList.add('bg-danger');
            } else if (parseInt(temp, 10) > 0) {
                thermalTemp.classList.add('text-gray-800');
                bgThermal.classList.add('bg-warning');
            } else if (parseInt(temp, 10) <= 0) {
                thermalTemp.classList.add('text-gray-200');
                bgThermal.classList.add('bg-primary');
            }
        }
    });
}

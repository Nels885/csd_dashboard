$('#btn_calc').on('click', function (event) {
    $.ajax({
        xhrFields: {
            withCredentials: true
        },
        url: 'https://mk4-wiki.denkdose.de/tools/satnav/calc_pin.php',
        type: 'GET',
        data: {
            type: encodeURIComponent(jQuery('#type').val()),
            serial: encodeURIComponent(jQuery('#serial').val()),
        },
        success: function (responseText) {
            let data = JSON.decode(responseText);
            console.log(data);
            if (data['result'] === 'OK') {
                $('#pin_code').val(data['data']);
            } else if (data['result'] === 'ERROR') {
                $('#pin_code').val('----');
                alert(data['message']);
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(jqXHR);
        }
    })
});

$('#btn_calc').on('click', function (event) {
    $.ajax({
        url: '/renault/decode/ajax/',
        type: 'GET',
        dataType: 'json',
        data: {
            precode: encodeURIComponent(jQuery('#precode').val()),
        },
        success: function (data) {
            console.log(data);
            if (data['result'] === 'OK') {
                $('#pin_code').val(data['code']);
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

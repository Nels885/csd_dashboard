function toolSystem(url, mode) {
    url = url + "?mode=" + mode;
    $.ajax({
        method: "get",
        url: url,
        success: function(data) {
            console.log(data);
            if (data['status'] === "busy") {
                addMessage(data['msg'], "warning");
            } else addMessage(data['msg']);
        },
        error: function(error) {
            console.log(error);
            addMessage("Action impossible !", "danger");
        }
    })
}


function aetChange(data, pk) {
    console.log(data)
    let id = '#aet' + pk;
    let status = data['status'];
    $(id).html(status);
    if (status !== 'Hors Ligne') {
        $(id + '-s').removeClass('disabled');
    }
    if (data['percent'] === '0') {
        $(id + '-progress').hide()
    } else {
        $(id + '-progressbar').css({'width': data['percent'].toString() + '%'});
        $(id + '-progress').show()
        if (data['percent'] === '100') {
            addMessage('Succès : Mise à jour du mbed avec succès !');
        }
    }
    if (status.indexOf('Pas besoin de MAJ') !== -1) {
        addMessage('Pas besoin de MAJ, Mbed déjà à jour !', 'warning');
    }
    $(".bd-loading-modal-lg").modal("hide");
}

function toolChange(data, pk) {
    console.log(data);
    let href = data['href'];
    let id = '#tool' + pk;
    // $(id+'-ip').html(data['ip_addr']);
    $(id+'-c').html(data['prog_count']);
    $(id+'-s').html(data['soft']);
    $(id+'-v').html(data['version']);
    $(id+'-d').html(data['device']);
    $(id+'-x').html(data['xelon']);
    $(id).html(data['status']);
    if (data['status_code'] === 404) {
        $(id + '-btn').html('<button class="btn btn-block btn-secondary" disabled>Webapp</button>');
        $(id+'-rb').html('<button class="btn btn-dark btn-circle btn-sm" disabled><i class="fas fa-rotate"></i></button>');
        $(id+'-stp').html('<button class="btn btn-dark btn-circle btn-sm" disabled><i class="fas fa-power-off"></i></button>');
    } else if (data['status'] === 'Libre') {
        $(id+'-btn').html('<a class="btn btn-block btn-secondary" href="' + href + '" target="_blank">Webapp</a>');
        $(id+'-rb').html('<button title="Reboot outil" class="btn btn-warning btn-circle btn-sm" onclick="toolRestart(' + pk + ')"><i class="fas fa-rotate"></i></button>');
        $(id+'-stp').html('<button title="Arrêt outil" class="btn btn-danger btn-circle btn-sm" onclick="toolStop(' + pk + ')"><i class="fas fa-power-off"></i></button>');
    } else {
        $(id+'-btn').html('<a class="btn btn-block btn-secondary" href="' + href + '" target="_blank">Webapp</a>');
        $(id+'-rb').html('<button class="btn btn-dark btn-circle btn-sm" disabled><i class="fas fa-rotate"></i></button>');
        $(id+'-stp').html('<button class="btn btn-dark btn-circle btn-sm" disabled><i class="fas fa-power-off"></i></button>');
    }
}

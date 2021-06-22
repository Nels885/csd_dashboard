function clock() {
    const date = new Date;
    const year = date.getFullYear();
    const month = date.getMonth();
    const months = ['Janvier', 'F&eacute;vrier', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Ao&ucirc;t', 'Septembre', 'Octobre', 'Novembre', 'D&eacute;cembre'];
    const day = date.getDay();
    const days = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];
    let d = date.getDate();
    if (d < 10) {
        d = "0" + d;
    }
    let hour = date.getHours();
    if (hour < 10) {
        hour = "0" + hour;
    }
    let minutes = date.getMinutes();
    if (minutes < 10) {
        minutes = "0" + minutes;
    }
    let seconds = date.getSeconds();
    if (seconds < 10) {
        seconds = "0" + seconds;
    }
    document.getElementById('datetime').innerHTML = days[day] + ' ' + d + ' ' + months[month] + ' ' + year + ' ' + hour + ':' + minutes + ':' + seconds;
}


function addMessage(text, extra_tags, fixed = false) {
    var message = $(`
            <div style="border-radius:0;" class="alert alert-icon alert-${extra_tags} alert-dismissible fade show mb-0" role="alert">\n
                    ${text}\n
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">\n
                    <span aria-hidden="true">&times;</span>\n
                </button>\n
            </div>`).hide();
    $("#messages").append(message);
    message.fadeIn(500);

    if (!fixed) {
        message.fadeTo(10000, 500).slideUp(500, function () {
            message.slideUp(500);
            message.remove();
        });
    }
}


function textCopy(text) {
    const elem = document.createElement('textarea');
    elem.value = text;
    document.body.appendChild(elem);
    elem.select();
    document.execCommand("copy");
    document.body.removeChild(elem);
    alert("Copied the text: " + elem.value);
}

function excelImport(url) {
    $.ajax({
        type: "GET",
        url: url,
        contentType: false,
        processData: false,
        cache: false,
        async: true,
        success: function (res) {
            addMessage("Importation Squalaetp en cours...", "warning");
            getProgress(
                res.task_id,
                progressBarId = "export-corvet-progress-bar",
                progressBarMessageId = "export-corvet-progress-message",
            );
        },
        error: function (err) {
            console.log(err);
            addMessage("Vous n'avez pas la permissions !", "warning");
        },
    })
}


$(function () {
    // Filter Batch buttons
    $(".out-filter-btn").each(function () {
        $(this).modalForm({formURL: $(this).data('form-url')});
    });

    // Commun modal button
    $(".bs-modal").each(function () {
        $(this).modalForm({formURL: $(this).data('form-url')});
    });
    $(".bs-large-modal").each(function () {
        $(this).modalForm({formURL: $(this).data('form-url'), modalID: "#large-modal"});
    });
    $(".bs-small-modal").each(function () {
        $(this).modalForm({formURL: $(this).data('form-url'), modalID: "#small-modal"});
    });

    // Hide message
    $(".fader-auto").fadeTo(10000, 500).slideUp(500, function () {
        $(".fader-auto").slideUp(500);
    });

    $("input[type=file]").change(function (e) {
        $(this).next('.custom-file-label').text(e.target.files[0].name);
    });

    $(".django-ckeditor-widget").css("width", "100%");

});


setInterval('clock()', 1000);

$('#detail-list a').on('click', function (e) {
    e.preventDefault();
    $(this).tab('show')
});

$('.modal').on('shown.bs.modal', function () {
    $(this).find('[autofocus]').focus();
});


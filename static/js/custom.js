function clock() {
    date = new Date;
    year = date.getFullYear();
    month = date.getMonth();
    months = new Array('Janvier', 'F&eacute;vrier', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Ao&ucirc;t', 'Septembre', 'Octobre', 'Novembre', 'D&eacute;cembre');
    day = date.getDay();
    days = new Array('Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi');
    d = date.getDate();
    if (d < 10) {
        d = "0" + d;
    }
    hour = date.getHours();
    if (hour < 10) {
        hour = "0" + hour;
    }
    minutes = date.getMinutes();
    if (minutes < 10) {
        minutes = "0" + minutes;
    }
    seconds = date.getSeconds();
    if (seconds < 10) {
        seconds = "0" + seconds;
    }
    resultat = days[day] + ' ' + d + ' ' + months[month] + ' ' + year + ' ' + hour + ':' + minutes + ':' + seconds;
    document.getElementById('datetime').innerHTML = resultat;
}

clock();
setInterval(clock, 1000);

$('#detail-list a').on('click', function (e) {
    e.preventDefault();
    $(this).tab('show')
});

$('.modal').on('shown.bs.modal', function () {
    $(this).find('[autofocus]').focus();
});

function addMessage(text, extra_tags) {
    var message = $(`
            <div style="border-radius:0;" class="alert alert-icon alert-${extra_tags} alert-dismissible fade show mb-0" role="alert">\n
                    ${text}\n
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">\n
                    <span aria-hidden="true">&times;</span>\n
                </button>\n
            </div>`).hide();
    $("#messages").append(message);
    message.fadeIn(500);

    message.fadeTo(10000, 500).slideUp(500, function () {
        message.slideUp(500);
        message.remove();
    });
}

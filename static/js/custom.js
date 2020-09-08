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

$('#detail-list a').on('click', function (e) {
    e.preventDefault();
    $(this).tab('show')
});

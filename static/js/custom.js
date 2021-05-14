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

$(function () {
    // Hide message
    $(".fader-auto").fadeTo(10000, 500).slideUp(500, function () {
        $(".fader-auto").slideUp(500);
    });

    $("input[type=file]").change(function (e) {
        $(this).next('.custom-file-label').text(e.target.files[0].name);
    });

    $(".django-ckeditor-widget").css("width", "100%")
});

getProgress = (taskId, progressBarId, progressBarMessageId, isDownloadFile = false) => {
    var progressUrl = `{% url 'progress' %}?task_id=${taskId}`;

    function onExportUserProgress(progressBarElement, progressBarMessageElement, progress) {
        progressBarMessageElement.innerHTML = `Progress ${progress.percent}% . . .`
        progressBarElement.setAttribute("style", `width: ${progress.percent}%`)
        progressBarElement.setAttribute("aria-valuenow", progress.percent)
    }

    function onExportUserSuccess(progressBarElement, progressBarMessageElement, result) {
        alert("Complete progress 100%")
        progressBarMessageElement.innerHTML = "Waiting event . . ."
        progressBarElement.setAttribute("style", "width: 0%")
        progressBarElement.setAttribute("aria-valuenow", 0)
        if (isDownloadFile) window.open(`{% url 'download' %}?task_id=${taskId}`, '_blank');
    }

    CeleryProgressBar.initProgressBar(progressUrl, {
        progressBarId: progressBarId,
        progressBarMessageId: progressBarMessageId,
        onProgress: onExportUserProgress,
        onSuccess: onExportUserSuccess,
    })
}
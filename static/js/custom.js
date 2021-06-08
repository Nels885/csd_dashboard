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


function textCopy(text) {
    console.log(text);
    const elem = document.createElement('textarea');
    elem.value = text;
    document.body.appendChild(elem);
    elem.select();
    document.execCommand("copy");
    document.body.removeChild(elem);
    alert("Copied the text: " + elem.value);
}


$(function () {
    // Log in buttons
    $(".login-btn").modalForm({formURL: "{% url 'dashboard:login' %}"});
    $(".logout-btn").modalForm({formURL: "{% url 'dashboard:logout' %}"});

    $(".create-post").modalForm({formURL: "{% url 'dashboard:create_post' %}", modalID: "#large-modal"});

    $(".create-weblink").modalForm({formURL: "{% url 'dashboard:create_weblink' %}", modalID: "#large-modal"});

    $(".create-corvet").modalForm({formURL: "{% url 'psa:create_corvet' %}", modalID: "#large-modal"});

    $(".create-batch").modalForm({formURL: "{% url 'reman:create_batch' %}"});

    $(".create-repair").modalForm({formURL: "{% url 'reman:create_repair' %}"});

    $(".create-etude-batch").modalForm({formURL: "{% url 'reman:create_etude_batch' %}"});

    $(".create-default").modalForm({formURL: "{% url 'reman:create_default' %}", modalID: "#create-large-modal"});

    $(".create-ref-reman").modalForm({formURL: "{% url 'reman:ref_reman_create' %}"});

    $(".create-ecu-hw").modalForm({formURL: "{% url 'reman:ecu_hw_create' %}", modalID: "#create-large-modal"});

    $(".create-tag-xelon").modalForm({formURL: "{% url 'tools:tag_xelon_add' %}", modalID: "#create-modal"});

    $(".create-suptech").modalForm({formURL: "{% url 'tools:suptech_add' %}", modalID: "#create-large-modal"});

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


clock();
setInterval(clock, 1000);

$('#detail-list a').on('click', function (e) {
    e.preventDefault();
    $(this).tab('show')
});

$('.modal').on('shown.bs.modal', function () {
    $(this).find('[autofocus]').focus();
});


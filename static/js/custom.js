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


function addMessage(text, extra_tags = "success", fixed = false) {
    var message = $(`
            <div style="border-radius:0;" class="alert alert-icon alert-${extra_tags} alert-dismissible fade show mb-0" role="alert">\n
                    ${text}\n
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">\n
                    <span aria-hidden="true">&times;</span>\n
                </button>\n
            </div>`).hide();
    $("#messages").append(message);
    message.fadeIn(500);

    if (!fixed && extra_tags === "success") {
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
    addMessage(elem.value + " copié !");
    // alert("Copied the text: " + elem.value);
}


function resultTask(task_id=null) {
    let url = new URL(window.location.href);
    let params = new URLSearchParams(url.search);
    if (task_id === null){
        task_id = params.get('task_id')
    }
    if (task_id) {
        $(".bd-loading-modal-lg").modal("show");
        var progressUrl = "/celery-progress/?task_id=" + task_id;
        // console.log(progressUrl);

        function customResult(resultElement, result) {
            // console.log(result)
            $(".bd-loading-modal-lg").modal("hide");
            addMessage(result.msg, result.tags);

            if (params.get('task_id')) {
                params.delete('task_id');
                url.search = params;
                // console.log(url.toString());
                window.history.pushState({}, null, url.toString())
            }
        }

        CeleryProgressBar.initProgressBar(progressUrl, {
            progressBarId: "search-progress-bar",
            progressBarMessageId: "search-progress-bar-message",
            onResult: customResult,
        })
    } else {
        $(".bd-loading-modal-lg").modal("hide");
    }
}


function celeryTask(url) {
    $(".bd-loading-modal-lg").modal("show");
    $.ajax({
        type: "GET",
        url: url,
        contentType: false,
        processData: false,
        cache: false,
        async: true,
        success: function (data) {
            // console.log(data);
            resultTask(data.task_id);
        },
        error: function (err) {
            // console.log(err);
            $(".bd-loading-modal-lg").modal("hide");
            addMessage("Vous n'avez pas la permissions !", "warning");
        },
    })
}




$(function () {
    // Filter Batch buttons
    $(".filter-btn").each(function () {
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


$(".unmask a").on('click', function (event) {
    event.preventDefault();
    if ($('.unmask input').attr("type") === "text") {
        $('.unmask input').attr('type', 'password');
        $('.unmask i').addClass("fa-eye-slash");
        $('.unmask i').removeClass("fa-eye");
    } else if ($('.unmask input').attr("type") === "password") {
        $('.unmask input').attr('type', 'text');
        $('.unmask i').removeClass("fa-eye-slash");
        $('.unmask i').addClass("fa-eye");
    }
});


$("#searchForm").submit(function (e) {
    e.preventDefault();
    let formData = new FormData($("#searchForm")[0]);
    $(".bd-loading-modal-lg").modal("show");
    $.ajax({
        method: "POST",
        url: $("#searchForm").attr("data-url"),
        data: formData,
        contentType: false,
        processData: false,
        success: function (data) {
            // console.log(data);
            if (data.task_id) {
                var progressUrl = "/celery-progress/?task_id=" + data.task_id;

                // console.log(progressUrl);

                function customResult(resultElement, result) {
                    window.location = data.url;
                }

                CeleryProgressBar.initProgressBar(progressUrl, {
                    progressBarId: "search-progress-bar",
                    progressBarMessageId: "search-progress-bar-message",
                    onResult: customResult,
                })
            } else window.location = data.url;
        },
        error: function (error_data) {
            $(".bd-loading-modal-lg").modal("hide");
            addMessage("(500) Internal Server Error", "danger");
        }
    });
});

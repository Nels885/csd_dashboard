$(function () {
    $("#export-corvet").on("submit", (e) => {
        e.preventDefault();
        let formData = new FormData($("#export-corvet")[0]);
        // formData.append("csrfmiddlewaretoken", "{% csrf_token %}");
        $.ajax({
            type: "POST",
            url: CORVET_URL,
            data: formData,
            contentType: false,
            processData: false,
            cache: false,
            async: true,
            success: function (res) {
                getProgress(
                    res.task_id,
                    progressBarId = "export-corvet-progress-bar",
                    progressBarMessageId = "export-corvet-progress-message",
                    isDownloadFile = true
                )
            },
            error: function (err) {
                console.log(err);
            },
        })
    });

    $("#export-corvet-vin").on("submit", (e) => {
        e.preventDefault();
        let formData = new FormData($("#export-corvet-vin")[0]);
        // formData.append("csrfmiddlewaretoken", "{% csrf_token %}");
        $.ajax({
            type: "POST",
            url: CORVET_VIN_URL,
            data: formData,
            contentType: false,
            processData: false,
            cache: false,
            async: true,
            success: function (res) {
                getProgress(
                    res.task_id,
                    progressBarId = "export-corvet-vin-progress-bar",
                    progressBarMessageId = "export-corvet-vin-progress-message",
                    isDownloadFile = true
                )
            },
            error: function (err) {
                console.log(err);
            },
        });
    });

    $("#export-reman").on("submit", (e) => {
        e.preventDefault();
        let formData = new FormData($("#export-reman")[0]);
        // formData.append("csrfmiddlewaretoken", "{% csrf_token %}");
        $.ajax({
            type: "POST",
            url: REMAN_URL,
            data: formData,
            contentType: false,
            processData: false,
            cache: false,
            async: true,
            success: function (res) {
                getProgress(
                    res.task_id,
                    progressBarId = "export-reman-progress-bar",
                    progressBarMessageId = "export-reman-progress-message",
                    isDownloadFile = true
                )
            },
            error: function (err) {
                console.log(err);
            },
        });
    });

    $("#export-tools").on("submit", (e) => {
        e.preventDefault();
        let formData = new FormData($("#export-tools")[0]);
        // formData.append("csrfmiddlewaretoken", "{% csrf_token %}");
        $.ajax({
            type: "POST",
            url: TOOLS_URL,
            data: formData,
            contentType: false,
            processData: false,
            cache: false,
            async: true,
            success: function (res) {
                getProgress(
                    res.task_id,
                    progressBarId = "export-tools-progress-bar",
                    progressBarMessageId = "export-tools-progress-message",
                    isDownloadFile = true
                )
            },
            error: function (err) {
                console.log(err);
            },
        });
    });
});
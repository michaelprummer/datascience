function SetupDB() {
    $.ajax({
        url: 'api/Api.php',
        data: {action: 'setup'},
        type: 'post',
        success: function (output) {
            alert(output);
        }
    });
}

function RemoveDB() {
    $.ajax({
        url: 'api/Api.php',
        data: {action: 'remove'},
        type: 'post',
        success: function (output) {
            alert(output);
        }
    });
}

function ClearDB() {
    $.ajax({
        url: 'api/Api.php',
        data: {action: 'clear'},
        type: 'post',
        success: function (output) {
            alert(output);
        }
    });
}
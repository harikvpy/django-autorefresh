function save_options() {
    var port = document.getElementById('port').value;
    localStorage['port'] = port;
    // Update status to let user know options were saved.
    var status = document.getElementById('status');
    status.textContent = 'Options saved.';
    setTimeout(function() {
            status.textContent = '';
        }, 1500);
}

function restore_options() {
    // Use default value port = 32000
    var port = localStorage['port'];
    if (port == undefined) {
        port = 32000;
    }
    document.getElementById('port').value = port;
}

document.addEventListener('DOMContentLoaded', restore_options);
document.getElementById('save').addEventListener('click', save_options);


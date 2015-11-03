"use strict";
// This is global as it is accessed from outside this module
var djangoautorefresh;

// introduce a namespace to keep everything else private
(function () {

const Cc = Components.classes;
const Ci = Components.interfaces;
const Cr = Components.results;
const Cu = Components.utils;

// From http://javascript.crockford.com/prototypal.html
function object(o) {
    function F() {}
    F.prototype = o;
    return new F();
}

function deArray(log) {
    return function(msg) {
        if (typeof(msg) != "string") {
            for(var i = 0; i < msg.length; ++i) {
                console.log(msg[i]);
            }
        } else {
            console.log(msg);
        }
    }
}

djangoautorefresh = {
    controlledWindow: null,
    serverSocket: null,
    timerId: 0,
    pollInterval: 1000,
    buttonID: 'djangoautorefresh-toolbar-button',

    onLoad: function() {
        // initialization code
        this.initialized = true;
        this.strings = document.getElementById("djangoautorefresh-strings");
        this.alignToolbarButton();

        var buttonInstalledPref =
            "extensions.djangoautorefresh.toolbarButtonInitiallyInstalled";
        var prefManager = Components.classes[
            "@mozilla.org/preferences-service;1"
        ].getService(Components.interfaces.nsIPrefBranch);
        if (!prefManager.getBoolPref(buttonInstalledPref)) {
            prefManager.setBoolPref(buttonInstalledPref, true)
            this.installToolbarButton();
        }

        this.maybeStartAutomatically();
    },

    log: function (msg) {
        if (typeof(Firebug) == "object" &&
            typeof(Firebug.Console) == "object") {
            this.log = Firebug.Console.log;
        } else if (typeof(console) == "object") {
            this.log = deArray(console.log);
        } else {
                throw "There's no way to log anything :( " + msg;
        }
        return this.log(msg);
    },

    pollForChanges: function() {
        //console.log("polling for changes...");
        const { XMLHttpRequest } = Components.classes["@mozilla.org/appshell/appShellService;1"]
                                       .getService(Components.interfaces.nsIAppShellService)
                                       .hiddenDOMWindow;
        var oReq = new XMLHttpRequest();
        oReq.addEventListener("load", function(e) {
            //console.log(oReq.response);
            var obj = JSON.parse(oReq.response);
            if (obj.changed) {
                //console.log("Django server reloaded, reloading location: " + djangoautorefresh.controlledWindow.document.location);
                djangoautorefresh.controlledWindow.document.location.reload();
            }
        });
        var prefs = this.getPreferences();
        var url = "http://localhost:" + prefs.portNumber;
        oReq.open("GET", url);
        oReq.send();
    },

    startPoller: function() {
        var wm = Components.classes['@mozilla.org/appshell/window-mediator;1']
            .getService(Components.interfaces.nsIWindowMediator);
        this.controlledWindow = wm.getMostRecentWindow(
                'navigator:browser'
            ).getBrowser().contentWindow;
        if (this.timerId != 0) {
            clearInterval(this.timerId);
            this.timerId = 0;
        }
        this.timerId = setInterval(function() {
            djangoautorefresh.pollForChanges();
        }, this.pollInterval);
    },

    toggleControlSocket: function() {
        if (this.timerId == 0) {
            this.startPoller();
        } else {
            clearInterval(this.timerId);
            this.timerId = 0;
        }
        this.alignToolbarButton();
    },

    maybeStartAutomatically: function () {
        var start = Components.classes[
                "@hari.xyz/djangoautorefresh/command-line-handler;1"
            ]
            .getService()
            .wrappedJSObject
            .startDjangoAutoRefreshOnce();
        if (start) {
            this.startPoller();

            // Adjust button.checked state
            var button = document.getElementById(this.buttonID);
            if (button) {
                button.checked = "true";
            }
        }
    },

    onToolbarButtonCommand: function(e) {
        this.toggleControlSocket();
    },

    getPreferences: function () {
            var prefManager = Components.classes[
                "@mozilla.org/preferences-service;1"
            ].getService(Components.interfaces.nsIPrefBranch);
            var portNumber = prefManager.getIntPref(
                "extensions.djangoautorefresh.portNumber"
            );
            return {
                portNumber: portNumber
            };
    },

    alignToolbarButton: function() {
        var button = document.getElementById(this.buttonID);
        if (! button) {
            return;
        }
        var ttText;
        if (this.timerId != 0) {
            // Add the 'active' class
            if (! button.className.match(/ active/)) {
                button.className += " active";
            }
            var prefs = this.getPreferences();

            ttText = this.strings.getFormattedString(
                "enabledToolbarTooltip",
                [ prefs.portNumber ]
            );
            button.checked = "true";
        } else {
            button.className = button.className.replace(/ active/, '');
            ttText = this.strings.getString('disabledToolbarTooltip');
            button.checked = false;
        }
        button.setAttribute('tooltiptext', ttText);
    },

    // Modified from https://developer.mozilla.org/en-US/docs/Code_snippets/Toolbar?redirectlocale=en-US&redirectslug=Code_snippets%3AToolbar#Adding_button_by_default
    installToolbarButton: function () {
        if (!document.getElementById(this.buttonID)) {
            var toolbar = document.getElementById('nav-bar');
            toolbar.insertItem(this.buttonID, null);
            toolbar.setAttribute("currentset", toolbar.currentSet);
            document.persist(toolbar.id, "currentset");

            this.alignToolbarButton();
        }
    },
};

window.addEventListener(
    "load",
    function djangoautorefreshOnload() {
        window.removeEventListener("load", djangoautorefreshOnload);
        djangoautorefresh.onLoad();
    },
    false,
    false
);

})();

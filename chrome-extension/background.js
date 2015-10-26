// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

var activeMap = {};
var timerIdMap = {};
var pollInterval = 1 * 1000;
var timerId = 0;

function autoRefresh(tabId) {
    var searchUrl = "http://localhost:32000/";
    var x = new XMLHttpRequest();
    x.open('GET', searchUrl);
    //x.responseType = 'json';
    x.onload = function() {
        //console.log("response from localhost received");
        var response = JSON.parse(x.response);
        if (response.changed) {
            console.log("changes detected, refreshing tab: "+tabId);
            chrome.tabs.reload(tabId);
        }
    };
    x.onerror = function() {
        console.log("network error");
    };
    x.send();
    timerIdMap[tabId] = window.setTimeout(autoRefresh, pollInterval, tabId);
}

function setIcon(active) {
    // changes the extension icon to reflect its state according
    // to the passed boolean argument.
    var iconFile = "icon_passive.png";
    if (active) {
        iconFile = "icon_active.png";
    }
    chrome.browserAction.setIcon({path:iconFile});
}

chrome.browserAction.onClicked.addListener(function() {
    // When the button is clicked, we toggle the active state of 
    // hte icon for the active tab and create an entry in the 
    // activeMap to reflect this state indexed by the tab id.
    var queryInfo = {
        active: true,
        currentWindow: true
    };
    chrome.tabs.query(queryInfo, function(tabs) {

        // chrome.tabs.query invokes the callback with a list of tabs that match the
        // query. When the popup is opened, there is certainly a window and at least
        // one tab, so we can safely assume that |tabs| is a non-empty array.
        // A window can only have one active tab at a time, so the array consists of
        // exactly one tab.
        var tab = tabs[0];

        // A tab is a plain object that provides information about the tab.
        // See https://developer.chrome.com/extensions/tabs#type-Tab
        //var url = tab.url;

        var curState = false;
        if (activeMap[tab.id] != undefined) {
            var curState = activeMap[tab.id];
        }
        // toggle curState
        if (curState) { 
            //console.log("deactivating auto refresh on tab: " + tab.id);
            window.clearTimeout(timerIdMap[tab.id]);
            delete activeMap[tab.id];
            delete timerIdMap[tab.id];
            curState = false;
        } else { 
            //console.log("activating auto refresh on tab: " + tab.id);
            activeMap[tab.id] = true;
            timerIdMap[tab.id] = window.setTimeout(autoRefresh, 1, tab.id);
            curState = true;
        }
        setIcon(curState);
    });
});

chrome.tabs.onActivated.addListener(function(activeInfo) {
    // if the activated tab has an entry in our activeMap
    // we paint the icon to reflect this state. If an entry
    // does not exist, we paint the icon as passive.
    var tabId = activeInfo.tabId;

    if (activeMap[tabId] != undefined) {
        setIcon(activeMap[tabId]);
    } else {
        setIcon(false);
    }
});

chrome.tabs.onRemoved.addListener(function(tabId, removeInfo) {
    // if an entry for the closed tab was made in the tab-autorefresh 
    // state map, remove it
    if (activeMap[tabId] !== undefined) {
        // entry exists! remove it
        //console.log("removing from refresh map tab: " + tabId); 
        delete activeMap[tabId]; 
        delete timerIdMap[tabId];
    }
});


require([
    "/static/app/search/pie.js",
    "splunkjs/mvc/searchmanager",
    "splunkjs/mvc/postprocessmanager",
    "splunkjs/mvc/simplexml/element/chart",
    "splunkjs/mvc/d3chart/d3chartview",
    "splunkjs/mvc/simplexml/ready!"
], function(JenkinsView, SearchManager, PostProcessManager, ChartElement, D3ChartView) {

    // Create a custom view
    var customView1 = new JenkinsView({
        id: "Artifactory",
        managerid: "search",
        el: $("#customview1")
    }).render();

    var search = new SearchManager({
        id: "search",
        earliest_time: "-60m@s",
        latest_time: "",
        cache: true,
        search: 'index=resystem sourcetype="appstat" Application="Artifactory" | stats latest(State) latest(CPU%) latest(MEM%) by host'
    });

    var customView2 = new JenkinsView({
        id: "Perforce",
        managerid: "search2",
        el: $("#customview2")
    }).render();

    var search2 = new SearchManager({
        id: "search2",
        earliest_time: "-60m@s",
        latest_time: "",
        cache: true,
        search: 'index=resystem sourcetype="appstat" Application="Perforce" | stats latest(State) latest(CPU%) latest(MEM%) by host'
    });

    var customView3 = new JenkinsView({
        id: "Bamboo",
        managerid: "search3",
        el: $("#customview3")
    }).render();

    var search3 = new SearchManager({
        id: "search3",
        earliest_time: "-60m@s",
        latest_time: "",
        cache: true,
        search: 'index=resystem sourcetype="appstat" Application="Bamboo" | stats latest(State) latest(CPU%) latest(MEM%) by host'
    });

    var customView4 = new JenkinsView({
        id: "Bitbucket",
        managerid: "search4",
        el: $("#customview4")
    }).render();

    var search4 = new SearchManager({
        id: "search4",
        earliest_time: "-60m@s",
        latest_time: "",
        cache: true,
        search: 'index=resystem sourcetype="appstat" Application="Bitbucket" | stats latest(State) latest(CPU%) latest(MEM%) latest(State) by host'
    });

    var customView5 = new JenkinsView({
        id: "Jenkins",
        managerid: "search5",
        el: $("#customview5")
    }).render();

    var search5 = new SearchManager({
        id: "search5",
        earliest_time: "-60m@s",
        latest_time: "",
        cache: true,
        search: 'index=resystem sourcetype="appstat" Application="Jenkins" | stats latest(State) latest(CPU%) latest(MEM%) by host'
    });

});

/*
require([
    "/static/app/search/pie.js",
    "splunkjs/mvc/searchmanager",
    "splunkjs/mvc/postprocessmanager",
    "splunkjs/mvc/simplexml/element/chart",
    "splunkjs/mvc/d3chart/d3chartview",
    "splunkjs/mvc/simplexml/ready!"
], function(JenkinsView, SearchManager, PostProcessManager, ChartElement, D3ChartView) {


    var customView = new JenkinsView({
        id: "Perforce",
        managerid: "search2",
        el: $("#customview2")
    }).render();

    var search2 = new SearchManager({
        id: "search2",
        earliest_time: "-60m@s",
        latest_time: "",
        cache: true,
        search: 'index=resystem sourcetype="appstat" Application="Perforce" | stats latest(State) latest(CPU%) latest(MEM%) by host'
    });

});


require([
    "/static/app/search/pie.js",
    "splunkjs/mvc/searchmanager",
    "splunkjs/mvc/postprocessmanager",
    "splunkjs/mvc/simplexml/element/chart",
    "splunkjs/mvc/d3chart/d3chartview",
    "splunkjs/mvc/simplexml/ready!"
], function(JenkinsView, SearchManager, PostProcessManager, ChartElement, D3ChartView) {

    var customView = new JenkinsView({
        id: "Bamboo",
        managerid: "search3",
        el: $("#customview3")
    }).render();

    var search3 = new SearchManager({
        id: "search3",
        earliest_time: "-60m@s",
        latest_time: "",
        cache: true,
        search: 'index=resystem sourcetype="appstat" Application="Bamboo" | stats latest(State) latest(CPU%) latest(MEM%) by host'
    });

});


require([
    "/static/app/search/pie.js",
    "splunkjs/mvc/searchmanager",
    "splunkjs/mvc/postprocessmanager",
    "splunkjs/mvc/simplexml/element/chart",
    "splunkjs/mvc/d3chart/d3chartview",
    "splunkjs/mvc/simplexml/ready!"
], function(JenkinsView, SearchManager, PostProcessManager, ChartElement, D3ChartView) {

    // Create a custom view
    var customView = new JenkinsView({
        id: "Bitbucket",
        managerid: "search4",
        el: $("#customview4")
    }).render();

    var search4 = new SearchManager({
        id: "search4",
        earliest_time: "-60m@s",
        latest_time: "",
        cache: true,
        search: 'index=resystem sourcetype="appstat" Application="Bitbucket" | stats latest(State) latest(CPU%) latest(MEM%) latest(State) by host'
    });

});



require([
    "/static/app/search/pie.js",
    "splunkjs/mvc/searchmanager",
    "splunkjs/mvc/postprocessmanager",
    "splunkjs/mvc/simplexml/element/chart",
    "splunkjs/mvc/d3chart/d3chartview",
    "splunkjs/mvc/simplexml/ready!"
], function(JenkinsView, SearchManager, PostProcessManager, ChartElement, D3ChartView) {

    // Create a custom view
    var customView = new JenkinsView({
        id: "Jenkins",
        managerid: "search5",
        el: $("#customview5")
    }).render();

    var search5 = new SearchManager({
        id: "search5",
        earliest_time: "-60m@s",
        latest_time: "",
        cache: true,
        search: 'index=resystem sourcetype="appstat" Application="Jenkins" | stats latest(State) latest(CPU%) latest(MEM%) by host'
    });

});
*/

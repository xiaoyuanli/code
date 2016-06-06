define(function(require, exports, module){
    // Base class for custom views
    var SimpleSplunkView = require('splunkjs/mvc/simplesplunkview');

    // Define the custom view class
    var JenkinsView = SimpleSplunkView.extend({
        className: "jenkinsview",

        // Change the value of the "data" property
        options: {
            data: "results"
        },

        // Override this method to configure your view
        // This function must return a handle to the view, which is then passed
        // to the updateView method as the first argument. Because there is no
        // visualization, just return 'this'
        createView: function() {
            return this;
        },

        // Override this method to put the Splunk data into the view
        updateView: function(viz, data) {
            // Print the data object to the console
            console.log("The data object: " + data);
            //console.log("The swapData object: " + swapData);


            var width = 550,
                height = 500,
                maxRadius = Math.min(width, height) / 2;

            
            data = data.toString().split(','); // Sets this to the first (and only) row
            console.log("data length is " + data.length);
            var multiLevelData = [];
            var level = 4; 
            var numPerArray = 4; //data per row 
            var numHosts = data.length/numPerArray; // number of hosts per application
            var prevColor; 

            console.log("data length is " + data.length);
  

            //insert middle label, hardcoded label for now
            var label = this.id.toString().split(',');
            multiLevelData.push(label);


            //sort data into levels
            for ( var i = 0; i < numPerArray; i++){
                var levelData = [];
                for( var j = 0; j < numHosts; j++){
                    levelData.push(data[j * numPerArray - 1 + level])
                }

                level--;
                multiLevelData.push(levelData);
            }


            var pieWidth = parseInt(maxRadius / multiLevelData.length) - multiLevelData.length;
            var color = d3.scale.ordinal().range(["#3182bd", "#6baed6", "#9ecae1", "#c6dbef", "#9edae5"]);

	    /*
            var svg = d3.select("#customview1").append("svg")
                .attr("width", width)
                .attr("height", height)
                .append("g")
                .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")"); 
            */

	    console.log("this id is " + this.el);
            var svg = d3.select(this.el).append("svg")
                .attr("width", width)
                .attr("height", height)
                .append("g")
                .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")"); 

            console.log("1st level is " + multiLevelData[0]);
            console.log("2nd level is " + multiLevelData[1]);
            console.log("3rd level is " + multiLevelData[2]);


            var drawPieChart = function(_data, index) {

                var pie = d3.layout.pie()
                    .sort(null)
                    .value(function(d) {
                        console.log("creating pie value for " + d);
                        return 1; //equal value to make all arcs equal length

                    });

                var arc = d3.svg.arc()
                    .outerRadius((index + 1) * pieWidth - 1)
                    .innerRadius(index * pieWidth)

             
                var g = svg.selectAll(".arc" + index).data(pie(_data)).enter().append("g")
                    .attr("class", "arc" + index);
             
                g.append("path")
                    .attr("d", arc)
                    .style("stroke", "white")
                    .style("stroke-width", 5)
                    .style("fill", function(d,i) {
                        console.log("creating color for " + d.data);

                        if(d.data > 50){
			    color(index);
                            return "#E36479";   //red 
                        }

			if(index == 4 && multiLevelData[3][i] == "X"){
				color(index);
				return "#E36479"; //red
			}
                        return color(index);
                    })
             
                g.append("text").attr("transform", function(d) {
                        return "translate(" + arc.centroid(d) + ")";
                    })
                    .attr("dy", ".35em").style("text-anchor", "middle")
                    .text(function(d) {
                        console.log("appending text for " + d.data);
                        var textLabel = d.data;

                        if(index == 2){
                            textLabel = "CPU: " + textLabel;
                        }
                        if(index == 1){
                            textLabel = "Disk: " + textLabel;
                        }
			


                        return textLabel;
                    });

            }//drawPieChart 

            //for calling hierarchical data to draw pie chart 
            for (var i = 0; i < multiLevelData.length; i++) {
                var _cData = multiLevelData[i];
                console.log("cData is " + _cData + " index is " + i);
                drawPieChart(_cData, i); //adjust index
            }


            //Add mouse events for application / center

            svg.selectAll("g.arc0")
                .on("mouseover", function(){
                    d3.select(this).select("path").transition()
                        .duration(300)
                        .style("fill", "gray");

                })
                .on("mouseout", function(){
                    d3.select(this).select("path").transition()
                        .duration(300)
                        .style("fill", color(0)); //change color back to level 0's color

                })
                .on("click", function(d) {
                    console.log("clicked on application " + d.data);
		    changePage("http://re-latitude:8000/en-US/app/search/new_drilldown?form.field1.earliest=-7d%40h&form.field1.latest=now&earliest=0&latest=&form.app=" + d.data);
                });


            //Add mouse events for hosts
            svg.selectAll("g.arc4")
                .on("mouseover", function(){
                    prevColor = d3.select(this).select("path").style("fill");
                    d3.select(this).select("path").transition()
                        .duration(300)
                        .style("fill", "gray");

                })
                .on("mouseout", function(){
                    d3.select(this).select("path").transition()
                        .duration(300)
                        .style("fill", prevColor); //change color back to level 4's color

                })
                .on("click", function(d) {
                    console.log("clicked on host " + d.data);
		    changePage("http://re-latitude:8000/en-US/app/search/server_view?form.field1.earliest=-7d%40h&form.field1.latest=now&earliest=0&latest=&form.host=" + d.data);
		    
            });



            
            //Changing pages upon clicking label
            
            var changePage = function(newUrl){
                
                window.location = newUrl;

            }//changePage
            


        }// updateView
    });

    return JenkinsView;

});

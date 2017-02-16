var anomaly_chart;
var dimension_chart;
var source_data;

var x_axis
var y_axis
var score_tolerance = 0.5

$(document).ready(function() {

    $('#scoreTolerance').bootstrapSlider({
        formatter: function(value) {

            if (value == 2){
                value = "2+";
            }

            return 'Current value: ' + value;
        },
    });


    $("#scoreTolerance").on("slideStop", function(slideEvt) {
        updateChartTolerance(slideEvt.value)
    });

});

function updateChartTolerance(tolerance = 0.5 ){

    // updating anomaly chart
    var column_a = []

    // Adjust anomalies table
    for(i=0; i < source_data.result.records.length; i++)
    {

        if ( json["result"][i][0] > 1 + tolerance ){
            column_a[i] = json["result"][i][2];
        } else {
            column_a[i] = null;
        }
    }

    column_a.unshift("Anomaly")

    dimension_chart.load({
        columns: [
            column_a
        ],
    });


    // updating anomaly table
    // TODO update table
}

function updateChartType(type = 'scatter' ){
    // TODO enum values
    dimension_chart.transform(type, y_axis);
}

function detectAnomaly(){

    var api_url = $( "#api-link" ).val();
    var field_name = $( "#field-name" ).val();

    $(".anomalyDetectionResults").fadeIn();
    $("#detectAnomaly").fadeOut();


    var response = $.getJSON(api_url, function(data) {
        data["x"] = "_id";
        data["y"] = field_name;
        json = JSON.stringify(data);

        // TODO dynamic links
        var url = "http://vmrtpa05.deri.ie:8002/detectAnomalies/lof";
        var dataType ="aplication/json";

        x_axis = data["x"]
        y_axis = data["y"]

        var data_source_dimensions = []

        source_data = data;

        $.ajax({
            type: "POST",
            url: url,
            data: json,
            success: function(data){

                json = JSON.parse(data);

                if (json["result"].length == 0) {

                   $(".anomalyDetectionResults").hide();
                   $(".noAnomalyDetected").fadeIn();

                   return false;

                }

                var table = "<tr><thead>"

                data_source_dimensions = []
                for (field in source_data.result.fields){
                    data_source_dimensions.push(source_data.result.fields[field].id)
                    table += "<th>" + source_data.result.fields[field].id + "</th>"
                }

                table += "<th> Anomaly Score </th> </thead> </tr>";

                for (index in json["result"]){
                    if (json["result"][index][0] > 1.0){

                        table += "<tr>";

                        for (dimension in data_source_dimensions) {
                            table += "<td>" + source_data.result.records[index][data_source_dimensions[dimension]] + "</td>"
                        }

                        table += "<td>" + json["result"][index][0] + "</td>"
                        table += "</tr>"

                    }
                }

                 table = "<table class='span12 table table-hover table-striped table-anomalies'>" + table + "</table>";
                 table = "<div class='alert alert-error top20'>The following values are detected as potential anomalies</div>" + table;

                 $("#anomaly-output").html(table);

                // Pares the data for the chart
                var column_x    = []
                var column_y    = []
                var column_a    = []
                var column_as   = []

                //json["result"][i][j] :: j
                // 0 - score
                // 1 - x
                // 2 - y

                // Parse X + Y + make Anomalies null
                for(i=0; i < source_data.result.records.length; i++)
                {
                    column_x[i] = source_data.result.records[i][x_axis];
                    column_y[i] = source_data.result.records[i][y_axis];
                    column_as[i] = json["result"][i][0];

                    if ( json["result"][i][0] > 1 + score_tolerance ){
                        column_a[i] = json["result"][i][2];
                    } else {
                        column_a[i] = null;
                    }
                }

                column_x.unshift(x_axis)
                column_y.unshift(y_axis)
                column_a.unshift("Anomaly")
                column_as.unshift("Anomaly Score")

                dimension_chart = c3.generate({
                    bindto: '#dimension-chart',
                    point: {
                        r: function(d) {

                            if (d.id == "Anomaly"){
                                return 4 * column_as[d.index + 1];
                            }
                            return 3;

                        }
                    },
                    data: {
                        x: x_axis,
                        columns: [
                            column_x,
                            column_y,
                            column_a,
                        ],
                        type: 'scatter'
                    },
                    grid: {
                        x: {
                            show: false
                        },
                        y: {
                            show: true
                        }
                    },
                    axis: {
                        x: {
                            type: 'category',
                            show: true,
                            tick: {
                                rotate: 75,
                                multiline: false
                            },
                            }
                    },
                    color: {
                        pattern: [ '#66A4E0', "#FF360C" ]
                    }
                });

                anomaly_chart = c3.generate({
                    bindto: '#anomaly-chart',
                    data: {
                        x: x_axis,
                        columns: [
                            column_x,
                            column_as,
                        ],
                        type: 'scatter'
                    },
                    grid: {
                        x: {
                            show: false
                        },
                        y: {
                            show: true
                        }
                    },
                    axis: {
                        x: {
                            type: 'category',
                            show: true,
                            tick: {
                                rotate: 75,
                                multiline: false
                            },
                            }
                    },
                    color: {
                        pattern: [ '#FF360C' ]
                    },
                    subchart: {
                        show: true,
                        onbrush: function (d) {
                            dimension_chart.zoom(d);
                            anomaly_chart.zoom(d);
                        },
                    }
                });

                $(".anomalyChatsControls").fadeIn();

            },
            dataType: "text",
            contentType: "application/json; charset=utf-8",
        });

    });
}
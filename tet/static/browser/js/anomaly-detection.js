$(document).ready(function() {

    $('#scoreTolerance').bootstrapSlider({
        formatter: function(value) {
            return 'Current value: ' + value;
        }
    });

});

function detectAnomaly(){

    var source_data;
    var api_url = $( "#api-link" ).val();
    var field_name = $( "#field-name" ).val();

    // $("#anomaly-output").html("<b>Loading...</b>")

    $(".anomalyDetectionResults").show();

    var response = $.getJSON(api_url, function(data) {
        data["x"] = "_id";
        data["y"] = field_name;
        json = JSON.stringify(data);

        var url = "http://vmrtpa05.deri.ie:8002/detectAnomalies/lof";
        var dataType ="aplication/json";

        var x_axis = data["x"]
        var y_axis = data["y"]
        var score_tolerance = 0.2

        source_data = data;

        $.ajax({
            type: "POST",
            url: url,
            data: json,
            success: function(data){
                 json = JSON.parse(data);
                 if (json["result"].length == 0){
                    $("#anomaly-output").html("<div class='alert alert-success top20'>No anomaly detected</div>");
                    return
                 }

                 var table = "<tr><th>" + field_name + "</th>";
                 table += "<th> Score </td></tr>";

                 for( anomaly  in json["result"]){
                    if (json["result"][anomaly][0] > 1.0){
                        table += "<tr><td>" + json["result"][anomaly][2] + "</td><td>" + json["result"][anomaly][0] + "</td></tr>";
                    }
                 }

                 table = "<table class='table table-hover'>" + table + "</table>";
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


                var dimension_chart = c3.generate({
                    bindto: '#dimension-chart',
                    point: {
                        r: function(d) {

                            if (d.id == "Anomaly"){
                                //console.log(d, 5 + ( column_as[d.index] * 5 ), 5 + ( column_as[d.index] * 2), column_as[d.index])
                                return 3 * column_as[d.index - 1];
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
                            // column_as,
                        ],
                        // hide: ['Anomaly Score'],
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

                var anomaly_chart = c3.generate({
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


            },
            dataType: "text",
            contentType: "application/json; charset=utf-8",
        });

    });
}
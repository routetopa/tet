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

    $("#anomaly-output").html("<b>Loading...</b>")
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
                    $("#anomaly-output").html("<div class='alert alert-success'>No anomaly detected</div>");
                    return
                 }
                 var table = "<tr><th>" + field_name + "</th>";
                 table += "<th> Score </td></tr>";

                 for( anomaly  in json["result"]){
                    table += "<tr><td>" + json["result"][anomaly][2] + "</td><td>" + json["result"][anomaly][0] + "</td></tr>";
                 }

                 table = "<table class='table table-hover'>" + table + "</table>";
                 table = "<div class='alert alert-error'>The following values are detected as potential anomalies</div>" + table;

                 $("#anomaly-output").html(table);

                // Pares the data for the chart
                var column_x = []
                var column_y = []
                var column_a = []

                //json["result"][i][j] :: j
                // 0 - score
                // 1 - x
                // 2 - y

                // Parse X + Y + make Anomalies null
                for(i=0; i < source_data.result.records.length; i++)
                {
                    column_x[i] = source_data.result.records[i][x_axis];
                    column_y[i] = source_data.result.records[i][y_axis];
                    if ( json["result"][i][0] > 1 + score_tolerance ){
                        column_a[i] = json["result"][i][2];
                    } else {
                        column_a[i] = null;
                    }
                }


                column_x.unshift(x_axis)
                column_y.unshift(y_axis)
                column_a.unshift("Anomaly")


                // Parse Y

                // Parse Anomalies


                var anomaly_chart = c3.generate({
                    bindto: '#anomaly-chart',
                    point: {
                        r: function(d) {
                            console.log(d)
                            if (d.id == "Anomaly"){
                                return 5; // d.value * 5;
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
                            // [ 'Anomaly' , null ,2, 1]

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
                        pattern: [ '#5FE00B', "#d80026" ]
                    }
                });


            },
            dataType: "text",
            contentType: "application/json; charset=utf-8",
        });

    });
}
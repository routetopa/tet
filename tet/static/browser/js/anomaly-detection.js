var anomaly_chart;
var dimension_chart;
var source_data;
var data_source_dimensions = []

var number_of_anomalies;
var number_of_local_anomalies;
var number_of_global_anomalies;
var highest_anomaly_score;

var x_axis
var y_axis
var score_tolerance = 0.5

var amountOfRecords
var neighboursAmount

var column_as = []

var json

$(document).ready(function() {

    $('#scoreTolerance').bootstrapSlider({
        formatter: function(value) {

            if (value == 5){
                value = "5+";
            }

            return 'Current value: ' + value;
        },
    });

    $("#scoreTolerance").on("slideStop", function(slideEvt) {

        score_tolerance = slideEvt.value

        updateChartTolerance(score_tolerance)
        updateTableTolerance(score_tolerance)
        updateAnomalyMetrics(score_tolerance)

    });

    $( "#field-name" ).change(function() {
        y_axis = $(this).val();
        updateChartDimension( $(this).val() )
        return false
    });

});







$(document).ready(function() {
    //var neighboursCount=document.getElementById("neighboursCount")

    var tmp = $('#neighboursCount').bootstrapSlider({

                    min:1,
                    max:20,
                    value:10,
                    formatter: function(value)
                    {
                        //getMaxNeighbours()
                        return "Current value: " + value;
                    }

            });
            getMaxNeighbours()

           function getMaxNeighbours()
           {
           if (typeof amountOfRecords !=='undefined')
            {
                //console.log(amountOfRecords)
                var newNeighboursMaxValue=amountOfRecords;
                if (newNeighboursMaxValue>=50)
                {
                    newNeighboursMaxValue=50
                    //console.log('test')
                    tmp.bootstrapSlider('setAttribute', 'max', newNeighboursMaxValue);
                }
                else
                {
                    //console.log('test<50')
                    tmp.bootstrapSlider('setAttribute', 'max', newNeighboursMaxValue);
                }
            }
            else
            {
                setTimeout(getMaxNeighbours,100)
            }
            }
     $("#neighboursCount").on("slideStop", function(slideEvt) {

        neighboursAmount = slideEvt.value


    });
    });





function updateAnomalyMetrics(tolerance = 0.5){

    var anomalies = []

    number_of_anomalies = 0;
    number_of_local_anomalies = 0;
    number_of_global_anomalies = 0;
    highest_anomaly_score = 0;

    // Adjust anomalies table
    for(i=0; i < source_data.result.records.length; i++)
    {

        if ( json[i][2] > 1 + tolerance ){

            number_of_anomalies++

            anomalies.push(json[i][2])

            if (json[i][3] == 'local'){
                number_of_local_anomalies++
            }

            if (json[i][3] == 'global'){
                number_of_global_anomalies++
            }

        }
    }

    if (number_of_anomalies > 0){
        highest_anomaly_score = Math.max.apply(Math, anomalies).toFixed(3);
    } else {
        highest_anomaly_score = "-";
    }

    $('#noOfAnomalies').html(number_of_anomalies);
    $('#noOfGlobalAnomalies').html(number_of_global_anomalies);
    $('#noOfLocalAnomalies').html(number_of_local_anomalies);
    $('#highestAnomalyScore').html(highest_anomaly_score);

}

function updateChartTolerance(tolerance = 0.5){

    // updating anomaly chart
    var column_a = []

    // Adjust anomalies table
    for(i=0; i < source_data.result.records.length; i++)
    {

        if ( json[i][2] > 1 + tolerance ){
            // column_a[i] = json["result"][i][2];
            column_a[i] = source_data.result.records[i][y_axis];
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

    return false
}

function updateChartType(type = 'scatter' ){
    // TODO enum values
    dimension_chart.transform(type, y_axis);
}

function updateTableTolerance(tolerance = 0.5){

    // updating anomaly table
    $('.table-anomalies tr.anomaly').hide();

    $(".table-anomalies tr.anomaly").each(function () {

        if ( $(this).attr("anomaly-score") >= tolerance + 1 ){
            $(this).show();
        }

    });

    return false
}

function updateChartDimension(field_name){
    if ( data_source_dimensions.indexOf(field_name) >= 0 ){

        var column_x  = []
        var column_y  = []
        var column_a  = []

        var current_y = y_axis;

        y_axis = field_name;

        for (i=0; i < source_data.result.records.length; i++){

            column_y[i] = source_data.result.records[i][y_axis];
            column_x[i] = source_data.result.records[i][x_axis];

            if ( json[i][2] > 1 + score_tolerance ){
                column_a[i] = column_y[i];
            } else {
                column_a[i] = null;
            }

        }

        column_x.unshift(x_axis)
        column_y.unshift(y_axis)
        column_a.unshift("Anomaly")

        // TODO replace with load()
        dimension_chart = dimension_chart.destroy();

        dimension_chart = c3.generate({
            bindto: '#dimension-chart',
            point: {
                r: function(d) {

                    if (d.id == "Anomaly"){
                        return 3 * column_as[d.index + 1];
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
                    show: false,
                },
                y: {
                    show: true,
                }
            },
            axis: {
                x: {
                    type: 'category',
                    show: true,
                    tick: {
                        rotate: 75,
                        multiline: false,
                        culling: {
                            max: 40 // the number of tick texts will be adjusted to less than this value
                        }
                    },
                },
                y: {
                    inner: true
                }
            },
            color: {
                pattern: [ '#66A4E0', "#FF360C" ]
            }
        });
    }
}


function detectAnomaly(){

    var api_url = $( "#api-link" ).val();
    var field_name = $( "#field-name" ).val();

    $(".anomalyDetectionResults").fadeIn();
    $("#detectAnomaly").fadeOut();

    var response = $.getJSON(api_url, function(data) {
        data["x"] = "_id";
        data["y"] = field_name;
        data["resource_url"] = api_url;
        data["neighbours"]=neighboursAmount;
        data["analysisFeatures"] = [];
        amountOfRecords=data["result"]["total"]-1
        //getMaxNeighbours()
        json = JSON.stringify(data);

        // TODO dynamic links
        //var url = "http://10.2.17.4:8888/detectAnomalies/lof";
        var url = "http://vmrtpa05.deri.ie:8003/detectAnomalies/lof";
        var dataType ="aplication/json";

        x_axis = data["x"]
        y_axis = data["y"]

        source_data = data;

        $.ajax({
            type: "POST",
            url: url,
            data: json,
            success: function(data){

                json = JSON.parse(data);

                if (json.length == 0) {

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

                for (index in json){
                    //console.log(index,json[index])
                    if (json[index][2] > 1.0){


                        table += "<tr class='anomaly' anomaly-score='" + json[index][2] + "'>";

                        for (dimension in data_source_dimensions) {
                            table += "<td>" + source_data.result.records[index][data_source_dimensions[dimension]] + "</td>"
                        }

                        table += "<td>" + json[index][2] + "</td>"
                        table += "</tr>"

                    }
                }

                table = "<table class='col-12 table table-hover -table-striped table-anomalies'>" + table + "</table>";
                table = "<div class='alert alert-error top20'>The following values are detected as potential anomalies</div>" + table;

                $("#anomaly-output").html(table);

                updateTableTolerance(score_tolerance)
                updateAnomalyMetrics(score_tolerance)

                // Pares the data for the chart
                var column_x    = []
                var column_y    = []
                var column_a    = []
                column_as       = []

                //json["result"][i][j] :: j
                // 0 - _id
                // 1 - FirstNumericColumn
                // 2 - Score
                // 3 - flag (type) // TODO check updated API

                // Parse X + Y + make Anomalies null
                for(i=0; i < source_data.result.records.length; i++)
                {
                    column_x[i] = source_data.result.records[i][x_axis];
                    column_y[i] = source_data.result.records[i][y_axis];
                    column_as[i] = json[i][2];
                    console.log()
                    if ( json[i][2] > 1 + score_tolerance ){
                        column_a[i] = json[i][1];
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
                            show: false,
                        },
                        y: {
                            show: true,
                        }
                    },
                    axis: {
                        x: {
                            type: 'category',
                            show: true,
                            tick: {
                                rotate: 75,
                                multiline: false,
                                culling: {
                                    max: 40 // the number of tick texts will be adjusted to less than this value
                                }
                            },
                        },
                        y: {
                            inner: true
                        }
                    },
                    color: {
                        pattern: [ '#66A4E0', "#FF360C" ]
                    }
                });

                anomaly_chart = c3.generate({
                    bindto: '#anomaly-chart',
                    grid: {
                        x: {
                            show: false,
                        },
                        y: {
                            show: true,
                        }
                    },
                    data: {
                        x: x_axis,
                        columns: [
                            column_x,
                            column_as
                        ],
                        //type: 'scatter'
                    },
                    axis: {
                        x: {
                            type: 'category',
                            tick: {
                                rotate: 75,
                                multiline: false,
                                culling: {
                                    max: 40 // the number of tick texts will be adjusted to less than this value
                                }
                            },
                        },
                        y: {
                            inner: true
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
                $("#recalculateAnomaly").fadeIn();

            },
            dataType: "text",
            contentType: "application/json; charset=utf-8",
        });

    });
}

function recalculateAnomaly() {

    $('.anomalyConfigurationAlert').hide();

    // '_id' send by default
    if ( $('input.anomalyDimensionCheckbox:checked').length > 1 ){

        var api_url = $( "#api-link" ).val();
        var field_name = $( "#field-name" ).val();

        var analysisFeatures = []

        dimension_chart.destroy()
        anomaly_chart.destroy()

        // charts
        $('#dimension-chart').html('<i class="fa fa-spinner fa-spin" style="font-size:24px"></i>');
        $('#anomaly-chart').html('<i class="fa fa-spinner fa-spin" style="font-size:24px"></i>');
        $("#anomaly-output").html('<i class="fa fa-spinner fa-spin" style="font-size:24px"></i>');

        // scores
        $("#noOfAnomalies").html('<i class="fa fa-spinner fa-spin"></i>');
        $("#noOfGlobalAnomalies").html('<i class="fa fa-spinner fa-spin"></i>');
        $("#noOfLocalAnomalies").html('<i class="fa fa-spinner fa-spin"></i>');
        $("#highestAnomalyScore").html('<i class="fa fa-spinner fa-spin"></i>');

        $('input.anomalyDimensionCheckbox:checked').each( function(){
            analysisFeatures.push( $(this).val() )
        })


        // TODO loading icon
        var response = $.getJSON(api_url, function(data) {
            data["x"] = "_id";
            data["y"] = field_name;
            data["resource_url"] = api_url;
            data["neighbours"] = neighboursAmount;
            data["analysisFeatures"] = analysisFeatures;

            json = JSON.stringify(data);

            // TODO dynamic links
            //var url = "http://10.2.17.4:8888/detectAnomalies/lof";
            var url = "http://vmrtpa05.deri.ie:8003/detectAnomalies/lof";
            var dataType ="aplication/json";

            x_axis = data["x"]
            y_axis = data["y"]

            source_data = data;

            $.ajax({
                type: "POST",
                url: url,
                data: json,
                success: function(data){

                    json = JSON.parse(data);

                    if (json.length == 0) {

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

                    for (index in json){
                        if (json[index][2] > 1.0){


                            table += "<tr class='anomaly' anomaly-score='" + json[index][2] + "'>";

                            for (dimension in data_source_dimensions) {
                                table += "<td>" + source_data.result.records[index][data_source_dimensions[dimension]] + "</td>"
                            }

                            table += "<td>" + json[index][2] + "</td>"
                            table += "</tr>"

                        }
                    }

                    table = "<table class='span12 table table-hover -table-striped table-anomalies'>" + table + "</table>";
                    table = "<div class='alert alert-error top20'>The following values are detected as potential anomalies</div>" + table;

                    $("#anomaly-output").html(table);

                    updateTableTolerance(score_tolerance)
                    updateAnomalyMetrics(score_tolerance)

                    // Pares the data for the chart
                    var column_x    = []
                    var column_y    = []
                    var column_a    = []
                    column_as       = []

                    //json["result"][i][j] :: j
                    // 0 - _id
                    // 1 - FirstNumericColumn
                    // 2 - Score
                    // 3 - flag (type) // TODO check updated API TODO check updated API

                    // Parse X + Y + make Anomalies null
                    for(i=0; i < source_data.result.records.length; i++)
                    {
                        column_x[i] = source_data.result.records[i][x_axis];
                        column_y[i] = source_data.result.records[i][y_axis];
                        column_as[i] = json[i][2];

                        if ( json[i][2] > 1 + score_tolerance ){
                            column_a[i] = json[i][1];
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
                                show: false,
                            },
                            y: {
                                show: true,
                            }
                        },
                        axis: {
                            x: {
                                type: 'category',
                                show: true,
                                tick: {
                                    rotate: 75,
                                    multiline: false,
                                    culling: {
                                        max: 40 // the number of tick texts will be adjusted to less than this value
                                    }
                                },
                            },
                            y: {
                                inner: true
                            }
                        },
                        color: {
                            pattern: [ '#66A4E0', "#FF360C" ]
                        }
                    });

                    anomaly_chart = c3.generate({
                        bindto: '#anomaly-chart',
                        grid: {
                            x: {
                                show: false,
                            },
                            y: {
                                show: true,
                            }
                        },
                        data: {
                            x: x_axis,
                            columns: [
                                column_x,
                                column_as
                            ],
                            //type: 'scatter'
                        },
                        axis: {
                            x: {
                                type: 'category',
                                tick: {
                                    rotate: 75,
                                    multiline: false,
                                    culling: {
                                        max: 40 // the number of tick texts will be adjusted to less than this value
                                    }
                                },
                            },
                            y: {
                                inner: true
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

    } else {
        $('.anomalyConfigurationAlert').fadeIn();
    }

    return false;

}

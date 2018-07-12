$(document).ready(function() {

var RawData=$.get($("#plotlycharts").attr("data-url"), function (data,status)
    {
        console.log("ready");
        var mainChartInnerWidth = $('#main-chart').innerWidth();
        var mainChartInnerHeight = $('#main-chart').innerHeight();
        for(i=0;i<data.length; i++) //iteration through all columns
        {
            console.log(data[i]);
            var layout = {
                title: "Values in field " + data[i][0],
                xaxis:{
                    tickangle: -45},
                yaxis:{
                    title: "Number of occurences"
                },
                width: mainChartInnerWidth,
                height: mainChartInnerHeight
            }

            var dataPlotly=[
                {
                    x: data[i][1],   //names of columns
                    y: data[i][2], //column values
                    type: 'bar'
                 }
            ];
            console.log(dataPlotly);
            Plotly.newPlot("a"+(i+1), dataPlotly, layout);
        }

    });
    $('#main-chart').on('slide.bs.carousel',function(e){

        var carouselIndex = $(e.relatedTarget).index();
        var graphdiv=$('#a'+carouselIndex)
        var mainChartInnerWidth = $('#main-chart').innerWidth();
        var mainChartInnerHeight = $('#main-chart').innerHeight();
        var layoutupdate=
            {
                autosize: true,
                width: mainChartInnerWidth,
                height: mainChartInnerHeight
            };
        Plotly.relayout("a"+carouselIndex, layoutupdate);

    });





});

$(document).ready(function() {

    var RawData=$.get($("#plotlycharts").attr("data-url"), function (data,status)
    {
        var InnerWidth = $('#wrap > .container ').innerWidth();
        for(i=0;i<data.length; i++) //iteration through all columns
        {
            var layout = {
                title: "Values in field " + data[i][0],
                xaxis:{
                    tickangle: -45},
                yaxis:{
                    title: "Number of occurences"
                },
                width: InnerWidth,
            }
            var dataPlotly=[
                {
                    x: data[i][1],   //names of columns
                    y: data[i][2], //column values
                    type: 'bar'
                 }
            ];
            var elementExists=$("#a"+(i+1));
            if(elementExists.length > 0){
                Plotly.newPlot("a"+(i+1), dataPlotly, layout);
            }
        }

    });
    $('#main-chart').on('slide.bs.carousel',function(e){
        var carouselIndex = $(e.relatedTarget).index();
        var InnerWidth = $('#wrap > .container ').innerWidth();
        var elementExists=$("#a"+carouselIndex);
        var layoutupdate=
            {
                autosize: true,
                width: InnerWidth
            };
        if(elementExists.length > 0){
            Plotly.relayout("a"+carouselIndex, layoutupdate);
        }
    });
});

var SEARCH_MODE = "AND"

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
    if($( "#ds-rc-slider" ).size()){ 
        var ds_id = $( "#ds-id" ).val();
        var ds_url = $( "#ds-url" ).val();
        var api_url = $( "#ds-api-url" ).val();
        function fetch_data(value){
             $("#ds-rc-output").html("<em>Loading...</em>")
              url =  api_url +"/get/" + ds_id + "/" + value;
              $.get(url, function(data){
                 html = ""
                 for (d in data["result"]){
                    html += "<li><a href='" + ds_url + data["result"][d]["id"] +"'>" + data["result"][d]["title"] + "</a></li>";
                 }
                 $("#ds-rc-output").html("<ul class='dataset-files'>"+ html +"</ul>")
             });
        }
        var ds_slider = $( "#ds-rc-slider" ).slider({
                   max: 10,
                   value: 1,
                   min:1,
                   slide: function( event, ui ) {
                     fetch_data(ui.value)
                   }   
        });
        fetch_data(1);
    }

    if ( $('.js-zeroclipboard-btn').size() ){
        var client = new ZeroClipboard( $(".js-zeroclipboard-btn") );
    }

    $('.lang_dropdown_toggle').on('click', function (event) {
        // Avoid following the href location when clicking
        event.preventDefault();

        // Avoid having the menu to close when clicking
        event.stopPropagation();

        $('.language_popup').toggle();

    });

    // Social sharing
    $('#social-sharing').jsSocials({
        showLabel: false,
        showCount: "inside",
        shareIn: "popup",
        shares: ["email", "twitter", "facebook", "googleplus"] // TODO SPOD share
    });

    // auto-adjust chart area
    $('#main-chart').on('slid', function() {
        $(window).trigger('resize');
        return false
    });

});

$(function () {
    //type ahead
    $('.main-search').typeahead({
        source: function (query, process) {
            return $.get('/api/typeahead', { query: query }, function (data) {
                return process(data.options);
            });
        },
        item: '<li class="span5"><a href="#"></a></li>'
    });
    
    //SQL editor
    if($("#query-editor").length > 0){
        var editor = ace.edit("query-editor");
        editor.getSession().setMode("ace/mode/sql");
        $("#exe-query").click(function(e){
            sql_api = $("#query-api").val() + "?sql=" + encodeURIComponent(editor.getValue());
            $("#query-output").html("");
            var jqxhr = $.get(sql_api, function (data){
                var tr = "";
                var table = "";
                if (data["success"] == true){
                   for(field in data["result"]["fields"]){
                    if (data["result"]["fields"][field]["id"] .startsWith("_")) continue;
                     tr += "<th>" + data["result"]["fields"][field]["id"] + "</th>";
                   }
                }
                table += "<tr>" + tr + "</tr>";
                tr=""
                for(record  in data["result"]["records"]){
                   for(field in data["result"]["fields"]){
                    var field_id = data["result"]["fields"][field]["id"];
                    if (field_id.startsWith("_")) continue;
                    tr += "<td>" + data["result"]["records"][record][field_id] + "</td>"
                   }
                   table += "<tr>" + tr + "</tr>";
                   tr=""
                }
                table = "<table class='table table-hover' width='100%'>"  + table + "</table>";
                $("#query-output").html(table);
            }).fail(function() {
                $("#query-output").html('<div class="alert alert-danger"><strong>Error</strong> Failed to excute the query </div>');
            });;
        });
    }

    // Results filters
    $('.expand-btn').click(function () {
        $(this).parent().parent().children('.filter-hidden').fadeIn('slow')
        $(this).hide()
    });

    // Results order
    // TODO server side processing
    $('#sort-btn-relevance').click(function () {

        // handle buttons icons and arrows (class)
        $('.active-filter').removeClass('active-filter');
        $(this).parent().addClass('active-filter');

        if ($(this).children('.fa').hasClass('fa-sort-amount-asc')) {
            $(this).children('.fa').removeClass('fa-sort-amount-asc').addClass('fa-sort-amount-desc')

            $('.dataset-list').find('li.dataset-item').sort(function(a, b) {
                return +a.getAttribute('search-relevance') - +b.getAttribute('search-relevance');
            }).appendTo($('.dataset-list'));

        } else {
            $(this).children('.fa').removeClass('fa-sort-amount-desc').addClass('fa-sort-amount-asc')

            $('.dataset-list').find('li.dataset-item').sort(function(a, b) {
                return +b.getAttribute('search-relevance') - +a.getAttribute('search-relevance');
            }).appendTo($('.dataset-list'));
        }

    });

    $('#sort-btn-name').click(function () {

        // handle buttons icons and arrows (class)
        $('.active-filter').removeClass('active-filter');
        $(this).parent().addClass('active-filter');

        if ($(this).children('.fa').hasClass('fa-sort-amount-asc')) {
            $(this).children('.fa').removeClass('fa-sort-amount-asc').addClass('fa-sort-amount-desc')

            $('.dataset-list').find('li.dataset-item').sort(function(a, b) {
                textA = a.getAttribute('search-name')
                textB = b.getAttribute('search-name')
                return (textB < textA) ? -1 : (textB > textA) ? 1 : 0;
            }).appendTo($('.dataset-list'));

        } else {
            $(this).children('.fa').removeClass('fa-sort-amount-desc').addClass('fa-sort-amount-asc')

            $('.dataset-list').find('li.dataset-item').sort(function(a, b) {
                textA = a.getAttribute('search-name')
                textB = b.getAttribute('search-name')
                return (textA < textB) ? -1 : (textA > textB) ? 1 : 0;
            }).appendTo($('.dataset-list'));

        }

    });

    $('#sort-btn-date').click(function () {

        // handle buttons icons and arrows (class)
        $('.active-filter').removeClass('active-filter');
        $(this).parent().addClass('active-filter');

        if ($(this).children('.fa').hasClass('fa-sort-amount-asc')) {
            $(this).children('.fa').removeClass('fa-sort-amount-asc').addClass('fa-sort-amount-desc')

            $('.dataset-list').find('li.dataset-item').sort(function(a, b) {
                return +b.getAttribute('search-date') - +a.getAttribute('search-date');
            }).appendTo($('.dataset-list'));

        } else {
            $(this).children('.fa').removeClass('fa-sort-amount-desc').addClass('fa-sort-amount-asc')

            $('.dataset-list').find('li.dataset-item').sort(function(a, b) {
                return +a.getAttribute('search-date') - +b.getAttribute('search-date');
            }).appendTo($('.dataset-list'));

        }

    });


    // Results filtering
    $('input:checkbox').click(function () {

        if ( $("#results-filter input:checked").length == 0){
            $("ul.dataset-list li.dataset-item").show();
            // update counter
            $("#results_count").html($("ul.dataset-list li.dataset-item:visible").length);
            return true
        }

        // Hide all
        $("ul.dataset-list li.dataset-item").hide();

        // TODO agree on default drill down algorithm
        if ( SEARCH_MODE == "OR"){
            $("#results-filter input:checked").each(function () {

                var filterKey = $(this).attr("filter-key");
                var filterValue = $(this).attr("filter-value");

                $("ul.dataset-list li.dataset-item[search-" + filterKey + "*='" + filterValue + "']").show()

            });
        } else {

            results_selector = "ul.dataset-list li.dataset-item"

//            $("#results-filter input:checked").each(function () {
//
//                var filterKey = $(this).attr("filter-key");
//                var filterValue = $(this).attr("filter-value");
//
//                results_selector += "[search-" + filterKey + "*='" + filterValue + "']"
//
//            });

            var results_filtered = $("ul.dataset-list li.dataset-item");

            $("#results-filter .panel-group").each(function () {

                var results_selector_filter = ''

                $("input:checked", this).each( function() {

                    var filterKey = $(this).attr("filter-key");
                    var filterValue = $(this).attr("filter-value");

                    if ( results_selector_filter ){
                        results_selector_filter += ", " + "[search-" + filterKey + "*='" + filterValue + "']"
                    } else {
                        results_selector_filter = "[search-" + filterKey + "*='" + filterValue + "']"
                    }

                })

                if (results_selector_filter){
                    results_filtered = results_filtered.filter( results_selector_filter )
                }

            });

            results_filtered.show()
        }

        // update counter
        $("#results_count").html($("ul.dataset-list li.dataset-item:visible").length);

        return true

    });


});

(function ($) {

    $.fn.randomize = function (childElem) {
        return this.each(function () {
            var $this = $(this);
            var elems = $this.children(childElem);

            elems.sort(function () {
                return (Math.round(Math.random()) - 0.5);
            });

            $this.remove(childElem);

            for (var i = 0; i < elems.length; i++)
                $this.append(elems[i]);
        });
    }

})(jQuery)

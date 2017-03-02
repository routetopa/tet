var SEARCH_MODE = "AND"
var csrftoken = getCookie('csrftoken');
var CURRENT_LANGUAGE = 'en'

$(document).ready(function(){

    CURRENT_LANGUAGE = $('#currentLanguage').val();

    $('[data-toggle="tooltip"]').tooltip(
        {html: true}
    );
    $('[data-toggle="tab"]').tab();

    if ( $('#ds-merged').size() ){
        var ds_merged = $( "#ds-merged" ).val();
        var response = $.getJSON(ds_merged, function(data) {
                if ($("#output").size() > 0){
                    var derivers = $.pivotUtilities.derivers;
                    var renderers = $.extend(
                                    $.pivotUtilities.renderers,
                                    $.pivotUtilities.c3_renderers,
                                    $.pivotUtilities.d3_renderers
                                    );
                    $("#output").pivotUI(data.result.records, { renderers: renderers}, false, CURRENT_LANGUAGE);

                }else{
                    columns = []
                    for (field in data.result.fields){
                        field_name = data.result.fields[field].id;
                        if (!field_name.startsWith("_")){
                            columns.push({ "data" : field_name , "title" : field_name  })
                        }
                    }
                    $('#ds-table').DataTable( {
                        data: data.result.records,
                        columns: columns
                    });
                }
            });
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

    $("#social-sharing").jsSocials("shareOption", "googleplus", "logo", "fa fa-google-plus");

    // auto-adjust chart area
    $('#main-chart').on('slid', function() {
        $(window).trigger('resize');
        return false
    });

});

$(function () {

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
    if($("#adv-query-editor").length > 0){
        var editor = ace.edit("adv-query-editor");
        editor.getSession().setMode("ace/mode/sql");

        $('a[href=#sqlquery]').click(function (e) {
            var sql = $('#query-editor').queryBuilder('getSQL').sql;
            sql = 'SELECT  * from  ' + '"' + resource_id + '" WHERE ' +sql;
            sql = sql.replace(new RegExp("_", 'g'), '"');
            editor.setValue(sql, 1)
        });
        
        $("#adv-exe-query").click(function(e){
            sql_api = $("#query-api").val() + "?sql=" + encodeURIComponent(editor.getValue());
            $("#adv-query-output").html("");
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
                $("#adv-query-output").html(table);
            }).fail(function() {
                $("#adv-query-output").html('<div class="alert alert-danger"><strong>Error</strong> Failed to excute the query </div>');
            });;
        });
    }

    $("#trigger-create-form").submit(function(e){
        e.preventDefault(e);
    });

    //Query Builder
    if($("#query-editor").length > 0){

        url = $( "#api-link" ).val();
        
        $.get(url, function(data){
            resource_id = data.result.resource_id;
            var to_be_removed = 0;
            for (field in data.result.fields){
                if (data.result.fields[field]["id"] == '_id'){
                    to_be_removed = field
                    continue;
                }
                data.result.fields[field]["label"] = data.result.fields[field]["id"];
                data.result.fields[field]["id"] = "_" + data.result.fields[field]["id"] + "_";
                if (data.result.fields[field]["type"] == "int4"){
                    data.result.fields[field]["type"] = "integer"
                }
                if (data.result.fields[field]["type"] == "text"){
                    data.result.fields[field]["type"] = "string"
                }
                if (data.result.fields[field]["type"] == "numeric"){
                    data.result.fields[field]["type"] = "double"
                }
            }
            data.result.fields.splice(to_be_removed, 1);
            $("#query-editor").queryBuilder({filters:data.result.fields});
        });

        $("#trigger").click(function(e){
             $( "#trigger-form" ).toggle( "slow", function() {});
        });

        $("#trigger-create").click(function(e){
            var sql = $('#query-editor').queryBuilder('getSQL').sql;
            sql = sql.replace(new RegExp("_", 'g'), '"');
            email = $("#trigger-email").val()
            notification = $("#trigger-text").val()
            $("#trigger-create").prop('disabled', true);
            $.ajax({
                url: '/en/create_trigger',
                type: 'POST',
                data: {
                    "sql":sql,
                    "email": email,
                    "notification" : notification,
                    'csrfmiddlewaretoken': csrftoken
                },
                dataType: 'json',
                success: function (result){
                    if (result.success){
                        $("#trigger-output").html('<div class="alert alert-success">' + result.message + '</div>');
                        $( "#trigger-form" ).toggle( 1300, function() {
                            $("#trigger-output").html('');
                        });
                    }else{
                        $("#trigger-output").html('<div class="alert alert-error">' + result.message + '</div>');
                    }
                    $("#trigger-create").prop('disabled', false);
                }
            }).fail(function() {
                $("#trigger-output").html('<div class="alert alert-error">Failed</div>');
                $("#trigger-create").prop('disabled', false);
            });
        });


        $("#download").click(function(e){
            var sql = $('#query-editor').queryBuilder('getSQL').sql;
            sql = 'SELECT  * from  ' + '"' + resource_id + '" WHERE ' +sql;
            sql = sql.replace(new RegExp("_", 'g'), '"');
            var form = $('<form></form>').attr('action', '/en/download').attr('method', 'post');
            form.append($("<input></input>").attr('type', 'hidden').attr('name', 'sql').attr('value', sql));
            form.append($("<input></input>").attr('type', 'hidden').attr('name', 'csrfmiddlewaretoken').attr('value', csrftoken));
            form.appendTo('body').submit().remove();
        });

        $("#exe-query").click(function(e){
            var sql = $('#query-editor').queryBuilder('getSQL').sql;
            sql = 'SELECT  * from  ' + '"' + resource_id + '" WHERE ' +sql;
            sql = sql.replace(new RegExp("_", 'g'), '"');
            sql_api = $("#query-api").val() + "?sql=" + encodeURIComponent(sql);
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


    // Combine Datasets
    $('#combineDatasets').click(function () {

        $(this).parent().siblings('.alert').hide();

        var selected_datasets = $("input[name='selected_datasets']:checked");

        if (selected_datasets.length > 0){

            return true

        } else {
            $(this).parent().siblings('.alert').fadeIn('slow');
        }

        return false;
    });

    // Refine / Combine tab
    $('#combineDatasetsTab').click(function () {
        $('#search-results .select_dataset').fadeIn('slow')
    });

    $('#refineDatasetsTab').click(function () {
        $('#search-results .select_dataset').hide()
    });

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

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// jquery extend function
// http://stackoverflow.com/a/23347795/536535
$.extend(
{
    redirectPost: function(location, args)
    {
        var form = $('<form></form>');
        form.attr("method", "post");
        form.attr("action", location);

        $.each( args, function( key, value ) {
            var field = $('<input></input>');

            field.attr("type", "hidden");
            field.attr("name", key);
            field.attr("value", value);

            form.append(field);
        });
        $(form).appendTo('body').submit();
    }
});
/*
function detectAnomaly(){
    var api_url = $( "#api-link" ).val();
    var field_name = $( "#field-name" ).val();
    $("#anomaly-output").html("<b>Loading...</b>")
    var response = $.getJSON(api_url, function(data) {
        data["x"] = "_id";
        data["y"] = field_name;
        json = JSON.stringify(data);
        var url = "http://vmrtpa05.deri.ie:8002/detectAnomalies/lof";
        var dataType ="aplication/json";
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
                 var table = "<tr><th>" + field_name + "</th></tr>";
                 for( amomaly  in json["result"]){
                    table += "<tr><td>" + json["result"][amomaly][2] + "</td></tr>";
                 }
                 table = "<table class='table table-hover'>" + table + "</table>";
                 table = "<div class='alert alert-error'>The following values are detected as potential anomalies</div>" + table;
                 $("#anomaly-output").html(table);
            },
            dataType: "text",
            contentType: "application/json; charset=utf-8",
        });

    });
}
*/

var SEARCH_MODE = "AND"

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();

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
});

$(function () {

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

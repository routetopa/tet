$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});

$(function () {

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
//        $("ul.dataset-list").randomize("li.dataset-item");

        $("input:checked").each(function () {

            var filter-key = $(this).attr("filter-key");
            var filter-value = $(this).attr("filter-value");


            alert("Do something for: " + filter-key + ", " + filter-value);
        });

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

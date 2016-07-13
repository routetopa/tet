$(function () {

    $('.sort-btn').click(function () {

        $('.active-filter').removeClass('active-filter');
        $(this).parent().addClass('active-filter');

        $("ul.dataset-list").randomize("li.dataset-item");

        if ($(this).children('.fa').hasClass('fa-sort-amount-asc')) {
            $(this).children('.fa').removeClass('fa-sort-amount-asc').addClass('fa-sort-amount-desc')
        } else {
            $(this).children('.fa').removeClass('fa-sort-amount-desc').addClass('fa-sort-amount-asc')
        }

    });

    $('input:checkbox').click(function () {
        $("ul.dataset-list").randomize("li.dataset-item");
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
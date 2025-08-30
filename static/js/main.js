//<!-- Scroll effect -->

$(window).on("scroll", function () {
    if ($(this).scrollTop() > 50) {
        $("#mainNavbar").addClass("navbar-scroll");
    } else {
        $("#mainNavbar").removeClass("navbar-scroll");
    }
});

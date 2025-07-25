$(document).ready(function() {
    // Initialize Owl Carousels
    $(".hero-slider").owlCarousel({
        items: 1,
        loop: true,
        autoplay: true,
        smartSpeed: 1000,
        dots: true,
        nav: true
    });

    $(".testimonial-slider").owlCarousel({
        items: 1,
        loop: true,
        autoplay: true,
        dots: true
    });

    // Initialize Lightbox
    lightbox.option({
        'resizeDuration': 200,
        'wrapAround': true
    });

    // Initialize WOW.js
    new WOW().init();

    // Smooth scroll for anchor links
    $('a[href*="#"]').on('click', function(e) {
        // Exclude elements that shouldn't smooth scroll
        if ($(this).hasClass('no-smooth-scroll') || 
            $(this).attr('data-toggle') === 'dropdown') {
            return;
        }
        
        e.preventDefault();
        var target = $(this).attr('href');
        if (target === '#') return;
        
        $('html, body').animate({
            scrollTop: $(target).offset().top
        }, 500, 'linear');
    });

    // Back to top button
    var backToTop = $('.back-to-top');
    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            backToTop.fadeIn();
        } else {
            backToTop.fadeOut();
        }
    });
    
    backToTop.click(function(e) {
        e.preventDefault();
        $('html, body').animate({scrollTop: 0}, 'slow');
    });
});




$(".testimonial-slider").owlCarousel({
    items: 3, // Display 3 items at once
    loop: true,
    autoplay: true,
    dots: true,
    nav: true,
    margin: 30, // Space between items
    responsive: {
        0: { // For mobile
            items: 1
        },
        768: { // For tablets
            items: 2
        },
        992: { // For desktops
            items: 3
        }
    }
});





// Add this script at the bottom of your template or in a separate JS file
document.addEventListener('DOMContentLoaded', function() {
    // Handle Read More clicks
    document.querySelectorAll('.read-more').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const newsId = this.getAttribute('data-news-id');
            const modal = document.getElementById(`news-modal-${newsId}`);
            modal.style.display = 'flex';
        });
    });

    // Handle close button clicks
    document.querySelectorAll('.close-modal').forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.news-modal').style.display = 'none';
        });
    });

    // Close modal when clicking outside content
    document.querySelectorAll('.news-modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    });
});
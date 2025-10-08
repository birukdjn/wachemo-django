// Core UI interactions without external plugins
document.addEventListener('DOMContentLoaded', function() {
    // Mobile nav toggle
    var navToggle = document.getElementById('navToggle');
    var navbarNav = document.getElementById('navbarNav');
    if (navToggle && navbarNav) {
        navToggle.addEventListener('click', function () {
            navbarNav.classList.toggle('hidden');
        });
    }

    // Profile dropdown toggle
    var profileBtn = document.getElementById('dropdownMenuButton');
    if (profileBtn) {
        var dropdownMenu = profileBtn.parentElement.querySelector('ul');
        profileBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            if (dropdownMenu) dropdownMenu.classList.toggle('hidden');
        });
        document.addEventListener('click', function () {
            if (dropdownMenu) dropdownMenu.classList.add('hidden');
        });
    }

    // Smooth scroll (basic)
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function (e) {
            var targetId = this.getAttribute('href');
            if (targetId && targetId.length > 1) {
                var el = document.querySelector(targetId);
                if (el) {
                    e.preventDefault();
                    el.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });

    // Back to top (optional if element exists)
    var backToTop = document.querySelector('.back-to-top');
    if (backToTop) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 300) {
                backToTop.style.display = 'block';
            } else {
                backToTop.style.display = 'none';
            }
        });
        backToTop.addEventListener('click', function (e) {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

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
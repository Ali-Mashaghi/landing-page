/*!
* Start Bootstrap - Personal v1.0.1 (https://startbootstrap.com/template-overviews/personal)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-personal/blob/master/LICENSE)
*/
document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.querySelector('.site-navbar');

    const updateNavbar = () => {
        navbar?.classList.toggle('is-scrolled', window.scrollY > 18);
    };

    updateNavbar();
    window.addEventListener('scroll', updateNavbar, { passive: true });

    const revealTargets = document.querySelectorAll(
        '.site-body section:not(.resume-hero), .site-body .project-modern-card, .site-body .glass-panel'
    );

    revealTargets.forEach((element, index) => {
        element.classList.add('reveal-on-scroll');
        element.style.transitionDelay = `${Math.min(index % 3, 2) * 80}ms`;
    });

    if (!('IntersectionObserver' in window)) {
        revealTargets.forEach((element) => element.classList.add('is-visible'));
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.12,
        rootMargin: '0px 0px -40px',
    });

    revealTargets.forEach((element) => observer.observe(element));
});
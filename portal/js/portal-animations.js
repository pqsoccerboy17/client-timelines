/**
 * Portal Animations
 * Subtle, polished animations for the EasyVista client portal.
 * - Animated number counters
 * - Scroll-triggered reveals (IntersectionObserver)
 * - Animated progress bars
 * - Staggered timeline reveals
 *
 * Respects prefers-reduced-motion automatically via CSS.
 * When reduced motion is preferred, elements appear instantly (no JS animation).
 */

(function () {
    'use strict';

    var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // ========================================
    // Animated Number Counters
    // ========================================
    // Elements with data-count-to="54" will count up from 0 on scroll into view.
    // Supports suffixes like "%" via data-count-suffix.

    function animateCounter(el) {
        var target = parseInt(el.getAttribute('data-count-to'), 10);
        var suffix = el.getAttribute('data-count-suffix') || '';
        var duration = 1200; // ms

        if (prefersReducedMotion || isNaN(target)) {
            el.textContent = target + suffix;
            return;
        }

        var start = 0;
        var startTime = null;

        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            var progress = Math.min((timestamp - startTime) / duration, 1);
            // Ease-out cubic
            var eased = 1 - Math.pow(1 - progress, 3);
            var current = Math.round(start + (target - start) * eased);
            el.textContent = current + suffix;
            if (progress < 1) {
                requestAnimationFrame(step);
            }
        }

        el.textContent = '0' + suffix;
        requestAnimationFrame(step);
    }

    // ========================================
    // Scroll-Triggered Reveals
    // ========================================
    // Elements with class "reveal" start invisible and get "revealed" when scrolled into view.
    // Stagger: elements with data-reveal-delay="100" get a transition-delay.

    function initReveals() {
        var revealElements = document.querySelectorAll('.reveal');
        if (!revealElements.length) return;

        if (prefersReducedMotion) {
            // Show everything immediately
            revealElements.forEach(function (el) {
                el.classList.add('revealed');
            });
            return;
        }

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var el = entry.target;
                    var delay = parseInt(el.getAttribute('data-reveal-delay'), 10) || 0;
                    if (delay > 0) {
                        el.style.transitionDelay = delay + 'ms';
                    }
                    el.classList.add('revealed');
                    observer.unobserve(el);
                }
            });
        }, {
            threshold: 0.15,
            rootMargin: '0px 0px -40px 0px'
        });

        revealElements.forEach(function (el) {
            observer.observe(el);
        });
    }

    // ========================================
    // Animated Progress Bars
    // ========================================
    // Elements with data-target-width="35" will animate from 0% to 35% width on scroll.

    function initProgressBars() {
        var bars = document.querySelectorAll('[data-target-width]');
        if (!bars.length) return;

        if (prefersReducedMotion) {
            bars.forEach(function (bar) {
                bar.style.width = bar.getAttribute('data-target-width') + '%';
            });
            return;
        }

        // Start at 0
        bars.forEach(function (bar) {
            bar.style.width = '0%';
        });

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var bar = entry.target;
                    var targetWidth = bar.getAttribute('data-target-width');
                    // Small delay for visual effect
                    setTimeout(function () {
                        bar.style.width = targetWidth + '%';
                    }, 200);
                    observer.unobserve(bar);
                }
            });
        }, {
            threshold: 0.3
        });

        bars.forEach(function (bar) {
            observer.observe(bar);
        });
    }

    // ========================================
    // Counter Elements (scroll-triggered)
    // ========================================

    function initCounters() {
        var counters = document.querySelectorAll('[data-count-to]');
        if (!counters.length) return;

        if (prefersReducedMotion) {
            counters.forEach(function (el) {
                var target = el.getAttribute('data-count-to');
                var suffix = el.getAttribute('data-count-suffix') || '';
                el.textContent = target + suffix;
            });
            return;
        }

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.5
        });

        counters.forEach(function (el) {
            observer.observe(el);
        });
    }

    // ========================================
    // SVG Progress Ring Animation
    // ========================================

    function getProgressColor(percent) {
        if (percent <= 25) return 'var(--color-danger)';
        if (percent <= 50) return 'var(--color-warning)';
        if (percent <= 75) return 'var(--color-ev-teal)';
        return 'var(--color-success)';
    }

    function initProgressRings() {
        var rings = document.querySelectorAll('.progress-ring__circle');
        if (!rings.length) return;

        rings.forEach(function (circle) {
            var radius = circle.r.baseVal.value;
            var circumference = 2 * Math.PI * radius;
            var percent = parseFloat(circle.getAttribute('data-percent')) || 0;

            // Apply progress-based color (skip Days ring — it's a countdown, not progress)
            if (circle.id !== 'days-ring' && percent > 0) {
                var color = getProgressColor(percent);
                circle.setAttribute('stroke', color);
                var wrapper = circle.closest('.hero-stat__ring-wrapper');
                if (wrapper) {
                    var valueEl = wrapper.querySelector('.hero-stat__value');
                    if (valueEl) valueEl.style.color = color;
                }
            }

            circle.style.strokeDasharray = circumference;

            if (prefersReducedMotion) {
                circle.style.strokeDashoffset = circumference - (percent / 100) * circumference;
                return;
            }

            // Start fully hidden
            circle.style.strokeDashoffset = circumference;

            var observer = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        setTimeout(function () {
                            circle.style.strokeDashoffset = circumference - (percent / 100) * circumference;
                        }, 300);
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });

            observer.observe(circle);
        });
    }

    // ========================================
    // Timeline Progress Line
    // ========================================

    function initTimelineProgress() {
        var progressLine = document.querySelector('.milestone-progress-fill');
        if (!progressLine) return;

        var targetHeight = progressLine.getAttribute('data-progress-height');
        if (!targetHeight) return;

        if (prefersReducedMotion) {
            progressLine.style.height = targetHeight;
            return;
        }

        progressLine.style.height = '0%';

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    setTimeout(function () {
                        progressLine.style.height = targetHeight;
                    }, 400);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        observer.observe(progressLine.parentElement);
    }

    // ========================================
    // Initialize Everything on DOMContentLoaded
    // ========================================

    function init() {
        initReveals();
        initCounters();
        initProgressBars();
        initProgressRings();
        initTimelineProgress();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

(() => {
    "use strict";

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    document.querySelectorAll(".kp-dashboard-media-fallback").forEach((image) => {
        const source = reduceMotion
            ? image.dataset.posterSrc
            : image.dataset.animatedSrc;

        if (source) {
            image.src = source;
        }

        image.addEventListener("error", () => {
            const fallback = image.dataset.fallback;

            if (!fallback || image.dataset.fallbackUsed) {
                return;
            }

            image.dataset.fallbackUsed = "true";
            image.src = fallback;
        });
    });

    const root = document.getElementById("dashboardSpotlight");

    if (!root) {
        return;
    }

    const slides = [...root.querySelectorAll("[data-dashboard-slide]")];
    const prev = document.getElementById("dashboardPrev");
    const next = document.getElementById("dashboardNext");
    const current = document.getElementById("dashboardCurrent");
    const pauseButton = document.getElementById("dashboardPause");
    const interval = 6500;
    let index = 0;
    let timer = null;
    let userPaused = false;

    const pause = () => {
        window.clearInterval(timer);
        timer = null;
    };

    const start = () => {
        pause();

        if (reduceMotion || userPaused || slides.length < 2 || document.hidden) {
            return;
        }

        timer = window.setInterval(() => {
            show(index + 1, false);
        }, interval);
    };

    const show = (requested, restart = true) => {
        if (!slides.length) {
            return;
        }

        index = (requested + slides.length) % slides.length;

        slides.forEach((slide, slideIndex) => {
            const active = slideIndex === index;
            slide.classList.toggle("active", active);
            slide.setAttribute("aria-hidden", active ? "false" : "true");
            slide.tabIndex = active ? 0 : -1;
        });

        if (current) {
            current.textContent = String(index + 1);
        }

        if (restart) {
            start();
        }
    };

    const updatePauseButton = () => {
        if (!pauseButton) {
            return;
        }

        if (reduceMotion) {
            pauseButton.hidden = true;
            return;
        }

        pauseButton.hidden = false;

        pauseButton.setAttribute("aria-pressed", String(userPaused));

        pauseButton.setAttribute(
            "aria-label",
            userPaused
                ? "Возобновить автоматическую смену котиков"
                : "Остановить автоматическую смену котиков"
        );

        const icon = pauseButton.querySelector("i");

        const label = pauseButton.querySelector("span");

        if (icon) {
            icon.className = userPaused ? "fas fa-play" : "fas fa-pause";
        }

        if (label) {
            label.textContent = userPaused ? "Продолжить" : "Пауза";
        }
    };

    prev?.addEventListener("click", () => show(index - 1));

    next?.addEventListener("click", () => show(index + 1));

    pauseButton?.addEventListener("click", () => {
        userPaused = !userPaused;

        updatePauseButton();

        if (userPaused) {
            pause();
        } else {
            start();
        }
    });
    root.addEventListener("mouseenter", pause);
    root.addEventListener("mouseleave", () => {
        if (!userPaused) {
            start();
        }
    });
    root.addEventListener("focusin", pause);
    root.addEventListener("focusout", () => {
        if (!userPaused) {
            start();
        }
    });
    document.addEventListener("visibilitychange", start);

    let touchStartX = null;

    root.addEventListener(
        "touchstart",
        (event) => {
            touchStartX = event.touches[0].clientX;
        },
        { passive: true }
    );

    root.addEventListener(
        "touchend",
        (event) => {
            if (touchStartX === null) {
                return;
            }

            const diff = event.changedTouches[0].clientX - touchStartX;
            touchStartX = null;

            if (Math.abs(diff) >= 45) {
                show(diff > 0 ? index - 1 : index + 1);
            }
        },
        { passive: true }
    );

    updatePauseButton();
    show(0, false);
    start();
})();

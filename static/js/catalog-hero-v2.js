(() => {
    "use strict";

    const root =
        document.getElementById(
            "homeCatsShowcase"
        );

    if (!root) {
        return;
    }

    const slides = [
        ...root.querySelectorAll(
            "[data-home-slide]"
        )
    ];

    const dots = [
        ...root.querySelectorAll(
            "[data-home-dot]"
        )
    ];

    if (!slides.length) {
        return;
    }

    const prev =
        document.getElementById(
            "homeCatPrev"
        );

    const next =
        document.getElementById(
            "homeCatNext"
        );

    const currentLabel =
        document.getElementById(
            "homeCatCurrent"
        );

    const progress =
        document.getElementById(
            "homeCatProgress"
        );

    const reduceMotion =
        window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        ).matches;

    let index = 0;
    let timer = null;

    const interval = 5600;


    const resetProgress = () => {

        if (!progress) {
            return;
        }

        progress.style.animation =
            "none";

        void progress.offsetWidth;

        if (!reduceMotion) {
            progress.style.animation =
                `kpHomeProgress ${interval}ms linear forwards`;
        }
    };


    const show = (
        nextIndex,
        restart = true
    ) => {

        index =
            (
                nextIndex
                +
                slides.length
            )
            %
            slides.length;


        slides.forEach(
            (slide, slideIndex) => {

                const active =
                    slideIndex
                    ===
                    index;

                slide.classList.toggle(
                    "active",
                    active
                );

                slide.setAttribute(
                    "aria-hidden",
                    active
                        ? "false"
                        : "true"
                );

                slide.tabIndex =
                    active
                        ? 0
                        : -1;
            }
        );


        dots.forEach(
            (dot, dotIndex) => {

                dot.classList.toggle(
                    "active",
                    dotIndex
                    ===
                    index
                );
            }
        );


        if (currentLabel) {

            currentLabel.textContent =
                String(
                    index + 1
                );
        }


        if (restart) {
            start();
        }
    };


    const start = () => {

        if (
            reduceMotion
            ||
            slides.length < 2
        ) {
            return;
        }

        clearInterval(
            timer
        );

        resetProgress();

        timer = setInterval(
            () => {
                show(
                    index + 1,
                    false
                );

                resetProgress();
            },
            interval
        );
    };


    const pause = () => {

        clearInterval(
            timer
        );

        if (progress) {
            progress.style
                .animationPlayState =
                "paused";
        }
    };


    const resume = () => {

        if (progress) {
            progress.style
                .animationPlayState =
                "running";
        }

        start();
    };


    if (prev) {

        prev.addEventListener(
            "click",
            () => {
                show(
                    index - 1
                );
            }
        );
    }


    if (next) {

        next.addEventListener(
            "click",
            () => {
                show(
                    index + 1
                );
            }
        );
    }


    dots.forEach(
        (dot) => {

            dot.addEventListener(
                "click",
                () => {

                    show(
                        Number(
                            dot.dataset
                                .homeDot
                        )
                    );
                }
            );
        }
    );


    root.addEventListener(
        "mouseenter",
        pause
    );

    root.addEventListener(
        "mouseleave",
        resume
    );


    document.addEventListener(
        "visibilitychange",
        () => {

            if (
                document.hidden
            ) {
                pause();
            } else {
                resume();
            }
        }
    );


    let touchStartX = null;


    root.addEventListener(
        "touchstart",
        (event) => {

            touchStartX =
                event.touches[0]
                    .clientX;
        },
        {
            passive: true
        }
    );


    root.addEventListener(
        "touchend",
        (event) => {

            if (
                touchStartX
                ===
                null
            ) {
                return;
            }

            const endX =
                event.changedTouches[0]
                    .clientX;

            const diff =
                endX
                -
                touchStartX;

            touchStartX =
                null;

            if (
                Math.abs(diff)
                <
                45
            ) {
                return;
            }

            show(
                diff > 0
                    ? index - 1
                    : index + 1
            );
        },
        {
            passive: true
        }
    );


    show(
        0,
        false
    );

    start();

})();

(() => {
    "use strict";

    const prefersReducedMotion =
        window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        ).matches;


    /* ======================================================
       PAGE READY
       ====================================================== */

    const markReady = () => {
        document.body.classList.add(
            "kp-ready"
        );
    };

    if (
        document.readyState ===
        "loading"
    ) {
        document.addEventListener(
            "DOMContentLoaded",
            markReady
        );
    } else {
        markReady();
    }


    /* ======================================================
       NAVBAR SCROLL
       ====================================================== */

    const navbar =
        document.querySelector(
            ".navbar"
        );

    const updateNavbar = () => {
        if (!navbar) return;

        navbar.classList.toggle(
            "kp-scrolled",
            window.scrollY > 12
        );
    };

    updateNavbar();

    window.addEventListener(
        "scroll",
        updateNavbar,
        {
            passive: true
        }
    );


    /* ======================================================
       ACTIVE NAV ITEM
       ====================================================== */

    const currentPath =
        window.location.pathname;

    document
        .querySelectorAll(
            ".navbar .nav-link"
        )
        .forEach((link) => {

            const href =
                link.getAttribute(
                    "href"
                );

            if (
                !href
                ||
                href === "#"
                ||
                href === "/"
            ) {
                return;
            }

            if (
                currentPath === href
                ||
                currentPath.startsWith(
                    href + "/"
                )
            ) {
                link.classList.add(
                    "active"
                );
            }
        });


    /* ======================================================
       SCROLL REVEAL
       ====================================================== */

    if (!prefersReducedMotion) {

        const targets =
            document.querySelectorAll(
                [
                    ".card",
                    ".table-responsive",
                    ".alert",
                    ".dashboard-title",
                    "main > .row",
                    "main > section"
                ].join(",")
            );

        targets.forEach(
            (element, index) => {

                element.classList.add(
                    "kp-reveal"
                );

                element.style.transitionDelay =
                    `${Math.min(
                        index * 28,
                        220
                    )}ms`;
            }
        );


        const observer =
            new IntersectionObserver(
                (entries) => {

                    entries.forEach(
                        (entry) => {

                            if (
                                entry.isIntersecting
                            ) {
                                entry.target
                                    .classList
                                    .add(
                                        "kp-visible"
                                    );

                                observer.unobserve(
                                    entry.target
                                );
                            }
                        }
                    );
                },
                {
                    threshold: 0.08,
                    rootMargin:
                        "0px 0px -20px 0px"
                }
            );


        targets.forEach(
            (element) => {
                observer.observe(
                    element
                );
            }
        );

    }


    /* ======================================================
       BUTTON RIPPLE
       ====================================================== */

    document.addEventListener(
        "pointerdown",
        (event) => {

            const button =
                event.target.closest(
                    ".btn"
                );

            if (
                !button
                ||
                prefersReducedMotion
            ) {
                return;
            }

            const rect =
                button.getBoundingClientRect();

            const ripple =
                document.createElement(
                    "span"
                );

            ripple.style.position =
                "absolute";

            ripple.style.left =
                `${event.clientX -
                   rect.left}px`;

            ripple.style.top =
                `${event.clientY -
                   rect.top}px`;

            ripple.style.width =
                "8px";

            ripple.style.height =
                "8px";

            ripple.style.borderRadius =
                "50%";

            ripple.style.pointerEvents =
                "none";

            ripple.style.background =
                "rgba(255,255,255,.45)";

            ripple.style.transform =
                "translate(-50%, -50%) scale(0)";

            ripple.style.transition =
                "transform 500ms ease, opacity 500ms ease";

            button.appendChild(
                ripple
            );

            requestAnimationFrame(
                () => {

                    ripple.style.transform =
                        "translate(-50%, -50%) scale(24)";

                    ripple.style.opacity =
                        "0";
                }
            );

            setTimeout(
                () => {
                    ripple.remove();
                },
                550
            );
        }
    );


    /* ======================================================
       CAT CARD SUBTLE POINTER DEPTH
       ====================================================== */

    if (
        !prefersReducedMotion
        &&
        window.matchMedia(
            "(pointer: fine)"
        ).matches
    ) {

        document
            .querySelectorAll(
                ".cat-card"
            )
            .forEach(
                (card) => {

                    card.addEventListener(
                        "mousemove",
                        (event) => {

                            const rect =
                                card.getBoundingClientRect();

                            const x =
                                (
                                    event.clientX
                                    -
                                    rect.left
                                )
                                /
                                rect.width
                                -
                                0.5;

                            const y =
                                (
                                    event.clientY
                                    -
                                    rect.top
                                )
                                /
                                rect.height
                                -
                                0.5;

                            card.style.transform =
                                `translateY(-8px)
                                 perspective(900px)
                                 rotateX(${(-y * 1.7).toFixed(2)}deg)
                                 rotateY(${(x * 1.7).toFixed(2)}deg)`;
                        }
                    );


                    card.addEventListener(
                        "mouseleave",
                        () => {

                            card.style.transform =
                                "";
                        }
                    );
                }
            );

    }


    /* ======================================================
       FORM FIELD STATE
       ====================================================== */

    document
        .querySelectorAll(
            ".form-control, .form-select"
        )
        .forEach(
            (field) => {

                const sync = () => {

                    field.classList.toggle(
                        "kp-has-value",
                        Boolean(
                            String(
                                field.value ?? ""
                            ).trim()
                        )
                    );
                };

                sync();

                field.addEventListener(
                    "input",
                    sync
                );

                field.addEventListener(
                    "change",
                    sync
                );
            }
        );

})();

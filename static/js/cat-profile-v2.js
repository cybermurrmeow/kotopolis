(() => {
    "use strict";

    const media =
        document.querySelector(
            ".kp-profile-media"
        );

    const image =
        document.querySelector(
            ".kp-profile-image"
        );

    const reduced =
        window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        ).matches;


    /* IMAGE DEPTH */

    if (
        media
        &&
        image
        &&
        !reduced
        &&
        window.matchMedia(
            "(pointer: fine)"
        ).matches
    ) {

        media.addEventListener(
            "mousemove",
            (event) => {

                const rect =
                    media.getBoundingClientRect();

                const x =
                    (
                        event.clientX
                        -
                        rect.left
                    )
                    /
                    rect.width
                    -
                    .5;

                const y =
                    (
                        event.clientY
                        -
                        rect.top
                    )
                    /
                    rect.height
                    -
                    .5;

                image.style.transform =
                    `scale(1.035)
                     translate(
                        ${x * 8}px,
                        ${y * 8}px
                     )`;
            }
        );


        media.addEventListener(
            "mouseleave",
            () => {

                image.style.transform =
                    "";
            }
        );
    }


    /* HEART PARTICLES */

    const heart =
        document.querySelector(
            ".kp-profile-heart"
        );

    if (
        heart
        &&
        !reduced
    ) {

        heart.addEventListener(
            "click",
            () => {

                for (
                    let i = 0;
                    i < 6;
                    i += 1
                ) {

                    const particle =
                        document.createElement(
                            "span"
                        );

                    particle.className =
                        "kp-heart-particle";

                    particle.textContent =
                        "♥";

                    particle.style.setProperty(
                        "--x",
                        `${(Math.random() - .5) * 80}px`
                    );

                    particle.style.setProperty(
                        "--y",
                        `${-35 - Math.random() * 60}px`
                    );

                    heart.appendChild(
                        particle
                    );

                    setTimeout(
                        () => {
                            particle.remove();
                        },
                        800
                    );
                }
            }
        );
    }

})();

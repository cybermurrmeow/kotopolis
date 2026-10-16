(() => {
    "use strict";

    const favoriteFormSelector =
        'form[action*="/favorite/"]';


    function updateFavoriteButton(
        button,
        active
    ) {

        if (!button) {
            return;
        }


        button.classList.toggle(
            "active",
            active
        );

        button.classList.toggle(
            "is-favorite",
            active
        );


        button.setAttribute(
            "aria-pressed",
            active
                ? "true"
                : "false"
        );


        const label =
            active
                ? "Убрать из избранного"
                : "Добавить в избранное";


        button.setAttribute(
            "aria-label",
            label
        );

        button.setAttribute(
            "title",
            label
        );


        const icon =
            button.querySelector(
                "i"
            );


        if (icon) {

            icon.classList.toggle(
                "fa-solid",
                active
            );

            icon.classList.toggle(
                "fas",
                active
            );

            icon.classList.toggle(
                "fa-regular",
                !active
            );

            icon.classList.toggle(
                "far",
                !active
            );
        }


        const labelNode =
            button.querySelector(
                "[data-favorite-label]"
            );


        if (labelNode) {

            labelNode.textContent =
                label;
        }
    }


    function clearScrollPending() {

        try {

            sessionStorage.removeItem(
                "kotopolis:scroll:pending"
            );

        } catch (_) {}
    }


    document.addEventListener(
        "click",
        (event) => {

            const form =
                event.target.closest(
                    favoriteFormSelector
                );


            if (!form) {
                return;
            }


            event.stopPropagation();

        },
        true
    );


    document.addEventListener(
        "submit",
        async (event) => {

            const form =
                event.target.closest(
                    favoriteFormSelector
                );


            if (!form) {
                return;
            }


            event.preventDefault();
            event.stopImmediatePropagation();

            clearScrollPending();


            const button =
                form.querySelector(
                    'button[type="submit"], button'
                );


            if (
                !button
                ||
                button.dataset.favoriteBusy
                ===
                "1"
            ) {
                return;
            }


            button.dataset.favoriteBusy =
                "1";

            button.disabled =
                true;


            try {

                const response =
                    await fetch(
                        form.action,
                        {
                            method: "POST",

                            body:
                                new FormData(
                                    form
                                ),

                            credentials:
                                "same-origin",

                            headers: {
                                "X-Requested-With":
                                    "XMLHttpRequest",

                                "Accept":
                                    "application/json"
                            }
                        }
                    );


                let data = null;


                try {

                    data =
                        await response.json();

                } catch (_) {}


                if (
                    !response.ok
                    ||
                    !data
                    ||
                    data.success
                    !== true
                ) {

                    throw new Error(
                        data?.error
                        ||
                        (
                            "HTTP "
                            +
                            response.status
                        )
                    );
                }


                updateFavoriteButton(
                    button,
                    Boolean(
                        data.is_favorite
                    )
                );


                if (
                    typeof button.animate
                    ===
                    "function"
                ) {

                    button.animate(
                        [
                            {
                                transform:
                                    "scale(1)"
                            },
                            {
                                transform:
                                    "scale(.9)"
                            },
                            {
                                transform:
                                    "scale(1)"
                            }
                        ],
                        {
                            duration: 140,
                            easing: "ease-out"
                        }
                    );
                }


            } catch (error) {

                console.error(
                    "Favorite AJAX error:",
                    error
                );


            } finally {

                button.disabled =
                    false;

                delete button.dataset
                    .favoriteBusy;

                clearScrollPending();
            }

        },
        true
    );

})();


/* ==========================================================
   FIX PACK 8F — FAVORITES NETWORK FEEDBACK
   ========================================================== */

(() => {
    "use strict";

    if (window.__kpFavoriteFeedbackInstalled) {
        return;
    }

    window.__kpFavoriteFeedbackInstalled = true;

    const originalFetch =
        window.fetch.bind(window);


    const getFavoriteButtons = () => [
        ...document.querySelectorAll(
            [
                ".kp-heart-button",
                "[data-favorite-button]",
                ".favorite-button"
            ].join(",")
        ),
    ];


    const getStatusRegion = () => {

        let region =
            document.getElementById(
                "kpFavoriteStatus"
            );

        if (region) {
            return region;
        }

        region =
            document.createElement("div");

        region.id =
            "kpFavoriteStatus";

        region.className =
            "kp-favorite-feedback";

        region.setAttribute(
            "role",
            "status"
        );

        region.setAttribute(
            "aria-live",
            "polite"
        );

        region.hidden = true;

        document.body.append(region);

        return region;
    };


    let hideTimer = null;


    const showFavoriteMessage = (
        message,
        type = "error"
    ) => {

        const region =
            getStatusRegion();

        region.textContent =
            message;

        region.dataset.type =
            type;

        region.hidden = false;


        if (hideTimer) {
            clearTimeout(hideTimer);
        }

        hideTimer =
            setTimeout(
                () => {
                    region.hidden = true;
                },
                5000
            );
    };


    const setFavoriteBusy = (
        busy
    ) => {

        getFavoriteButtons()
            .forEach(
                (button) => {

                    if (busy) {

                        if (
                            !button.dataset
                                .favoriteWasDisabled
                        ) {
                            button.dataset
                                .favoriteWasDisabled =
                                button.disabled
                                    ? "1"
                                    : "0";
                        }

                        button.disabled = true;

                        button.setAttribute(
                            "aria-busy",
                            "true"
                        );
                    }

                    else {

                        const wasDisabled =
                            button.dataset
                                .favoriteWasDisabled
                                === "1";

                        button.disabled =
                            wasDisabled;

                        button.removeAttribute(
                            "aria-busy"
                        );

                        delete button.dataset
                            .favoriteWasDisabled;
                    }
                }
            );
    };


    window.fetch = async (
        input,
        init
    ) => {

        const url =
            typeof input === "string"
                ? input
                : input?.url || "";

        const isFavoriteRequest =
            /\/favorite(?:\/|$)/i.test(
                url
            );


        if (!isFavoriteRequest) {
            return originalFetch(
                input,
                init
            );
        }


        setFavoriteBusy(true);


        try {

            const response =
                await originalFetch(
                    input,
                    init
                );


            if (!response.ok) {

                showFavoriteMessage(
                    "Не удалось сохранить избранное. Попробуй ещё раз."
                );
            }


            return response;
        }

        catch (error) {

            showFavoriteMessage(
                "Не удалось сохранить избранное. Проверь соединение и попробуй ещё раз."
            );

            throw error;
        }

        finally {

            setFavoriteBusy(false);
        }
    };

})();

/* FIX PACK 8F FAVORITES */

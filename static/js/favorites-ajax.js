(() => {
    "use strict";

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    document
        .querySelectorAll(".kp-favorite-image[data-poster-src]")
        .forEach((image) => {
            const source = reduceMotion
                ? image.dataset.posterSrc
                : image.dataset.animatedSrc;
            if (source) image.src = source;
        });

    let hideTimer;
    function showError(message) {
        let region = document.getElementById("kpFavoriteStatus");
        if (!region) {
            region = document.createElement("div");
            region.id = "kpFavoriteStatus";
            region.className = "kp-favorite-feedback";
            region.setAttribute("role", "status");
            region.setAttribute("aria-live", "polite");
            document.body.append(region);
        }
        region.textContent = message;
        region.dataset.type = "error";
        region.hidden = false;
        clearTimeout(hideTimer);
        hideTimer = setTimeout(() => {
            region.hidden = true;
        }, 5000);
    }

    function updateButton(button, active) {
        button.classList.toggle("active", active);
        button.classList.toggle("is-favorite", active);
        button.setAttribute("aria-pressed", String(active));
        const label = active ? "Убрать из избранного" : "Добавить в избранное";
        button.setAttribute("aria-label", label);
        button.title = label;
        const icon = button.querySelector("i");
        if (icon) {
            for (const name of ["fa-solid", "fas"]) icon.classList.toggle(name, active);
            for (const name of ["fa-regular", "far"])
                icon.classList.toggle(name, !active);
        }
        const text = button.querySelector("[data-favorite-label]");
        if (text) text.textContent = label;
    }

    document.addEventListener(
        "submit",
        async (event) => {
            const form = event.target.closest('form[action*="/favorite/"]');
            if (!form) return;
            event.preventDefault();
            event.stopImmediatePropagation();
            const button = form.querySelector("button[type=submit], button");
            if (!button || button.disabled) return;
            button.disabled = true;
            button.setAttribute("aria-busy", "true");

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: new FormData(form),
                    credentials: "same-origin",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        Accept: "application/json",
                    },
                });
                if (response.redirected) {
                    window.location.assign(response.url);
                    return;
                }
                const data = await response.json();
                if (!response.ok || data.success !== true) {
                    throw new Error(
                        data.error ||
                            "Не удалось сохранить избранное. Попробуй ещё раз."
                    );
                }
                updateButton(button, Boolean(data.is_favorite));
                if (!reduceMotion && typeof button.animate === "function") {
                    button.animate(
                        [
                            { transform: "scale(1)" },
                            { transform: "scale(.9)" },
                            { transform: "scale(1)" },
                        ],
                        { duration: 140, easing: "ease-out" }
                    );
                }
                const card = form.closest(".kp-favorite-card");
                if (card && !data.is_favorite) {
                    // Reload the favorites page so its count and empty state agree with the DB.
                    window.location.reload();
                }
            } catch (error) {
                showError(
                    error instanceof SyntaxError
                        ? "Сессия устарела. Обнови страницу и попробуй ещё раз."
                        : error.message || "Проверь соединение и попробуй ещё раз."
                );
            } finally {
                button.disabled = false;
                button.removeAttribute("aria-busy");
            }
        },
        true
    );
})();

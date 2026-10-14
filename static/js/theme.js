(function () {
    "use strict";

    const key = "kotopolis-theme";
    const root = document.documentElement;

    function applyTheme(theme) {
        const dark = theme === "dark";
        root.dataset.theme = dark ? "dark" : "light";
        root.dataset.bsTheme = root.dataset.theme;
        const button = document.getElementById("theme-toggle");
        if (button) {
            const label = dark ? "Включить светлую тему" : "Включить тёмную тему";
            button.setAttribute("aria-pressed", String(dark));
            button.setAttribute("aria-label", label);
            button.title = label;
        }
    }

    let saved = "light";
    try {
        saved = localStorage.getItem(key);
    } catch {
        // Theme switching still works when browser storage is unavailable.
    }
    applyTheme(saved);

    document.addEventListener("DOMContentLoaded", function () {
        applyTheme(root.dataset.theme);
        const button = document.getElementById("theme-toggle");
        if (!button) return;
        button.addEventListener("click", function () {
            const theme = root.dataset.theme === "dark" ? "light" : "dark";
            applyTheme(theme);
            try {
                localStorage.setItem(key, theme);
            } catch {
                // Keep the current page usable without persistent storage.
            }
        });
    });

    window.addEventListener("storage", function (event) {
        if (event.key === key || event.key === null) applyTheme(event.newValue);
    });
})();

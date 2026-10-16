(() => {
    "use strict";

    // Фильтры одного каталога используют общую позицию: ключ содержит только pathname.

    try {
        window.sessionStorage.getItem("");
    } catch (_) {
        return;
    }

    if ("scrollRestoration" in history) {
        history.scrollRestoration = "manual";
    }

    const PREFIX = "kotopolis:scroll:";

    const PENDING = "kotopolis:scroll:pending";

    const pageKey = (pathname = location.pathname) => {
        return PREFIX + pathname;
    };

    const getY = (pathname = location.pathname) => {
        try {
            const raw = sessionStorage.getItem(pageKey(pathname));

            if (raw === null) {
                return null;
            }

            const value = Number(raw);

            return Number.isFinite(value) ? value : null;
        } catch (_) {
            return null;
        }
    };

    const save = () => {
        try {
            sessionStorage.setItem(
                pageKey(),
                String(Math.max(0, window.scrollY || window.pageYOffset || 0))
            );
        } catch (_) {}
    };

    let ticking = false;

    const requestSave = () => {
        if (ticking) {
            return;
        }

        ticking = true;

        requestAnimationFrame(() => {
            save();

            ticking = false;
        });
    };

    window.addEventListener("scroll", requestSave, {
        passive: true,
    });

    window.addEventListener("pagehide", save);

    window.addEventListener("beforeunload", save);

    document.addEventListener(
        "submit",
        () => {
            save();

            try {
                sessionStorage.setItem(
                    PENDING,
                    JSON.stringify({
                        pathname: location.pathname,

                        y: window.scrollY || 0,

                        at: Date.now(),
                    })
                );
            } catch (_) {}
        },
        true
    );

    document.addEventListener(
        "click",
        (event) => {
            const link = event.target.closest("a[href]");

            if (!link) {
                return;
            }

            const href = link.getAttribute("href");

            if (
                !href ||
                href.startsWith("#") ||
                href.startsWith("javascript:") ||
                link.target === "_blank" ||
                link.hasAttribute("download")
            ) {
                return;
            }

            let url;

            try {
                url = new URL(link.href, location.href);
            } catch (_) {
                return;
            }

            if (url.origin !== location.origin) {
                return;
            }

            save();

            // При смене фильтра возвращаемся к прежнему месту каталога.

            if (url.pathname === location.pathname) {
                try {
                    sessionStorage.setItem(
                        PENDING,
                        JSON.stringify({
                            pathname: location.pathname,

                            y: window.scrollY || 0,

                            at: Date.now(),
                        })
                    );
                } catch (_) {}
            }
        },
        true
    );

    let userInterrupted = false;

    const interrupt = () => {
        userInterrupted = true;
    };

    window.addEventListener("wheel", interrupt, {
        passive: true,
        once: true,
    });

    window.addEventListener("touchstart", interrupt, {
        passive: true,
        once: true,
    });

    window.addEventListener("pointerdown", interrupt, {
        passive: true,
        once: true,
    });

    const navigationType = () => {
        const entry = performance.getEntriesByType("navigation")[0];

        return entry ? entry.type : "";
    };

    const getTarget = () => {
        let target = null;

        const navType = navigationType();

        if (navType === "back_forward" || navType === "reload") {
            target = getY();
        }

        try {
            const raw = sessionStorage.getItem(PENDING);

            if (raw) {
                const pending = JSON.parse(raw);

                const fresh = Date.now() - Number(pending.at || 0) < 30000;

                if (
                    pending.pathname === location.pathname &&
                    fresh &&
                    Number.isFinite(Number(pending.y))
                ) {
                    target = Number(pending.y);
                }

                sessionStorage.removeItem(PENDING);
            }
        } catch (_) {}

        return target;
    };

    const targetY = getTarget();

    if (targetY === null || targetY < 1) {
        return;
    }

    // На время восстановления отключаем плавную прокрутку.

    const html = document.documentElement;

    html.classList.add("kp-restoring-scroll");

    const restore = () => {
        if (userInterrupted) {
            return;
        }

        const maxY = Math.max(
            0,
            document.documentElement.scrollHeight - window.innerHeight
        );

        const destination = Math.min(targetY, maxY);

        window.scrollTo(0, destination);
    };

    // Повторяем после загрузки изображений, которые могут изменить высоту страницы.

    const attempts = [0, 20, 60, 140, 300, 600];

    attempts.forEach((delay) => {
        window.setTimeout(restore, delay);
    });

    window.addEventListener("load", restore, {
        once: true,
    });

    window.setTimeout(() => {
        html.classList.remove("kp-restoring-scroll");
    }, 700);
})();

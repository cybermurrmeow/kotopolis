(() => {
    "use strict";

    const form = document.getElementById("catalogFilterForm");

    if (!form) {
        return;
    }

    const grid = document.getElementById("cats-grid");

    const cards = [...document.querySelectorAll("#cats-grid .cat-card")];

    const advanced = document.getElementById("advancedFilters");

    const advancedToggle = document.getElementById("advancedFiltersToggle");

    const filterCount = document.getElementById("activeFilterCount");

    const statusInput = document.getElementById("statusFilter");

    const sortSelect = document.getElementById("catalogSort");

    const motionToggle = document.getElementById("catalogMotionToggle");

    const picker = document.querySelector(".kp-picker");

    const pickerToggle = document.getElementById("pickerMobileToggle");

    const mediaImages = [...document.querySelectorAll(".kp-media-fallback")];

    mediaImages.forEach((image) => {
        image.addEventListener("error", () => {
            const fallback = image.dataset.fallback;

            if (!fallback || image.dataset.fallbackUsed) {
                return;
            }

            image.dataset.fallbackUsed = "true";

            image.src = fallback;
        });
    });

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let motionEnabled = !reduceMotion;

    mediaImages.forEach((image) => {
        const source = motionEnabled
            ? image.dataset.animatedSrc
            : image.dataset.posterSrc;

        if (source) {
            image.src = source;
        }
    });

    const updateMotionButton = () => {
        if (!motionToggle) {
            return;
        }

        motionToggle.setAttribute("aria-pressed", String(motionEnabled));

        const icon = motionToggle.querySelector("i");

        const label = motionToggle.querySelector("span");

        if (icon) {
            icon.className = motionEnabled ? "fas fa-pause" : "fas fa-play";
        }

        if (label) {
            label.textContent = motionEnabled ? "Остановить анимацию" : "Анимация";
        }
    };

    motionToggle?.addEventListener("click", () => {
        motionEnabled = !motionEnabled;

        mediaImages.forEach((image) => {
            const next = motionEnabled
                ? image.dataset.animatedSrc
                : image.dataset.posterSrc;

            if (!next) {
                return;
            }

            delete image.dataset.fallbackUsed;

            image.src = next;
        });

        updateMotionButton();
    });

    updateMotionButton();

    document.querySelectorAll(".kp-filter-chip").forEach((chip) => {
        chip.addEventListener("click", () => {
            if (statusInput) {
                statusInput.value = chip.dataset.filterValue || "";
            }

            form.submit();
        });
    });

    const fillSelect = (id, dataKey) => {
        const select = document.getElementById(id);

        if (!select) {
            return;
        }

        const current = String(select.dataset.current || "").trim();

        const values = [
            ...new Set(
                cards
                    .map((card) => String(card.dataset[dataKey] || "").trim())
                    .filter(Boolean)
            ),
        ].sort((a, b) => a.localeCompare(b, "ru"));

        if (current && !values.includes(current)) {
            values.unshift(current);
        }

        values.forEach((value) => {
            const option = document.createElement("option");

            option.value = value;
            option.textContent = value;

            select.append(option);
        });

        select.value = current;
    };

    fillSelect("genderFilterVisible", "gender");

    fillSelect("moodFilterVisible", "mood");

    fillSelect("personalityFilterVisible", "personality");

    document.querySelectorAll("[data-filter-target]").forEach((visible) => {
        const hidden = document.getElementById(visible.dataset.filterTarget);

        if (hidden && hidden.value) {
            visible.value = hidden.value;
        }

        visible.addEventListener("change", () => {
            if (hidden) {
                hidden.value = visible.value;
            }

            updateCount();
        });
    });

    const advancedNames = ["gender", "mood", "personality"];

    const countAdvanced = () => {
        let count = 0;

        advancedNames.forEach((name) => {
            const field = form.elements[name];

            if (field && String(field.value || "").trim()) {
                count += 1;
            }
        });

        return count;
    };

    function updateCount() {
        if (!filterCount) {
            return;
        }

        const count = countAdvanced();

        filterCount.textContent = String(count);

        filterCount.hidden = count === 0;
    }

    if (advanced && advancedToggle) {
        if (countAdvanced() > 0) {
            advanced.hidden = false;

            advancedToggle.setAttribute("aria-expanded", "true");
        }

        advancedToggle.addEventListener("click", () => {
            const opening = advanced.hidden;

            advanced.hidden = !opening;

            advancedToggle.setAttribute("aria-expanded", String(opening));

            if (opening) {
                advanced.querySelector("select")?.focus();
            }
        });
    }

    updateCount();

    const search = form.querySelector('input[name="search"]');

    search?.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            search.value = "";
            search.focus();
        }
    });

    const originalOrder = new Map(cards.map((card, index) => [card, index]));

    const sortCards = () => {
        if (!grid || !sortSelect) {
            return;
        }

        const mode = sortSelect.value;

        const sorted = [...cards];

        sorted.sort((a, b) => {
            if (mode === "name-asc") {
                return (a.dataset.name || "").localeCompare(b.dataset.name || "", "ru");
            }

            if (mode === "age-asc" || mode === "age-desc") {
                const rawA = a.dataset.age;

                const rawB = b.dataset.age;

                const validA = rawA !== "";

                const validB = rawB !== "";

                if (validA && !validB) {
                    return -1;
                }

                if (!validA && validB) {
                    return 1;
                }

                if (validA && validB) {
                    const ageA = Number(rawA);

                    const ageB = Number(rawB);

                    return mode === "age-asc" ? ageA - ageB : ageB - ageA;
                }
            }

            return originalOrder.get(a) - originalOrder.get(b);
        });

        sorted.forEach((card) => {
            grid.append(card);
        });
    };

    sortSelect?.addEventListener("change", sortCards);

    const compactScreen = window.matchMedia("(max-width: 360px), (max-height: 640px)");

    const setPickerCollapsed = (collapsed) => {
        if (!picker || !pickerToggle) {
            return;
        }

        picker.classList.toggle("kp-picker-collapsed", collapsed);

        pickerToggle.setAttribute("aria-expanded", String(!collapsed));

        const label = pickerToggle.querySelector("span");

        const icon = pickerToggle.querySelector("i");

        if (label) {
            label.textContent = collapsed ? "Настроить подбор" : "Свернуть подбор";
        }

        if (icon) {
            icon.className = collapsed ? "fas fa-chevron-down" : "fas fa-chevron-up";
        }
    };

    if (picker && pickerToggle) {
        if (compactScreen.matches) {
            setPickerCollapsed(true);
        }

        pickerToggle.addEventListener("click", () => {
            setPickerCollapsed(!picker.classList.contains("kp-picker-collapsed"));
        });
    }

    document
        .querySelectorAll(".kp-heart-button:not(.kp-home-indicator)")
        .forEach((button) => {
            button.addEventListener("click", () => {
                button.classList.add("kp-heart-click");

                setTimeout(() => {
                    button.classList.remove("kp-heart-click");
                }, 500);
            });
        });
})();

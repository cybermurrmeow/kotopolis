(() => {
    "use strict";
    const container = document.getElementById("compatibilityFilters");
    if (!container) return;
    const cards = [...document.querySelectorAll("#cats-grid .cat-card")];
    const buttons = [...container.querySelectorAll("[data-group]")];
    const title = document.getElementById("catalog-results-title");
    const selected = document.getElementById("compatibilitySelected");
    const empty = document.getElementById("compatibilityEmpty");
    const form = document.getElementById("catalogFilterForm");
    const keys = {home: "compat_home", activity: "compat_activity", vocal: "compat_vocal", age: "compat_age"};
    let state = {home: [], activity: "", vocal: "", age: ""};
    const word = n => n % 10 === 1 && n % 100 !== 11 ? "котик" :
        [2, 3, 4].includes(n % 10) && ![12, 13, 14].includes(n % 100) ? "котика" : "котиков";
    const normalize = value => String(value ?? "").trim().toLowerCase();
    const booleanValue = value => ["1", "true"].includes(normalize(value));
    const matches = (card, filter) => {
        const data = card.dataset;
        if (!filter.home.every(value => booleanValue(data[value + "Friendly"]))) return false;
        const activities = {low: "низкий", medium: "средний", high: "высокий"};
        const vocals = {silent: "молчаливый", talkative: "разговорчивый"};
        if (filter.activity && normalize(data.activity) !== activities[filter.activity]) return false;
        if (filter.vocal && normalize(data.vocal) !== vocals[filter.vocal]) return false;
        if (filter.age) {
            if (normalize(data.age) === "" || !Number.isFinite(Number(data.age))) return false;
            const age = Number(data.age);
            if (filter.age === "0-2" && !(age >= 0 && age <= 2)) return false;
            if (filter.age === "3-5" && !(age >= 3 && age <= 5)) return false;
            if (filter.age === "6+" && !(age >= 6)) return false;
        }
        return true;
    };
    const active = () => state.home.length > 0 || Boolean(state.activity || state.vocal || state.age);
    const isSelected = button => button.dataset.group === "home" ?
        state.home.includes(button.dataset.value) : state[button.dataset.group] === button.dataset.value;
    const candidate = button => {
        const next = {...state, home: [...state.home]};
        const {group, value} = button.dataset;
        if (group === "home") {
            if (!next.home.includes(value)) next.home.push(value);
        } else next[group] = value;
        return next;
    };
    const syncForm = () => {
        if (!form) return;
        Object.entries(keys).forEach(([group, key]) => {
            let input = form.querySelector('input[data-picker-param="' + key + '"]');
            if (!input) {
                input = document.createElement("input");
                input.type = "hidden";
                input.name = key;
                input.dataset.pickerParam = key;
                form.append(input);
            }
            input.value = group === "home" ? state.home.join(",") : state[group];
            input.disabled = !input.value;
        });
    };
    const writeURL = () => {
        const url = new URL(location.href);
        Object.entries(keys).forEach(([group, key]) => {
            const value = group === "home" ? state.home.join(",") : state[group];
            value ? url.searchParams.set(key, value) : url.searchParams.delete(key);
        });
        history.pushState(null, "", url);
    };
    const render = () => {
        let count = 0;
        cards.forEach(card => {
            card.hidden = !matches(card, state);
            if (!card.hidden) count += 1;
        });
        buttons.forEach(button => {
            const pressed = isSelected(button);
            const total = cards.filter(card => matches(card, candidate(button))).length;
            button.setAttribute("aria-pressed", String(pressed));
            button.classList.toggle("kp-facet-zero", total === 0);
            button.querySelector(".kp-facet-count").textContent = total;
            const label = button.querySelector("span").textContent;
            button.setAttribute("aria-label", label + ", " + total + " " + word(total) + (total === 0 ? ", нет совпадений" : ""));
        });
        title.replaceChildren(document.createTextNode((active() ? "Подходит " : "") + count + " " + word(count)));
        if (active()) {
            const base = document.createElement("small");
            base.className = "kp-picker-base";
            base.textContent = " из " + cards.length;
            title.append(base);
        }
        selected.replaceChildren();
        selected.hidden = !active();
        buttons.filter(isSelected).forEach(button => {
            const remove = document.createElement("button");
            remove.type = "button";
            remove.className = "kp-picker-selected-chip";
            const label = button.querySelector("span").textContent;
            remove.textContent = label + " ×";
            remove.setAttribute("aria-label", "Убрать условие: " + label);
            remove.addEventListener("click", () => {
                const {group, value} = button.dataset;
                if (group === "home") state.home = state.home.filter(item => item !== value);
                else state[group] = "";
                commit();
            });
            selected.append(remove);
        });
        if (active()) {
            const reset = document.createElement("button");
            reset.type = "button";
            reset.className = "kp-compatibility-reset";
            reset.textContent = "Сбросить подбор";
            reset.addEventListener("click", resetSelection);
            selected.append(reset);
        }
        empty.hidden = !active() || count !== 0;
        syncForm();
    };
    const commit = () => { writeURL(); render(); };
    const resetSelection = () => {
        state = {home: [], activity: "", vocal: "", age: ""};
        commit();
    };
    const readURL = () => {
        const params = new URL(location.href).searchParams;
        state.home = [...new Set((params.get(keys.home) || "").split(","))].filter(value => ["kids", "cats", "dogs"].includes(value));
        ["activity", "vocal", "age"].forEach(group => {
            const value = params.get(keys[group]) || "";
            state[group] = buttons.some(button => button.dataset.group === group && button.dataset.value === value) ? value : "";
        });
        render();
    };
    buttons.forEach(button => button.addEventListener("click", () => {
        const {group, value} = button.dataset;
        if (group === "home") state.home = isSelected(button) ? state.home.filter(item => item !== value) : [...state.home, value];
        else state[group] = isSelected(button) ? "" : value;
        commit();
    }));
    document.querySelectorAll("[data-compat-reset]").forEach(button => button.addEventListener("click", resetSelection));
    window.addEventListener("popstate", readURL);
    readURL();
})();

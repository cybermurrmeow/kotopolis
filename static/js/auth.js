(() => {
    "use strict";
    const root = document.querySelector(".kp-auth3");
    if (!root) return;
    const messages = root.querySelector("[data-auth-messages]");
    if (messages) {
        const main = root.closest("main");
        [...main.children]
            .filter((node) => node.classList.contains("alert"))
            .forEach((alert) => {
                alert.classList.add("kp-auth3-notice");
                messages.append(alert);
            });
    }
    root.querySelectorAll("[data-auth-password]").forEach((button) => {
        const input = document.getElementById(button.dataset.authPassword);
        if (!input) return;
        button.addEventListener("click", () => {
            const reveal = input.type === "password";
            input.type = reveal ? "text" : "password";
            button.textContent = reveal ? "Скрыть" : "Показать";
            button.setAttribute(
                "aria-label",
                reveal ? "Скрыть пароль" : "Показать пароль"
            );
            button.setAttribute("aria-pressed", String(reveal));
        });
    });
    const password = root.querySelector("#register-password");
    const confirm = root.querySelector("#register-confirm-password");
    if (password && confirm) {
        const strength = root.querySelector("[data-auth-strength]");
        const match = root.querySelector("[data-auth-match]");
        const update = () => {
            const value = password.value;
            const rules = {
                length: value.length >= 8,
                letter: /[a-zа-яё]/i.test(value),
                number: /\d/.test(value),
            };
            Object.entries(rules).forEach(([name, passed]) => {
                const item = root.querySelector('[data-auth-rule="' + name + '"]');
                item.classList.toggle("is-met", passed);
                item.setAttribute(
                    "aria-label",
                    item.textContent + (passed ? ": выполнено" : ": пока не выполнено")
                );
            });
            const valid = Object.values(rules).every(Boolean);
            const score = !valid
                ? 0
                : value.length >= 14
                  ? 3
                  : value.length >= 10 || /[^a-zа-яё0-9]/i.test(value)
                    ? 2
                    : 1;
            strength.textContent = !value
                ? "ещё не введён"
                : ["слишком простой", "нормальный", "хороший", "крепкий"][score];
            strength.dataset.level = score;
            match.textContent = !confirm.value
                ? ""
                : confirm.value === value
                  ? "Пароли совпадают"
                  : "Пароли пока не совпадают";
            match.classList.toggle(
                "is-match",
                Boolean(confirm.value) && confirm.value === value
            );
        };
        password.addEventListener("input", update);
        confirm.addEventListener("input", update);
        update();
    }
    const code = root.querySelector("[data-auth-code]");
    const cells = [...root.querySelectorAll("[data-auth-digit]")];
    if (code && cells.length === 6) {
        code.classList.add("kp-auth3-code-source");
        code.setAttribute("aria-hidden", "true");
        code.tabIndex = -1;
        cells.forEach((cell) => (cell.hidden = false));
        const sync = () => {
            code.value = cells.map((cell) => cell.value).join("");
        };
        const insert = (text, start) => {
            const digits = text.replace(/[^0-9]/g, "").slice(0, 6 - start);
            [...digits].forEach((digit, index) => {
                cells[start + index].value = digit;
            });
            sync();
            cells[Math.min(start + digits.length, 5)].focus();
        };
        cells.forEach((cell, index) => {
            cell.addEventListener("focus", () => cell.select());
            cell.addEventListener("input", () => {
                const digits = cell.value.replace(/[^0-9]/g, "");
                if (digits.length > 1) {
                    insert(digits, index);
                    return;
                }
                cell.value = digits.slice(-1);
                sync();
                if (cell.value && index < 5) cells[index + 1].focus();
            });
            cell.addEventListener("paste", (event) => {
                event.preventDefault();
                const text = event.clipboardData.getData("text");
                const digits = text.replace(/[^0-9]/g, "");
                insert(text, digits.length === 6 ? 0 : index);
            });
            cell.addEventListener("keydown", (event) => {
                if (event.key === "Backspace" && !cell.value && index > 0) {
                    event.preventDefault();
                    cells[index - 1].value = "";
                    cells[index - 1].focus();
                    sync();
                }
                if (event.key === "ArrowLeft" && index > 0) {
                    event.preventDefault();
                    cells[index - 1].focus();
                }
                if (event.key === "ArrowRight" && index < 5) {
                    event.preventDefault();
                    cells[index + 1].focus();
                }
                if (event.key === "Enter") {
                    event.preventDefault();
                    code.form.requestSubmit();
                }
            });
        });
        code.form.addEventListener("submit", (event) => {
            sync();
            if (!/^[0-9]{6}$/.test(code.value)) {
                event.preventDefault();
                const error = root.querySelector("[data-auth-code-error]");
                if (error) error.textContent = "Введи все 6 цифр.";
                (cells.find((cell) => !cell.value) || cells[0]).focus();
            }
        });
        insert(code.value, 0);
        cells[0].focus();
    }
})();

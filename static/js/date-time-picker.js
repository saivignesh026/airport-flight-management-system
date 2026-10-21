/* A compact, accessible calendar and time picker for native date fields.
   The original named input becomes a hidden transport field, so submitted
   values keep the browser's standard YYYY-MM-DD / HH:MM / datetime-local form. */
(function () {
    "use strict";

    const pad = (n) => String(n).padStart(2, "0");
    const parseValue = (value, kind) => {
        if (!value) return null;
        const parts = value.split(kind === "datetime-local" ? "T" : ":");
        const date = kind === "date" || kind === "datetime-local" ? parts[0].split("-").map(Number) : null;
        const timeText = kind === "time" ? value : kind === "datetime-local" ? (parts[1] || "") : "";
        const time = timeText ? timeText.split(":").map(Number) : null;
        return {
            date: date && date.length === 3 ? new Date(date[0], date[1] - 1, date[2]) : null,
            hour: time ? time[0] || 0 : null,
            minute: time ? time[1] || 0 : null,
            second: time ? time[2] || 0 : 0
        };
    };
    const dateValue = (date) => `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
    const localDateLabel = (date, options) => new Intl.DateTimeFormat(undefined, options).format(date);

    function enhance(original) {
        const kind = original.type;
        if (!/^(date|time|datetime-local)$/.test(kind) || original.closest(".date-time-picker")) return;

        const required = original.required;
        const hasSeconds = original.step && Number(original.step) < 60;
        const current = parseValue(original.value, kind);
        let draftDate = current?.date || new Date();
        let draftHour = current?.hour ?? new Date().getHours();
        let draftMinute = current?.minute ?? new Date().getMinutes();
        let draftSecond = current?.second ?? 0;
        let viewDate = new Date(draftDate.getFullYear(), draftDate.getMonth(), 1);

        const wrapper = document.createElement("div");
        wrapper.className = "date-time-picker";
        wrapper.dataset.kind = kind;
        wrapper.dataset.required = String(required);
        original.parentNode.insertBefore(wrapper, original);
        wrapper.appendChild(original);
        original.type = "hidden";
        original.required = false;
        original.classList.add("date-time-picker-value");

        const visible = document.createElement("input");
        visible.type = "text";
        visible.readOnly = kind !== "time";
        visible.className = "date-time-picker-input";
        visible.id = original.id || `date-time-${Math.random().toString(36).slice(2, 9)}`;
        visible.setAttribute("aria-haspopup", "dialog");
        visible.setAttribute("aria-expanded", "false");
        visible.setAttribute("autocomplete", "off");
        visible.setAttribute("placeholder", kind === "time" ? "HH:MM · 24-hour time" : kind === "date" ? "Choose a date" : "Choose date & time");
        if (kind === "time") {
            visible.inputMode = "text";
            visible.autocapitalize = "off";
            visible.spellcheck = false;
        }
        wrapper.appendChild(visible);
        original.removeAttribute("id");

        const trigger = document.createElement("button");
        trigger.type = "button";
        trigger.className = "date-time-picker-trigger";
        trigger.setAttribute("aria-label", kind === "time" ? "Open time picker" : kind === "date" ? "Open date picker" : "Open date and time picker");
        trigger.setAttribute("aria-haspopup", "dialog");
        trigger.setAttribute("aria-expanded", "false");
        trigger.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="5" width="17" height="16" rx="2.5"/><path d="M7.5 3v4m9-4v4M4 9.5h16M8 13h.01M12 13h.01M16 13h.01M8 17h.01M12 17h.01"/></svg>';
        wrapper.appendChild(trigger);

        const popover = document.createElement("section");
        popover.className = "date-time-popover";
        popover.id = `${visible.id}-popover`;
        popover.setAttribute("role", "dialog");
        popover.setAttribute("aria-label", kind === "time" ? "Choose a time" : kind === "date" ? "Choose a date" : "Choose date and time");
        popover.hidden = true;
        wrapper.appendChild(popover);
        visible.setAttribute("aria-controls", popover.id);
        trigger.setAttribute("aria-controls", popover.id);

        function displayValue(value) {
            const parsed = parseValue(value, kind);
            if (!parsed) { visible.value = ""; return; }
            if (kind === "date") visible.value = localDateLabel(parsed.date, { day: "numeric", month: "short", year: "numeric" });
            else if (kind === "time") visible.value = `${pad(parsed.hour)}:${pad(parsed.minute)}`;
            else visible.value = `${localDateLabel(parsed.date, { day: "numeric", month: "short", year: "numeric" })}  ·  ${pad(parsed.hour)}:${pad(parsed.minute)}`;
        }
        displayValue(original.value);

        function parseTypedTime(value) {
            const match = value.trim().match(/^(?:(\d{1,2}):(\d{2})(?::(\d{2}))?|(\d{2})(\d{2})(\d{2})?)$/);
            if (!match) return null;
            const hour = Number(match[1] ?? match[4]);
            const minute = Number(match[2] ?? match[5]);
            const second = Number(match[3] ?? match[6] ?? 0);
            if (hour > 23 || minute > 59 || second > 59) return null;
            return { hour, minute, second };
        }
        function formatTimeValue(typed, raw) {
            let second = typed.second;
            const explicitlyEnteredSeconds = /(?::\d{2}|\d{6})$/.test(raw.trim());
            if (hasSeconds && !explicitlyEnteredSeconds) {
                const existing = parseValue(original.value, "time");
                if (existing && existing.hour === typed.hour && existing.minute === typed.minute) second = existing.second;
            }
            return `${pad(typed.hour)}:${pad(typed.minute)}${hasSeconds ? `:${pad(second)}` : ""}`;
        }

        function setError(message) {
            visible.setAttribute("aria-invalid", "true");
            const errorId = `${visible.id}-error`;
            let error = wrapper.querySelector(".field-error");
            if (!error) {
                error = document.createElement("span");
                error.className = "field-error";
                error.id = errorId;
                wrapper.insertAdjacentElement("afterend", error);
            }
            error.textContent = message;
            visible.setAttribute("aria-describedby", errorId);
        }
        function clearError() {
            visible.removeAttribute("aria-invalid");
            visible.removeAttribute("aria-describedby");
            wrapper.parentElement?.querySelector(`#${CSS.escape(`${visible.id}-error`)}`)?.remove();
            visible.dispatchEvent(new Event("input", { bubbles: true }));
        }

        function close(restoreFocus) {
            popover.hidden = true;
            visible.setAttribute("aria-expanded", "false");
            trigger.setAttribute("aria-expanded", "false");
            wrapper.classList.remove("is-open");
            if (restoreFocus) visible.focus({ preventScroll: true });
        }
        function open() {
            document.querySelectorAll(".date-time-picker.is-open").forEach((item) => {
                if (item !== wrapper) {
                    item.querySelector(".date-time-popover").hidden = true;
                    item.querySelector(".date-time-picker-input")?.setAttribute("aria-expanded", "false");
                    item.querySelector(".date-time-picker-trigger")?.setAttribute("aria-expanded", "false");
                    item.classList.remove("is-open");
                }
            });
            const value = parseValue(original.value, kind);
            if (value) {
                draftDate = value.date || draftDate;
                draftHour = value.hour ?? draftHour;
                draftMinute = value.minute ?? draftMinute;
                draftSecond = value.second;
            }
            viewDate = new Date(draftDate.getFullYear(), draftDate.getMonth(), 1);
            render();
            popover.hidden = false;
            visible.setAttribute("aria-expanded", "true");
            trigger.setAttribute("aria-expanded", "true");
            wrapper.classList.add("is-open");
            const initial = popover.querySelector(".date-time-day.is-selected") || popover.querySelector(".date-time-spin-input") || popover.querySelector(".date-time-apply");
            initial?.focus({ preventScroll: true });
        }

        function commit() {
            if (kind === "time") {
                const typed = parseTypedTime(visible.value);
                if (visible.value.trim() && !typed) {
                    setError("Enter time as HH:MM in 24-hour format.");
                    visible.focus({ preventScroll: true });
                    return;
                }
                if (typed) {
                    draftHour = typed.hour;
                    draftMinute = typed.minute;
                    original.value = formatTimeValue(typed, visible.value);
                    draftSecond = parseValue(original.value, "time").second;
                }
            }
            if (kind === "date") original.value = dateValue(draftDate);
            else if (kind === "time") original.value = `${pad(draftHour)}:${pad(draftMinute)}${hasSeconds ? `:${pad(draftSecond)}` : ""}`;
            else original.value = `${dateValue(draftDate)}T${pad(draftHour)}:${pad(draftMinute)}${hasSeconds ? `:${pad(draftSecond)}` : ""}`;
            displayValue(original.value);
            original.dispatchEvent(new Event("input", { bubbles: true }));
            original.dispatchEvent(new Event("change", { bubbles: true }));
            clearError();
            close(true);
        }

        function renderCalendar() {
            const monthHeading = document.createElement("div");
            monthHeading.className = "date-time-month-heading";
            const previous = document.createElement("button");
            previous.type = "button";
            previous.className = "date-time-month-nav";
            previous.setAttribute("aria-label", "Previous month");
            previous.textContent = "‹";
            previous.addEventListener("click", () => { viewDate.setMonth(viewDate.getMonth() - 1); render(); popover.querySelector(".date-time-month-nav")?.focus(); });
            const title = document.createElement("strong");
            title.textContent = localDateLabel(viewDate, { month: "long", year: "numeric" });
            title.setAttribute("aria-live", "polite");
            const next = document.createElement("button");
            next.type = "button";
            next.className = "date-time-month-nav";
            next.setAttribute("aria-label", "Next month");
            next.textContent = "›";
            next.addEventListener("click", () => { viewDate.setMonth(viewDate.getMonth() + 1); render(); popover.querySelectorAll(".date-time-month-nav")[1]?.focus(); });
            monthHeading.append(previous, title, next);
            popover.appendChild(monthHeading);

            const calendar = document.createElement("div");
            calendar.className = "date-time-calendar";
            ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"].forEach((day) => {
                const label = document.createElement("span");
                label.className = "date-time-weekday";
                label.textContent = day;
                calendar.appendChild(label);
            });
            const first = new Date(viewDate.getFullYear(), viewDate.getMonth(), 1);
            const start = new Date(first.getFullYear(), first.getMonth(), 1 - first.getDay());
            for (let index = 0; index < 42; index++) {
                const date = new Date(start.getFullYear(), start.getMonth(), start.getDate() + index);
                const day = document.createElement("button");
                day.type = "button";
                day.className = "date-time-day";
                day.textContent = String(date.getDate());
                day.setAttribute("aria-label", localDateLabel(date, { weekday: "long", month: "long", day: "numeric", year: "numeric" }));
                const sameDate = dateValue(date) === dateValue(draftDate);
                day.setAttribute("aria-pressed", String(sameDate));
                if (date.getMonth() !== viewDate.getMonth()) day.classList.add("is-outside");
                if (sameDate) day.classList.add("is-selected");
                if (dateValue(date) === dateValue(new Date())) day.classList.add("is-today");
                day.addEventListener("click", () => {
                    draftDate = date;
                    if (kind === "date") commit();
                    else {
                        viewDate = new Date(date.getFullYear(), date.getMonth(), 1);
                        render();
                        popover.querySelector(".date-time-day.is-selected")?.focus();
                    }
                });
                calendar.appendChild(day);
            }
            popover.appendChild(calendar);
        }

        function renderTime() {
            const heading = document.createElement("div");
            heading.className = "date-time-time-heading";
            const caption = document.createElement("span");
            caption.textContent = kind === "datetime-local" ? "LOCAL TIME" : "SELECT TIME";
            const current = document.createElement("strong");
            current.textContent = `${pad(draftHour)}:${pad(draftMinute)}`;
            heading.append(caption, current);
            popover.appendChild(heading);

            const controls = document.createElement("div");
            controls.className = "date-time-spin-controls";
            const currentTime = () => { current.textContent = `${pad(draftHour)}:${pad(draftMinute)}`; };

            const makeSpinner = (unit, label, initial, maximum) => {
                const column = document.createElement("div");
                column.className = "date-time-spin-unit";
                const title = document.createElement("span");
                title.className = "date-time-spin-label";
                title.textContent = label;
                const increase = document.createElement("button");
                increase.type = "button";
                increase.className = "date-time-spin-arrow";
                increase.textContent = "⌃";
                increase.setAttribute("aria-label", `Increase ${label.toLowerCase()}`);
                const value = document.createElement("input");
                value.type = "text";
                value.className = "date-time-spin-input";
                value.inputMode = "numeric";
                value.maxLength = 2;
                value.value = pad(initial);
                value.setAttribute("role", "spinbutton");
                value.setAttribute("aria-label", label);
                value.setAttribute("aria-valuemin", "0");
                value.setAttribute("aria-valuemax", String(maximum));
                value.setAttribute("aria-valuenow", String(initial));
                const decrease = document.createElement("button");
                decrease.type = "button";
                decrease.className = "date-time-spin-arrow is-down";
                decrease.textContent = "⌄";
                decrease.setAttribute("aria-label", `Decrease ${label.toLowerCase()}`);

                const currentValue = () => unit === "hour" ? draftHour : draftMinute;
                const setValue = (next, direction, animate) => {
                    const normalized = (next + maximum + 1) % (maximum + 1);
                    if (unit === "hour") draftHour = normalized;
                    else draftMinute = normalized;
                    value.value = pad(normalized);
                    value.setAttribute("aria-valuenow", String(normalized));
                    currentTime();
                    if (kind === "time") visible.value = `${pad(draftHour)}:${pad(draftMinute)}`;
                    if (animate) {
                        value.classList.remove("tick-up", "tick-down");
                        void value.offsetWidth;
                        value.classList.add(direction > 0 ? "tick-up" : "tick-down");
                    }
                };
                increase.addEventListener("click", () => setValue(currentValue() + 1, 1, true));
                decrease.addEventListener("click", () => setValue(currentValue() - 1, -1, true));
                value.addEventListener("input", () => {
                    if (!/^\d{1,2}$/.test(value.value)) return;
                    const next = Number(value.value);
                    if (next > maximum) return;
                    if (unit === "hour") draftHour = next;
                    else draftMinute = next;
                    value.setAttribute("aria-valuenow", String(next));
                    currentTime();
                    if (kind === "time") visible.value = `${pad(draftHour)}:${pad(draftMinute)}`;
                });
                value.addEventListener("change", () => {
                    const next = Number(value.value);
                    setValue(Number.isInteger(next) && next >= 0 && next <= maximum ? next : currentValue(), 1, false);
                });
                value.addEventListener("keydown", (event) => {
                    if (event.key === "ArrowUp" || event.key === "ArrowDown") {
                        event.preventDefault();
                        setValue(currentValue() + (event.key === "ArrowUp" ? 1 : -1), event.key === "ArrowUp" ? 1 : -1, true);
                    } else if (event.key === "Enter") {
                        event.preventDefault();
                        commit();
                    }
                });
                column.append(title, increase, value, decrease);
                return column;
            };

            controls.append(makeSpinner("hour", "Hour", draftHour, 23));
            const separator = document.createElement("span");
            separator.className = "date-time-spin-separator";
            separator.textContent = ":";
            controls.append(separator, makeSpinner("minute", "Minute", draftMinute, 59));
            popover.appendChild(controls);
            const hint = document.createElement("p");
            hint.className = "date-time-picker-hint";
            hint.textContent = "Use the up/down arrows or type a value. Minutes step in single minutes.";
            popover.appendChild(hint);
        }

        function render() {
            popover.replaceChildren();
            if (kind !== "time") renderCalendar();
            if (kind !== "date") renderTime();
            const footer = document.createElement("div");
            footer.className = "date-time-footer";
            if (!required && original.value) {
                const clear = document.createElement("button");
                clear.type = "button";
                clear.className = "date-time-clear";
                clear.textContent = "Clear";
                clear.addEventListener("click", () => {
                    original.value = "";
                    displayValue("");
                    original.dispatchEvent(new Event("input", { bubbles: true }));
                    original.dispatchEvent(new Event("change", { bubbles: true }));
                    clearError();
                    close(true);
                });
                footer.appendChild(clear);
            } else {
                const spacer = document.createElement("span");
                footer.appendChild(spacer);
            }
            if (kind !== "date") {
                const apply = document.createElement("button");
                apply.type = "button";
                apply.className = "date-time-apply";
                apply.textContent = kind === "datetime-local" ? "Apply date & time" : "Set time";
                apply.addEventListener("click", commit);
                footer.appendChild(apply);
            }
            popover.appendChild(footer);
        }

        trigger.addEventListener("click", () => popover.hidden ? open() : close(false));
        visible.addEventListener("click", () => { if (kind !== "time" && popover.hidden) open(); });
        visible.addEventListener("keydown", (event) => {
            if (kind === "time" && event.key === "Enter") {
                event.preventDefault();
                if (visible.value.trim()) commit();
                else open();
            }
            else if (event.key === "Enter" || event.key === "ArrowDown") { event.preventDefault(); open(); }
            if (event.key === "Escape" && !popover.hidden) close(true);
        });
        visible.addEventListener("change", () => {
            if (kind !== "time") return;
            if (!visible.value.trim()) {
                original.value = "";
                clearError();
                original.dispatchEvent(new Event("change", { bubbles: true }));
                return;
            }
            const typed = parseTypedTime(visible.value);
            if (!typed) { setError("Enter time as HH:MM in 24-hour format."); return; }
            draftHour = typed.hour;
            draftMinute = typed.minute;
            draftSecond = typed.second;
            original.value = formatTimeValue(typed, visible.value);
            clearError();
            original.dispatchEvent(new Event("change", { bubbles: true }));
        });
        document.addEventListener("pointerdown", (event) => {
            if (!wrapper.contains(event.target) && !popover.hidden) close(false);
        });
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && !popover.hidden) close(true);
        });

        original.addEventListener("change", () => displayValue(original.value));
        original.form?.addEventListener("submit", (event) => {
            if (event.defaultPrevented) return;
            if (kind === "time" && visible.value.trim()) {
                const typed = parseTypedTime(visible.value);
                if (!typed) {
                    event.preventDefault();
                    setError("Enter time as HH:MM in 24-hour format.");
                    visible.focus({ preventScroll: true });
                    return;
                }
                original.value = formatTimeValue(typed, visible.value);
            }
            if (!required || original.value) return;
            event.preventDefault();
            setError(kind === "time" ? "Choose a time to continue." : kind === "date" ? "Choose a date to continue." : "Choose a date and time to continue.");
            visible.focus({ preventScroll: true });
            open();
        }, true);
        original.form?.addEventListener("reset", () => {
            window.setTimeout(() => {
                displayValue(original.value);
                clearError();
                close(false);
            }, 0);
        });
    }

    function init() {
        document.querySelectorAll('input[type="date"], input[type="time"], input[type="datetime-local"]').forEach(enhance);
    }
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
    else init();
})();

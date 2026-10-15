/* searchable-select.js
   Replaces every <select> with a searchable popover. The native <select> stays
   in the DOM (visually hidden) so forms, `required` validation, labels and
   other scripts that read/write `select.value` keep working.
   Opt out per select with: <select data-native>
   Script order (all with `defer`): searchable-select.js, navbar.js,
   table-pagination.js. */
(function () {
    "use strict";

    const MAX_RENDER = 150;          // cap DOM nodes per open on huge lists
    const POPOVER_HEIGHT = 260;      // approx., used to decide drop-up
    const coarsePointer = window.matchMedia("(pointer: coarse)");

    let openInstance = null;         // only one popover is ever open
    let uid = 0;

    function enhance(select) {
        if (select.multiple || select.dataset.native !== undefined) return;
        if (select.closest(".custom-select-wrapper")) return;

        const id = "cs" + ++uid;
        let optionData = [];         // [{ index, text, lower, disabled }]
        let visible = [];            // option data currently rendered
        let activeIdx = -1;          // index within `visible`

        // ---- DOM -------------------------------------------------------------
        const wrapper = document.createElement("div");
        wrapper.className = "custom-select-wrapper";
        select.parentNode.insertBefore(wrapper, select);
        wrapper.appendChild(select);

        select.classList.add("custom-select-native");
        select.tabIndex = -1;
        select.setAttribute("aria-hidden", "true");

        const trigger = document.createElement("div");
        trigger.className = "custom-select-trigger";
        trigger.tabIndex = 0;
        trigger.setAttribute("role", "combobox");
        trigger.setAttribute("aria-haspopup", "listbox");
        trigger.setAttribute("aria-expanded", "false");
        trigger.setAttribute("aria-controls", id + "-list");

        const label = select.labels && select.labels[0];
        if (label) {
            label.id = label.id || id + "-label";
            trigger.setAttribute("aria-labelledby", label.id);
        } else {
            trigger.setAttribute("aria-label", select.getAttribute("aria-label") || select.name || "Select");
        }

        const dropdown = document.createElement("div");
        dropdown.className = "custom-select-dropdown";

        const search = document.createElement("input");
        search.type = "text";
        search.className = "custom-select-search";
        search.placeholder = "Filter options...";
        search.autocomplete = "off";
        search.setAttribute("aria-label", "Filter options");
        search.setAttribute("aria-controls", id + "-list");

        const list = document.createElement("div");
        list.className = "custom-select-options";
        list.id = id + "-list";
        list.setAttribute("role", "listbox");

        dropdown.append(search, list);
        wrapper.append(trigger, dropdown);

        // ---- State sync ------------------------------------------------------
        function syncTrigger() {
            const opt = select.options[select.selectedIndex];
            trigger.textContent = opt ? opt.textContent.trim() : "Select...";
            trigger.classList.toggle("is-placeholder", !opt || opt.value === "");
            const disabled = select.disabled;
            wrapper.classList.toggle("is-disabled", disabled);
            trigger.setAttribute("aria-disabled", String(disabled));
            trigger.tabIndex = disabled ? -1 : 0;
        }

        function readOptions() {
            optionData = Array.from(select.options).map((o, index) => {
                const text = o.textContent.trim();
                return { index, text, lower: text.toLowerCase(), disabled: o.disabled };
            });
        }

        // ---- Rendering (only while open) --------------------------------------
        function render(query) {
            const q = (query || "").trim().toLowerCase();
            const matches = q ? optionData.filter((o) => o.lower.includes(q)) : optionData;
            visible = matches.slice(0, MAX_RENDER);
            activeIdx = -1;

            const frag = document.createDocumentFragment();
            visible.forEach((o, i) => {
                const el = document.createElement("div");
                el.className = "custom-select-option";
                el.id = id + "-opt-" + i;
                el.setAttribute("role", "option");
                el.dataset.pos = String(i);
                if (o.index === select.selectedIndex) {
                    el.classList.add("selected");
                    el.setAttribute("aria-selected", "true");
                }
                if (o.disabled) el.setAttribute("aria-disabled", "true");
                el.textContent = o.text;
                frag.appendChild(el);
            });

            if (matches.length === 0) {
                const none = document.createElement("div");
                none.className = "custom-select-no-results";
                none.textContent = "No matching options";
                frag.appendChild(none);
            } else if (matches.length > MAX_RENDER) {
                const hint = document.createElement("div");
                hint.className = "custom-select-hint";
                hint.textContent = "Showing first " + MAX_RENDER + " of " + matches.length + " \u2014 keep typing to narrow";
                frag.appendChild(hint);
            }

            list.replaceChildren(frag);

            // Start on the selected item (or the first match when filtering).
            const selectedPos = visible.findIndex((o) => o.index === select.selectedIndex);
            setActive(q ? firstEnabled(0, 1) : selectedPos >= 0 ? selectedPos : firstEnabled(0, 1), !q);
        }

        function firstEnabled(from, step) {
            for (let i = from; i >= 0 && i < visible.length; i += step) {
                if (!visible[i].disabled) return i;
            }
            return -1;
        }

        function setActive(pos, scroll) {
            const prev = list.children[activeIdx];
            if (prev) prev.classList.remove("is-active");
            activeIdx = pos;
            const el = list.children[pos];
            if (el && pos >= 0) {
                el.classList.add("is-active");
                search.setAttribute("aria-activedescendant", el.id);
                if (scroll) el.scrollIntoView({ block: "nearest" });
            } else {
                search.removeAttribute("aria-activedescendant");
            }
        }

        // ---- Open / close / choose ---------------------------------------------
        function open(viaKeyboard, seed) {
            if (select.disabled || openInstance === api) return;
            if (openInstance) openInstance.close();

            readOptions();
            syncTrigger();   // picks up programmatic `select.value = ...` changes

            // One layout read, before any writes, to pick the open direction.
            const rect = trigger.getBoundingClientRect();
            const below = window.innerHeight - rect.bottom;
            wrapper.classList.toggle("drop-up", below < POPOVER_HEIGHT && rect.top > below);

            if (viaKeyboard) wrapper.dataset.input = "key";   // keyboard = no animation
            else delete wrapper.dataset.input;

            search.value = seed || "";
            render(seed);
            wrapper.classList.add("open");
            trigger.setAttribute("aria-expanded", "true");
            openInstance = api;

            // Don't summon the on-screen keyboard for short lists on touch.
            if (!coarsePointer.matches || optionData.length > 10) {
                requestAnimationFrame(() => search.focus({ preventScroll: true }));
            }
        }

        function close(restoreFocus) {
            if (openInstance !== api) return;
            wrapper.classList.remove("open");
            trigger.setAttribute("aria-expanded", "false");
            openInstance = null;
            if (restoreFocus) trigger.focus({ preventScroll: true });
        }

        function choose(pos) {
            const o = visible[pos];
            if (!o || o.disabled) return;
            const changed = select.selectedIndex !== o.index;
            select.selectedIndex = o.index;
            syncTrigger();
            close(true);
            if (changed) {
                select.dispatchEvent(new Event("input", { bubbles: true }));
                select.dispatchEvent(new Event("change", { bubbles: true }));
            }
        }

        const api = { close };

        // ---- Events ------------------------------------------------------------
        trigger.addEventListener("click", () => {
            if (openInstance === api) close(false);
            else open(false);
        });

        trigger.addEventListener("keydown", (e) => {
            if (select.disabled) return;
            if (e.key === "Enter" || e.key === " " || e.key === "ArrowDown" || e.key === "ArrowUp") {
                e.preventDefault();
                open(true);
            } else if (e.key === "Escape" && openInstance === api) {
                close(false);
            } else if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
                e.preventDefault();
                open(true, e.key);   // type-to-search straight from the trigger
            }
        });

        // Delegated: one listener for every option (click, not pointerdown, so
        // scrolling the list on touch never selects by accident).
        list.addEventListener("click", (e) => {
            const el = e.target.closest(".custom-select-option");
            if (el) choose(Number(el.dataset.pos));
        });

        list.addEventListener("pointermove", (e) => {
            if (e.pointerType !== "mouse") return;
            const el = e.target.closest(".custom-select-option");
            if (el && Number(el.dataset.pos) !== activeIdx && el.getAttribute("aria-disabled") !== "true") {
                setActive(Number(el.dataset.pos), false);
            }
        });

        search.addEventListener("input", () => render(search.value));

        search.addEventListener("keydown", (e) => {
            switch (e.key) {
                case "ArrowDown": {
                    e.preventDefault();
                    const n = firstEnabled(activeIdx + 1, 1);
                    if (n >= 0) setActive(n, true);
                    break;
                }
                case "ArrowUp": {
                    e.preventDefault();
                    const p = firstEnabled(activeIdx - 1, -1);
                    if (p >= 0) setActive(p, true);
                    break;
                }
                case "Home":
                    if (e.ctrlKey) { e.preventDefault(); setActive(firstEnabled(0, 1), true); }
                    break;
                case "End":
                    if (e.ctrlKey) { e.preventDefault(); setActive(firstEnabled(visible.length - 1, -1), true); }
                    break;
                case "Enter":
                    e.preventDefault();       // never submit the form from the filter box
                    if (activeIdx >= 0) choose(activeIdx);
                    break;
                case "Escape":
                    e.preventDefault();
                    close(true);
                    break;
                case "Tab":
                    close(false);
                    break;
            }
        });

        // Label clicks and programmatic focus land on the hidden select.
        select.addEventListener("focus", () => trigger.focus({ preventScroll: true }));

        // Keep the trigger in sync when other code changes the select.
        select.addEventListener("change", syncTrigger);
        if (select.form) {
            select.form.addEventListener("reset", () => setTimeout(syncTrigger, 0));
        }
        new MutationObserver(syncTrigger).observe(select, {
            childList: true, subtree: true, attributes: true, attributeFilter: ["disabled", "selected"]
        });

        syncTrigger();
    }

    // One global outside-press listener (not one per select).
    document.addEventListener("pointerdown", (e) => {
        if (openInstance && !e.target.closest(".custom-select-wrapper.open")) openInstance.close(false);
    });

    function init() {
        document.querySelectorAll("select").forEach(enhance);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
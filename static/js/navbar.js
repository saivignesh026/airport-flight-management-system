/* navbar.js
   Theme toggle, active links, scroll shadow, mobile menu, split-view upgrade.
   Script order (all with `defer`): searchable-select.js, navbar.js,
   table-pagination.js (pagination LAST). */
(function () {
    "use strict";

    const root = document.documentElement;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const mobileMq = window.matchMedia("(max-width: 768px)");
    const THEME_KEY = "theme";

    function storedTheme() {
        try { return localStorage.getItem(THEME_KEY); } catch (e) { return null; }
    }

    // --- 1. Dark / light mode -------------------------------------------------
    function initTheme() {
        const btn = document.getElementById("theme-toggle");
        const systemDark = window.matchMedia("(prefers-color-scheme: dark)");
        const isDark = () => root.classList.contains("dark-mode");
        const setDark = (dark) => {
            root.classList.toggle("dark-mode", dark);
            if (btn) {
                btn.setAttribute("aria-pressed", String(dark));
                btn.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
            }
        };

        // Safety net if theme-init.js was not added to <head> (idempotent).
        const saved = storedTheme();
        setDark(saved ? saved === "dark" : systemDark.matches);

        if (btn) {
            btn.addEventListener("click", () => {
                const next = !isDark();
                try { localStorage.setItem(THEME_KEY, next ? "dark" : "light"); } catch (e) { /* ignore */ }

                // Swap the theme in one paint. View Transitions can briefly
                // composite a white snapshot while moving into warm light mode.
                setDark(next);
            });
        }

        // Follow the OS only while the user hasn't chosen explicitly.
        systemDark.addEventListener("change", (e) => {
            if (!storedTheme()) setDark(e.matches);
        });
    }

    // --- 2. Active navigation -------------------------------------------------
    function initActiveLinks() {
        const navLinks = document.querySelector(".nav-links");
        if (!navLinks) return;

        const normalize = (p) => {
            const s = p.toLowerCase().replace(/\/+$/, "");
            return s === "" ? "/" : s;
        };
        const current = normalize(window.location.pathname);
        const matches = (linkPath) =>
            current === linkPath || (linkPath !== "/" && current.startsWith(linkPath + "/"));

        document.querySelectorAll(".nav-item").forEach((el) => {
            el.classList.remove("active");
            el.removeAttribute("aria-current");
        });

        navLinks.querySelectorAll("a.nav-item").forEach((link) => {
            const href = link.getAttribute("href");
            if (!href || href.startsWith("#")) return;
            if (current === normalize(link.pathname)) {
                link.classList.add("active");
                link.setAttribute("aria-current", "page");
            }
        });

        document.querySelectorAll(".dropdown-content a").forEach((link) => {
            const href = link.getAttribute("href");
            if (!href || href.startsWith("#")) return;
            if (matches(normalize(link.pathname))) {
                link.classList.add("active");
                link.setAttribute("aria-current", "page");
                const parentBtn = link.closest(".dropdown")?.querySelector(".dropbtn");
                if (parentBtn) parentBtn.classList.add("active");
            }
        });
    }

    // --- 3. Scroll shadow -----------------------------------------------------
    // IntersectionObserver on a 1px sentinel at the top of the page: zero
    // scroll listeners, and the class only changes when the state flips.
    function initScrollShadow() {
        const navbar = document.querySelector(".navbar");
        if (!navbar || !("IntersectionObserver" in window)) return;

        const sentinel = document.createElement("div");
        sentinel.setAttribute("aria-hidden", "true");
        sentinel.style.cssText =
            "position:absolute;top:0;left:0;width:1px;height:8px;pointer-events:none;visibility:hidden";
        document.body.prepend(sentinel);

        new IntersectionObserver(([entry]) => {
            navbar.classList.toggle("navbar-scrolled", !entry.isIntersecting);
        }).observe(sentinel);
    }

    // A slim progress rail gives long operations pages a quiet film-timeline cue.
    function initScrollProgress() {
        const rail = document.createElement("div");
        rail.className = "scroll-cinema-rail";
        rail.setAttribute("aria-hidden", "true");
        document.body.appendChild(rail);
        let queued = false;
        const paint = () => {
            const range = document.documentElement.scrollHeight - window.innerHeight;
            const progress = range > 0 ? window.scrollY / range : 0;
            rail.style.transform = `scaleX(${Math.min(1, Math.max(0, progress))})`;
            queued = false;
        };
        window.addEventListener("scroll", () => {
            if (queued) return;
            queued = true;
            window.requestAnimationFrame(paint);
        }, { passive: true });
        paint();
    }

    // --- 4. Mobile hamburger menu ----------------------------------------------
    function initMobileMenu() {
        const navContainer = document.querySelector(".nav-container");
        const navLinks = document.querySelector(".nav-links");
        if (!navContainer || !navLinks) return;

        navLinks.id = navLinks.id || "primary-nav";

        const toggleBtn = document.createElement("button");
        toggleBtn.type = "button";
        toggleBtn.className = "nav-toggle-btn";
        toggleBtn.setAttribute("aria-label", "Toggle navigation");
        toggleBtn.setAttribute("aria-controls", navLinks.id);
        toggleBtn.setAttribute("aria-expanded", "false");
        toggleBtn.innerHTML =
            '<span class="hamburger-bar"></span><span class="hamburger-bar"></span><span class="hamburger-bar"></span>';
        navContainer.appendChild(toggleBtn);

        const setOpen = (open) => {
            navLinks.classList.toggle("nav-open", open);
            toggleBtn.classList.toggle("is-active", open);
            toggleBtn.setAttribute("aria-expanded", String(open));
        };
        const isOpen = () => navLinks.classList.contains("nav-open");

        toggleBtn.addEventListener("click", () => setOpen(!isOpen()));

        // Close on outside press, Escape, or when growing past the breakpoint.
        document.addEventListener("pointerdown", (e) => {
            if (isOpen() && !navContainer.contains(e.target)) setOpen(false);
        });
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && isOpen()) {
                setOpen(false);
                toggleBtn.focus();
            }
        });
        mobileMq.addEventListener("change", (e) => { if (!e.matches) setOpen(false); });

        // Sub-menus inside the mobile panel (matchMedia: no layout read).
        document.querySelectorAll(".dropbtn").forEach((btn) => {
            const dropdown = btn.closest(".dropdown");
            dropdown.addEventListener("pointerenter", () => {
                if (!mobileMq.matches) btn.setAttribute("aria-expanded", "true");
            });
            dropdown.addEventListener("pointerleave", () => {
                if (!mobileMq.matches) btn.setAttribute("aria-expanded", "false");
            });
            dropdown.addEventListener("focusin", () => btn.setAttribute("aria-expanded", "true"));
            dropdown.addEventListener("focusout", () => {
                window.setTimeout(() => {
                    if (!dropdown.contains(document.activeElement)) btn.setAttribute("aria-expanded", "false");
                }, 0);
            });
            btn.addEventListener("click", (e) => {
                if (!mobileMq.matches) return;
                e.preventDefault();
                const open = btn.parentElement.classList.toggle("active-mobile");
                btn.setAttribute("aria-expanded", String(open));
            });
        });
    }

    // --- 5. Auto-upgrade CRUD pages into a split view --------------------------
    // All moves happen into detached panes, and the wrapper is attached once,
    // so the browser lays the page out a single time.
    function initSplitLayout() {
        const main = document.querySelector("main.main-container");
        if (!main || main.querySelector(".dashboard-wrapper") || main.querySelector(".stats-grid")) return;

        const headings = Array.from(main.querySelectorAll(":scope > h1, :scope > div > h1"));
        const tables = main.querySelectorAll("table");
        const addForms = Array.from(main.querySelectorAll("form"))
            .filter((f) => !f.closest("td") && f.method.toLowerCase() === "post");

        if (tables.length !== 1 || addForms.length !== 1 || headings.length < 2) return;

        const form = addForms[0];
        const secondHeading = headings[1];
        const formDiv = form.closest("div");
        // Move the form's wrapper div only if it lives inside <main>, isn't the
        // first child, and doesn't also contain the table.
        const formTarget =
            formDiv && main.contains(formDiv) && formDiv !== main.firstElementChild && !formDiv.contains(tables[0])
                ? formDiv
                : form;

        const wrapper = document.createElement("div");
        wrapper.className = "dashboard-wrapper";
        if (tables[0].classList.contains("flight-schedule-table")) {
            wrapper.classList.add("schedule-wide");
        }
        const leftPane = document.createElement("div");
        leftPane.className = "split-table-pane";
        const rightPane = document.createElement("div");
        rightPane.className = "split-form-pane";

        const originalChildren = Array.from(main.children);
        rightPane.append(secondHeading, formTarget);
        originalChildren.forEach((child) => {
            if (child.parentNode === main) leftPane.appendChild(child);
        });

        wrapper.append(leftPane, rightPane);
        main.appendChild(wrapper);
    }

    // --- 6. Page identity and scroll reveals ---------------------------------
    function initPageExperience() {
        const main = document.querySelector("main.main-container");
        if (!main || main.querySelector(".ops-hero") || main.querySelector(".page-hero")) return;

        const split = main.querySelector(".dashboard-wrapper");
        const heading = split
            ? split.querySelector(".split-table-pane h1")
            : main.querySelector(":scope > h1");
        if (!heading) return;

        const path = window.location.pathname.toLowerCase();
        const identity = path.includes("manifest")
            ? { label: "PASSENGER SERVICES", icon: "manifest", tone: "coral", stamp: "JOURNEYS", index: "04", note: "Passenger manifest and flight assignments." }
            : path.includes("booking")
                ? { label: "PASSENGER SERVICES", icon: "ticket", tone: "coral", stamp: "JOURNEYS", index: "04", note: "Bookings, payment, check-in and baggage." }
                : path.includes("passenger")
                    ? { label: "PASSENGER SERVICES", icon: "passenger", tone: "coral", stamp: "JOURNEYS", index: "04", note: "Passenger records and traveler details." }
                    : path.includes("employee")
                        ? { label: "PEOPLE & ADMINISTRATION", icon: "staff", tone: "violet", stamp: "AIRPORT TEAM", index: "05", note: "Staff records and airport assignments." }
                        : path.includes("department")
                            ? { label: "PEOPLE & ADMINISTRATION", icon: "department", tone: "violet", stamp: "AIRPORT TEAM", index: "05", note: "Departments and operational teams." }
                            : path.includes("role")
                                ? { label: "PEOPLE & ADMINISTRATION", icon: "role", tone: "violet", stamp: "AIRPORT TEAM", index: "05", note: "Roles and access responsibilities." }
                                : path.includes("terminal")
                                    ? { label: "AIRPORT INFRASTRUCTURE", icon: "terminal", tone: "cyan", stamp: "AIRFIELD", index: "03", note: "Terminal locations and service status." }
                                    : path.includes("gate")
                                        ? { label: "AIRPORT INFRASTRUCTURE", icon: "gate", tone: "cyan", stamp: "AIRFIELD", index: "03", note: "Gate assignments and availability." }
                                        : path.includes("runway")
                                            ? { label: "AIRPORT INFRASTRUCTURE", icon: "runway", tone: "cyan", stamp: "AIRFIELD", index: "03", note: "Runway specifications and operational status." }
                                            : path.includes("airport")
                                                ? { label: "AIRPORT INFRASTRUCTURE", icon: "airport", tone: "cyan", stamp: "AIRFIELD", index: "03", note: "Airport locations and network details." }
                                                : path.includes("airline")
                                                    ? { label: "FLEET & CARRIERS", icon: "globe", tone: "blue", stamp: "FLEET", index: "02", note: "Carrier records and airline details." }
                                                    : path.includes("aircraft")
                                                        ? { label: "FLEET & CARRIERS", icon: "plane", tone: "blue", stamp: "FLEET", index: "02", note: "Aircraft records, capacity and fleet details." }
                                                        : path.includes("instance")
                                                            ? { label: "FLIGHT OPERATIONS", icon: "calendar", tone: "blue", stamp: "SCHEDULE", index: "01", note: "Scheduled services, gates and flight status." }
                                                            : { label: "FLIGHT OPERATIONS", icon: "route", tone: "blue", stamp: "SCHEDULE", index: "01", note: "Routes, origins and destinations." };
        const hero = document.createElement("section");
        hero.className = `page-hero page-hero-${identity.tone}`;
        hero.innerHTML = `<div class="page-hero-copy"><span class="page-hero-kicker"><i></i>${identity.label} <span class="hero-separator">/</span> OPERATIONS DESK</span><div class="page-hero-title"></div><p>${identity.note}</p></div><div class="page-hero-visual" aria-hidden="true"><span class="page-hero-orbit orbit-a"></span><span class="page-hero-orbit orbit-b"></span><span class="page-hero-glyph"><svg class="ui-icon"><use href="#icon-${identity.icon}"></use></svg></span><span class="page-hero-code">${identity.stamp}<br><b>${identity.index}</b></span></div>`;
        hero.querySelector(".page-hero-title").appendChild(heading);
        if (split) main.insertBefore(hero, split);
        else main.insertBefore(hero, main.firstChild);

        const revealItems = main.querySelectorAll(
            ".stat-card, .ops-table-wrap, .table-container, .dashboard-wrapper, .form-container, main > form, main > table, .flight-dashboard, .detail-panel"
        );
        if (reduceMotion.matches || !("IntersectionObserver" in window)) return;
        const observer = new IntersectionObserver((entries, io) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                entry.target.classList.add("is-revealed");
                io.unobserve(entry.target);
            });
        }, { threshold: 0.08, rootMargin: "0px 0px -24px 0px" });
        revealItems.forEach((item, index) => {
            item.classList.add("reveal-on-scroll");
            item.style.setProperty("--reveal-delay", `${Math.min(index % 6, 5) * 55}ms`);
            observer.observe(item);
        });
    }

    // Associate the older label/control markup and surface native validation
    // messages inline, including controls enhanced by searchable-select.js.
    function initForms() {
        let controlIndex = 0;
        document.querySelectorAll("form").forEach((form) => {
            const labels = Array.from(form.querySelectorAll("label"));
            labels.forEach((label) => {
                let control = label.htmlFor ? document.getElementById(label.htmlFor) : null;
                if (!control) {
                    let next = label.nextElementSibling;
                    while (next && next.tagName === "BR") next = next.nextElementSibling;
                    if (next?.classList.contains("date-time-picker")) control = next.querySelector(".date-time-picker-input");
                    else if (next?.classList.contains("custom-select-wrapper")) control = next.querySelector("select");
                    else if (next && /^(INPUT|SELECT|TEXTAREA)$/.test(next.tagName)) control = next;
                }
                if (!control || !form.contains(control)) return;
                if (!control.id) control.id = `form-control-${++controlIndex}`;
                if (label.htmlFor !== control.id) label.htmlFor = control.id;
                if (control.required || control.closest(".date-time-picker")?.dataset.required === "true") label.classList.add("is-required");
            });

            const showError = (control) => {
                if (control.validity.valid) return;
                form.classList.add("form-validation-attempted");
                control.setAttribute("aria-invalid", "true");
                const errorId = `${control.id}-error`;
                let error = form.querySelector(`#${CSS.escape(errorId)}`);
                if (!error) {
                    error = document.createElement("span");
                    error.id = errorId;
                    error.className = "field-error";
                    const wrapper = control.closest(".custom-select-wrapper");
                    (wrapper || control).insertAdjacentElement("afterend", error);
                }
                error.textContent = control.validationMessage || "Check this field.";
                const describedBy = new Set((control.getAttribute("aria-describedby") || "").split(/\s+/).filter(Boolean));
                describedBy.add(errorId);
                control.setAttribute("aria-describedby", Array.from(describedBy).join(" "));
            };
            const clearError = (control) => {
                if (!control.validity.valid) return;
                control.removeAttribute("aria-invalid");
                const errorId = `${control.id}-error`;
                form.querySelector(`#${CSS.escape(errorId)}`)?.remove();
                const describedBy = (control.getAttribute("aria-describedby") || "").split(/\s+/).filter((id) => id && id !== errorId);
                if (describedBy.length) control.setAttribute("aria-describedby", describedBy.join(" "));
                else control.removeAttribute("aria-describedby");
            };

            form.addEventListener("invalid", (event) => showError(event.target), true);
            form.addEventListener("input", (event) => {
                if (/^(INPUT|SELECT|TEXTAREA)$/.test(event.target.tagName)) clearError(event.target);
            });
            form.addEventListener("change", (event) => {
                if (/^(INPUT|SELECT|TEXTAREA)$/.test(event.target.tagName)) clearError(event.target);
            });
            form.addEventListener("reset", () => {
                form.classList.remove("form-validation-attempted");
                form.querySelectorAll("[aria-invalid='true']").forEach(clearError);
            });
            form.addEventListener("submit", (event) => {
                if (event.defaultPrevented) return;
                const button = form.querySelector("button[type='submit'].btn-submit, input[type='submit'].btn-submit");
                if (!button) return;
                button.classList.add("is-submitting");
                button.setAttribute("aria-busy", "true");
                button.disabled = true;
            });
        });

        document.querySelectorAll("[data-operational-date]").forEach((time) => {
            const raw = time.getAttribute("datetime") || time.textContent.trim();
            const parsed = new Date(raw.replace(" ", "T"));
            if (Number.isNaN(parsed.getTime())) return;
            time.dateTime = parsed.toISOString();
            time.textContent = new Intl.DateTimeFormat(undefined, {
                month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
            }).format(parsed);
        });
    }

    function init() {
        initTheme();
        initActiveLinks();
        initScrollShadow();
        initScrollProgress();
        initMobileMenu();
        initSplitLayout();
        initPageExperience();
        initForms();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();

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
            if (btn) btn.setAttribute("aria-pressed", String(dark));
        };

        // Safety net if theme-init.js was not added to <head> (idempotent).
        const saved = storedTheme();
        setDark(saved ? saved === "dark" : systemDark.matches);

        if (btn) {
            btn.addEventListener("click", () => {
                const next = !isDark();
                try { localStorage.setItem(THEME_KEY, next ? "dark" : "light"); } catch (e) { /* ignore */ }

                // Rare action, so a short crossfade is fine. The browser
                // snapshots the page and fades it on the GPU, which is far
                // cheaper than transitioning colours on every element.
                if (document.startViewTransition && !reduceMotion.matches) {
                    document.startViewTransition(() => setDark(next));
                } else {
                    setDark(next);
                }
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

    function init() {
        initTheme();
        initActiveLinks();
        initScrollShadow();
        initMobileMenu();
        initSplitLayout();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
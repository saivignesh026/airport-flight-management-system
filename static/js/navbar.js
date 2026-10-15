document.addEventListener("DOMContentLoaded", function () {
    // --- 1. Dark/Light Mode Logic ---
    const themeToggle = document.getElementById("theme-toggle");
    const iconMoon = document.querySelector(".icon-moon");
    const iconSun = document.querySelector(".icon-sun");

    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
        if (iconMoon && iconSun) {
            iconMoon.style.display = "none";
            iconSun.style.display = "inline-block";
        }
    }

    if (themeToggle) {
        themeToggle.addEventListener("click", () => {
            document.body.classList.toggle("dark-mode");
            const isDark = document.body.classList.contains("dark-mode");
            localStorage.setItem("theme", isDark ? "dark" : "light");
            if (iconMoon && iconSun) {
                iconMoon.style.display = isDark ? "none" : "inline-block";
                iconSun.style.display = isDark ? "inline-block" : "none";
            }
        });
    }

    // --- 2. Active Navigation & Scroll Depth ---
    const navbar = document.querySelector(".navbar");
    const navLinksContainer = document.querySelector(".nav-links");
    const currentPath = window.location.pathname.toLowerCase();

    if (navLinksContainer) {
        document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));

        navLinksContainer.querySelectorAll("a.nav-item").forEach(link => {
            if (currentPath === link.getAttribute("href").toLowerCase()) {
                link.classList.add("active");
            }
        });

        document.querySelectorAll(".dropdown-content a").forEach(link => {
            const linkHref = link.getAttribute("href").toLowerCase();
            if (currentPath === linkHref || (linkHref !== "/" && currentPath.startsWith(linkHref))) {
                link.classList.add("active");
                const parentBtn = link.closest(".dropdown")?.querySelector(".dropbtn");
                if (parentBtn) parentBtn.classList.add("active");
            }
        });
    }

    window.addEventListener("scroll", function () {
        if (!navbar) return;
        navbar.classList.toggle("navbar-scrolled", window.scrollY > 8);
    }, { passive: true });

    // --- 3. Mobile Hamburger Menu ---
    const navContainer = document.querySelector(".nav-container");
    if (navContainer && navLinksContainer) {
        const toggleBtn = document.createElement("button");
        toggleBtn.className = "nav-toggle-btn";
        toggleBtn.setAttribute("aria-label", "Toggle navigation");
        toggleBtn.innerHTML = `
            <span class="hamburger-bar"></span>
            <span class="hamburger-bar"></span>
            <span class="hamburger-bar"></span>
        `;
        navContainer.appendChild(toggleBtn);

        toggleBtn.addEventListener("click", function () {
            navLinksContainer.classList.toggle("nav-open");
            toggleBtn.classList.toggle("is-active");
        });

        document.querySelectorAll(".dropbtn").forEach(btn => {
            btn.addEventListener("click", e => {
                if (window.innerWidth <= 768) {
                    e.preventDefault();
                    btn.parentElement.classList.toggle("active-mobile");
                }
            });
        });
    }

    // --- 4. Auto-Upgrade CRUD Pages into Side-by-Side Split View ---
    const main = document.querySelector("main.main-container");
    if (main && !main.querySelector(".dashboard-wrapper") && !main.querySelector(".stats-grid")) {
        const headings = Array.from(main.querySelectorAll(":scope > h1, :scope > div > h1"));
        const tables = main.querySelectorAll("table");
        const addForms = Array.from(main.querySelectorAll("form")).filter(f => !f.closest("td") && f.method.toLowerCase() === "post");

        if (tables.length === 1 && addForms.length === 1 && headings.length >= 2) {
            const wrapper = document.createElement("div");
            wrapper.className = "dashboard-wrapper";

            const leftPane = document.createElement("div");
            leftPane.className = "split-table-pane";

            const rightPane = document.createElement("div");
            rightPane.className = "split-form-pane";

            const secondHeading = headings[1];
            const formTarget = addForms[0].closest("div:not(.main-container)") && addForms[0].closest("div") !== main.firstElementChild
                ? addForms[0].closest("div")
                : addForms[0];

            // Move elements smoothly into Left (Table) and Right (Add Form) panes
            secondHeading.parentNode.insertBefore(wrapper, secondHeading);
            rightPane.appendChild(secondHeading);
            rightPane.appendChild(formTarget);

            Array.from(main.children).forEach(child => {
                if (child !== wrapper) {
                    leftPane.appendChild(child);
                }
            });

            wrapper.appendChild(leftPane);
            wrapper.appendChild(rightPane);
        }
    }

    // --- 5. Semantic Status Pills for Operational Clarity ---
    const statusMap = {
        "active": "status-success",
        "open": "status-success",
        "operational": "status-success",
        "on time": "status-success",
        "confirmed": "status-success",
        "payment received": "status-success",
        "checked-in": "status-success",
        "boarded": "status-success",
        "claimed": "status-success",
        "arrived": "status-success",

        "scheduled": "status-info",
        "boarding": "status-info",
        "departed": "status-info",
        "loaded": "status-info",
        "screened": "status-info",
        "sorted": "status-info",
        "in-transit": "status-info",

        "delayed": "status-warning",
        "maintenance": "status-warning",
        "under construction": "status-warning",
        "on leave": "status-warning",
        "pending": "status-warning",
        "not boarded": "status-warning",

        "cancelled": "status-danger",
        "closed": "status-danger",
        "inactive": "status-danger",
        "resigned": "status-danger",
        "failed": "status-danger",
        "lost": "status-danger",
        "no show": "status-danger"
    };

    document.querySelectorAll("td").forEach(td => {
        if (td.children.length === 0) {
            const raw = td.textContent.trim();
            const key = raw.toLowerCase();
            if (statusMap[key]) {
                td.innerHTML = `<span class="status-pill ${statusMap[key]}">${raw}</span>`;
            }
        }
    });
});
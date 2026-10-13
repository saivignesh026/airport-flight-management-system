document.addEventListener("DOMContentLoaded", function () {
    const navbar = document.querySelector(".navbar");
    const navLinksContainer = document.querySelector(".nav-links");
    const currentPath = window.location.pathname.toLowerCase();

    // 1. Highlight active navigation item and parent dropdowns
    if (navLinksContainer) {
        // Clear all active states first
        document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
        
        // Handle standalone links (like Home)
        const topLinks = navLinksContainer.querySelectorAll("a.nav-item");
        topLinks.forEach((link) => {
            const linkHref = link.getAttribute("href").toLowerCase();
            if (currentPath === linkHref) {
                link.classList.add("active");
            }
        });

        // Handle dropdown links
        const dropdownLinks = document.querySelectorAll(".dropdown-content a");
        dropdownLinks.forEach((link) => {
            const linkHref = link.getAttribute("href").toLowerCase();
            // Match exact path or sub-routes (e.g. /Aircraft/update/1 matches /Aircraft)
            if (currentPath === linkHref || (linkHref !== "/" && currentPath.startsWith(linkHref))) {
                link.classList.add("active");
                // Highlight the parent dropdown button
                const parentDropdownBtn = link.closest('.dropdown').querySelector('.dropbtn');
                if (parentDropdownBtn) {
                    parentDropdownBtn.classList.add('active');
                }
            }
        });
    }

    // 2. Add an elevation shadow when scrolling down
    window.addEventListener("scroll", function () {
        if (window.scrollY > 10) {
            navbar.classList.add("navbar-scrolled");
        } else {
            navbar.classList.remove("navbar-scrolled");
        }
    });

    // 3. Responsive hamburger menu toggle for mobile devices
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
        
        // Toggle dropdowns on mobile click
        const dropBtns = document.querySelectorAll('.dropbtn');
        dropBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                if(window.innerWidth <= 768) {
                    e.preventDefault();
                    btn.parentElement.classList.toggle('active-mobile');
                }
            });
        });
    }
});
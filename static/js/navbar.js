document.addEventListener("DOMContentLoaded", function () {
    // --- Dark/Light Mode Logic ---
    const themeToggle = document.getElementById('theme-toggle');
    const iconMoon = document.querySelector('.icon-moon');
    const iconSun = document.querySelector('.icon-sun');

    // Check local storage for saved theme
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
        if (iconMoon && iconSun) {
            iconMoon.style.display = 'none';
            iconSun.style.display = 'inline-block';
        }
    }

    // Toggle Theme on click
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            
            if (document.body.classList.contains('dark-mode')) {
                localStorage.setItem('theme', 'dark');
                iconMoon.style.display = 'none';
                iconSun.style.display = 'inline-block';
            } else {
                localStorage.setItem('theme', 'light');
                iconMoon.style.display = 'inline-block';
                iconSun.style.display = 'none';
            }
        });
    }

    // --- Navigation Logic ---
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
            if (currentPath === linkHref || (linkHref !== "/" && currentPath.startsWith(linkHref))) {
                link.classList.add("active");
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
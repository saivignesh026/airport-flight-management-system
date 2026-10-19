/* theme-init.js
   Load this in <head> as a plain <script src="..."></script> (no defer/async).
   It sets the theme class on <html> before the first paint, so dark-mode users
   never see a white flash. Falls back to the OS setting when the user has not
   picked a theme yet. */
(function () {
    try {
        var saved = localStorage.getItem("theme");
        var dark = saved
            ? saved === "dark"
            : window.matchMedia("(prefers-color-scheme: dark)").matches;
        if (dark) document.documentElement.classList.add("dark-mode");
    } catch (e) { /* storage blocked: stay on light */ }
})();
/* Visual navigation feedback only: links and forms keep native browser behavior. */
(() => {
    const root = document.documentElement;
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    let resetTimer;

    function reset() {
        clearTimeout(resetTimer);
        root.classList.remove('page-navigating');
    }

    function showProgress() {
        if (reducedMotion.matches) return;
        root.classList.add('page-navigating');
        clearTimeout(resetTimer);
        // A cancelled or failed navigation must never leave feedback stuck.
        resetTimer = setTimeout(reset, 8000);
    }

    // Run in the head so a native transition can suppress the fallback entrance.
    window.addEventListener('pagereveal', (event) => {
        if (!event.viewTransition) return;
        root.classList.add('native-page-transition');
        event.viewTransition.finished.then(reset, reset);
    });
    window.addEventListener('pageshow', () => {
        clearTimeout(resetTimer);
        root.classList.remove('page-navigating');
    });
    reducedMotion.addEventListener('change', reset);

    document.addEventListener('click', (event) => {
        if (event.defaultPrevented || event.button !== 0 || event.metaKey ||
            event.ctrlKey || event.shiftKey || event.altKey) return;
        const link = event.target.closest('a[href]');
        if (!link || link.hasAttribute('download') ||
            (link.target && link.target !== '_self')) return;
        const url = new URL(link.href, location.href);
        if (url.origin !== location.origin || !/^https?:$/.test(url.protocol)) return;
        // In-page anchors do not load another document.
        if (url.pathname === location.pathname && url.search === location.search && url.hash) return;
        queueMicrotask(() => { if (!event.defaultPrevented) showProgress(); });
    });
    document.addEventListener('submit', (event) => {
        const form = event.target;
        const target = event.submitter?.formTarget || form.target;
        const action = event.submitter?.formAction || form.action;
        if ((target && target !== '_self') || form.method === 'dialog' ||
            new URL(action, location.href).origin !== location.origin) return;
        queueMicrotask(() => { if (!event.defaultPrevented) showProgress(); });
    });
})();

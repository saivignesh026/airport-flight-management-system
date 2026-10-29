/* table-pagination.js
   Search + pagination + status pills for every <table>.
   Opt out per table with: <table data-no-paginate>

   Performance model: only the current page's rows (max ROWS_PER_PAGE) are ever
   attached to the DOM. Filtering runs against text cached once at start-up.
   Script order (all with `defer`): this file must be LAST, because it detaches
   rows and earlier scripts need to see the whole page first. */
(function () {
    "use strict";

    const ROWS_PER_PAGE = 6;

    // Map (not an object) so text like "constructor" can never match.
    const STATUS = new Map([
        ["active", "status-success"], ["open", "status-success"], ["operational", "status-success"],
        ["on time", "status-success"], ["confirmed", "status-success"], ["payment received", "status-success"],
        ["checked-in", "status-success"], ["boarded", "status-success"], ["claimed", "status-success"],
        ["arrived", "status-success"],
        ["refunded", "status-info"],

        ["scheduled", "status-info"], ["boarding", "status-info"], ["departed", "status-info"],
        ["loaded", "status-info"], ["screened", "status-info"], ["sorted", "status-info"],
        ["in-transit", "status-info"],

        ["delayed", "status-warning"], ["maintenance", "status-warning"], ["under construction", "status-warning"],
        ["on leave", "status-warning"], ["pending", "status-warning"], ["not boarded", "status-warning"],

        ["cancelled", "status-danger"], ["closed", "status-danger"], ["inactive", "status-danger"],
        ["resigned", "status-danger"], ["failed", "status-danger"], ["lost", "status-danger"],
        ["no show", "status-danger"], ["unloaded", "status-info"]
    ]);

    // Plain text cells whose whole content is a known status become pills.
    // Built with createElement/textContent (never innerHTML) so cell text can't
    // be re-parsed as markup.
    function decorateStatus(row) {
        for (const td of row.cells) {
            if (td.childElementCount) continue;
            const raw = td.textContent.trim();
            const cls = STATUS.get(raw.toLowerCase());
            if (!cls) continue;
            const pill = document.createElement("span");
            pill.className = "status-pill " + cls;
            pill.textContent = raw;
            td.replaceChildren(pill);
        }
    }

    function enhance(table) {
        if (table.dataset.noPaginate !== undefined) return null;

        // Ensure header rows (<tr> with <th>) live in <thead> so swapping
        // rows in <tbody> never wipes them out.
        const headerRows = Array.from(table.rows).filter(
            (tr) =>
                tr.parentNode.tagName !== "THEAD" &&
                tr.parentNode.tagName !== "TFOOT" &&
                !tr.querySelector(":scope > td")
        );
        if (headerRows.length) {
            const thead = table.tHead || table.createTHead();
            headerRows.forEach((tr) => thead.appendChild(tr));
        }

        const rows = Array.from(table.rows).filter(
            (tr) => tr.parentNode.tagName !== "TFOOT" && tr.querySelector(":scope > td") && !tr.querySelector(":scope > td.table-empty")
        );

        // Pills first, then cache searchable text (once, not per keystroke).
        rows.forEach(decorateStatus);
        let entries = rows.map((row, originalIndex) => ({
            row,
            originalIndex,
            text: row.textContent.replace(/\s+/g, " ").toLowerCase()
        }));

        let filtered = entries;
        let page = 1;

        // ---- Chrome ---------------------------------------------------------
        let container = table.parentElement;
        if (!container.classList.contains("table-container")) {
            container = document.createElement("div");
            container.className = "table-container";
            table.parentNode.insertBefore(container, table);
            container.appendChild(table);
        }

        const searchBar = document.createElement("div");
        searchBar.className = "table-search-container";
        searchBar.innerHTML =
            '<span class="page-info table-count-badge" aria-live="polite"></span>' +
            '<input type="text" class="table-search-input" placeholder="Search table..." ' +
            'aria-label="Search table" autocomplete="off">' +
            '<button type="button" class="table-search-clear" aria-label="Clear table search" hidden>Clear</button>';
        container.insertBefore(searchBar, table);

        const countBadge = searchBar.querySelector(".table-count-badge");
        const searchInput = searchBar.querySelector(".table-search-input");
        const clearSearch = searchBar.querySelector(".table-search-clear");

        const sortableHeaders = Array.from((table.tHead || table).querySelectorAll("th")).filter((th) => {
            const label = th.textContent.trim().toLowerCase();
            return label && !/^(action|actions|edit|delete)$/.test(label);
        });
        let sortColumn = -1;
        let sortDirection = 1;
        const collator = new Intl.Collator(undefined, { numeric: true, sensitivity: "base" });
        sortableHeaders.forEach((th) => {
            th.tabIndex = 0;
            th.setAttribute("aria-sort", "none");
            th.setAttribute("data-sortable", "true");
            th.title = "Sort by " + th.textContent.trim();
        });

        const nav = document.createElement("div");
        nav.className = "pagination-controls";
        nav.innerHTML =
            '<span class="page-info" aria-live="polite"></span>' +
            '<div class="pagination-buttons">' +
            '<button type="button" class="page-btn btn-prev">\u2190 Previous</button>' +
            '<button type="button" class="page-btn btn-next">Next \u2192</button>' +
            "</div>";
        container.parentNode.insertBefore(nav, container.nextSibling);

        const pageInfo = nav.querySelector(".page-info");
        const prevBtn = nav.querySelector(".btn-prev");
        const nextBtn = nav.querySelector(".btn-next");

        // ---- Row host + empty state -------------------------------------------
        const host = rows.length ? rows[0].parentNode : (table.tBodies[0] || table.createTBody());
        const singleHost = rows.every((r) => r.parentNode === host);

        const emptyRow = document.createElement("tr");
        const emptyCell = document.createElement("td");
        emptyCell.className = "table-empty";
        emptyCell.colSpan =
            (table.tHead && table.tHead.rows[0] && table.tHead.rows[0].cells.length) ||
            (rows[0] && rows[0].cells.length) || 1;
        emptyCell.textContent = rows.length ? "No matches. Try a different search." : "No records to display yet.";
        emptyRow.appendChild(emptyCell);
        if (!singleHost) { emptyRow.hidden = true; host.appendChild(emptyRow); }

        // ---- Render -----------------------------------------------------------
        function render() {
            const totalPages = Math.max(1, Math.ceil(filtered.length / ROWS_PER_PAGE));
            page = Math.min(Math.max(page, 1), totalPages);

            const start = (page - 1) * ROWS_PER_PAGE;
            const slice = filtered.slice(start, start + ROWS_PER_PAGE).map((e) => e.row);

            if (singleHost) {
                // Swap the whole page in one DOM operation.
                host.replaceChildren(...(slice.length ? slice : [emptyRow]));
            } else {
                const show = new Set(slice);
                rows.forEach((r) => { r.hidden = !show.has(r); });
                emptyRow.hidden = slice.length > 0;
            }

            if (filtered.length === 0) {
                emptyCell.textContent = rows.length ? "No matches. Try a different search." : "No records to display yet.";
            }

            countBadge.textContent = filtered.length === rows.length
                ? rows.length + " records"
                : filtered.length + " of " + rows.length + " records";
            pageInfo.textContent = "Page " + page + " of " + totalPages;
            prevBtn.disabled = page === 1;
            nextBtn.disabled = page === totalPages;
            nav.hidden = filtered.length <= ROWS_PER_PAGE;
        }

        // One delegated listener. `click` (not pointerdown) so Enter/Space work
        // and touch-scrolling past the buttons never pages by accident.
        nav.addEventListener("click", (e) => {
            const btn = e.target.closest("button");
            if (!btn || btn.disabled) return;
            page += btn === nextBtn ? 1 : -1;
            render();
            // A button that just disabled itself would drop keyboard focus.
            if (btn.disabled) (btn === nextBtn ? prevBtn : nextBtn).focus();
        });

        // Coalesce typing into one filter per frame (no added input latency).
        let frame = 0;
        searchInput.addEventListener("input", () => {
            cancelAnimationFrame(frame);
            frame = requestAnimationFrame(() => {
                const q = searchInput.value.trim().toLowerCase();
                filtered = q ? entries.filter((e) => e.text.includes(q)) : entries;
                clearSearch.hidden = !q;
                page = 1;
                render();
            });
        });

        clearSearch.addEventListener("click", () => {
            searchInput.value = "";
            clearSearch.hidden = true;
            filtered = entries;
            page = 1;
            render();
            searchInput.focus();
        });

        const sortByHeader = (th) => {
            const column = th.cellIndex;
            if (sortColumn === column) sortDirection *= -1;
            else { sortColumn = column; sortDirection = 1; }
            sortableHeaders.forEach((header) => header.setAttribute("aria-sort", header === th ? (sortDirection === 1 ? "ascending" : "descending") : "none"));
            entries = entries.slice().sort((a, b) => {
                const left = a.row.cells[column]?.textContent.trim() || "";
                const right = b.row.cells[column]?.textContent.trim() || "";
                if (!left && right) return 1;
                if (left && !right) return -1;
                return collator.compare(left, right) * sortDirection || a.originalIndex - b.originalIndex;
            });
            const q = searchInput.value.trim().toLowerCase();
            filtered = q ? entries.filter((entry) => entry.text.includes(q)) : entries;
            page = 1;
            render();
        };
        sortableHeaders.forEach((th) => {
            th.addEventListener("click", () => sortByHeader(th));
            th.addEventListener("keydown", (event) => {
                if (event.key !== "Enter" && event.key !== " ") return;
                event.preventDefault();
                sortByHeader(th);
            });
        });

        render();

        // ---- Stable height ------------------------------------------------------
        // Pin the container to the height of a full page so the pagination bar
        // doesn't jump under the cursor on a short last page / few results.
        return {
            container,
            hasFullPage: () => filtered.length - (page - 1) * ROWS_PER_PAGE >= ROWS_PER_PAGE
        };
    }

    // Read all heights first, then write them: one layout pass, not one per table.
    function pinHeights(tables) {
        const targets = tables.filter((t) => t.hasFullPage());
        const heights = targets.map((t) => t.container.offsetHeight);
        targets.forEach((t, i) => { t.container.style.minHeight = heights[i] + "px"; });
    }

    function init() {
        const tables = Array.from(document.querySelectorAll("table")).map(enhance).filter(Boolean);
        pinHeights(tables);

        // Column widths change with the viewport, so re-measure after resizing.
        let timer = 0;
        window.addEventListener("resize", () => {
            clearTimeout(timer);
            timer = setTimeout(() => {
                tables.forEach((t) => { t.container.style.minHeight = ""; });
                pinHeights(tables);
            }, 200);
        }, { passive: true });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();

document.addEventListener("DOMContentLoaded", function () {
    const ROWS_PER_PAGE = 6;

    document.querySelectorAll("table").forEach(function (table) {
        const allRows = Array.from(table.querySelectorAll("tr")).filter(tr => tr.querySelector("td") !== null);
        let filteredRows = [...allRows];
        let currentPage = 1;

        if (!table.parentElement.classList.contains("table-container")) {
            const container = document.createElement("div");
            container.className = "table-container";
            table.parentNode.insertBefore(container, table);
            container.appendChild(table);
        }

        const targetContainer = table.closest(".table-container");

        // Header Chrome with Live Count + Search Input
        const searchContainer = document.createElement("div");
        searchContainer.className = "table-search-container";
        searchContainer.innerHTML = `
            <span class="page-info table-count-badge">${allRows.length} total records</span>
            <input type="text" class="table-search-input" placeholder="Search table...">
        `;
        targetContainer.insertBefore(searchContainer, table);

        const countBadge = searchContainer.querySelector(".table-count-badge");
        const nav = document.createElement("div");
        nav.className = "pagination-controls";
        targetContainer.parentNode.insertBefore(nav, targetContainer.nextSibling);

        function renderTable() {
            const totalPages = Math.ceil(filteredRows.length / ROWS_PER_PAGE) || 1;
            if (currentPage > totalPages) currentPage = totalPages;

            const start = (currentPage - 1) * ROWS_PER_PAGE;
            const end = start + ROWS_PER_PAGE;

            allRows.forEach(row => (row.style.display = "none"));
            filteredRows.slice(start, end).forEach(row => (row.style.display = ""));

            countBadge.textContent = filteredRows.length === allRows.length
                ? `${allRows.length} records`
                : `${filteredRows.length} of ${allRows.length} records`;

            nav.innerHTML = `
                <span class="page-info">Page ${currentPage} of ${totalPages}</span>
                <div class="pagination-buttons">
                    <button type="button" class="page-btn btn-prev" ${currentPage === 1 ? "disabled" : ""}>← Previous</button>
                    <button type="button" class="page-btn btn-next" ${currentPage === totalPages ? "disabled" : ""}>Next →</button>
                </div>
            `;

            nav.querySelector(".btn-prev").addEventListener("pointerdown", () => {
                if (currentPage > 1) {
                    currentPage--;
                    renderTable();
                }
            });

            nav.querySelector(".btn-next").addEventListener("pointerdown", () => {
                if (currentPage < totalPages) {
                    currentPage++;
                    renderTable();
                }
            });

            nav.style.display = allRows.length <= ROWS_PER_PAGE && filteredRows.length === allRows.length ? "none" : "flex";
        }

        const searchInput = searchContainer.querySelector(".table-search-input");
        searchInput.addEventListener("input", function (e) {
            const query = e.target.value.toLowerCase();
            filteredRows = allRows.filter(row => row.textContent.toLowerCase().includes(query));
            currentPage = 1;
            renderTable();
        });

        renderTable();
    });
});
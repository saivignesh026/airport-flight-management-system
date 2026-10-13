document.addEventListener("DOMContentLoaded", function () {
    const ROWS_PER_PAGE = 5;

    document.querySelectorAll("table").forEach(function (table) {
        // Collect ONLY data rows (skips header rows with <th>)
        const allRows = Array.from(table.querySelectorAll("tr")).filter(function (tr) {
            return tr.querySelector("td") !== null;
        });

        let filteredRows = [...allRows]; // Initially, all rows are visible
        let currentPage = 1;

        // Wrap the table in .table-container if not already wrapped
        if (!table.parentElement.classList.contains("table-container")) {
            const container = document.createElement("div");
            container.className = "table-container";
            table.parentNode.insertBefore(container, table);
            container.appendChild(table);
        }
        
        const targetContainer = table.closest(".table-container");

        // 1. Create and inject Search Bar dynamically
        const searchContainer = document.createElement("div");
        searchContainer.className = "table-search-container";
        searchContainer.innerHTML = `<input type="text" class="table-search-input" placeholder="Search records...">`;
        targetContainer.insertBefore(searchContainer, table);

        // 2. Create Pagination Controls container
        const nav = document.createElement("div");
        nav.className = "pagination-controls";
        targetContainer.parentNode.insertBefore(nav, targetContainer.nextSibling);

        // Render Function: Handles both searching and paginating
        function renderTable() {
            const totalPages = Math.ceil(filteredRows.length / ROWS_PER_PAGE) || 1;
            
            // Ensure current page doesn't exceed total pages after a search
            if (currentPage > totalPages) currentPage = totalPages;

            const start = (currentPage - 1) * ROWS_PER_PAGE;
            const end = start + ROWS_PER_PAGE;

            // Hide ALL rows first
            allRows.forEach(row => row.style.display = "none");

            // Show ONLY the filtered rows for the current page
            filteredRows.slice(start, end).forEach(row => row.style.display = "");

            // Update Pagination UI
            nav.innerHTML = `
                <span class="page-info">Showing page ${currentPage} of ${totalPages} (${filteredRows.length} records found)</span>
                <div class="pagination-buttons">
                    <button type="button" class="page-btn btn-prev" ${currentPage === 1 ? "disabled" : ""}>Previous</button>
                    <button type="button" class="page-btn btn-next" ${currentPage === totalPages ? "disabled" : ""}>Next</button>
                </div>
            `;

            // Attach event listeners to new buttons
            nav.querySelector(".btn-prev").addEventListener("click", () => {
                if (currentPage > 1) { currentPage--; renderTable(); }
            });
            nav.querySelector(".btn-next").addEventListener("click", () => {
                if (currentPage < totalPages) { currentPage++; renderTable(); }
            });

            // Hide pagination completely if there's no need for it
            if (allRows.length <= ROWS_PER_PAGE && filteredRows.length === allRows.length) {
                nav.style.display = 'none';
            } else {
                nav.style.display = 'flex';
            }
        }

        // 3. Search Event Listener
        const searchInput = searchContainer.querySelector(".table-search-input");
        searchInput.addEventListener("input", function (e) {
            const query = e.target.value.toLowerCase();
            
            filteredRows = allRows.filter(row => {
                // Check if any text inside the row matches the search query
                return row.textContent.toLowerCase().includes(query);
            });
            
            currentPage = 1; // Always reset to page 1 when searching
            renderTable();
        });

        // Initialize Table
        renderTable();
    });
});
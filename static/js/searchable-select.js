document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("select").forEach(function (select) {
        // Hide the native select but keep it in the DOM for form submission & validation
        select.style.display = "none";

        // 1. Create Wrapper
        const wrapper = document.createElement("div");
        wrapper.className = "custom-select-wrapper";
        select.parentNode.insertBefore(wrapper, select);
        wrapper.appendChild(select);

        // 2. Create Display Button (shows currently selected option)
        const trigger = document.createElement("div");
        trigger.className = "custom-select-trigger";
        trigger.tabIndex = 0;

        const selectedOption = select.options[select.selectedIndex];
        trigger.textContent = selectedOption ? selectedOption.textContent.trim() : "Select...";
        wrapper.appendChild(trigger);

        // 3. Create Dropdown Panel (Search Input + Options List)
        const dropdown = document.createElement("div");
        dropdown.className = "custom-select-dropdown";

        const searchInput = document.createElement("input");
        searchInput.type = "text";
        searchInput.className = "custom-select-search";
        searchInput.placeholder = "Search...";
        dropdown.appendChild(searchInput);

        const optionsList = document.createElement("div");
        optionsList.className = "custom-select-options";
        dropdown.appendChild(optionsList);

        wrapper.appendChild(dropdown);

        // 4. Populate Options
        function renderOptions(filter = "") {
            optionsList.innerHTML = "";
            let matchCount = 0;

            Array.from(select.options).forEach((opt, index) => {
                const text = opt.textContent.trim();
                if (text.toLowerCase().includes(filter.toLowerCase())) {
                    matchCount++;
                    const item = document.createElement("div");
                    item.className = "custom-select-option";
                    if (index === select.selectedIndex) {
                        item.classList.add("selected");
                    }
                    item.textContent = text;

                    item.addEventListener("click", function (e) {
                        e.stopPropagation();
                        select.selectedIndex = index;
                        select.dispatchEvent(new Event("change"));
                        trigger.textContent = text;
                        closeDropdown();
                    });

                    optionsList.appendChild(item);
                }
            });

            if (matchCount === 0) {
                const noResult = document.createElement("div");
                noResult.className = "custom-select-no-results";
                noResult.textContent = "No matches found";
                optionsList.appendChild(noResult);
            }
        }

        function openDropdown() {
            // Close any other open searchable dropdowns first
            document.querySelectorAll(".custom-select-wrapper.open").forEach(w => {
                if (w !== wrapper) w.classList.remove("open");
            });
            wrapper.classList.add("open");
            searchInput.value = "";
            renderOptions();
            setTimeout(() => searchInput.focus(), 10);
        }

        function closeDropdown() {
            wrapper.classList.remove("open");
        }

        // 5. Event Listeners
        trigger.addEventListener("click", function (e) {
            e.stopPropagation();
            if (wrapper.classList.contains("open")) {
                closeDropdown();
            } else {
                openDropdown();
            }
        });

        searchInput.addEventListener("click", function (e) {
            e.stopPropagation();
        });

        searchInput.addEventListener("input", function (e) {
            renderOptions(e.target.value);
        });

        // Initial render
        renderOptions();
    });

    // Close dropdown when clicking anywhere outside
    document.addEventListener("click", function () {
        document.querySelectorAll(".custom-select-wrapper.open").forEach(w => {
            w.classList.remove("open");
        });
    });
});
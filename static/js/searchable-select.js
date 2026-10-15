document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("select").forEach(function (select) {
        select.style.display = "none";

        const wrapper = document.createElement("div");
        wrapper.className = "custom-select-wrapper";
        select.parentNode.insertBefore(wrapper, select);
        wrapper.appendChild(select);

        const trigger = document.createElement("div");
        trigger.className = "custom-select-trigger";
        trigger.tabIndex = 0;

        const selectedOption = select.options[select.selectedIndex];
        trigger.textContent = selectedOption ? selectedOption.textContent.trim() : "Select...";
        wrapper.appendChild(trigger);

        const dropdown = document.createElement("div");
        dropdown.className = "custom-select-dropdown";

        const searchInput = document.createElement("input");
        searchInput.type = "text";
        searchInput.className = "custom-select-search";
        searchInput.placeholder = "Filter options...";
        dropdown.appendChild(searchInput);

        const optionsList = document.createElement("div");
        optionsList.className = "custom-select-options";
        dropdown.appendChild(optionsList);

        wrapper.appendChild(dropdown);

        function renderOptions(filter = "") {
            optionsList.innerHTML = "";
            let matchCount = 0;
            const query = filter.toLowerCase();

            Array.from(select.options).forEach((opt, index) => {
                const text = opt.textContent.trim();
                if (!query || text.toLowerCase().includes(query)) {
                    matchCount++;
                    const item = document.createElement("div");
                    item.className = "custom-select-option";
                    if (index === select.selectedIndex) item.classList.add("selected");
                    item.textContent = text;

                    item.addEventListener("pointerdown", function (e) {
                        e.stopPropagation();
                        select.selectedIndex = index;
                        select.dispatchEvent(new Event("change"));
                        trigger.textContent = text;
                        wrapper.classList.remove("open");
                    });

                    optionsList.appendChild(item);
                }
            });

            if (matchCount === 0) {
                const noResult = document.createElement("div");
                noResult.className = "custom-select-no-results";
                noResult.textContent = "No matching options";
                optionsList.appendChild(noResult);
            }
        }

        trigger.addEventListener("pointerdown", function (e) {
            e.stopPropagation();
            e.preventDefault();
            const isOpen = wrapper.classList.contains("open");

            document.querySelectorAll(".custom-select-wrapper.open").forEach(w => {
                w.classList.remove("open");
            });

            if (!isOpen) {
                wrapper.classList.add("open");
                searchInput.value = "";
                renderOptions();
                requestAnimationFrame(() => searchInput.focus());
            }
        });

        dropdown.addEventListener("pointerdown", e => e.stopPropagation());
        searchInput.addEventListener("input", e => renderOptions(e.target.value));
    });

    document.addEventListener("pointerdown", function () {
        document.querySelectorAll(".custom-select-wrapper.open").forEach(w => {
            w.classList.remove("open");
        });
    });
});
(function () {
    "use strict";

    // ── State ──────────────────────────────────────────────
    const state = {
        query: "",
        activeEpochs: new Set(),   // lowercase epoch strings
        sort: "default"
    };

    // ── DOM refs ───────────────────────────────────────────
    const pieceList      = document.getElementById("piece-list");
    const searchInput    = document.getElementById("search-input");
    const sortSelect     = document.getElementById("sort-select");
    const epochContainer = document.getElementById("epoch-filters");
    const activeRow      = document.getElementById("active-filter-row");
    const activeTags     = document.getElementById("active-tags");
    const filterCount    = document.getElementById("filter-count");
    const noResults      = document.getElementById("no-results");
    const clearAll       = document.getElementById("clear-all");
    const clearAll2      = document.getElementById("clear-all-2");

    // All piece cards — NodeList converted to array so we can sort
    let allCards = Array.from(pieceList.querySelectorAll(".piece-card"));
    const total  = allCards.length;

    // ── Build epoch buttons from data ──────────────────────
    function buildEpochButtons() {
        // Collect unique epochs from card data attributes
        const epochs = new Map(); // lowercase -> display string
        allCards.forEach(card => {
            const key     = card.dataset.epoch;
            const display = card.dataset.epochDisplay;
            if (!epochs.has(key)) epochs.set(key, display);
        });

        // Sort epochs alphabetically by display name
        const sorted = Array.from(epochs.entries()).sort((a, b) =>
            a[1].localeCompare(b[1])
        );

        sorted.forEach(([key, display]) => {
            const btn = document.createElement("button");
            btn.className    = "btn btn-outline epoch-btn";
            btn.dataset.epoch = key;
            btn.textContent  = display;
            btn.addEventListener("click", () => toggleEpoch(key, display, btn));
            epochContainer.appendChild(btn);
        });
    }

    // ── Toggle an epoch filter ─────────────────────────────
    function toggleEpoch(key, display, btn) {
        if (state.activeEpochs.has(key)) {
            state.activeEpochs.delete(key);
            btn.classList.remove("epoch-btn--active");
        } else {
            state.activeEpochs.add(key);
            btn.classList.add("epoch-btn--active");
        }
        applyFilters();
    }

    // ── Main filter + sort logic ───────────────────────────
    function applyFilters() {
        const query  = state.query.trim().toLowerCase();
        const epochs = state.activeEpochs;
        const sort   = state.sort;

        // 1. Filter
        let visible = allCards.filter(card => {
            // Text search: match title OR composer
            const matchesText = !query ||
                card.dataset.title.includes(query) ||
                card.dataset.composer.includes(query);

            // Epoch filter: must match one of the active epochs (OR logic)
            const matchesEpoch = epochs.size === 0 ||
                epochs.has(card.dataset.epoch);

            return matchesText && matchesEpoch;
        });

        // 2. Sort the visible subset
        if (sort !== "default") {
            visible = sortCards(visible, sort);
        }

        // 3. Re-order DOM: append in new order, hide the rest
        // First hide all
        allCards.forEach(card => { card.style.display = "none"; });

        // Then show and reorder visible ones
        visible.forEach(card => {
            card.style.display = "";
            pieceList.appendChild(card); // moves to end in sorted order
        });

        // 4. Update UI chrome
        updateCount(visible.length);
        updateActiveTags();
        noResults.style.display = visible.length === 0 ? "block" : "none";
    }

    // ── Sort helper ────────────────────────────────────────
    function sortCards(cards, mode) {
        return [...cards].sort((a, b) => {
            switch (mode) {
                case "year-asc":
                    return parseYear(a) - parseYear(b);
                case "year-desc":
                    return parseYear(b) - parseYear(a);
                case "title-asc":
                    return a.dataset.title.localeCompare(b.dataset.title);
                case "composer-asc":
                    return a.dataset.composer.localeCompare(b.dataset.composer);
                default:
                    return 0;
            }
        });
    }

    function parseYear(card) {
        // Year might be a range like "1842-1910" or blank — take first 4 digits
        const match = (card.dataset.year || "").match(/\d{4}/);
        return match ? parseInt(match[0], 10) : 9999;
    }

    // ── Active filter tag display ──────────────────────────
    function updateActiveTags() {
        activeTags.innerHTML = "";

        const hasQuery  = state.query.trim() !== "";
        const hasEpochs = state.activeEpochs.size > 0;
        const hasSort   = state.sort !== "default";
        const hasAny    = hasQuery || hasEpochs || hasSort;

        activeRow.style.display = hasAny ? "flex" : "none";

        if (hasQuery) {
            activeTags.appendChild(makeTag(
                `Search: "${state.query.trim()}"`,
                () => {
                    state.query = "";
                    searchInput.value = "";
                    applyFilters();
                }
            ));
        }

        state.activeEpochs.forEach(epochKey => {
            // Find display name from button
            const btn = epochContainer.querySelector(`[data-epoch="${epochKey}"]`);
            const label = btn ? btn.textContent : epochKey;
            activeTags.appendChild(makeTag(
                `Epoch: ${label}`,
                () => {
                    state.activeEpochs.delete(epochKey);
                    if (btn) btn.classList.remove("epoch-btn--active");
                    applyFilters();
                }
            ));
        });

        if (hasSort) {
            const sortLabel = sortSelect.options[sortSelect.selectedIndex].text;
            activeTags.appendChild(makeTag(
                `Sort: ${sortLabel}`,
                () => {
                    state.sort = "default";
                    sortSelect.value = "default";
                    applyFilters();
                }
            ));
        }
    }

    function makeTag(label, onRemove) {
        const tag = document.createElement("span");
        tag.className = "active-tag";

        const text = document.createElement("span");
        text.textContent = label;

        const x = document.createElement("button");
        x.className   = "active-tag-remove";
        x.textContent = "×";
        x.setAttribute("aria-label", `Remove filter: ${label}`);
        x.addEventListener("click", onRemove);

        tag.appendChild(text);
        tag.appendChild(x);
        return tag;
    }

    // ── Count display ──────────────────────────────────────
    function updateCount(n) {
        if (n === total) {
            filterCount.textContent = `Showing all ${total} pieces`;
        } else {
            filterCount.textContent = `Showing ${n} of ${total} pieces`;
        }
    }

    // ── Reset everything ───────────────────────────────────
    function resetAll() {
        state.query = "";
        state.activeEpochs.clear();
        state.sort = "default";

        searchInput.value  = "";
        sortSelect.value   = "default";

        epochContainer.querySelectorAll(".epoch-btn--active").forEach(btn => {
            btn.classList.remove("epoch-btn--active");
        });

        // Restore original DOM order
        allCards.forEach(card => {
            card.style.display = "";
            pieceList.appendChild(card);
        });

        updateCount(total);
        updateActiveTags();
        noResults.style.display = "none";
    }

    // ── Dropdown toggle (replaces inline onclick handlers) ─
    window.toggleDropdown = function (id) {
        const el = document.getElementById(id);
        if (!el) return;
        el.classList.toggle("hide");
        el.classList.toggle("show");
    };

    // Keep old names working in case anything still uses them
    window.toggleStudiedForm  = window.toggleDropdown;
    window.toggleProgramForm  = window.toggleDropdown;
    window.toggleNewProgram   = window.toggleDropdown;

    // ── Event listeners ────────────────────────────────────
    searchInput.addEventListener("input", () => {
        state.query = searchInput.value;
        applyFilters();
    });

    sortSelect.addEventListener("change", () => {
        state.sort = sortSelect.value;
        applyFilters();
    });

    clearAll.addEventListener("click", resetAll);
    if (clearAll2) clearAll2.addEventListener("click", resetAll);

    // ── Init ───────────────────────────────────────────────
    buildEpochButtons();
    updateCount(total);

})();
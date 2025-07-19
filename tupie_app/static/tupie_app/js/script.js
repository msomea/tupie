document.addEventListener("DOMContentLoaded", function () {
    const regionSelect = document.getElementById("id_region");

    if (!regionSelect) return; // Safety check

    // ✅ Utility: Populate dropdown
    function populateRegions(regions) {
        regionSelect.innerHTML = '<option value="">-- Select Region --</option>';
        regions.forEach(region => {
            const opt = document.createElement("option");
            opt.value = region.region_code;
            opt.textContent = region.region_name;
            regionSelect.appendChild(opt);
        });
    }

    // ✅ Fetch all Tanzanian regions
    function loadRegions() {
        fetch(`/get_regions/`)  // ✅ No country parameter anymore
            .then(response => {
                if (!response.ok) throw new Error("Network error loading regions");
                return response.json();
            })
            .then(data => {
                populateRegions(data);
            })
            .catch(error => {
                console.error("Error loading regions:", error);
                regionSelect.innerHTML = '<option value="">Failed to load regions</option>';
            });
    }

    // ✅ Load regions immediately
    loadRegions();
});

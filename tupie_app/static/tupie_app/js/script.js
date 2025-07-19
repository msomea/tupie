document.addEventListener("DOMContentLoaded", function () {
    const regionSelect = document.getElementById("id_region");
    const districtSelect = document.getElementById("id_district");
    const wardSelect = document.getElementById("id_ward");
    const placeSelect = document.getElementById("id_place");

    function clearOptions(select, message) {
        select.innerHTML = "";
        const opt = document.createElement("option");
        opt.value = "";
        opt.textContent = message;
        select.appendChild(opt);
    }

    // Start by clearing
    clearOptions(districtSelect, "-- Select District --");
    clearOptions(wardSelect, "-- Select Ward --");
    clearOptions(placeSelect, "-- Select Place --");

    // Load Districts when Region changes
    regionSelect.addEventListener("change", function () {
        const regionId = this.value;
        clearOptions(districtSelect, "-- Loading Districts... --");
        clearOptions(wardSelect, "-- Select Ward --");
        clearOptions(placeSelect, "-- Select Place --");

        if (!regionId) {
            clearOptions(districtSelect, "-- Select District --");
            return;
        }

        fetch(`/get_districts/?region=${regionId}`)
            .then(res => res.json())
            .then(data => {
                clearOptions(districtSelect, "-- Select District --");
                data.forEach(d => {
                    let opt = document.createElement("option");
                    opt.value = d.district_code;
                    opt.textContent = d.district_name;
                    districtSelect.appendChild(opt);
                });
            })
            .catch(() => clearOptions(districtSelect, "Failed to load districts"));
    });

    // Load Wards when District changes
    districtSelect.addEventListener("change", function () {
        const districtId = this.value;
        clearOptions(wardSelect, "-- Loading Wards... --");
        clearOptions(placeSelect, "-- Select Place --");

        if (!districtId) {
            clearOptions(wardSelect, "-- Select Ward --");
            return;
        }

        fetch(`/get_wards/?district=${districtId}`)
            .then(res => res.json())
            .then(data => {
                clearOptions(wardSelect, "-- Select Ward --");
                data.forEach(w => {
                    let opt = document.createElement("option");
                    opt.value = w.ward_code;
                    opt.textContent = w.ward_name;
                    wardSelect.appendChild(opt);
                });
            })
            .catch(() => clearOptions(wardSelect, "Failed to load wards"));
    });

    // Load Places when Ward changes
    wardSelect.addEventListener("change", function () {
        const wardId = this.value;
        clearOptions(placeSelect, "-- Loading Places... --");

        if (!wardId) {
            clearOptions(placeSelect, "-- Select Place --");
            return;
        }

        fetch(`/get_places/?ward=${wardId}`)
            .then(res => res.json())
            .then(data => {
                clearOptions(placeSelect, "-- Select Place --");
                data.forEach(p => {
                    let opt = document.createElement("option");
                    opt.value = p.id;
                    opt.textContent = p.place_name;
                    placeSelect.appendChild(opt);
                });
            })
            .catch(() => clearOptions(placeSelect, "Failed to load places"));
    });
});

(function () {
    "use strict";
    const passenger = document.getElementById("Passenger_ID");
    const fields = document.getElementById("new-passenger-fields");
    if (!passenger || !fields) return;
    function sync() {
        fields.disabled = Boolean(passenger.value);
        fields.hidden = Boolean(passenger.value);
    }
    passenger.addEventListener("change", sync);
    passenger.form.addEventListener("reset", () => setTimeout(sync, 0));
    sync();
})();

function openNav() {
    //si se preciona, colapsar el nav
    var navbar = document.getElementById("naveMenu"); // replace "myNavbar" with the ID of your navbar
    if (navbar.classList.contains("collapse")) {
        navbar.classList.remove("collapse"); // remove "show" class to collapse navbar
    } else {
        navbar.classList.add("collapse"); // add "show" class to expand navbar
    }
}

try {
    const regionSelect = document.getElementById("regionProducto");
    const comunaSelect = document.getElementById("comunaProducto");

    regionSelect.addEventListener("change", function() {
        const regionSeleccionada = regionSelect.value
        if (regionSeleccionada !== "0") {
            // Agrega las opciones de comuna correspondientes a la región seleccionada
            let request = new XMLHttpRequest();
            request.open("GET", "http://localhost:8000/comunas/" + regionSeleccionada);
            request.responseType = "json";
            request.send();
            request.onload = () => {
                const comunasPorRegion = request.response;
                comunaSelect.innerHTML = "";
                comunaSelect.disabled = false;
                comunasPorRegion.forEach(comuna => {
                    const option = document.createElement("option");
                    option.value = comuna.id;
                    option.textContent = comuna.nombre;
                    comunaSelect.appendChild(option);
                });
            };

        }
    });
} catch {
    console.log("no hay regiones")
}
regionSelect.addEventListener("change", function() {
    const regionSeleccionada = regionSelect.value
    if (regionSeleccionada !== "0") {
        // Agrega las opciones de comuna correspondientes a la región seleccionada
        let request = new XMLHttpRequest();
        request.open("GET", "http://127.0.0.1:8000/comunas/" + regionSeleccionada);
        request.responseType = "json";
        request.send();
        request.onload = () => {
            const comunasPorRegion = request.response;
            comunaSelect.innerHTML = "";
            comunaSelect.disabled = false;
            comunasPorRegion.forEach(comuna => {
                const option = document.createElement("option");
                option.value = comuna.id;
                option.textContent = comuna.nombre;
                comunaSelect.appendChild(option);
            });
        };

    }
});


const modalEditar = document.getElementById('modalModificarProducto');
modalEditar.addEventListener('show.bs.modal', function(event) {
    const button = event.relatedTarget;
    const nombre = button.getAttribute('data-nombre');
    const precio = button.getAttribute('data-precio');
    const marca = button.getAttribute('data-marca');
    const costoEnvio = button.getAttribute('data-costoenvio');

    document.getElementById('nombre').value = nombre;
    document.getElementById('precio').value = precio;
    document.getElementById('marca').value = marca;
    document.getElementById('cde').value = costoEnvio;
});
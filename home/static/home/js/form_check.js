document.addEventListener('DOMContentLoaded', function() {
    const ofertaCheckbox = document.getElementById('id_oferta');
    const precioAnterior = document.getElementById('id_precioAnterior').closest('p');
    const descuento = document.getElementById('id_descuento').closest('p');

    //Mostrar/ocultar los campos
    function toggleFields() {
        if (ofertaCheckbox.checked) {
            precioAnterior.style.display = "block";
            descuento.style.display = "block";
        } else {
            precioAnterior.style.display = "none";
            descuento.style.display = "none";
        }
    }

    toggleFields();

    ofertaCheckbox.addEventListener('change', toggleFields);
});

document.addEventListener("DOMContentLoaded", function() {
    // Previsualización de la imagen principal
    const imagenPrincipal = document.querySelector('input[name="productoimagen_set-0-imagen"]');
    const imagenPrincipalPreview = document.createElement("img");
    imagenPrincipalPreview.style.display = "none";
    imagenPrincipalPreview.style.maxWidth = "150px";
    imagenPrincipalPreview.style.marginTop = "10px";
    imagenPrincipal.parentNode.appendChild(imagenPrincipalPreview);

    imagenPrincipal.addEventListener("change", function(event) {
        const file = event.target.files[0];
        if (file) {
            imagenPrincipalPreview.src = URL.createObjectURL(file);
            imagenPrincipalPreview.style.display = "block";
        } else {
            imagenPrincipalPreview.style.display = "none";
        }
    });

    // Previsualización de imágenes adicionales
    const imagenesAdicionales = document.querySelector('input[name="productoimagen_set-0-image"]');
    const imagenesAdicionalesPreview = document.createElement("div");
    imagenesAdicionalesPreview.style.marginTop = "1px";
    imagenesAdicionales.parentNode.appendChild(imagenesAdicionalesPreview);

    imagenesAdicionales.addEventListener("change", function(event) {
        imagenesAdicionalesPreview.innerHTML = '';
        const files = event.target.files;
        if (files) {
            for (let i = 0; i < files.length; i++) {
                const img = document.createElement("img");
                img.src = URL.createObjectURL(files[i]);
                img.style.maxWidth = "100px";
                img.style.marginRight = "10px";
                imagenesAdicionalesPreview.appendChild(img);
            }
        }
    });
});
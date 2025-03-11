// Obtener el token CSRF de las cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Función para establecer una cookie
function setCookie(name, value, days) {
    let date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));  // Duración de la cookie
    let expires = "expires=" + date.toUTCString();
    document.cookie = name + "=" + encodeURIComponent(value) + ";" + expires + ";path=/";
}

const csrftoken = getCookie('csrftoken');
let usuarioLogueado = document.getElementById('cart-total').getAttribute('data-login');
if(usuarioLogueado === 'true'){
    usuarioLogueado = true;
}
else{
    usuarioLogueado = false;
}

// Esperar a que el DOM esté completamente cargado
function updateCartInfo(newCount) {
    document.getElementById('cart-total').innerText = `${newCount}`; // Actualiza la cantidad
}
const cartUrl = document.getElementById('cart-action').getAttribute('data-url');
// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    document.body.addEventListener('click', function(event) {
        if (event.target.classList.contains('editar-carrito')) {
            let button = event.target;
            let productoId = button.getAttribute('data-producto');
            let usuarioId = button.getAttribute('data-usuario');
            let vendedor = button.getAttribute('data-vendedor');
            let envio = button.getAttribute('data-envio');
            let action = button.getAttribute('data-action');

            if(document.getElementById('id_rango_fecha')){
                let rango = document.getElementById('id_rango_fecha').value;
                largo = rango.split(' ').length;
                let fecha_inicio = null;
                let fecha_fin = null;
                if(largo === 3){
                    fecha_inicio = rango.split(' ')[0];
                    fecha_fin = rango.split(' ')[2];
                }
                else{
                    fecha_inicio = rango.split(' ')[0];
                    fecha_fin = rango.split(' ')[0];
                }
                console.log("rango", fecha_inicio, fecha_fin)
            }
            else{
                let fecha_inicio = null;
                let fecha_fin = null;
                console.log("no se pudo obtener rango")
            }

            
            if (usuarioLogueado) {
                if(document.getElementById('id_rango_fecha')){
                    let rango = document.getElementById('id_rango_fecha').value;
                    largo = rango.split(' ').length;
                    let fecha_inicio = null;
                    let fecha_fin = null;
                    if(largo === 3){
                        fecha_inicio = rango.split(' ')[0];
                        fecha_fin = rango.split(' ')[2];
                    }
                    else{
                        fecha_inicio = rango.split(' ')[0];
                        fecha_fin = rango.split(' ')[0];
                    }
                    console.log("rango", fecha_inicio, fecha_fin)

                    localStorage.setItem(productoId, JSON.stringify({productoId, usuarioId, vendedor, envio, action, fecha_inicio, fecha_fin}));
                }
                else{
                    fecha_inicio = null;
                    fecha_fin = null;
                    console.log("no se pudo obtener rango")

                    localStorage.setItem(productoId, JSON.stringify({productoId, usuarioId, vendedor, envio, action, fecha_inicio, fecha_fin}));
                }
                // Obtener la URL desde el HTML
                const cartUrl = document.getElementById('cart-action').getAttribute('data-url');
                if (action === 'remove') {
                    // Mostrar mensaje de "Eliminando producto..."
                    Swal.fire({
                        title: 'Eliminando producto...',
                        text: 'Por favor, espera un momento.',
                        icon: 'info',
                        allowOutsideClick: false,
                        showConfirmButton: false,
                        timerProgressBar: true,
                        didOpen: () => {
                            Swal.showLoading();
                        }
                    });
                } else {
                    // Mostrar mensaje de "Agregando producto..."
                    Swal.fire({
                        title: 'Agregando producto...',
                        text: 'Por favor, espera un momento.',
                        icon: 'info',
                        allowOutsideClick: false,
                        showConfirmButton: false,
                        timerProgressBar: true,
                        didOpen: () => {
                            Swal.showLoading();
                        }
                    });
                }
                // Hacer la llamada fetch a la API
                fetch(cartUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        'producto_id': productoId,
                        'usuario_id': usuarioId,
                        'vendedor': vendedor,
                        'envio': envio,
                        'action': action,
                        'fecha_inicio': localStorage.getItem(productoId) ? JSON.parse(localStorage.getItem(productoId))['fecha_inicio'] : null,
                        'fecha_fin': localStorage.getItem(productoId) ? JSON.parse(localStorage.getItem(productoId))['fecha_fin'] : null,
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (data.removed) {
                            // Elimina el contenedor del producto del DOM
                            const itemElement = document.querySelector(`.cart-item[data-producto="${productoId}"]`);
                            if (itemElement) {
                                itemElement.remove(); // Elimina el elemento del DOM
                            }
                        } else {
                            // Actualiza el contador en el frontend
                            document.getElementById('cart-total').textContent = data.newCount;
                        }
                        // Mostrar mensaje de éxito
                        Swal.fire({
                            title: data.removed ? '¡Producto Agregado!' : '¡Producto actualizado!',
                            text: data.removed ? 'El producto ha sido Agregado al carrito.' : 'El producto se ha actualizado en el carrito.',
                            icon: 'success',
                            timer: 2000,
                            showConfirmButton: false
                        });
                        localStorage.removeItem(productoId);
                        window.location.href = "/carrito/";
                    } else {
                        Swal.fire({
                            title: 'Error',
                            text: 'Hubo un error al modificar el producto: ' + data.message,
                            icon: 'error',
                            showConfirmButton: true
                        });
                    }
                })
                .catch(error => {
                    Swal.fire({
                        title: 'Error',
                        text: 'No se pudo agregar el producto. Intenta de nuevo más tarde.',
                        icon: 'error',
                        showConfirmButton: true
                    });
                });
            } else {
                // Manejar carrito en cookies
                let cart = JSON.parse(getCookie('cart')) || {};  // Obtener carrito de la cookie, o crear uno vacío si no existe
                let fecha_inicio = null;
                let fecha_fin = null;
                if(document.getElementById('id_rango_fecha')){
                    let rango = document.getElementById('id_rango_fecha').value;
                    largo = rango.split(' ').length;
                    if(largo === 3){
                        fecha_inicio = rango.split(' ')[0];
                        fecha_fin = rango.split(' ')[2];
                    }
                    else{
                        fecha_inicio = rango.split(' ')[0];
                        fecha_fin = rango.split(' ')[0];
                    }
                    console.log("rango", fecha_inicio, fecha_fin)
                }
                const uniqueKey = `${productoId}_${fecha_inicio}_${fecha_fin}`;
                let count = cart[uniqueKey] || 0;  // Obtener la cantidad del producto en el carrito, o 0 si no existe

                if (action === 'add') {
                    cart[uniqueKey] = {
                        count: count + 1,
                        fecha_inicio: fecha_inicio,
                        fecha_fin: fecha_fin
                    };
                } else if (action === 'remove' && count > 0) {
                    if (cart[uniqueKey]) {
                        cart[uniqueKey].count = count - 1;
                        if (cart[uniqueKey].count === 0) {
                            delete cart[uniqueKey];
                        }
                    }
                }

                // Guardar el carrito actualizado en la cookie
                setCookie('cart', JSON.stringify(cart), 7);  // Guardar por 7 días
                updateCartInfo(Object.values(cart).reduce((a, b) => a + b, 0));  // Actualizar la cantidad total en el carrito
                // Mostrar mensaje de éxito
                Swal.fire({
                    title: action === 'add' ? '¡Producto agregado!' : '¡Producto eliminado!',
                    text: action === 'add' ? 'El producto ha sido agregado al carrito.' : 'El producto ha sido eliminado del carrito.',
                    icon: 'success',
                    timer: 2000,
                    showConfirmButton: false
                })
                //redirect to cart
                window.location.href = "/carrito/";
            }
        }
    });
});


document.querySelectorAll('.modificar-carrito').forEach(button => {
    
    button.addEventListener('click', (event) => {
        const action = button.getAttribute('data-action');
        const productoId = button.getAttribute('data-producto');
        const fecha_inicio = button.getAttribute('data-inicio');
        const fecha_fin = button.getAttribute('data-termino');
        
        //si los usuarios no están logueados

        if (!usuarioLogueado) {
            let cart = JSON.parse(getCookie('cart')) || {};
            const uniqueKey = `${productoId}_${fecha_inicio}_${fecha_fin}`;
            console.log(uniqueKey)
            
            if (action === 'add') {
            cart[uniqueKey] = {
                count: (cart[uniqueKey] ? cart[uniqueKey].count : 0) + 1,
                fecha_inicio: fecha_inicio,
                fecha_fin: fecha_fin
            };
            } else if (action === 'remove') {
            if (cart[uniqueKey]) {
                cart[uniqueKey].count -= 1;
                if (cart[uniqueKey].count <= 0) {
                delete cart[uniqueKey];
                }
            }
            }

            setCookie('cart', JSON.stringify(cart), 7);
            updateCartInfo(Object.values(cart).reduce((total, item) => total + item.count, 0));
            Swal.fire({
            title: action === 'add' ? '¡Producto agregado!' : '¡Producto eliminado!',
            text: action === 'add' ? 'El producto ha sido agregado al carrito.' : 'El producto ha sido eliminado del carrito.',
            icon: 'success',
            timer: 2000,
            showConfirmButton: false
            });
            return;
        }
        
        if(usuarioLogueado){
            fetch(cartUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken  // Asegúrate de que esto esté definido
                },
                body: JSON.stringify({
                    producto_id: productoId,
                    action: action
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const itemElement = document.querySelector(`.cart-item[data-producto="${productoId}"]`);
                    const elemento = document.querySelector(`.container-carro[data-producto="${productoId}"]`);
                    window.location.href = "/carrito/";
                    // Mostrar mensaje de éxito
                    Swal.fire({
                        title: data.removed ? '¡Producto eliminado!' : '¡Producto actualizado!',
                        text: data.removed ? 'El producto ha sido eliminado del carrito.' : 'El producto se ha actualizado en el carrito.',
                        icon: 'success',
                        timer: 2000,
                        showConfirmButton: false
                    })
                } else {
                    Swal.fire({
                        title: 'Error',
                        text: 'Hubo un error al modificar el producto: ' + data.message,
                        icon: 'error',
                        showConfirmButton: true
                    });
                }
            });
        }
    });
});

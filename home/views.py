import datetime
from pyexpat.errors import messages
from django.forms import modelformset_factory
from django.utils import timezone
import time
from django.contrib import messages
from imaplib import _Authenticator
from django.http import HttpResponse, JsonResponse
from datetime import timedelta

from django.views import View
from .models import  Arriendo
from django.db.models import Sum, Count, Q
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.decorators import login_required, user_passes_test




from home.models import Comuna, Producto, Carrito, Order, OrderItem, User, Region, ProductoImagen, Transaccion, Perfil,Disponibilidad
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth import authenticate, login, logout

from .forms import agregarProducto, loginForm,Empresa  , productoForm, RegistroForm, UserUpdateForm, PerfilUpdateForm, CambiarPasswordForm, DireccionForm, EmpresaForm, modificarProductoFrom, ImagenFormSet, filtroMarca, filtroArrendador, filtroPrecio, filtroRegion, filtroCombustible, DisponibilidadForm, filtroDisponibilidad


from django.contrib.auth import get_user,update_session_auth_hash
from .models import Direccion, Empresa
import requests
import json
import hashlib
from social_django.utils import psa

#se importan librerias de webpay
from django.shortcuts import redirect
from django.urls import reverse
from random import randrange
from transbank.error.transbank_error import TransbankError
from transbank.webpay.webpay_plus.transaction import Transaction, WebpayOptions 
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
import urllib.parse



# Create your views here.

def is_admin(user):
    return user.is_staff or user.is_superuser

def home(request):
    return render(request, 'home/home.html')

# Configuración del comercio
commerce_code_integracion = "597055555532"  # Reemplaza con tu código de comercio
codigo_comercio_produccion = "597047675047"
api_key = "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"  # Reemplaza con tu API Key



# Create your views here.
def is_authenticated(user):
    return user.is_authenticated

def getCantidadProductos(request):
    cartItems = 0
    if request.user.is_authenticated:
        print("USUARIO AUTENTICADO")
        order, created = Order.objects.get_or_create(cliente=request.user, pagoProcesado=False)
        cartItems = order.get_cart_items
    else:
        try:
            cart = request.COOKIES.get('cart')
            cart = urllib.parse.unquote(cart)
            cart = json.loads(cart)
            for i in cart:
                cartItems += cart[i]
        except:
            cart = {}
        items = []
        order = {'get_cart_total':0, 'get_cart_items':cartItems}
        cartItems = order['get_cart_items']
        print("CART",cart)
    print("CART ITEEEEEMS",cartItems)
    return cartItems


def index(request):
    #seleccionar las últimas 3 maquinarias
    maquinarias = Producto.objects.all()[::-1][:3]
    for maquinaria in maquinarias:
        maquinaria.imagen = ProductoImagen.objects.filter(producto=maquinaria).first()
    cartItems = getCantidadProductos(request)
    context = {'cartItems': cartItems, 'maquinarias': maquinarias}
    return render(request, 'home/main.html',context)

def producto(request, VIN):
    cartItems = getCantidadProductos(request)
    producto = Producto.objects.get(VIN=VIN)
    producto.imagen = ProductoImagen.objects.filter(producto=producto).first()
    disponibilidad = Disponibilidad.objects.filter(Producto=producto)
    disponibilidadForm = DisponibilidadForm()
    disponibilidades = Disponibilidad.objects.filter(Producto=producto)
    if(request.user.is_authenticated):
        bloqueadasUsuario=OrderItem.objects.filter(idProducto=producto, order__pagoProcesado=False, order__cliente=request.user)
    else:
        bloqueadasUsuario = []
    bloqueadas=OrderItem.objects.filter(idProducto=producto, order__pagoProcesado=True)
    
    print("diosponibilidad",disponibilidades)
    rangos_disponibles = [
        {'inicio': (disponibilidad.fecha_inicio).strftime('%Y-%m-%d'), 'fin': (disponibilidad.fecha_termino + timedelta(days=1)).strftime('%Y-%m-%d'),}
        for disponibilidad in disponibilidades
    ]
    rango_bloqueadas = [
        {'inicio': bloqueada.fecha_inicio.strftime('%Y-%m-%d'), 'fin': bloqueada.fecha_termino.strftime('%Y-%m-%d'),}
        for bloqueada in bloqueadas
    ]
    rango_bloqueadasUsuario = [
        {'inicio': bloqueada.fecha_inicio.strftime('%Y-%m-%d'), 'fin': bloqueada.fecha_termino.strftime('%Y-%m-%d'),}
        for bloqueada in bloqueadasUsuario
    ]
    print('Disponibilidades:',rangos_disponibles)  
    #print(producto.imagen.url)

    datos = {
        'producto': producto,
        'cartItems': cartItems,
        'disponibilidadForm': disponibilidadForm,
        'rangos_disponibles': rangos_disponibles, #fechas disponibles para arrendar el producto
        'rango_bloqueadas': rango_bloqueadas, #fechas bloqueadas debido a que se ha arrendado el producto en esa fecha
        'rango_bloqueadasUsuario': rango_bloqueadasUsuario, #fechas bloqueadas por el usuario actual en el carrito
    }
    #print(producto)
    return render(request, 'home/producto.html',datos)

def nosotros(request):
    try:
        cartItems = getCantidadProductos(request)
    except:
        cartItems = 0
    context = {'cartItems': cartItems}
    return render(request, 'home/nosotros.html',context)


MAX_INTENTOS = 3
BLOQUEO_MINUTOS = 5

def userlogin(request):
    datos = {
        'form': loginForm(),
        'error': None,
    }

    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        password = request.POST.get('password')

        if not usuario or not password:
            datos['error'] = 'Usuario o contraseña incorrectos.'
            return render(request, 'home/login.html', datos)

        try:
            user = User.objects.get(username=usuario)
        except User.DoesNotExist:
            datos['error'] = 'Usuario o contraseña incorrectos.'
            return render(request, 'home/login.html', datos)

        intentos_fallidos = request.session.get(f'intentos_fallidos_{usuario}', 0)
        bloqueo_hasta = request.session.get(f'bloqueo_hasta_{usuario}')

        if bloqueo_hasta:
            bloqueo_hasta = timezone.make_aware(timezone.datetime.fromtimestamp(bloqueo_hasta))


        if bloqueo_hasta and timezone.now() < bloqueo_hasta:
            tiempo_restante = bloqueo_hasta - timezone.now()
            minutos_restantes = tiempo_restante.seconds // 60
            segundos_restantes = tiempo_restante.seconds % 60
            datos['error'] = f'Has alcanzado el límite de intentos. Inténtalo de nuevo en {minutos_restantes} minutos y {segundos_restantes} segundos.'
            return render(request, 'home/login.html', datos)

    
        user = authenticate(username=usuario, password=password)

        if user is not None:
            login(request, user)
            request.session[f'intentos_fallidos_{usuario}'] = 0
            recordarme = request.POST.get('recordarme')
            if recordarme == 'on':
                request.session.set_expiry(1209600)  # 2 semanas
            else:
                request.session.set_expiry(0)
            return redirect('index')
        else:

            intentos_fallidos += 1
            request.session[f'intentos_fallidos_{usuario}'] = intentos_fallidos

            if intentos_fallidos >= MAX_INTENTOS:
                bloqueo_hasta = timezone.now() + timezone.timedelta(minutes=BLOQUEO_MINUTOS)
                request.session[f'bloqueo_hasta_{usuario}'] = bloqueo_hasta.timestamp()
                datos['error'] = 'Has alcanzado el límite de intentos. Inténtalo de nuevo en 5 minutos.'
            else:
                datos['error'] = f'Usuario o contraseña incorrectos. Te quedan {MAX_INTENTOS - intentos_fallidos} intentos.'

            return render(request, 'home/login.html', datos)

    return render(request, 'home/login.html', datos)

def userlogout(request):
    logout(request)
    return redirect('index')

def registro(request):
    cartItems = getCantidadProductos(request)

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
        else:
            mensaje_error = "Por favor, corrige los errores en el formulario."
            datos = {
                'form': form,
                'cartItems': cartItems,
                'mensaje': mensaje_error  
            }
            return render(request, 'home/registro.html', datos)
    else:
        form = RegistroForm()
        datos = {
            'form': form,
            'cartItems': cartItems
        }
        return render(request, 'home/registro.html', datos)

@login_required
def perfil(request):
    usuario = request.user

    return render(request, 'home/perfil.html', {'user': usuario})


@login_required
def actualizar_perfil(request):
    try:
        perfil = Perfil.objects.get(user=request.user)
    except Perfil.DoesNotExist:
        perfil = Perfil.objects.create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        password_form = CambiarPasswordForm(user=request.user, data=request.POST)

        # Formularios para direcciones y empresas
        direccion_form = DireccionForm(request.POST)
        empresa_form = EmpresaForm(request.POST)

        if 'update_info' in request.POST:
            p_form = PerfilUpdateForm(request.POST, instance=perfil)
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, 'Información actualizada correctamente.')
                return redirect('actualizar_perfil')
        elif 'add_direccion' in request.POST:
            if direccion_form.is_valid():
                nueva_direccion = direccion_form.save(commit=False)
                nueva_direccion.perfil = perfil
                nueva_direccion.save()
                messages.success(request, 'Dirección añadida correctamente.')
                return redirect('actualizar_perfil')
        elif 'add_empresa' in request.POST:
            if empresa_form.is_valid():
                nueva_empresa = empresa_form.save(commit=False)
                nueva_empresa.perfil = perfil
                nueva_empresa.save()
                messages.success(request, 'Empresa añadida correctamente.')
                return redirect('actualizar_perfil')
        elif 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  
                messages.success(request, 'Contraseña cambiada correctamente.')
                return redirect('actualizar_perfil')  
        elif 'delete_direccion' in request.POST:
            direccion_id = request.POST.get('direccion_id')
            direccion = get_object_or_404(Direccion, id=direccion_id, perfil=perfil)
            direccion.delete()
            messages.success(request, 'Dirección eliminada correctamente.')
            return redirect('actualizar_perfil')
        elif 'delete_empresa' in request.POST:
            empresa_id = request.POST.get('empresa_id')
            empresa = get_object_or_404(Empresa, id=empresa_id, perfil=perfil)
            empresa.delete()
            messages.success(request, 'Empresa eliminada correctamente.')
            return redirect('actualizar_perfil')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = PerfilUpdateForm(instance=perfil)  
        password_form = CambiarPasswordForm(user=request.user)
        direccion_form = DireccionForm()
        empresa_form = EmpresaForm()

    # Obtener todas las direcciones y empresas
    direcciones = perfil.direcciones.all()
    empresas = perfil.empresas.all()

    if not perfil.rut:
        messages.warning(request, 'Por favor ingresa tu RUT.')

    return render(request, 'home/modificacion_usuario.html', {
        'u_form': u_form,
        'p_form': p_form,
        'password_form': password_form,
        'direccion_form': direccion_form,
        'empresa_form': empresa_form,
        'direcciones': direcciones,
        'empresas': empresas,
    })



def get_comunas(request, region_id):
    comunas = Comuna.objects.filter(region_id=region_id).values('id', 'nombre')
    return JsonResponse(list(comunas), safe=False)

def tienda(request):
    filtro=request.session.get('filtro',None)
    #agregar los filtros que pueden no estar
    filtro=get_filtros(filtro)
    if request.method == 'POST':
        filtro=request.session.get('filtro',None)
        print("FILTRO EN SESION",filtro)
        filtro=get_filtros(filtro)
        print("FILTRO EN TIENDA",filtro)
        form_id = request.POST.get('form_id')
        if form_id == 'formulario_marca':
            formFiltros = filtroMarca(request.POST)
            marca = formFiltros['marcas'].value()
            if marca != [] and marca != None:
                request.session['filtro'] = {'marca':marca}
            else:
                request.session['filtro'] = {'marca':None}
            request.session['filtro'] = {'precio_min':filtro.get('precio_min',None),'precio_max':filtro.get('precio_max',None),'marca':marca,'arrendador':filtro.get('arrendador',None),'region':filtro.get('region',None),'fecha_inicio':filtro.get('fecha_inicio',None),'fecha_termino':filtro.get('fecha_termino',None)}
        elif form_id == 'formulario_arrendador':
            formArrendador = filtroArrendador(request.POST)
            arrendador = formArrendador['arrendador'].value()
            if arrendador != [] and arrendador != None:
                request.session['filtro'] = {'arrendador':arrendador}
            else:
                request.session['filtro'] = {'arrendador':None}
            request.session['filtro'] = {'precio_min':filtro.get('precio_min',None),'precio_max':filtro.get('precio_max',None),'marca':filtro.get('marca',None),'arrendador':arrendador,'region':filtro.get('region',None),'fecha_inicio':filtro.get('fecha_inicio',None),'fecha_termino':filtro.get('fecha_termino',None)}
        elif form_id == 'formulario_precio':
            formPrecio = filtroPrecio(request.POST)
            precio_min = formPrecio['precio_min'].value()
            precio_max = formPrecio['precio_max'].value()
            if precio_max == '':
                precio_max = None
            request.session['filtro'] = {'precio_min':precio_min,'precio_max':precio_max,'marca':filtro.get('marca',None),'arrendador':filtro.get('arrendador',None),'region':filtro.get('region',None),'fecha_inicio':filtro.get('fecha_inicio',None),'fecha_termino':filtro.get('fecha_termino',None)}
        elif form_id == 'formulario_region':
            formRegion = filtroRegion(request.POST)
            region = formRegion['region'].value()
            request.session['filtro'] = {'precio_min':filtro.get('precio_min',None),'precio_max':filtro.get('precio_max',None),'marca':filtro.get('marca',None),'arrendador':filtro.get('arrendador',None),'region':region,'fecha_inicio':filtro.get('fecha_inicio',None),'fecha_termino':filtro.get('fecha_termino',None)}
        elif form_id == 'formulario_disponibilidad':
            formDisponibilidad = filtroDisponibilidad(request.POST)
            fechaRango=formDisponibilidad['fechaRango'].value()
            fecha_inicio=fechaRango.split(' ')[0]
            fecha_termino=fechaRango.split(' ')[2]
            request.session['filtro'] = {'precio_min':filtro.get('precio_min',None),'precio_max':filtro.get('precio_max',None),'marca':filtro.get('marca',None),'arrendador':filtro.get('arrendador',None),'region':filtro.get('region',None),'fecha_inicio':fecha_inicio,'fecha_termino':fecha_termino}
        else:
            request.session['filtro'] = None
        print("pos ",request.session['filtro'])
        return redirect('tienda')
    if filtro != None:
        productos = get_productos(request,filtro)
        print("productos filtrados",productos)
    else:
        productos = get_productos(request)
    formFiltros= filtroMarca()
    formArrendador = filtroArrendador()
    filtroPrecios = filtroPrecio()
    filtroRegiones = filtroRegion()
    filtroCombustibles = filtroCombustible()
    formDisponibilidad = filtroDisponibilidad()
    cartItems = getCantidadProductos(request)
    marcas = Producto.objects.values('marca').distinct()
    regiones = Region.objects.all()
    combustibles = {'Diesel':'Diesel','Gasolina':'Gasolina','Electrico':'Electrico'}
    arrendador = {'Particular':'Particular','Empresa':'Empresa'}
    tipo = {'Maquinaria':'Maquinaria','Vehiculo':'Vehiculo'}
    #se cargan los productos desde base de datos
    datos = {
        'productos': productos,
        'cartItems': cartItems,
        'marcas': marcas,
        'regiones': regiones,
        'combustibles': combustibles,
        'arrendador': arrendador,
        'tipo': tipo,
        'formFiltros': formFiltros,
        'formArrendador': formArrendador,
        'filtroPrecios': filtroPrecios,
        'filtroRegiones': filtroRegiones,
        'filtroCombustibles': filtroCombustibles,
        'formDisponibilidad': filtroDisponibilidad
    }

    return render(request, 'home/tienda.html',datos)

def get_filtros(filtro=None):
    if filtro == None:
        filtro = {
            'precio_min':None,
            'precio_max':None,
            'marca':None,
            'arrendador':None,
            'region':None
        }
    filtro['precio_min'] = filtro.get('precio_min',None)
    #si los valores no son numeros se asigna None
    if filtro['precio_min'] != None:
        try:
            filtro['precio_min'] = int(filtro['precio_min'])
        except:
            filtro['precio_min'] = None
    filtro['precio_max'] = filtro.get('precio_max',None)
    #si los valores no son numeros se asigna None
    if filtro['precio_max'] != None:
        try:
            filtro['precio_max'] = int(filtro['precio_max'])
        except:
            filtro['precio_max'] = None
    filtro['marca'] = filtro.get('marca',None)
    filtro['arrendador'] = filtro.get('arrendador',None)
    filtro['region'] = filtro.get('region',None)
    print("Filtros obtenidos",filtro)
    return filtro


def carrito(request, token_ws=None):
    cartItems = getCantidadProductos(request)
    orderItems = 0
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(cliente=request.user, pagoProcesado=False)
        orderItems = order.orderitem_set.all()
        #print(orderItems)
        if order.pagoProcesado == False:
            items = order.orderitem_set.all()
            for item in items:
                item.idProducto.imagen = ProductoImagen.objects.filter(producto=item.idProducto).first().imagen.url
                dias = item.fecha_termino - item.fecha_inicio
                dias = dias.days
                item.dias = dias +1
            cartItems = order.get_cart_items
    else:
        try:
            cart = request.COOKIES.get('cart')
            cart = urllib.parse.unquote(cart)
            cart = json.loads(cart)
            orderItems = []
            cartItems = cart.values().__len__()
            for i in cart:
                try:
                    vin= i.split('_')[0]
                    product = Producto.objects.get(VIN=vin)
                    orderItems.append(product)
                except:
                    pass
        except:
            cart = {}
        items = []
        order = {'get_cart_total':0, 'get_cart_items':cartItems}
        cartItems = order['get_cart_items']

        for i in cart:
            try:
                vin= i.split('_')[0]
                product = Producto.objects.get(VIN=vin)
                total = (product.precio)
                order['get_cart_total'] += total+int(product.costoEnvio)
                order['get_cart_items'] += 1
                
                fecha_inicio = cart[i]['fecha_inicio']
                fecha_fin = cart[i]['fecha_fin']

                fecha_inicio = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d')
                fecha_fin = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d')

                item = {
                    'idProducto':{
                        'VIN':product.VIN,
                        'nombre':product.nombre,
                        'precio':product.precio,
                        'imagenURL':ProductoImagen.objects.filter(producto=product.VIN).first().imagen.url,
                        'costoEnvio':product.costoEnvio,
                        'vendedor':product.vendedor,
                        'descripcion':product.descripcion,
                        'cantidad':1,
                        'dias':(fecha_fin - fecha_inicio).days,
                        'fecha_inicio':fecha_inicio.date(),
                        'fecha_termino':fecha_fin.date(),
                    }
                }
                print(item)
                items.append(item)
            except:
                pass
    comision = 0
    total = round(order.get_cart_total * 1.1)
    context = {'items': items, cartItems: 'cartItems','orderItems': orderItems, 'cartItems': cartItems, 'order': order, 'total': total}
    #si link viene con token, se debe llamar a confirmacion de pago
    if request.GET.get('token_ws'):
        token_ws = request.GET.get('token_ws')
        #print("Webpay Plus Transaction.commit")
        token = token_ws
        response = Transaction(WebpayOptions(commerce_code_integracion, api_key,'INTEGRATION')).commit(token) #Obtiene estado de transaccion
        if response['status'] == 'AUTHORIZED':
            #guardarTransaccion(response)
            order, created = Order.objects.get_or_create(cliente=request.user, pagoProcesado=False)
            total = order.get_cart_total
            comision = total * 0.1
            order.pagoProcesado = True
            order.save()
            #se genera la transacción en base de datos
            transaccion = Transaccion.objects.create(
                usuario=request.user,
                orden=order,
                monto=total+comision,
                estado='exitoso'
            )
            transaccion.save()
            print(f"Transacción creada: {transaccion}")

            return redirect('pago_exitoso', order_id=order.id)
        else:
            return redirect('pago_rechazado', order_id=order.id)
    elif request.method == 'POST' and request.POST.get('pago') == 'pago':
        if request.user.is_authenticated:
            return redirect('pago')
        else:

            return redirect('registro')
        #Se llama a pago
        return redirect('pago')
    
    #print(request.method,request.POST.get('action'))
    return render(request, 'home/carrito.html',context)

def actualizar_carrito(request):
    if request.user.is_authenticated:
        transaction_id = datetime.datetime.now().timestamp()
        data=json.loads(request.body)
        productId = data['productId']
        action = data['action']

        #print('Action:', action)
        #print('productId:', productId)

        customer = request.user
        product = Producto.objects.get(VIN=productId)
        orden, created = Order.objects.get_or_create(cliente=request.user, pagoProcesado=False)
        if orden.transaction_id == '0':
            orden.transaction_id= transaction_id
        orderItem, created = OrderItem.objects.get_or_create(idProducto=product, idUsuario=request.user,order=orden)

        #si el producto esta agregado se debe sumar 1, si no esta agregado se debe crear y sumar 1
        if action == 'add':
            if orderItem.cantidad == 0:
                orderItem.cantidad = 1
                orderItem.save()
            else:
                orderItem.cantidad = (orderItem.cantidad + 1)
                orderItem.save()
        else:
            orderItem.cantidad = (orderItem.cantidad - 1)
            orderItem.save()
            if orderItem.cantidad <= 0:
                orderItem.delete()

    #es necesario validar disponibilidad de maquina *necesario implementar a futuro.
    return JsonResponse('item agregado', safe=False)

def pago(request):
    user = request.user
    if user.is_authenticated:
        #print("Webpay Plus Transaction.create")
        order, created = Order.objects.get_or_create(cliente=request.user, pagoProcesado=False)
        session_id = (str(request.user)) #se genera session id *se debe cambiar por session id de usuario
        buy_order = str(order.transaction_id) #se genera orden de compra *se debe cambiar por orden de compra
        precioFinal = order.get_cart_total*1.1
        precioFinal = round(precioFinal)
        if precioFinal == 0:
            return redirect('carrito')
    else:
        order= json.loads(request.COOKIES.get('cart'))
        total = 0
        for item in order:
            producto = Producto.objects.get(VIN=item)
            total = total + ( producto.precio * order[item]['cantidad'])
            total *= 1.1
            total = round(total)
            #se crea oreden de compra y se le asigna un id de transaccion con timestamp  
        #print("Webpay Plus Transaction.create")
        buy_order = str(datetime.datetime.now().timestamp())
        session_id = ("ANON"+str(randrange(100000)))
        precioFinal = total
    
    amount = str(precioFinal)#monto de productos cargados en carrito
    return_url = request.build_absolute_uri('/carrito/') #url de retorno

    response = Transaction(WebpayOptions(commerce_code_integracion, api_key,'INTEGRATION')).create(buy_order, session_id, amount, return_url) #se llama a api de webpay

    url = response['url'] #se obtiene url de pago
    token = response['token'] #se obtiene token de pago *se debe guardar en base de datos para confirmacion de pago o devolucion de pago
    print(response)
    print(return_url)
          
    #print(response)
    return redirect(f'{url}?TBK_TOKEN={token}')
    #return render(request, 'home/carrito.html', {'request': create_request, 'response': response})


def pago_exitoso(request,order_id):
    orden = get_object_or_404(Order, id=order_id)
    orden.boleta_generada = True
    trans=Transaccion.objects.get(orden=orden)
    print("transaccion",trans.monto)
    items = orden.orderitem_set.all()
    context = {'orden': orden, 'items': items, 'trans':trans}
    return render(request,'home/pago_exitoso.html', context)

def pago_rechazado(request, order_id):
    orden = get_object_or_404(Order, id=order_id)
    context = {'orden': orden}
    return render(request, 'home/pago_rechazado.html',context)


@login_required
def agregar_producto_al_carrito(request, producto_id):
    producto = Producto.objects.get(VIN=producto_id)
    carrito = Carrito.objects.get(usuario=request.user)
    carrito.productos.add(producto)
    return HttpResponse('Producto agregado al carrito')

def agregar_producto_al_carrito_en_cookie(request, producto_id):
    producto = Producto.objects.get(VIN=producto_id)

    if(request.COOKIES.get('cart')):
        carrito = request.COOKIES.get('cart')
        carrito = carrito.split(',')
        carrito.append(producto_id)
        carrito = ','.join(carrito)
    else:
        carrito = producto_id
    response = HttpResponse('Producto agregado al carrito')
    response.set_cookie('carrito', carrito)
    return response

def obtener_carrito_de_cookie(request):
    if(request.COOKIES.get('cart')):
        carrito = request.COOKIES.get('cart')
        carrito = carrito.split(',')
    else:
        carrito = []
    return carrito

def obtener_carrito_de_usuario(request):
    carrito = Carrito.objects.get(usuario=request.user)
    return carrito.productos.all()



def misProductos(request):
    if not request.user.is_authenticated:
        return redirect(userlogin)
    
    DisponibilidadFormSet = modelformset_factory(
        Disponibilidad, 
        form=DisponibilidadForm, 
        extra=1)

    form = agregarProducto(request.POST, request.FILES,user=request.user)
    ImagenForm= ImagenFormSet(queryset=ProductoImagen.objects.none())
    dispForm = DisponibilidadFormSet(queryset=Disponibilidad.objects.none())
    cartItems = getCantidadProductos(request)
    productos = get_mis_productos(request)
    context = {'cartItems': cartItems, 'productos': productos, 'form': form, 'imagen_formset': ImagenForm, 'disponibilidad_formset': dispForm}
    if request.method == 'POST':
        vin=agregar_producto(request)
        if vin:
            return redirect('producto', VIN=vin)
        else:
            context['form'] = form
    return render(request, 'home/misProductos.html',context)

def get_productos(request,filtros=None):
    #colocar todos los filtros en un diccionario
    if filtros == None:
        filtros={
            'marca':None,
            'arrendador':None,
            'precio_min':None,
            'precio_max':None,
            'region':None,
            'fecha_inicio':None,
            'fecha_termino':None,
        }
    
    if filtros != None:
        productos = Producto.objects.all()
        if 'marca' in filtros and filtros['marca'] != None and filtros['marca'] != []:
            productos = productos.filter(marca__in=filtros['marca'])
        
        if 'arrendador' in filtros and filtros['arrendador'] != None and filtros['arrendador'] != []:
            arrendadores = User.objects.filter(username__in=filtros['arrendador'])
            productos = productos.filter(vendedor__in=arrendadores)
        
        if 'precio_min' in filtros and filtros['precio_min'] != None:
            productos = productos.filter(precio__gte=filtros['precio_min'])
        
        if 'precio_max' in filtros and filtros['precio_max'] != None:
            productos = productos.filter(precio__lte=filtros['precio_max'])
        if 'region' in filtros and filtros['region'] != None and filtros ['region'] != [] and filtros['region'] != '':
            try:
                region = Region.objects.get(nombre=filtros['region'])
                productos = productos.filter(region=region)
            except Region.DoesNotExist:
                productos = productos.none()
        if 'fecha_inicio' in filtros and filtros['fecha_inicio'] != None and filtros['fecha_inicio'] != '':
            fecha_inicio = datetime.datetime.strptime(filtros['fecha_inicio'], '%Y-%m-%d')
            if 'fecha_termino' in filtros and filtros['fecha_termino'] != None and filtros['fecha_termino'] != '':
                fecha_termino = datetime.datetime.strptime(filtros['fecha_termino'], '%Y-%m-%d')
                disponibilidades = Disponibilidad.objects.filter(fecha_inicio__lte=fecha_inicio, fecha_termino__gte=fecha_termino)
                productos = productos.filter(disponibilidades__in=disponibilidades)
            else:
                disponibilidades = Disponibilidad.objects.filter(fecha_inicio__lte=fecha_inicio)
                productos = productos.filter(disponibilidades_in=disponibilidades)
    else:
        productos = Producto.objects.all()
    
    for producto in productos:
        producto.imagen = ProductoImagen.objects.filter(producto=producto).first()
    return productos

def get_mis_productos(request):
    productos = Producto.objects.filter(vendedor=request.user)
    for producto in productos:
        producto.imagen = ProductoImagen.objects.filter(producto=producto).first()
    return productos

def userlogout(request):
    logout(request)
    return redirect(userlogin)

def checkout(request):
    cartItems = getCantidadProductos(request)
    context = {'cartItems': cartItems}
    #hace falta implementar checkout automatico
    return render(request, 'home/checkout.html',context)

def modificar_producto(request, producto_id):
    producto = get_object_or_404(Producto, VIN=producto_id)

    if request.method == 'POST':
        form = modificarProductoFrom(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = modificarProductoFrom(instance=producto)

    context = {'form': form, 'producto': producto}
    return render(request, 'home/misProductos.html', context)

def agregar_producto(request):
    print("Agregando producto")
    form = productoForm()
    vendedor = request.user
    print(vendedor)
    if request.method == 'POST':
        print("POST")


        #obtener calendarios de disponibilidad con name disponibilidad_rango
        rangos_fechas = []
        for key in request.POST:
            if 'rango_fecha' in key:
                valores = request.POST.getlist(key)
                for valor in valores:
                    rangos_fechas.append(valor)
                    print(key)
                    print(valor)
        print("Rangos de fechas:", rangos_fechas)

        form = productoForm(request.POST, request.FILES)
        imagen_formset = ImagenFormSet(request.POST, request.FILES)
        form.instance.vendedor = vendedor
        if form.instance.costoEnvio == None or form.instance.costoEnvio == '' or form.instance.costoEnvio == 0:
            form.instance.costoEnvio = 0
        print("EL COSTO DE ENVÍO ES: ",form.instance.costoEnvio)
        print(vendedor)
        if form.is_valid() and imagen_formset.is_valid():
            print("Formulario valido")
            product = form.save(commit=False)
            product.vendedor = vendedor
            product.save()
            for imagen in imagen_formset:
                print("guardando imagen")
                image = imagen.save(commit=False)
                image.producto = product
                image.save()
                print("Imagen guardada")
            #recargar pagina
            form.save()
            for rango in rangos_fechas:
                if rango == '':
                    continue
                elif rango.split(' ').__len__() == 1:
                    fecha_inicio = rango
                    fecha_termino = rango
                else:
                    fecha_inicio = rango.split(' ')[0]
                    fecha_termino = rango.split(' ')[2]
                disponibilidad = Disponibilidad(Producto=product, fecha_inicio=fecha_inicio, fecha_termino=fecha_termino)
                disponibilidad.save()
            return product.VIN
#
    else:
        print("GET")
        form = agregarProducto()
        imagen_formset = ImagenFormSet(queryset=ProductoImagen.objects.none())
    context = {'form':form}

def eliminar_producto(request,VIN):
    producto = Producto.objects.get(VIN=VIN)
    producto.delete()
    return redirect('index')

def busqueda(request): #busqueda de productos mediante barra de busqueda
    query = request.GET.get('query')
    if query:
        productos = Producto.objects.filter(nombre__icontains=query)
        for producto in productos:
            producto.imagen = ProductoImagen.objects.filter(producto=producto).first()
        #print(productos)
        context = {'productos':productos}
        render(request, 'home/tienda.html',context)
    else:
        productos = Producto.objects.all()
    context = {'productos':productos}
    return render(request, 'home/tienda.html',context)


def afiliados(request):
    return render(request, 'home/afiliados.html')

def cargar():
    Region.objects.all().delete()
    Comuna.objects.all().delete()
    region=Region.objects.all()
    regiones = open('home/static/home/js/regiones.json', 'r')
    regiones = regiones.read()
    #colocar datos json en mapa
    regiones = json.loads(regiones)
    print(regiones)
    for region in regiones['regiones']:
        aux=Region.objects.create(nombre=region['region'])
        for comuna in region['comunas']:
            Comuna.objects.create(nombre=comuna, region=aux)
    
#cargar()
        
def comunas(request, id):
    print("obteniendo datos")
    region = Region.objects.get(id=id)
    comunas = Comuna.objects.filter(region=region)
    comunas_list = list(comunas.values())
    comunas_json = json.dumps(comunas_list)
    return HttpResponse(comunas_json, content_type='application/json')



def add_to_cart(request):
    data = json.loads(request.body)
    data['success'] = False

    print("DATA",data)
    
    if request.user.is_authenticated and request.method == 'POST':
        productId = data['producto_id']
        action = data.get('action', 'add')

        try:
            customer = request.user
            product = Producto.objects.get(VIN=productId)
            order, created = Order.objects.get_or_create(cliente=request.user, pagoProcesado=False)
        
            fecha_inicio = data['fecha_inicio']
            fecha_termino = data['fecha_fin']
            print("fehca de inicio y termino",fecha_inicio, fecha_termino)
            orderItem = OrderItem.objects.filter(idProducto=product, idUsuario=request.user, order=order).first()

            if not orderItem:
                orderItem = OrderItem(idProducto=product, idUsuario=request.user, order=order, cantidad=0)

            if action == 'add':
                OrderItem.objects.create(idProducto=product, idUsuario=request.user ,order=order, cantidad=1, fecha_inicio=datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d").date(), fecha_termino=datetime.datetime.strptime(fecha_termino, "%Y-%m-%d").date())
            else:
                orderItem.cantidad -= 1
            
            orderItem.save()

            if orderItem.cantidad <= 0:
                orderItem.delete()
                data['removed'] = True  # Indica que el producto ha sido eliminado
            else:
                data['removed'] = False

            total_items = OrderItem.objects.filter(order=order).aggregate(total=Sum('cantidad'))['total'] or 0
            
            data['success'] = True
            data['newCount'] = total_items  # Enviar el nuevo total de artículos en la respuesta
        except Producto.DoesNotExist:
            data['success'] = False
            data['message'] = "Producto no encontrado"
        except Exception as e:
            data['success'] = False
            data['message'] = str(e)

    return JsonResponse(data)

def preguntas_frecuentes(request):
    faqs = [
    {
        "pregunta": "¿Cómo puedo registrar un vehículo o maquinaria en la plataforma?",
        "respuesta": "Para registrar un vehículo o maquinaria, debes iniciar sesión en tu cuenta y acceder a la sección de 'Mis Productos'. Allí encontrarás un formulario donde podrás ingresar todos los detalles del equipo que deseas publicar, incluyendo características, fotografías y precios de alquiler. Una vez completado, solo tienes que seguir las indicaciones para finalizar el registro."
    },
    {
        "pregunta": "¿Qué documentos necesito para publicar un vehículo?",
        "respuesta": "Generalmente, necesitarás proporcionar documentos que verifiquen la propiedad del vehículo, como el título de propiedad, y en algunos casos, el seguro vigente y la identificación del propietario. Los requisitos específicos pueden variar, por lo que te recomendamos revisar nuestra sección de ayuda o comunicarte con soporte para obtener detalles exactos."
    },
    {
        "pregunta": "¿Qué métodos de pago aceptan?",
        "respuesta": "Aceptamos una variedad de métodos de pago seguros, que incluyen tarjetas de crédito y débito. La disponibilidad de cada método dependerá de tu ubicación y de los servicios de WebPay."
    },
    {
        "pregunta": "¿Cómo puedo cancelar una reserva?",
        "respuesta": "Puedes cancelar una reserva accediendo a tu cuenta en la sección de 'Mis Reservas'. Selecciona la reserva que deseas cancelar y sigue las instrucciones de cancelación. Ten en cuenta que puede aplicarse una política de cancelación dependiendo de cuándo realices la cancelación."
    },
    {
        "pregunta": "¿La plataforma garantiza la calidad de los vehículos o maquinarias?",
        "respuesta": "La plataforma verifica la documentación y estado de los productos listados, pero la calidad final del vehículo o maquinaria depende de cada propietario. Te recomendamos revisar las fotos y la descripción detalladamente y, si es posible, contactar al propietario para aclarar cualquier duda antes de realizar la reserva."
    },
    {
        "pregunta": "¿Qué hago si tengo un problema con un producto alquilado?",
        "respuesta": "En caso de que tengas algún inconveniente con el producto alquilado, contacta primero al propietario para resolverlo de forma directa. Si no puedes solucionar el problema, comunícate con nuestro equipo de soporte para recibir asistencia."
    },
    {
        "pregunta": "¿Puedo modificar o eliminar mi anuncio después de publicarlo?",
        "respuesta": "Sí, puedes modificar o eliminar tu anuncio en cualquier momento desde tu cuenta en la sección de 'Mis Productos'. Simplemente selecciona el anuncio que deseas editar o eliminar y sigue las instrucciones que aparecerán."
    },
    {
        "pregunta": "¿Hay un límite en la cantidad de productos que puedo publicar?",
        "respuesta": "No existe un límite específico en la cantidad de productos que puedes publicar, aunque recomendamos que mantengas solo aquellos que estén realmente disponibles. Sin embargo, si tienes un número grande de productos, puede ser necesario cumplir con ciertos requisitos adicionales."
    },
    {
        "pregunta": "¿Cuánto tiempo se tarda en procesar un pago?",
        "respuesta": "Los tiempos de procesamiento pueden variar según el método de pago que hayas elegido. Por lo general, los pagos con tarjeta de crédito y servicios en línea se procesan inmediatamente, mientras que las transferencias bancarias pueden tardar entre 1 y 3 días hábiles."
    },
    {
        "pregunta": "¿Cómo protegen mis datos personales?",
        "respuesta": "Tomamos la protección de tus datos personales muy en serio. Utilizamos encriptación y otras medidas de seguridad para asegurar la protección de tu información y cumplir con las normativas de privacidad vigentes. Puedes obtener más detalles en nuestra política de privacidad."
    }
]

    return render(request, 'home/preguntas_frecuentes.html', {'faqs': faqs})

def atencion_cliente(request):
    return render(request, 'home/atencion_cliente.html')

@login_required
def dashboard(request):
    arriendos = OrderItem.objects.filter(idProducto__vendedor=request.user)
    hoy = timezone.now()
    productos = Producto.objects.filter(vendedor=request.user)
    arriendos = OrderItem.objects.filter(idProducto__vendedor=request.user)
    transacciones = Order.objects.filter(orderitem__idUsuario=request.user)

    total_productos = productos.count()
    total_arriendos = arriendos.count()

    hace_una_semana = hoy - timedelta(weeks=1)
    hace_15_dias = hoy - timedelta(days=15)
    hace_un_mes = hoy - timedelta(days=30)
    hace_un_anio = hoy - timedelta(days=365)

    ingresos_1_semana = sum(item.get_total for item in arriendos.filter(order__date_ordered__gte=hace_una_semana))
    ingresos_15_dias = sum(item.get_total for item in arriendos.filter(order__date_ordered__gte=hace_15_dias))
    ingresos_1_mes = sum(item.get_total for item in arriendos.filter(order__date_ordered__gte=hace_un_mes))
    ingresos_1_anio = sum(item.get_total for item in arriendos.filter(order__date_ordered__gte=hace_un_anio))

    
    total_ganancias = sum(item.get_total for item in arriendos)

  
    tasa_utilizacion = arriendos.values('idProducto__nombre').annotate(total_arriendos=Count('id')).order_by('-total_arriendos')
    for item in tasa_utilizacion:
        item['porcentaje'] = (item['total_arriendos'] / total_arriendos) * 100
        item['porcentaje'] = round(item['porcentaje'], 0)
  
    ganancias_por_maquinaria = {}
    for item in arriendos:
        producto_nombre = item.idProducto.nombre
        if producto_nombre in ganancias_por_maquinaria:
            ganancias_por_maquinaria[producto_nombre] += item.get_total
        else:
            ganancias_por_maquinaria[producto_nombre] = item.get_total

   
    ganancias_por_maquinaria = [{'producto_nombre': nombre, 'ganancias': ganancia} for nombre, ganancia in ganancias_por_maquinaria.items()]

    maquinaria_arriendada = arriendos.values('idProducto__nombre').annotate(cantidad=Count('id')).order_by('-cantidad')

    
    compras = OrderItem.objects.filter(idUsuario=request.user)

    context = {
        'productos': productos,
        'arriendos': arriendos,
        'transacciones': transacciones,
        'total_productos': total_productos,
        'total_arriendos': total_arriendos,
        'total_ganancias': total_ganancias,
        'tasa_utilizacion': tasa_utilizacion,
        'ganancias_por_maquinaria': ganancias_por_maquinaria,
        'maquinaria_arriendada': maquinaria_arriendada,
        'compras': compras,
         'ingresos_1_semana': ingresos_1_semana,
        'ingresos_15_dias': ingresos_15_dias,
        'ingresos_1_mes': ingresos_1_mes,
        'ingresos_1_anio': ingresos_1_anio,
    }

    return render(request, 'home/dashboard.html', context)

def eula(request):
    return render(request, 'home/eula.html')
def privacidad(request):
    return render(request, 'home/privacidad.html')

@user_passes_test(is_admin)
@login_required
def dashboard_admin(request):
    productos = Producto.objects.all()
    usuarios = User.objects.all()
    arriendos = OrderItem.objects.all()
    transacciones = Order.objects.all()

    total_productos = productos.count()
    total_usuarios = usuarios.count()
    total_arriendos = arriendos.count()

    hoy = timezone.now()
    hace_una_semana = hoy - timedelta(weeks=1)
    hace_15_dias = hoy - timedelta(days=15)
    hace_un_mes = hoy - timedelta(days=30)
    hace_1_anio = hoy - timedelta(days=365)

    ingresos_1_semana = sum(item.get_total for item in arriendos.filter(order__date_ordered__gte=hace_una_semana))
    ingresos_15_dias = sum(item.get_total for item in arriendos.filter(order__date_ordered__gte=hace_15_dias))
    ingresos_1_mes = sum(item.get_total for item in arriendos.filter(order__date_ordered__gte=hace_un_mes))
    ingresos_1_anio = sum(item.get_total for item in arriendos.filter(order__date_ordered__gte=hace_1_anio))
    

    total_ganancias = sum(item.get_total for item in arriendos)

    tasa_utilizacion = arriendos.values('idProducto__nombre').annotate(total_arriendos=Count('id')).order_by('-total_arriendos')
    for item in tasa_utilizacion:
        item['porcentaje'] = (item['total_arriendos'] / total_arriendos) * 100
        item['porcentaje'] = round(item['porcentaje'], 0)

    ganancias_por_maquinaria = {}

    for item in arriendos:
        producto_nombre = item.idProducto.nombre
        if producto_nombre in ganancias_por_maquinaria:
            ganancias_por_maquinaria[producto_nombre] += item.get_total
        else:
            ganancias_por_maquinaria[producto_nombre] = item.get_total

    ganancias_por_maquinaria = [{'producto_nombre': nombre, 'ganancias': ganancia} for nombre, ganancia in ganancias_por_maquinaria.items()]

    maquinaria_arriendada = arriendos.values('idProducto__nombre').annotate(cantidad=Count('id')).order_by('-cantidad')

    top_arrendadores = arriendos.values('idProducto__vendedor__username').annotate(total_arriendos=Count('id')).order_by('-total_arriendos')[:5]

    total_arriendos_top = sum(item['total_arriendos'] for item in top_arrendadores)


    for item in top_arrendadores:
        item['porcentaje'] = (item['total_arriendos'] / total_arriendos_top) * 100
        item['porcentaje'] = round(item['porcentaje'], 0)
    context = {
        'productos': productos,
        'usuarios': usuarios,
        'arriendos': arriendos,
        'transacciones': transacciones,
        'total_productos': total_productos,
        'total_usuarios': total_usuarios,
        'total_arriendos': total_arriendos,
        'total_ganancias': total_ganancias,

        'tasa_utilizacion': tasa_utilizacion,
        'ganancias_por_maquinaria': ganancias_por_maquinaria,
        'maquinaria_arriendada': maquinaria_arriendada,
        'top_arrendadores': top_arrendadores,

        'ingresos_1_semana': ingresos_1_semana,
        'ingresos_15_dias': ingresos_15_dias,
        'ingresos_1_mes': ingresos_1_mes,
        'ingresos_1_anio': ingresos_1_anio,

    }

    return render(request, 'home/dashboard_admin.html', context)




@login_required
def misArriendos(request):

    ordenes = Order.objects.filter(cliente=request.user).order_by('-date_ordered')
    ordenes_con_items = []
    for orden in ordenes:
        items = OrderItem.objects.filter(order=orden)
        ordenes_con_items.append({
            'orden': orden,
            'items': items,
        })

    return render(request, 'home/misArriendos.html', {'ordenes_con_items': ordenes_con_items})

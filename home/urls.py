#from tkinter import Menu
from unicodedata import name
from django import views
from django.urls import path,include
from home.views import * 
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', index, name='index'),
    path('nosotros/', nosotros, name='nosotros'),
    path('login/', userlogin, name='userlogin'),
    path('tienda/', tienda, name='tienda'),
    path('carrito/', carrito, name='carrito'),
    path('pago/', pago, name='pago'),
    path('producto/<str:VIN>/', producto, name='producto'),
    path('pago_exitoso/<int:order_id>/', pago_exitoso, name='pago_exitoso'),
    path('pago_rechazado/<int:order_id>/', pago_rechazado, name='pago_rechazado'),
    path('actualizar_carrito/', actualizar_carrito, name='actualizar_carrito'),
    path('registro/', registro, name='registro'),
    path('logout/', userlogout, name='userlogout'),
    path('misProductos/', misProductos, name='misProductos'),
    path('checkout/', checkout, name='checkout'),
    path('modificar_producto/<str:VIN>/', modificar_producto, name='modificar_producto'),
    path('eliminar_producto/<str:VIN>/', eliminar_producto, name='eliminar_producto'),
    path('tienda/busqueda/', busqueda, name='busqueda'),
    path('afiliados/', afiliados, name='afiliados'),
    #path('afiliados/registro/', afiliados_registro, name='afiliados_registro'),
    path('dashboard/', dashboard, name='dashboard'),
    path('comunas/<str:id>/', comunas, name='comunas'),
    #path('contact/', contact, name='contact'),
    #path('tracker/', tracker, name='tracker'),
    #path('search/', search, name='search'),
    #path('products/<int:myid>', productView, name='productView'),
    path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('preguntas_frecuentes/', preguntas_frecuentes, name='preguntas_frecuentes'),
    path('atencion_cliente/', atencion_cliente, name='atencion_cliente'),
    path('eula/', eula, name='eula'),
    path('politicas_privacidad/', privacidad, name='politicas_privacidad'),
    path('admin_dashboard/', dashboard_admin, name='dashboard_admin'),
 path('misArriendos/', misArriendos, name='misArriendos'),
    path('comunas/<int:region_id>/', get_comunas, name='get_comunas'),

    path('perfil/', perfil, name='perfil'),
    path('actualizar_perfil/', actualizar_perfil, name='actualizar_perfil'),
    path('oauth/', include('social_django.urls', namespace='social'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
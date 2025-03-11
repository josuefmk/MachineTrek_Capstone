from django.contrib import admin
from .models import Producto, Carrito, Customer, Order, OrderItem, Region, Comuna, ProductoImagen, Transaccion, Perfil, Disponibilidad

# Register your models here.


admin.site

admin.site.register(Producto)
admin.site.register(Carrito)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Region)
admin.site.register(Comuna)
admin.site.register(ProductoImagen)
admin.site.register(Transaccion)
admin.site.register(Perfil)
admin.site.register(Disponibilidad)
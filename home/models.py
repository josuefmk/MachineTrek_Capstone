from django.db import models

import datetime
import re
import django.contrib.admin
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
# Create your models here.


class loginForm(models.Model):
    username = models.CharField(max_length=100,verbose_name='usuario')
    password = models.CharField(max_length=100, verbose_name='password')
    checkbox = models.BooleanField(default=False, verbose_name='recordarme')



class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=10)  

    def __str__(self):
        return f"{self.user.username} - {self.rut}"

class Direccion(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='direcciones', default=1) 
    direccion = models.CharField(max_length=100, verbose_name='Dirección')

    def __str__(self):
        return self.direccion


class Empresa(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='empresas')
    nombre = models.CharField(max_length=100, verbose_name='Nombre de la Empresa')
    direccion = models.CharField(max_length=100, verbose_name='Dirección de la Empresa')
    rutEmpresa = models.CharField(max_length=10, verbose_name='RUT de la empresa' ,null=True, blank=True)  
    comunaEmpresa = models.CharField(max_length=100, verbose_name='Comuna de la empresa', null=True, blank=True)
    regionEmpresa = models.CharField(max_length=100, verbose_name='Region la empresa',  null=True, blank=True)
    telefonoEmpresa = models.CharField(max_length=100, verbose_name='Teléfono de la empresa', null=True, blank=True)
    emailEmpresa = models.CharField(max_length=100, verbose_name='Email de la empresa', null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.perfil.user.username})"

    
class modificarProductoFrom(models.Model):
    Nombre = models.CharField(max_length=100,verbose_name='nombre')
    Precio = models.IntegerField(verbose_name='precio')
    Oferta = models.BooleanField(default=False, verbose_name='oferta')
    PrecioAnterior = models.IntegerField(verbose_name='precio anterior',default=0)
    Descuento = models.IntegerField(verbose_name='descuento',default=0, null=True, help_text='Ingrece el porcentaje de descuento. Ejemplo: 10%')
    tipoEnvio = models.CharField(max_length=100,verbose_name='tipo de envio',default='')
    costoEnvio = models.FloatField(verbose_name='costo de envio',default=0)
    Descripcion = models.TextField(verbose_name='descripcion')
    region = models.CharField(max_length=100,verbose_name='region')
    comuna = models.CharField(max_length=100,verbose_name='comuna')
    imagen = models.ImageField(verbose_name='imagen', storage=S3Boto3Storage(), upload_to='productos/', default='default.jpg')


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100, verbose_name='nombre')
    apellido = models.CharField(max_length=100, verbose_name='apellido')
    rut = models.CharField(max_length=100, verbose_name='rut')
    email = models.CharField(max_length=100, verbose_name='email')
    password = models.CharField(max_length=2000, verbose_name='password')
    telefono = models.CharField(max_length=100, verbose_name='telefono')
    direccion = models.CharField(max_length=100, verbose_name='direccion')
    comuna = models.CharField(max_length=100, verbose_name='comuna')
    region = models.CharField(max_length=100, verbose_name='region')

    class Meta:
        db_table = 'User'
    
    def __str__(self):
        return self.nombre
    
class Region(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name='nombre')
    class Meta:
        db_table = 'Region'
    def __str__(self):
        return self.nombre
        
    
class Comuna(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name='nombre')
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    codigoPostal = models.CharField(max_length=10, verbose_name='Código Postal', null=True, blank=True)
    class Meta:
        db_table = 'Comuna'
    def __str__(self):
        return self.nombre
    
class Producto(models.Model):
    marca = models.CharField(max_length=100, verbose_name='marca', default='')
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE)  # vendedor es el nombre de la tienda, esto se obtiene desde el usuario.
    nombre = models.CharField(max_length=100, verbose_name='nombre', default='')
    precio = models.IntegerField(verbose_name='precio', default=0)
    oferta = models.BooleanField(default=False, verbose_name='oferta', blank=True)  # si es oferta, se debe ingresar el precio anterior (precioAnterior)
    precioAnterior = models.IntegerField(verbose_name='precio anterior', default=0)
    descuento = models.IntegerField(verbose_name='descuento', default=0, null=True, help_text='Ingrese el porcentaje de descuento. Ejemplo: 10%')  # porcentaje de descuento, solo es necesario si es oferta (oferta = True)
    VIN = models.CharField(primary_key=True, verbose_name='VIN', max_length=100, default='')  # VIN es el código de producto, es único para cada producto.
    patente = models.CharField(max_length=100, verbose_name='patente', default='', blank=True)  # patente es el código de producto, es único para cada producto.
    descripcion = models.TextField(verbose_name='descripcion', default='')
    tipoEnvio = models.CharField(max_length=100, verbose_name='tipo de envio', default='')  # tipo de envio, ej: envio gratis, envio por pagar, etc.
    costoEnvio = models.IntegerField(verbose_name='costo de envio', default=0)  # costo de envio, solo es necesario si es envio por pagar.
    total = models.IntegerField(verbose_name='total', default=0)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'Producto'
    
    def __str__(self):
        return self.VIN
    
    def save(self, *args, **kwargs):
        if self.precioAnterior is None:
            self.precioAnterior = 0
        if self.descuento:
            descuento_decimal = self.descuento / 100
            self.precioAnterior = self.precio
            self.precio = round(self.precio - round(self.precio * descuento_decimal))
        if self.precio:
            if self.costoEnvio is None:
                self.costoEnvio = 0
            self.total = self.precio + self.costoEnvio
        super().save(*args, **kwargs)

class Disponibilidad(models.Model):
    Producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='disponibilidades')
    fecha_inicio = models.DateTimeField(verbose_name='fecha inicio', default=timezone.now)
    fecha_termino = models.DateTimeField(verbose_name='fecha termino', default=timezone.now)

    def __str__(self):
        return f'{self.Producto.nombre}: {self.fecha_inicio} - {self.fecha_termino}'


class ProductoImagen(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    imagen = models.ImageField(verbose_name='Imagen principal', storage=S3Boto3Storage(), upload_to='productos/', default='default.jpg')
    
    class Meta:
        db_table = 'ProductoImagen'
    
    def __str__(self):
        return self.producto.VIN
    

class Carrito(models.Model):
    id = models.AutoField(primary_key=True)
    idUsuario = models.ForeignKey(User, on_delete=models.CASCADE)
    idOrder = models.ForeignKey('Order', on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.IntegerField(verbose_name='cantidad')
    class Meta:
        db_table = 'Carrito'
    def __str__(self):
        return self.idUsuario    

class DireccionEnvio(models.Model):
    id = models.AutoField(primary_key=True)
    idUsuario = models.ForeignKey(User, on_delete=models.CASCADE)
    calle = models.CharField(max_length=100,verbose_name='calle')
    numero = models.IntegerField(verbose_name='numero')
    comuna = models.CharField(max_length=100,verbose_name='comuna')
    region = models.CharField(max_length=100,verbose_name='region')
    estado = models.CharField(max_length=100, verbose_name='estado', default='Por definir')
    class Meta:
        db_table = 'DireccionEnvio'
    def __str__(self):
        return self.idUsuario

class Order(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank = True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    pagoProcesado = models.BooleanField(default=False)
    enPreparacion = models.BooleanField(default=False)
    enRetiro = models.BooleanField(default=False)
    retirado = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, default=timezone.now().timestamp()) 
    DireccionEnvio = models.ForeignKey('DireccionEnvio', on_delete=models.SET_NULL, blank=True, null=True)
    boleta_generada = models.BooleanField(default=False, null=True)

    def __str__(self):
        return str(self.id)
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.cantidad for item in orderitems])
        return total
    @property
    def get_comision_total(self):
        total = self.get_cart_total * 0.1
        total = round(total)
        return total
    
class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    idUsuario = models.ForeignKey(User, on_delete=models.CASCADE)
    idProducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(verbose_name='cantidad', default=0)
    fecha_inicio = models.DateField(verbose_name='fecha inicio', default=timezone.now,null=True)
    fecha_termino = models.DateField(verbose_name='fecha termino', default=timezone.now,null=True)
    costo_compra = models.IntegerField(verbose_name='costo compra', default=0, null=True)
    class Meta:
        db_table = 'OrderItem'
    def __str__(self):
        return f'{self.idProducto.pk}'
    @property
    def get_total(self):
        dias = (self.fecha_termino - self.fecha_inicio).days+1
        total = self.idProducto.total * dias
        return total
    @property
    def get_comision(self):
        comision = self.get_total * 0.1
        comision = round(comision)
        print("COMISION", comision)
        return comision


class Home(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
    url = models.URLField(blank=True)

    def __str__(self):
        return self.title

class Transaccion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  
    orden = models.ForeignKey('Order', on_delete=models.CASCADE)  
    monto = models.IntegerField(verbose_name='Monto')  
    estado = models.CharField(max_length=20, choices=[
        ('exitoso', 'Exitoso'),
        ('rechazado', 'Rechazado'),
    ], default='exitoso')  # Estado del pago
    
    def __str__(self):
        return f"Transacción {self.id} para Orden {self.orden.id}"

class Arriendo(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()
    costo = models.FloatField()

    def __str__(self):
        return f'Arriendo de {self.producto.nombre} por {self.usuario.username}'

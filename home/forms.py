from django import forms
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from django.utils.safestring import mark_safe
from .models import loginForm , Producto, modificarProductoFrom, User, Region, Comuna,Perfil, Direccion, Empresa,Disponibilidad, ProductoImagen


class loginForm(forms.ModelForm):
    usuario = forms.CharField(label='Usuario', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    recordarme = forms.BooleanField(label='Recordarme', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    class Meta:
        model = loginForm
        fields = ['usuario', 'password', 'recordarme']
class RegistroForm(UserCreationForm):
    first_name = forms.CharField(
        label='Nombre',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    rut = forms.CharField(
        label='RUT',
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        label='Nombre de Usuario',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Tu contraseña debe contener al menos 8 caracteres, incluyendo números y letras."
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Ingresa nuevamente la contraseña para confirmar."
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'rut', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Este nombre de usuario ya está en uso. Por favor, elige otro.")
        return username

    def clean_rut(self):
        rut = self.cleaned_data.get("rut")
        # Elimina la validación de RUT
        # validar_rut(rut)  

        # Verificar si el RUT ya está registrado
        if Perfil.objects.filter(rut__iexact=rut).exists():
            raise ValidationError("Este RUT ya está registrado.")
        return rut

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este email ya está registrado.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r'[A-Za-z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra.")
        if not re.search(r'\d', password1):
            raise ValidationError("La contraseña debe contener al menos un número.")
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Las contraseñas no coinciden.")

        return cleaned_data

    def save(self, commit=True):
        user = super(RegistroForm, self).save(commit=False)
        if commit:
            user.save()
            Perfil.objects.create(
                user=user,
                rut=self.cleaned_data["rut"]
            )
        return user
class DireccionForm(forms.ModelForm):
    direccion = forms.CharField(
        label='Dirección',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Direccion
        fields = ['direccion']





class EmpresaForm(forms.ModelForm):
    nombre = forms.CharField(
        label='Nombre de la Empresa',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    direccion = forms.CharField(
        label='Dirección de la Empresa',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    rutEmpresa = forms.CharField(
        label='RUT de la Empresa',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    regionEmpresa = forms.ModelChoiceField(
        label='Región de la Empresa',
        queryset=Region.objects.all(),
        empty_label='Seleccione una región',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    comunaEmpresa = forms.ModelChoiceField(
        label='Comuna de la Empresa',
        queryset=Comuna.objects.none(),
        empty_label='Seleccione una comuna',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    telefonoEmpresa = forms.CharField(
        label='Teléfono de la Empresa',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    emailEmpresa = forms.EmailField(
        label='Email de la Empresa',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Empresa
        fields = ['nombre', 'direccion', 'rutEmpresa', 'regionEmpresa', 'comunaEmpresa', 'telefonoEmpresa', 'emailEmpresa']
   

class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Nombre',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get("email")
        user_id = self.instance.id
        if User.objects.filter(email__iexact=email).exclude(id=user_id).exists():
            raise ValidationError("Este email ya está registrado por otro usuario.")
        return email

class PerfilUpdateForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['rut']  

    def clean_rut(self):
        rut = self.cleaned_data.get("rut")
        perfil_id = self.instance.id
        if Perfil.objects.filter(rut__iexact=rut).exclude(id=perfil_id).exists():
            raise ValidationError("Este RUT ya está registrado por otro usuario.")
        return rut

class CambiarPasswordForm(DjangoPasswordChangeForm):
    old_password = forms.CharField(
        label='Contraseña Actual',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    new_password1 = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        help_text="Tu contraseña debe contener al menos 8 caracteres, incluyendo números y letras."
    )
    new_password2 = forms.CharField(
        label='Confirmar Nueva Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        help_text="Ingresa nuevamente la contraseña para confirmar."
    )

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        if len(password1) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r'[A-Za-z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra.")
        if not re.search(r'\d', password1):
            raise ValidationError("La contraseña debe contener al menos un número.")
    
        return password1

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error('new_password2', "Las contraseñas no coinciden.")

        return cleaned_data

class agregarProducto(forms.ModelForm):
    marca = forms.CharField(label='Marca', widget=forms.TextInput(attrs={'class': 'form-control'}),error_messages={'required': ''})
    VIN = forms.CharField(label='VIN', widget=forms.TextInput(attrs={'class': 'form-control'}), required=True,error_messages={'required': ''})
    patente = forms.CharField(label='Patente', widget=forms.TextInput(attrs={'class': 'form-control'}) ,required=False)
    nombre = forms.CharField(label='Nombre', widget=forms.TextInput(attrs={'class': 'form-control'}), required=True,error_messages={'required': ''})
    precio = forms.IntegerField(label='Precio', widget=forms.TextInput(attrs={'class': 'form-control'}),  required=True,initial=0,error_messages={'required': ''})
    oferta = forms.BooleanField(label='Oferta', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id':'id_oferta'}))
    precioAnterior = forms.IntegerField(label='Precio anterior', widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_precioAnterior'}) ,required=False, initial=0)
    descuento = forms.FloatField(label='Descuento', required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'id':'id_descuento'}), initial=0)
    descripcion = forms.CharField(label='Descripcion', widget=forms.TextInput(attrs={'class': 'form-control'}), required=True,error_messages={'required': ''})
    tipoEnvio = forms.ChoiceField(
        label='Tipo de envio',
        choices=[('gratis', 'Gratis'), ('retiro', 'Retiro'), ('flete', 'Flete')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        error_messages={'required': ''}
    )
    costoEnvio = forms.IntegerField(
        label='Costo de envio',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
        required=False,
        initial=0
    )
    vendedor = forms.ModelChoiceField(label='Vendedor', queryset=User.objects.all(), widget=forms.HiddenInput(),required=False)
    region = forms.ModelChoiceField(label='Region', queryset=Region.objects.all(), widget=forms.Select( attrs={'id':'regionProducto'}),required=True,error_messages={'required': ''})
    comuna = forms.ModelChoiceField(label='Comuna', queryset=Comuna.objects.none(), widget=forms.Select( attrs={'id':'comunaProducto'}),required=True,error_messages={'required': ''})

    def __init__(self, *args,user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendedor'].initial = user
        
        #Agregar asterisco rojo a los campos obligatorios
        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"<span style='color: red;'>*</span> {field.label}"  
                field.label = mark_safe(field.label)  
                
    class Meta:
        model = Producto
        fields = ['VIN', 'patente', 'marca', 'nombre', 'precio', 'oferta', 'precioAnterior', 'descuento', 'descripcion', 'region', 'comuna', 'tipoEnvio', 'costoEnvio']    

class modificarProductoFrom(forms.ModelForm):
    vendedor = forms.CharField(label='Vendedor', widget=forms.TextInput(attrs={'class': 'form-control'}))
    nombre = forms.CharField(label='Nombre', widget=forms.TextInput(attrs={'class': 'form-control'}))
    precio = forms.FloatField(label='Precio', widget=forms.TextInput(attrs={'class': 'form-control'}))
    oferta = forms.BooleanField(label='Oferta', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    precioAnterior = forms.FloatField(label='Precio anterior', widget=forms.TextInput(attrs={'class': 'form-control'}))
    descuento = forms.FloatField(label='Descuento', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(label='Descripcion', widget=forms.TextInput(attrs={'class': 'form-control'}))
    tipoEnvio = forms.CharField(label='Tipo de envio', widget=forms.TextInput(attrs={'class': 'form-control'}))
    costoEnvio = forms.FloatField(label='Costo de envio', widget=forms.TextInput(attrs={'class': 'form-control'}))
    imagen = forms.ImageField(label='Imagen', widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Producto
        fields = ['vendedor', 'nombre', 'precio', 'oferta', 'precioAnterior', 'descuento', 'descripcion', 'tipoEnvio', 'costoEnvio', 'imagen']

class productoForm(forms.ModelForm):
    VIN = forms.CharField(label='VIN', widget=forms.TextInput(attrs={'class': 'form-control'}))
    marca = forms.CharField(label='Marca', widget=forms.TextInput(attrs={'class': 'form-control'}))
    nombre = forms.CharField(label='Nombre', widget=forms.TextInput(attrs={'class': 'form-control'}))
    precio = forms.FloatField(label='Precio', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    oferta = forms.BooleanField(label='Oferta', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    descuento = forms.FloatField(label='Descuento', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(label='Descripcion', widget=forms.Textarea(attrs={'class': 'form-control'}))
    tipoEnvio = forms.CharField(label='Tipo de envio', widget=forms.TextInput(attrs={'class': 'form-control'}))
    costoEnvio = forms.FloatField(label='Costo de envio', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Producto
        fields = ['VIN', 'marca', 'nombre', 'precio', 'oferta', 'descuento', 'descripcion', 'tipoEnvio', 'costoEnvio']

class Regiones (forms.ModelForm):
    nombre = forms.CharField(label='Nombre', widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Region
        fields = ['nombre']


class DisponibilidadForm(forms.ModelForm):
    rango_fecha = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'id_rango_fecha',
            'class': 'form-control',
            'placeholder': 'Selecciona un rango de fechas'
        }),
        required=False  # Para evitar que el campo sea obligatorio en el formset
    )

    class Meta:
        model = Disponibilidad
        fields = []  # No incluimos 'fecha_inicio' ni 'fecha_termino' directamente

    def clean(self):
        cleaned_data = super().clean()
        rango_fecha = cleaned_data.get('rango_fecha')

        if rango_fecha:
            fechas = rango_fecha.split(' to ')  # flatpickr devuelve un rango con ' to '
            if len(fechas) == 2:
                fecha_inicio, fecha_termino = fechas
                cleaned_data['fecha_inicio'] = fecha_inicio
                cleaned_data['fecha_termino'] = fecha_termino
            else:
                raise forms.ValidationError("Por favor, selecciona un rango de fechas válido.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.fecha_inicio = self.cleaned_data.get('fecha_inicio')
        instance.fecha_termino = self.cleaned_data.get('fecha_termino')
        if commit:
            instance.save()
        return instance


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result




class ImagenForm(forms.ModelForm):
    image = MultipleFileField(label= 'Cargar más imágenes', required=False)
    class Meta:
        model = ProductoImagen
        fields = ['imagen']

ImagenFormSet = forms.inlineformset_factory(Producto, ProductoImagen, form=ImagenForm, extra=1,can_delete=False)


class filtroMarca(forms.Form):
    marcas = forms.ModelMultipleChoiceField(
        queryset=Producto.objects.values_list('marca', flat=True).distinct(), 
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input','name':"marca",'class':"marca-checkbox"}), 
        required=False)

class filtroArrendador(forms.Form):
    arrendador = forms.ModelChoiceField(
        queryset=User.objects.filter(producto__isnull=False).distinct(), 
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input','name':"arrendador",'class':"arrendador-checkbox"}),
        required=False,
        to_field_name='username'
    )

class filtroPrecio(forms.Form):
    precio_min = forms.FloatField(label='Precio minimo', widget=forms.NumberInput(attrs={'class': 'form-control', 'id':'precioMin'}), required=False)
    precio_max = forms.FloatField(label='Precio maximo', widget=forms.NumberInput(attrs={'class': 'form-control','id':'precioMax'}), required=False)

class filtroRegion(forms.Form):
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-control','id':'region'}), 
        required=False,
        to_field_name='nombre'
    )

class filtroCombustible(forms.Form):
    combustible = forms.ChoiceField(
        choices=[('Todos','Todos'),('Bencina', 'Bencina'), ('Diesel', 'Diesel'), ('Electrico', 'Electrico'), ('Hibrido', 'Hibrido')],
        widget=forms.Select(attrs={'class': 'form-control','id':'combustible'}), 
        required=False
    )

class filtroDisponibilidad(forms.Form):
    fechaRango = forms.CharField(label='Fecha', widget=forms.TextInput(attrs={'class': 'form-control', 'id':'fechaRango'}), required=False)
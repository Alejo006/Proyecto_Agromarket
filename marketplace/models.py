from django.db import models
from django.utils import timezone
from datetime import timedelta

# 🔵 Función para fecha de expiración por defecto
def default_fecha_expiracion():
    return timezone.now() + timedelta(days=2)

class Usuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('Agricultor', 'Agricultor'),
        ('Consumidor', 'Consumidor'),
        ('Empresa', 'Empresa'),
    ]
    
    nombre = models.CharField(max_length=255)
    documento = models.CharField(max_length=50, unique=True)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    contraseña = models.TextField()
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES)

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre

class ProductoAgricultor(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo_usuario': 'Agricultor'})
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=50)
    cantidad_disponible = models.PositiveIntegerField()
    ubicacion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class ProductoEmpresa(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo_usuario': 'Empresa'})
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=5, decimal_places=2)
    unidad_medida = models.CharField(max_length=50)
    cantidad_disponible = models.PositiveIntegerField()
    ubicacion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre_empresa = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

class ImagenProducto(models.Model):
    producto_agricultor = models.ForeignKey(ProductoAgricultor, on_delete=models.CASCADE, null=True, blank=True, related_name='imagenes')
    producto_empresa = models.ForeignKey(ProductoEmpresa, on_delete=models.CASCADE, null=True, blank=True, related_name='imagenes')

    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)  # ← CAMBIO AQUÍ

    def clean(self):
        from django.core.exceptions import ValidationError
        if (self.producto_agricultor and self.producto_empresa) or (not self.producto_agricultor and not self.producto_empresa):
            raise ValidationError('Debe estar asociado a un solo tipo de producto, no a ambos o ninguno.')

    def __str__(self):
        return str(self.imagen)

class Separacion(models.Model):
    consumidor = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo_usuario': 'Consumidor'})
    producto_agricultor = models.ForeignKey(ProductoAgricultor, on_delete=models.CASCADE, null=True, blank=True)
    producto_empresa = models.ForeignKey(ProductoEmpresa, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.PositiveIntegerField()
    fecha_separacion = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField(default=default_fecha_expiracion)

    def clean(self):
        from django.core.exceptions import ValidationError
        if (self.producto_agricultor and self.producto_empresa) or (not self.producto_agricultor and not self.producto_empresa):
            raise ValidationError('Debe separar solo un tipo de producto, no ambos o ninguno.')

    def __str__(self):
        return f"Separación de {self.consumidor.nombre}"







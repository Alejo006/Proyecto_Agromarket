from django.db import models
from django.utils import timezone
from datetime import timedelta

# 🔵 Función para definir una fecha de expiración por defecto (2 días desde el momento actual)
def default_fecha_expiracion():
    return timezone.now() + timedelta(days=2)

# 🔵 Modelo para representar a los usuarios del sistema
class Usuario(models.Model):
    # Opciones de tipo de usuario: Agricultor, Consumidor o Empresa
    TIPO_USUARIO_CHOICES = [
        ('Agricultor', 'Agricultor'),
        ('Consumidor', 'Consumidor'),
        ('Empresa', 'Empresa'),
    ]
    
    nombre = models.CharField(max_length=255)  # Nombre del usuario
    documento = models.CharField(max_length=50, unique=True)  # Documento único de identificación
    correo = models.EmailField(unique=True)  # Correo electrónico único
    telefono = models.CharField(max_length=20)  # Número telefónico
    direccion = models.TextField()  # Dirección del usuario
    contraseña = models.TextField()  # Contraseña (⚠️ debe cifrarse en producción)
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES)  # Tipo de usuario

    def __str__(self):
        return self.nombre  # Representación legible del objeto

# 🔵 Modelo para representar categorías de productos
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)  # Nombre único de la categoría
    descripcion = models.TextField(null=True, blank=True)  # Descripción opcional

    def __str__(self):
        return self.nombre

# 🔵 Modelo para productos publicados por agricultores
class ProductoAgricultor(models.Model):
    # Solo se permiten usuarios con tipo 'Agricultor'
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

# 🔵 Modelo para productos publicados por empresas
class ProductoEmpresa(models.Model):
    # Solo se permiten usuarios con tipo 'Empresa'
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo_usuario': 'Empresa'})
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=5, decimal_places=2)  # Descuento en porcentaje
    unidad_medida = models.CharField(max_length=50)
    cantidad_disponible = models.PositiveIntegerField()
    ubicacion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre_empresa = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

# 🔵 Modelo para las imágenes asociadas a productos (de agricultor o empresa)
class ImagenProducto(models.Model):
    # Asociaciones opcionales, pero debe existir solo una (se valida en clean)
    producto_agricultor = models.ForeignKey(ProductoAgricultor, on_delete=models.CASCADE, null=True, blank=True, related_name='imagenes')
    producto_empresa = models.ForeignKey(ProductoEmpresa, on_delete=models.CASCADE, null=True, blank=True, related_name='imagenes')

    # Campo de imagen que se almacena en la carpeta 'productos/'
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)  # ← CAMBIO AQUÍ

    def clean(self):
        # Validación para asegurar que solo se asocie a un tipo de producto (no ambos ni ninguno)
        from django.core.exceptions import ValidationError
        if (self.producto_agricultor and self.producto_empresa) or (not self.producto_agricultor and not self.producto_empresa):
            raise ValidationError('Debe estar asociado a un solo tipo de producto, no a ambos o ninguno.')

    def __str__(self):
        return str(self.imagen)

# 🔵 Modelo para registrar una separación de producto por parte de un consumidor
class Separacion(models.Model):
    consumidor = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo_usuario': 'Consumidor'})  # Solo consumidores pueden separar
    producto_agricultor = models.ForeignKey(ProductoAgricultor, on_delete=models.CASCADE, null=True, blank=True)
    producto_empresa = models.ForeignKey(ProductoEmpresa, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.PositiveIntegerField()
    fecha_separacion = models.DateTimeField(default=timezone.now)  # Fecha y hora actual
    fecha_expiracion = models.DateTimeField(default=default_fecha_expiracion)  # Por defecto, 2 días después

    def clean(self):
        # Validación para asegurar que la separación sea de solo un tipo de producto
        from django.core.exceptions import ValidationError
        if (self.producto_agricultor and self.producto_empresa) or (not self.producto_agricultor and not self.producto_empresa):
            raise ValidationError('Debe separar solo un tipo de producto, no ambos o ninguno.')

    def __str__(self):
        return f"Separación de {self.consumidor.nombre}"

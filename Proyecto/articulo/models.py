from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver

class Piezas(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)  # Este es el nombre de la pieza. Es un campo de texto con un máximo de 200 caracteres.
    ficha_historica = models.TextField()  # Este es un campo de texto para la ficha histórica de la pieza.
    fecha_de_ingreso = models.DateField()  # Esta es la fecha en que la pieza ingresó. Es un campo de fecha.
    personal_ingresante = models.CharField(max_length=200)  # Este es el personal que ingresó la pieza. Es un campo de texto con un máximo de 200 caracteres.
    fecha_de_registro = models.DateTimeField(auto_now_add=True)  # Esta es la fecha y hora en que se registró la pieza. Se establece automáticamente en el momento en que se crea la pieza.

class Imagen(models.Model):
    pieza = models.ForeignKey(Piezas, related_name='imagenes', on_delete=models.CASCADE)  # Este es un enlace a la pieza a la que pertenece esta imagen. Si la pieza se elimina, también se eliminará esta imagen.
    imagen = models.ImageField(upload_to='piezas/', null=True, blank=True)  # Este es el campo de la imagen. Las imágenes se subirán al directorio 'piezas/'. Este campo puede estar vacío.


class Donante(models.Model):
    TIPO_ID = [
        ('V', 'VENEZOLANO'),
        ('E', 'EXTRANJERO'),
        ('P', 'RIF PERSONAL'),
        ('J', 'RIF JURIDICO'),
    ]

    tipo_identidad = models.CharField(max_length=1, choices=TIPO_ID, default='V')  # Tipo de identidad del donante
    numero_identidad = models.CharField(max_length=10, unique=True, default='0000000000')
    nombre_apellido = models.CharField(max_length=200)  # Nombre y apellido del donante
    numero_telefono = models.CharField(max_length=15)  # Número de contacto del donante
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.tipo_identidad} {self.numero_identidad} - {self.nombre_apellido}'

@receiver(post_save, sender=Donante)
def log_donante_save(sender, instance, created, **kwargs):
    action = 'creó' if created else 'actualizó'
    Bitacora.objects.create(user=instance.user, action=f'{action} un donante')

@receiver(pre_delete, sender=Donante)
def log_donante_delete(sender, instance, **kwargs):
    Bitacora.objects.create(user=instance.user, action='va a eliminar un donante')

class Bitacora(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username if self.user else "Usuario desconocido"} {self.action} at {self.timestamp}'

@receiver(post_save, sender=Piezas)
def log_pieza_save(sender, instance, created, **kwargs):
    action = 'creó' if created else 'actualizó'
    Bitacora.objects.create(user=instance.user, action=f'{action} una pieza')

@receiver(post_delete, sender=Piezas)
def log_pieza_delete(sender, instance, **kwargs):
    Bitacora.objects.create(user=instance.user, action='eliminó una pieza')


class Artesano(models.Model):
    codigo = models.CharField(max_length=100, primary_key=True)
    nombre_y_apellido = models.CharField(max_length=200)
    biografia = models.TextField()

class Referencias(models.Model):
    Codigo_de_Referencia = models.AutoField(primary_key=True)
    Exposiciones = models.CharField(max_length=200)
    Tratamiento = models.CharField(max_length=200)
    Ubicacion_Deposito = models.CharField(max_length=200)

class DatosTecnicos(models.Model):
    Codigo_de_Datos_Tecnicos = models.AutoField(primary_key=True)
    Procedencia = models.CharField(max_length=200)
    Cultura = models.CharField(max_length=200)
    Valor = models.DecimalField(max_digits=10, decimal_places=2)
    Propetario_Original = models.CharField(max_length=200)

class EstadoConservacion(models.Model):
    Codigo_de_Estado_de_Conservacion = models.AutoField(primary_key=True)
    Condicion = models.CharField(max_length=200)
    Integridad = models.CharField(max_length=200)

class SolicitudPrestamo(models.Model):
    nombre_solicitante = models.CharField(max_length=100)
    pieza_solicitada = models.ForeignKey(Piezas, on_delete=models.CASCADE)
    fecha_solicitud = models.DateField(auto_now_add=True)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import PiezasForm, ImagenForm, UserForm, DonanteForm, ArtesanoForm, EstadoConservacionForm, DatosTecnicosForm, ReferenciasForm, SolicitudPrestamoForm
from .models import Piezas, Imagen, Donante, Bitacora, Artesano, EstadoConservacion, Referencias, DatosTecnicos, SolicitudPrestamo
@login_required
def create_user(request):
    # Esta vista permite al superusuario crear nuevos usuarios.
    # Solo se puede acceder a esta vista si el usuario está autenticado.
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        if request.user.is_superuser:  # Solo permitir al superusuario crear nuevos usuarios
            User.objects.create_user(username=username, password=password, email=email)
            return HttpResponse('Usuario creado exitosamente')
        else:
            return HttpResponse('No tienes permiso para crear usuarios')
    else:
        form = UserForm()  # Crea una instancia del formulario
    return render(request, 'crear_usuario.html', {'form': form})

def vista_principal(request):
    # Esta es la vista de la aplicación.
    # Cuando un usuario visita tu sitio, esta es la primera página que verá.
    return render(request, 'pantalla_principal.html')

@login_required
def agregar_pieza(request):
    # Esta vista permite a los usuarios agregar nuevas piezas a la base de datos.
    # Si la solicitud es POST, se valida el formulario y se guarda la nueva pieza.
    # Si la solicitud es GET, se muestra el formulario para agregar una nueva pieza.
    if request.method == 'POST':
        form = PiezasForm(request.POST)
        if form.is_valid():
            pieza = form.save(commit=False)
            pieza.user = request.user
            pieza.save()
            for file in request.FILES.getlist('imagenes'):
                Imagen.objects.create(imagen=file, pieza=pieza)
            return redirect('consultar_piezas')
    else:
        form = PiezasForm()

    return render(request, 'agregar_pieza.html', {'form': form})

def consultar_piezas(request):
    # Esta vista muestra todas las piezas en la base de datos.
    # Se obtienen todas las piezas con Piezas.objects.all() y luego se pasan al template.
    piezas = Piezas.objects.all()
    return render(request, 'consultar_piezas.html', {'piezas': piezas})

def editar_piezas(request, id_pieza):
    # Esta vista permite a los usuarios editar piezas existentes.
    # Si la solicitud es POST, se valida el formulario y se guardan los cambios.
    # Si la solicitud es GET, se muestra el formulario para editar la pieza.
    pieza = get_object_or_404(Piezas, id=id_pieza)
    if request.method == 'POST':
        form = PiezasForm(request.POST, instance=pieza)
        if form.is_valid():
            form.save()
            for file in request.FILES.getlist('imagenes'):
                Imagen.objects.create(imagen=file, pieza=pieza)
            return redirect('consultar_piezas')
    else:
        form = PiezasForm(instance=pieza)

    return render(request, 'editar_piezas.html', {'form': form})

def eliminar_piezas(request, id_pieza):
    # Esta vista permite a los usuarios eliminar piezas existentes.
    # Si la solicitud es POST, se elimina la pieza.
    # Si la solicitud es GET, se redirige al usuario a la página de consulta de piezas.
    pieza = get_object_or_404(Piezas, id=id_pieza)
    if request.method == 'POST':
        pieza.delete()
        return redirect('consultar_piezas')  # Redirige a la página de consulta de piezas
    # Si no es una solicitud POST, simplemente redirige sin confirmación
    return redirect('consultar_piezas')

def vista_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Aquí creamos el registro en la bitácora
            Bitacora.objects.create(user=user, action='inició sesión')
            return redirect('vista_principal')
    return render(request, 'login.html')

def logout_view(request):
    # Antes de cerrar la sesión, creamos el registro en la bitácora
    Bitacora.objects.create(user=request.user, action='cerró sesión')
    logout(request)
    return redirect('login')

@login_required
def registrar_donante(request):
    if request.method == 'POST':
        form = DonanteForm(request.POST)
        if form.is_valid():
            donante = form.save(commit=False)
            donante.user = request.user
            donante.save()
            return redirect('listar_donantes')
    else:
        form = DonanteForm()
    return render(request, 'registrar_donante.html', {'form': form})

def listar_donantes(request):
    donantes = Donante.objects.all()
    return render(request, 'listar_donantes.html', {'donantes': donantes})

def editar_donante(request, numero_identidad):
    donante = get_object_or_404(Donante, numero_identidad=numero_identidad)
    if request.method == 'POST':
        form = DonanteForm(request.POST, instance=donante)
        if form.is_valid():
            form.save()
            return redirect('listar_donantes')
    else:
        form = DonanteForm(instance=donante)
    return render(request, 'editar_donante.html', {'form': form})

@login_required
def eliminar_donante(request, numero_identidad):
    donante = Donante.objects.get(numero_identidad=numero_identidad)
    if request.method == 'POST':
        Bitacora.objects.filter(user=donante.user).delete()
        donante.delete()
        if request.user.is_authenticated:
            Bitacora.objects.create(user=request.user, action='eliminó un donante')
        return redirect('listar_donantes')
    return render(request, 'eliminar_donante.html', {'donante': donante})

def bitacora_view(request):
    bitacora = Bitacora.objects.all().order_by('-timestamp')
    return render(request, 'bitacora.html', {'bitacora': bitacora})

def crear_artesano(request):
    if request.method == 'POST':
        form = ArtesanoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vista_principal')
    else:
        form = ArtesanoForm()
    return render(request, 'crear_artesano.html', {'form': form})

def listar_artesanos(request):
    artesanos = Artesano.objects.all()
    return render(request, 'listar_artesanos.html', {'artesanos': artesanos})

def nueva_referencia(request):
    if request.method == "POST":
        form = ReferenciasForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('referencias')
    else:
        form = ReferenciasForm()
    return render(request, 'nueva_referencia.html', {'form': form})

def editar_referencia(request, pk):
    referencia = get_object_or_404(Referencias, pk=pk)
    if request.method == "POST":
        form = ReferenciasForm(request.POST, instance=referencia)
        if form.is_valid():
            form.save()
            return redirect('referencias')
    else:
        form = ReferenciasForm(instance=referencia)
    return render(request, 'editar_referencia.html', {'form': form})

def eliminar_referencia(request, pk):
    referencia = get_object_or_404(Referencias, pk=pk)
    if request.method == "POST":
        referencia.delete()
        return redirect('referencias')
    return render(request, 'eliminar_referencia.html', {'object': referencia})

def listar_referencias(request):
    referencias = Referencias.objects.all()
    return render(request, 'listar_referencias.html', {'referencias': referencias})

def nuevo_dato_tecnico(request):
    if request.method == "POST":
        form = DatosTecnicosForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('datostecnicos')
    else:
        form = DatosTecnicosForm()
    return render(request, 'nuevo_dato_tecnico.html', {'form': form})

def editar_dato_tecnico(request, pk):
    dato_tecnico = get_object_or_404(DatosTecnicos, pk=pk)
    if request.method == "POST":
        form = DatosTecnicosForm(request.POST, instance=dato_tecnico)
        if form.is_valid():
            form.save()
            return redirect('datostecnicos')
    else:
        form = DatosTecnicosForm(instance=dato_tecnico)
    return render(request, 'editar_dato_tecnico.html', {'form': form})

def eliminar_dato_tecnico(request, pk):
    dato_tecnico = get_object_or_404(DatosTecnicos, pk=pk)
    if request.method == "POST":
        dato_tecnico.delete()
        return redirect('datostecnicos')
    return render(request, 'eliminar_dato_tecnico.html', {'object': dato_tecnico})

def listar_datos_tecnicos(request):
    datos_tecnicos = DatosTecnicos.objects.all()
    return render(request, 'listar_datos_tecnicos.html', {'datos_tecnicos': datos_tecnicos})

def nuevo_estado_conservacion(request):
    if request.method == "POST":
        form = EstadoConservacionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('estadoconservacion')
    else:
        form = EstadoConservacionForm()
    return render(request, 'nuevo_estado_conservacion.html', {'form': form})

def editar_estado_conservacion(request, pk):
    estado_conservacion = get_object_or_404(EstadoConservacion, pk=pk)
    if request.method == "POST":
        form = EstadoConservacionForm(request.POST, instance=estado_conservacion)
        if form.is_valid():
            form.save()
            return redirect('estadoconservacion')
    else:
        form = EstadoConservacionForm(instance=estado_conservacion)
    return render(request, 'editar_estado_conservacion.html', {'form': form})

def eliminar_estado_conservacion(request, pk):
    estado_conservacion = get_object_or_404(EstadoConservacion, pk=pk)
    if request.method == "POST":
        estado_conservacion.delete()
        return redirect('estadoconservacion')
    return render(request, 'eliminar_estado_conservacion.html', {'object': estado_conservacion})

def listar_estados_conservacion(request):
    estados_conservacion = EstadoConservacion.objects.all()
    return render(request, 'listar_estados_conservacion.html', {'estados_conservacion': estados_conservacion})

def mostrar_web(request):
    piezas = Piezas.objects.all()
    return render(request, 'web.html', {'piezas': piezas})

def solicitar_prestamo(request):
    if request.method == 'POST':
        form = SolicitudPrestamoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mostrar_web')
    else:
        form = SolicitudPrestamoForm()
    return render(request, 'solicitar_prestamo.html', {'form': form})

def solicitudes_prestamos(request):
    solicitudes = SolicitudPrestamo.objects.all() # Obtén todas las solicitudes de préstamo
    return render(request, 'solicitudes_prestamos.html', {'solicitudes': solicitudes})
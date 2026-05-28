from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.

# Vista para manejar el inicio de sesión de los usuarios
def login_view(request):
    # Si el usuario envía el formulario (POST)
    if request.method == "POST":
        # Creamos una instancia del formulario con los datos recibidos
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Si los datos son válidos (usuario y clave correctos), obtenemos el usuario
            user = form.get_user()
            # Iniciamos la sesión en el navegador
            login(request, user)
            messages.success(request, f"¡Bienvenido de nuevo, {user.username}!")
            # Redirige a la página de inicio (sedes) o a donde intentaba entrar antes
            return redirect(request.GET.get('next', 'index'))
        else:
            # Mensaje de error si el usuario o contraseña no coinciden
            messages.error(request, "Usuario o contraseña incorrectos. Verifica las mayúsculas.")
    else:
        # Si es una petición normal (GET), mostramos el formulario vacío
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

# Vista para cerrar la sesión actual
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión exitosamente.")
    return redirect('login')

# Vista para ver y editar el perfil del usuario
@login_required
def profile_view(request):
    user = request.user
    if request.method == "POST":
        # Capturamos los datos del formulario de modificación
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, "Tu perfil ha sido actualizado correctamente.")
        return redirect('profile')
    return render(request, 'profile.html', {'user': user})

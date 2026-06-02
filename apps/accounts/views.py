from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import user as custom_user, role as account_role
from django.contrib.auth.hashers import make_password, check_password

# Create your views here.

# Vista para manejar el inicio de sesión de los usuarios
def login_view(request):
    if request.method == "POST":
        username_val = request.POST.get('username', '').strip()
        password_val = request.POST.get('password', '').strip()

        # Validación básica de campos vacíos
        if not username_val or not password_val:
            messages.warning(request, "Por favor, ingrese tanto el usuario como la contraseña.")
            return render(request, "login.html")

        # 1. Búsqueda en la tabla personalizada 'accounts_user'
        user_record = custom_user.objects.filter(
            username=username_val, 
            is_active=True
        ).first()

        # 2. Verificación de credenciales
        if user_record and check_password(password_val, user_record.password):
            
            # 3. Validar que el rol sea ID 1
            # Verificamos que role_id no sea None antes de comparar
            if user_record.role_id_id != 1:
                messages.error(request, "Acceso denegado: No tiene permisos de administrador.")
                return render(request, "login.html")

            # 4. Iniciar sesión
            request.session['user_id'] = user_record.id
            request.session['username'] = user_record.username
            
            messages.success(request, "¡Bienvenido!")
            return redirect('add_sede')
        
        else:
            # Error genérico por seguridad
            messages.error(request, "Usuario o contraseña incorrectos.")
            return render(request, "login.html")
            
    # 5. Si no es POST, mostrar el formulario
    return render(request, "login.html")



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

# Vista para el registro de nuevos usuarios
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # form.save() guarda el usuario en la base de datos de forma permanente
            user = form.save()
            
            # Si el usuario NO está logueado, hacemos auto-login (flujo normal de registro)
            if not request.user.is_authenticated:
                login(request, user)
                messages.success(request, f"¡Cuenta creada exitosamente! Bienvenido, {user.username}.")
                return redirect('index')
            else:
                # Si ya estás logueado, solo confirmamos la creación y volvemos al perfil
                messages.success(request, f"Usuario '{user.username}' creado correctamente.")
                return redirect('profile')
        else:
            messages.error(request, "No se pudo crear la cuenta. Verifica que la contraseña sea segura.")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})

# Vista para el registro manual en la tabla personalizada 
@login_required
def custom_register_view(request):
    if request.method == "POST":
        username_val = request.POST.get('username')
        password_val = request.POST.get('password')
        role_id_val = request.POST.get('role_id')

        if username_val and password_val:
            # Buscamos el objeto Rol si se seleccionó uno
            role_obj = None
            if role_id_val:
                role_obj = account_role.objects.filter(id=role_id_val).first()

            # Guardamos manualmente en la tabla personalizada 'accounts_user'
            # Usamos make_password para que la clave sea segura (formato de 128 caracteres)
            custom_user.objects.create(
                username=username_val,
                password=make_password(password_val),
                role_id=role_obj,
                is_active=True
            )
            messages.success(request, f"Usuario '{username_val}' registrado exitosamente en la tabla personalizada.")
            return redirect('profile')
        else:
            messages.error(request, "El nombre de usuario y la contraseña son obligatorios.")

    roles_list = account_role.objects.all()
    return render(request, "custom_register.html", {"roles": roles_list})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.bookings.views import reservations_db # Importamos la lista de reservas

# --- SIMULACIÓN DE BASE DE DATOS PARA SEDES Y AMBIENTES ---
# Movido fuera de la función para que sea global y editable durante la ejecución del servidor
sedes_data = {
    # Sede Principal CATA con su lista de ambientes
    'sena-cata': {
        'nombre': 'SENA CATA', 
        'icon': 'bi-building-fill-check',
        'descripcion': 'Sede principal enfocada en tecnologías avanzadas y coordinación técnica.',
        'ambientes': [
            'AMBIENTE 201', 'AMBIENTE 202', 'AMBIENTE 203', 'AMBIENTE 204', 
            'AMBIENTE 205', 'AMBIENTE 206', 'AMBIENTE 207', 'AMBIENTE 208', 
            'BIBLIOTECA', 'BILINGÜISMO', 'GASTRONOMIA', 'SALON MULTIPLE'
        ]
    },
    # Sede Casa de Apoyo
    'casa-de-apoyo': {
        'nombre': 'Casa de Apoyo', 
        'icon': 'bi-house-gear-fill',
        'descripcion': 'Espacios dedicados al soporte administrativo y bienestar del aprendiz.',
        'ambientes': ['Sala de Juntas', 'Oficina Bienestar']
    },
    # Sede Granja
    'granja': {
        'nombre': 'Granja', 
        'icon': 'bi-tree-fill',
        'descripcion': 'Ambientes de formación agroindustrial y proyectos productivos sostenibles.',
        'ambientes': ['Invernadero', 'Establo', 'Apiario', 'Zona de Cultivo']
    },
}

# Vista para listar las sedes y ambientes
@login_required
def environment_list(request):
    # Pasamos el diccionario de sedes para que la lista sea dinámica
    return render(request, 'environment_list.html', {'sedes': sedes_data})

# Vista para mostrar los ambientes específicos de una sede
@login_required
def environment_detail(request, sede_slug):
    # Obtenemos la información completa de la sede solicitada
    sede_info = sedes_data.get(sede_slug)
    if not sede_info:
        return redirect('environment_list')

    context = {
        'sede': sede_info,
        'sede_slug': sede_slug, # Lo pasamos para construir las URLs en el template
        'reservations': reservations_db, # Pasamos las reservas para mostrarlas en el detalle
    }
    return render(request, 'environment_detail.html', context)

# Vista para agregar un nuevo ambiente a una sede
@login_required
def add_environment(request, sede_slug):
    if request.method == "POST":
        nombre = request.POST.get('nombre_ambiente').upper()
        if nombre and sede_slug in sedes_data:
            if nombre not in sedes_data[sede_slug]['ambientes']:
                sedes_data[sede_slug]['ambientes'].append(nombre)
                messages.success(request, f"Ambiente '{nombre}' agregado exitosamente.")
            else:
                messages.error(request, "Ese ambiente ya existe en esta sede.")
    return redirect('environment_detail', sede_slug=sede_slug)

# Vista para eliminar un ambiente de una sede
@login_required
def delete_environment(request, sede_slug, ambiente_name):
    if sede_slug in sedes_data:
        if ambiente_name in sedes_data[sede_slug]['ambientes']:
            sedes_data[sede_slug]['ambientes'].remove(ambiente_name)
            messages.success(request, f"Ambiente '{ambiente_name}' eliminado correctamente.")
    return redirect('environment_detail', sede_slug=sede_slug)

# Vista para modificar el nombre de un ambiente existente
@login_required
def edit_environment(request, sede_slug, ambiente_name):
    if request.method == "POST":
        nuevo_nombre = request.POST.get('nuevo_nombre').upper()
        if nuevo_nombre and sede_slug in sedes_data:
            ambientes = sedes_data[sede_slug]['ambientes']
            if ambiente_name in ambientes:
                if nuevo_nombre not in ambientes:
                    # Actualizar en la lista de ambientes de la sede
                    index = ambientes.index(ambiente_name)
                    ambientes[index] = nuevo_nombre
                    
                    # Actualizar las reservas existentes para mantener la integridad de los datos
                    for res in reservations_db:
                        if res['ambiente'] == ambiente_name:
                            res['ambiente'] = nuevo_nombre
                            
                    messages.success(request, f"Ambiente '{ambiente_name}' actualizado a '{nuevo_nombre}'.")
                else:
                    messages.error(request, "Ese nombre de ambiente ya existe.")
    return redirect('environment_detail', sede_slug=sede_slug)

# Vista para agregar una nueva sede institucional
@login_required
def add_sede(request):
    if request.method == "POST":
        nombre = request.POST.get('nombre_sede')
        descripcion = request.POST.get('descripcion', '')
        # Generamos un slug simple basado en el nombre
        slug = nombre.lower().strip().replace(" ", "-")
        
        if slug not in sedes_data:
            sedes_data[slug] = {
                'nombre': nombre,
                'descripcion': descripcion,
                'icon': 'bi-building', # Icono por defecto
                'ambientes': []
            }
            messages.success(request, f"Sede '{nombre}' creada exitosamente.")
        else:
            messages.error(request, "Esta sede ya existe.")
    return redirect('environment_list')

# Vista para modificar la información de una sede
@login_required
def edit_sede(request, sede_slug):
    if request.method == "POST" and sede_slug in sedes_data:
        sedes_data[sede_slug]['nombre'] = request.POST.get('nuevo_nombre')
        sedes_data[sede_slug]['descripcion'] = request.POST.get('nueva_descripcion')
        messages.success(request, "Información de la sede actualizada.")
    return redirect('environment_list')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.directory.views import instructores_db # Importamos el registro de instructores

# Create your views here.
# --- SIMULACIÓN DE BASE DE DATOS (TEMPORAL) ---
# En una aplicación real, esto sería un modelo de Django en la base de datos.
# Usamos una lista global para simular el almacenamiento de reservas.
# Cada reserva es un diccionario con un ID único.
reservations_db = []
next_reservation_id = 1
# ----------------------------------------------

# Función auxiliar para determinar la jornada según la hora de inicio
def obtener_jornada(hora_str):
    hora = int(hora_str.split(':')[0])
    if 6 <= hora < 12:
        return "DÍA"
    elif 12 <= hora < 18:
        return "TARDE"
    else:
        return "NOCHE"

@login_required
def booking_list(request):
    # Pasa todas las reservas simuladas a la plantilla
    context = {
        'reservations': reservations_db,
    }
    return render(request, 'booking_list.html', context)

# Vista para el formulario de reserva
@login_required
def reserve_view(request, ambiente_name):
    global next_reservation_id

    if request.method == "POST":
        # Aquí capturamos los datos enviados por el formulario
        instructor = request.POST.get('instructor').upper()
        materia = request.POST.get('materia').upper()
        inicio = request.POST.get('hora_inicio')
        fin = request.POST.get('hora_fin')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')

        # REGISTRO AUTOMÁTICO: Si el instructor no está en el directorio, lo agregamos
        if not any(i['nombre'] == instructor for i in instructores_db):
            instructores_db.append({'nombre': instructor, 'materia': materia})
            messages.info(request, f"Nuevo instructor '{instructor}' añadido al directorio.")

        # Validación de disponibilidad: Evita que se crucen reservas en el mismo ambiente
        for res in reservations_db:
            if res['ambiente'] == ambiente_name:
                # Verificar si las fechas se solapan
                fecha_solapada = fecha_inicio <= res['fecha_fin'] and fecha_fin >= res['fecha_inicio']
                # Verificar si las horas se solapan
                hora_solapada = inicio < res['hora_fin'] and fin > res['hora_inicio']

                if fecha_solapada and hora_solapada:
                    messages.error(request, f"El ambiente ya está ocupado por {res['instructor']} del {res['fecha_inicio']} al {res['fecha_fin']} en ese horario.")
                    return render(request, 'reserve_form.html', {'ambiente': ambiente_name, 'booking': request.POST})

        # Creamos una nueva reserva y la añadimos a nuestra "base de datos" simulada
        new_reservation = {
            'id': next_reservation_id,
            'ambiente': ambiente_name,
            'instructor': instructor,
            'materia': materia,
            'hora_inicio': inicio,
            'hora_fin': fin,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'user': request.user.username, # Guardamos quién hizo la reserva
            'jornada': obtener_jornada(inicio) # Calculamos la jornada
        }
        reservations_db.append(new_reservation)
        next_reservation_id += 1

        messages.success(request, f"Reserva exitosa para {ambiente_name} por {instructor}.")
        # Redirigimos a la lista de reservas para que el usuario vea el resultado inmediatamente
        return redirect('booking_list')
        
    # Pasamos la lista de instructores para las sugerencias del formulario (datalist)
    return render(request, 'reserve_form.html', {'ambiente': ambiente_name, 'instructores': instructores_db})

# Vista para eliminar una reserva
@login_required
def delete_booking(request, booking_id):
    global reservations_db
    # Buscamos la reserva por ID
    reservation_to_delete = next((r for r in reservations_db if r['id'] == booking_id), None)

    if reservation_to_delete:
        # Solo el usuario que hizo la reserva o un superusuario puede eliminarla
        if request.user.username == reservation_to_delete['user'] or request.user.is_superuser:
            reservations_db.remove(reservation_to_delete)
            messages.success(request, f"Reserva para {reservation_to_delete['ambiente']} eliminada exitosamente.")
        else:
            messages.error(request, "No tienes permiso para eliminar esta reserva.")
    else:
        messages.error(request, "Reserva no encontrada.")
    return redirect('booking_list')

# Vista para editar una reserva
@login_required
def edit_booking(request, booking_id):
    global reservations_db
    reservation_to_edit = next((r for r in reservations_db if r['id'] == booking_id), None)

    if not reservation_to_edit:
        messages.error(request, "Reserva no encontrada para editar.")
        return redirect('booking_list')
    
    # Solo el usuario que hizo la reserva o un superusuario puede editarla
    if not (request.user.username == reservation_to_edit['user'] or request.user.is_superuser):
        messages.error(request, "No tienes permiso para editar esta reserva.")
        return redirect('booking_list')

    if request.method == "POST":
        instructor = request.POST.get('instructor').upper()
        materia = request.POST.get('materia').upper()
        inicio = request.POST.get('hora_inicio')
        fin = request.POST.get('hora_fin')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')

        # Validación de disponibilidad al editar (excluyendo la reserva actual)
        for res in reservations_db:
            if res['id'] != booking_id and res['ambiente'] == reservation_to_edit['ambiente']:
                if (fecha_inicio <= res['fecha_fin'] and fecha_fin >= res['fecha_inicio']) and \
                   (inicio < res['hora_fin'] and fin > res['hora_inicio']):
                    messages.error(request, "Error: Los nuevos datos coinciden con otra reserva existente.")
                    return render(request, 'reserve_form.html', {'ambiente': reservation_to_edit['ambiente'], 'booking': request.POST})

        reservation_to_edit.update({
            'instructor': instructor,
            'materia': materia,
            'hora_inicio': inicio,
            'hora_fin': fin,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'jornada': obtener_jornada(inicio)
        })

        # También actualizamos el directorio al editar si es necesario
        if not any(i['nombre'] == instructor for i in instructores_db):
            instructores_db.append({'nombre': instructor, 'materia': materia})

        messages.success(request, f"Reserva para {reservation_to_edit['ambiente']} actualizada exitosamente.")
        return redirect('booking_list')
    
    # Si es GET, mostramos el formulario pre-rellenado
    return render(request, 'reserve_form.html', {'ambiente': reservation_to_edit['ambiente'], 'booking': reservation_to_edit, 'instructores': instructores_db})

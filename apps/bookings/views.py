from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reserva
from apps.infrastructure.models import Ambiente
from apps.directory.models import Instructor

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
    # Filtramos usando el ORM de Django
    mis_reservas = Reserva.objects.filter(user=request.user).order_by('-fecha_inicio')
    context = {
        'reservations': mis_reservas,
        'titulo_pagina': 'Mis Reservas Personales'
    }
    return render(request, 'booking_list.html', context)

@login_required
def environment_bookings(request, ambiente_name):
    # Filtramos por el nombre del ambiente relacionado
    reservas_ambiente = Reserva.objects.filter(ambiente__nombre=ambiente_name)
    context = {
        'ambiente': ambiente_name,
        'reservations': reservas_ambiente,
    }
    return render(request, 'environment_bookings.html', context)

# Vista para el formulario de reserva
@login_required
def reserve_view(request, ambiente_name):
    if request.method == "POST":
        instructor = request.POST.get('instructor').upper()
        materia = request.POST.get('materia').upper()
        inicio = request.POST.get('hora_inicio')
        fin = request.POST.get('hora_fin')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')

        # Validación: Hora de fin debe ser mayor a inicio
        if inicio >= fin:
            messages.error(request, "La hora de fin debe ser posterior a la hora de inicio.")
            return render(request, 'reserve_form.html', {'ambiente': ambiente_name, 'booking': request.POST})

        # Obtener o crear instructor en el directorio
        Instructor.objects.get_or_create(nombre=instructor, defaults={'materia': materia})
        
        # Obtener objeto ambiente
        ambiente_obj = get_object_or_404(Ambiente, nombre=ambiente_name)

        # Validación de disponibilidad en la DB
        solapada = Reserva.objects.filter(
            ambiente=ambiente_obj,
            fecha_inicio__lte=fecha_fin,
            fecha_fin__gte=fecha_inicio,
            hora_inicio__lt=fin,
            hora_fin__gt=inicio
        ).exists()

        if solapada:
            messages.error(request, "El ambiente ya está ocupado en ese horario.")
            return render(request, 'reserve_form.html', {'ambiente': ambiente_name, 'booking': request.POST})

        # Guardar en la base de datos
        Reserva.objects.create(
            ambiente=ambiente_obj,
            instructor=instructor,
            materia=materia,
            hora_inicio=inicio,
            hora_fin=fin,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            user=request.user,
            jornada=obtener_jornada(inicio)
        )

        messages.success(request, f"Reserva exitosa para {ambiente_name} por {instructor}.")
        return redirect('booking_list')
        
    return render(request, 'reserve_form.html', {'ambiente': ambiente_name, 'instructores': Instructor.objects.all()})

@login_required
def delete_booking(request, booking_id):
    reserva = get_object_or_404(Reserva, id=booking_id)
    if request.user == reserva.user or request.user.is_superuser:
        reserva.delete()
        messages.success(request, "Reserva eliminada exitosamente.")
    else:
        messages.error(request, "No tienes permiso para eliminar esta reserva.")
    return redirect('booking_list')

@login_required
def edit_booking(request, booking_id):
    reserva = get_object_or_404(Reserva, id=booking_id)

    if not (request.user == reserva.user or request.user.is_superuser):
        messages.error(request, "No tienes permiso para editar esta reserva.")
        return redirect('booking_list')

    if request.method == "POST":
        reserva.instructor = request.POST.get('instructor').upper()
        reserva.materia = request.POST.get('materia').upper()
        reserva.hora_inicio = request.POST.get('hora_inicio')
        reserva.hora_fin = request.POST.get('hora_fin')
        reserva.fecha_inicio = request.POST.get('fecha_inicio')
        reserva.fecha_fin = request.POST.get('fecha_fin')
        reserva.jornada = obtener_jornada(reserva.hora_inicio)
        reserva.save()

        messages.success(request, "Reserva actualizada exitosamente.")
        return redirect('booking_list')
    
    return render(request, 'reserve_form.html', {
        'ambiente': reserva.ambiente.nombre, 
        'booking': reserva, 
        'instructores': Instructor.objects.all()
    })

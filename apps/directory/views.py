from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# --- SIMULACIÓN DE BASE DE DATOS PARA INSTRUCTORES ---
# Lista global para mantener el registro de instructores de forma persistente durante la ejecución
instructores_db = [
    {'nombre': 'RICARDO ALARCÓN', 'materia': 'PROGRAMACIÓN DE SOFTWARE'},
]

@login_required
def directory_list(request):
    # Ordenamos la lista alfabéticamente por nombre antes de mostrarla
    lista_ordenada = sorted(instructores_db, key=lambda i: i['nombre'])
    return render(request, 'directory_list.html', {'instructores': lista_ordenada})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Instructor

@login_required
def directory_list(request):
    # Ordenamos la lista alfabéticamente por nombre antes de mostrarla
    lista_ordenada = Instructor.objects.all().order_by('nombre')
    return render(request, 'directory_list.html', {'instructores': lista_ordenada})

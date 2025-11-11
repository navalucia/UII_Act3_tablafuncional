# --- START OF FILE views.py (MODIFICADO para relación Miembro-Clase) ---

from django.shortcuts import render, redirect, get_object_or_404
from .models import Miembro, Clase, Empleado # Importar Clase
from django.contrib import messages
from django.http import HttpResponse


def inicio_gym(request):
    context = {}
    return render(request, 'app_gym/inicio.html', context)


# --- VISTAS PARA MIEMBROS (MODIFICADAS) ---

def agregar_miembro(request):
    # Obtener todas las clases disponibles para el formulario
    clases_disponibles = Clase.objects.all().order_by('nombre_clase')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono', '')
        membresia_activa = request.POST.get('membresia_activa') == 'on'
        imagen = request.FILES.get('imagen')
        clase_id = request.POST.get('clase_inscrita') # Obtener el ID de la clase seleccionada

        clase_inscrita_obj = None
        if clase_id: # Solo si se seleccionó una clase
            clase_inscrita_obj = get_object_or_404(Clase, pk=clase_id)

        Miembro.objects.create(
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=fecha_nacimiento,
            email=email,
            telefono=telefono,
            membresia_activa=membresia_activa,
            imagen=imagen,
            clase_inscrita=clase_inscrita_obj # Asignar el objeto Clase
        )
        messages.success(request, 'Miembro agregado exitosamente!')
        return redirect('ver_miembros')

    context = {'clases_disponibles': clases_disponibles}
    return render(request, 'miembros/agregar_miembros.html', context)


def ver_miembros(request):
    print("\n--- INICIANDO VISTA: ver_miembros ---")
    try:
        # Usar select_related para obtener los datos de la clase en la misma consulta
        miembros = Miembro.objects.all().select_related('clase_inscrita').order_by('apellido', 'nombre')
        print(f"DEBUG: Queryset de Miembros obtenido. Cantidad: {miembros.count()}")

        if not miembros.exists():
            print("DEBUG: ¡No se encontraron miembros en la base de datos!")
            messages.info(request, "No hay miembros registrados para mostrar. ¡Añade algunos!")

        context = {'miembros': miembros}
        print("DEBUG: Contexto preparado para renderizar la plantilla.")
        return render(request, 'miembros/ver_miembros.html', context)

    except Exception as e:
        print(f"ERROR: Se produjo un error en ver_miembros: {e}")
        messages.error(request, f"Ocurrió un error al cargar los miembros: {e}")
        return render(request, 'app_gym/inicio.html', {'error_message': str(e)})
    finally:
        print("--- FINALIZANDO VISTA: ver_miembros ---\n")


def actualizar_miembro(request, pk):
    miembro = get_object_or_404(Miembro, pk=pk)
    clases_disponibles = Clase.objects.all().order_by('nombre_clase') # Para el select

    if request.method == 'POST':
        print("====================================")
        print("Método POST detectado para actualizar miembro:", miembro.id)
        print("Datos recibidos:", request.POST)
        print("Archivos recibidos:", request.FILES)
        print("Nombre antes:", miembro.nombre)

        miembro.nombre = request.POST.get('nombre')
        miembro.apellido = request.POST.get('apellido')
        miembro.fecha_nacimiento = request.POST.get('fecha_nacimiento')
        miembro.email = request.POST.get('email')
        miembro.telefono = request.POST.get('telefono', '')
        miembro.membresia_activa = request.POST.get('membresia_activa') == 'on'

        clase_id = request.POST.get('clase_inscrita')
        if clase_id:
            miembro.clase_inscrita = get_object_or_404(Clase, pk=clase_id)
        else: # Si no se selecciona ninguna clase (la opción "Sin Clase")
            miembro.clase_inscrita = None

        if 'imagen' in request.FILES:
            if miembro.imagen:
                miembro.imagen.delete(save=False)
            miembro.imagen = request.FILES['imagen']
        elif 'borrar_imagen' in request.POST:
            if miembro.imagen:
                miembro.imagen.delete(save=False)
            miembro.imagen = None

        miembro.save()
        print("Miembro guardado. Nuevo nombre:", miembro.nombre)
        print("====================================")
        messages.info(request, 'Miembro actualizado exitosamente!')
        return redirect('ver_miembros')

    context = {
        'miembro': miembro,
        'clases_disponibles': clases_disponibles
    }
    return render(request, 'miembros/actualizar_miembros.html', context)


def borrar_miembro(request, pk):
    miembro = get_object_or_404(Miembro, pk=pk)
    if request.method == 'POST':
        if miembro.imagen:
            miembro.imagen.delete()
        miembro.delete()
        messages.error(request, 'Miembro eliminado correctamente.')
        return redirect('ver_miembros')
    context = {'miembro': miembro}
    return render(request, 'miembros/confirmar_borrar_miembros.html', context)


# --- VISTAS PARA CLASES (Sin cambios, para referencia) ---

def agregar_clase(request):
    if request.method == 'POST':
        nombre_clase = request.POST.get('nombre_clase')
        descripcion = request.POST.get('descripcion')
        horario = request.POST.get('horario')
        duracion_minutos = request.POST.get('duracion_minutos')
        cupo_maximo = request.POST.get('cupo_maximo')
        nivel_dificultad = request.POST.get('nivel_dificultad')

        try:
            Clase.objects.create(
                nombre_clase=nombre_clase,
                descripcion=descripcion,
                horario=horario,
                duracion_minutos=int(duracion_minutos),
                cupo_maximo=int(cupo_maximo),
                nivel_dificultad=nivel_dificultad,
            )
            messages.success(request, 'Clase agregada exitosamente!')
            return redirect('ver_clases')
        except ValueError:
            messages.error(request, 'Error: Duración y cupo deben ser números enteros.')
        except Exception as e:
            messages.error(request, f'Error al agregar la clase: {e}')

    return render(request, 'clases/agregar_clase.html')


def ver_clases(request):
    try:
        clases = Clase.objects.all().order_by('horario', 'nombre_clase')
        if not clases.exists():
            messages.info(request, "No hay clases registradas para mostrar. ¡Añade algunas!")
        context = {'clases': clases}
        return render(request, 'clases/ver_clases.html', context)
    except Exception as e:
        messages.error(request, f"Ocurrió un error al cargar las clases: {e}")
        return render(request, 'app_gym/inicio.html', {'error_message': str(e)})


def actualizar_clase(request, pk):
    clase = get_object_or_404(Clase, pk=pk)
    if request.method == 'POST':
        clase.nombre_clase = request.POST.get('nombre_clase')
        clase.descripcion = request.POST.get('descripcion')
        clase.horario = request.POST.get('horario')
        clase.duracion_minutos = request.POST.get('duracion_minutos')
        clase.cupo_maximo = request.POST.get('cupo_maximo')
        clase.nivel_dificultad = request.POST.get('nivel_dificultad')

        try:
            clase.duracion_minutos = int(clase.duracion_minutos)
            clase.cupo_maximo = int(clase.cupo_maximo)
            clase.save()
            messages.info(request, 'Clase actualizada exitosamente!')
            return redirect('ver_clases')
        except ValueError:
            messages.error(request, 'Error: Duración y cupo deben ser números enteros.')
        except Exception as e:
            messages.error(request, f'Error al actualizar la clase: {e}')

    context = {
        'clase': clase,
        'niveles_dificultad': Clase.nivel_dificultad.field.choices
    }
    return render(request, 'clases/actualizar_clase.html', context)


def borrar_clase(request, pk):
    clase = get_object_or_404(Clase, pk=pk)
    if request.method == 'POST':
        clase.delete()
        messages.error(request, 'Clase eliminada correctamente.')
        return redirect('ver_clases')
    context = {'clase': clase}
    return render(request, 'clases/confirmar_borrar_clase.html', context)

# --- END OF FILE views.py (MODIFICADO para relación Miembro-Clase) ---
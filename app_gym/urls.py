from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio_gym, name='inicio_gym'),

    # URLs para Miembros
    path('miembros/', views.ver_miembros, name='ver_miembros'),
    path('miembros/agregar/', views.agregar_miembro, name='agregar_miembro'),
    path('miembros/actualizar/<int:pk>/', views.actualizar_miembro, name='actualizar_miembro'),
    path('miembros/borrar/<int:pk>/', views.borrar_miembro, name='borrar_miembro'),

    # NUEVAS URLs para Clases
    path('clases/', views.ver_clases, name='ver_clases'),
    path('clases/agregar/', views.agregar_clase, name='agregar_clase'),
    path('clases/actualizar/<int:pk>/', views.actualizar_clase, name='actualizar_clase'),
    path('clases/borrar/<int:pk>/', views.borrar_clase, name='borrar_clase'),
]

from django.contrib import admin
from django.urls import path
from .views import*

urlpatterns = [
    path('inicio_agromarket/', inicio_agromarket, name='inicio_agromarket'),
    path('login_registro_agromarket/', login_registro_agromarket, name='login_registro_agromarket'),
    path('login_usuario/', login_usuario, name='login_usuario'),
    path('registro_usuario/', registro_usuario, name='registro_usuario'),
    path('panel_consumidor/', panel_consumidor, name='panel_consumidor'),
    path('informacion/', informacion, name='informacion'),

    path('panel_empresa/', panel_empresa, name='panel_empresa'),
    path('informacion2/', informacion2, name='informacion2'),
    path('publicar_producto_empresa/', publicar_producto_empresa, name='publicar_producto_empresa'),
    path('publicar_producto_form/', publicar_producto_form, name='publicar_producto_form'),
    path('mis_productos/', mis_productos, name='mis_productos'),
    path('editar_producto/<int:producto_id>/', editar_producto, name='editar_producto'),
    path('eliminar_producto/<int:producto_id>/', eliminar_producto, name='eliminar_producto'),
    path('form_editar_producto/<int:producto_id>/', form_editar_producto, name='form_editar_producto'),
    
    path('panel_agricultor/', panel_agricultor, name='panel_agricultor'),
    path('informacion3/', informacion3, name='informacion3'),
    path('publicar_producto_agricultor/', publicar_producto_agricultor, name='publicar_producto_agricultor'),
    path('publicar_producto_form_A/', publicar_producto_form_A, name='publicar_producto_form_A'),
    path('mis_productos_agricultor/', mis_productos_agricultor, name='mis_productos_agricultor'),
    path('editar_producto_agricultor/<int:producto_id>/', editar_producto_agricultor, name='editar_producto_agricultor'),
    path('eliminar_producto_agricultor/<int:producto_id>/', eliminar_producto_agricultor, name='eliminar_producto_agricultor'),
    path('form_editar_producto_agricultor/<int:producto_id>/', form_editar_producto_agricultor, name='form_editar_producto_agricultor'),


    path('separar_producto/<int:producto_id>/', separar_producto, name='separar_producto'),
    path('separar_producto_agricultor/<int:producto_id>/', separar_producto_agricultor, name='separar_producto_agricultor'),
    path('separar_producto_empresa/<int:producto_id>/', separar_producto_empresa, name='separar_producto_empresa'),

    





]
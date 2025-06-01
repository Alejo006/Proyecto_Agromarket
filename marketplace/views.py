from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from .models import *
from django.contrib.auth.decorators import login_required
from .models import ProductoEmpresa, ImagenProducto, Categoria
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.html import escape

#modulo para la vista de inicio de agromarket
def inicio_agromarket(request):
    return render(request, 'inicio_agromarket.html',{})

def login_registro_agromarket(request):
    return render(request, 'login_registro_agromarket.html',{})


#modulos para inicio secion y registro de usuarios
def login_usuario(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contraseña')

        try:
            usuario = Usuario.objects.get(correo=correo)
            if usuario.contraseña == contrasena:
                request.session['usuario_id'] = usuario.id
                if usuario.tipo_usuario == 'Agricultor':
                    return redirect('panel_agricultor')
                elif usuario.tipo_usuario == 'Consumidor':
                    return redirect('panel_consumidor')
                elif usuario.tipo_usuario == 'Empresa':
                    return redirect('panel_empresa')
            else:
                messages.error(request, "Contraseña incorrecta.")
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado. Verifique el correo.")

    return render(request, 'login_registro_agromarket.html')  # Aquí usas un solo archivo

def registro_usuario(request):
    if request.method == 'POST':
        try:
            correo = request.POST.get('correo')
            if Usuario.objects.filter(correo=correo).exists():
                messages.error(request, "El correo ya está registrado.")
                return redirect('registro_usuario')

            usuario = Usuario.objects.create(
                nombre=request.POST.get('nombre'),
                documento=request.POST.get('documento'),
                correo=correo,
                telefono=request.POST.get('telefono'),
                direccion=request.POST.get('direccion'),
                contraseña=request.POST.get('contraseña'),
                tipo_usuario=request.POST.get('tipo_usuario')
            )

            messages.success(request, f"Usuario {usuario.nombre} registrado correctamente.")
            return redirect('login_usuario')

        except Exception as e:
            messages.error(request, f"Error al registrar el usuario: {e}")
            return redirect('registro_usuario')

    return render(request, 'login_registro_agromarket.html')  # También usas el mismo archivo



def panel_consumidor(request):
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    productos_agricultores = ProductoAgricultor.objects.all()
    productos_empresas = ProductoEmpresa.objects.all()
    return render(request, 'panel_consumidor.html', {
        'usuario': usuario,
        'productos_agricultores': productos_agricultores,
        'productos_empresas': productos_empresas,
        
    })

def informacion(request):
    return render(request, 'informacion.html',{})


def panel_empresa(request):
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    productos_agricultores = ProductoAgricultor.objects.all()
    productos_empresas = ProductoEmpresa.objects.all()
    return render(request, 'panel_empresa.html', {
        'usuario': usuario,
        'productos_agricultores': productos_agricultores,
        'productos_empresas': productos_empresas,
    })

def informacion2(request):
    return render(request, 'informacion2.html',{})


def publicar_producto_empresa(request):
    # Verificar si el usuario está autenticado
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para acceder a esta página.")
        return redirect('login_usuario')

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        if usuario.tipo_usuario != 'Empresa':
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect('login_usuario')  # o a otro panel
    except Usuario.DoesNotExist:
        messages.error(request, "Usuario no encontrado.")
        return redirect('login_usuario')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        descuento = request.POST.get('descuento', 0)
        unidad_medida = request.POST.get('unidad_medida')
        cantidad_disponible = request.POST.get('cantidad_disponible')
        ubicacion = request.POST.get('ubicacion')
        nombre_empresa = request.POST.get('nombre_empresa')
        categoria_id = request.POST.get('categoria')
        imagenes = request.FILES.getlist('imagenes')

        try:
            categoria = Categoria.objects.get(id=categoria_id)

            producto = ProductoEmpresa.objects.create(
                usuario=usuario,
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                descuento=descuento,
                unidad_medida=unidad_medida,
                cantidad_disponible=cantidad_disponible,
                ubicacion=ubicacion,
                nombre_empresa=nombre_empresa,
                categoria=categoria
            )

            # Guardar imágenes si corresponde
            for imagen in imagenes:
                producto.imagenes.create(imagen=imagen)

            messages.success(request, "Producto publicado correctamente.")
            return redirect('panel_empresa')

        except Categoria.DoesNotExist:
            messages.error(request, "Categoría no válida.")
        except Exception as e:
            messages.error(request, f"Error al guardar el producto: {str(e)}")

    categorias = Categoria.objects.all()
    return render(request, 'publicar_producto_empresa.html', {'categorias': categorias})

def publicar_producto_form(request):
    categorias = Categoria.objects.all()
    return render(request, 'publicar_producto_form.html', {'categorias': categorias})  






def mis_productos(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return JsonResponse({'html': '<p>No has iniciado sesión.</p>'}, status=403)

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        productos = ProductoEmpresa.objects.filter(usuario=usuario)

        if not productos.exists():
            return JsonResponse({'html': '<p>No tienes productos publicados.</p>'})

        html = ""
        for producto in productos:
            html += f'''
                <div class="producto" id="producto-{producto.id}">
                    <p><strong>{escape(producto.nombre)}</strong> - ${producto.precio}</p>
            '''

            # Mostrar imágenes si hay
            if producto.imagenes.all():
                html += '<div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px;">'
                for imagen in producto.imagenes.all():
                    html += f'<img src="{imagen.imagen.url}" alt="Imagen del producto" width="120px" height="120px" style="object-fit: cover; border-radius: 5px; border: 1px solid #ccc;" />'
                html += '</div>'

            # Botones de acciones
            html += f'''
                <div style="margin-top: 10px;">
                    <button class="btn-editar" data-id="{producto.id}">✏️ Editar</button>
                    <form action="/marketplace/eliminar_producto/{producto.id}/" method="POST" class="form-eliminar" style="display:inline;">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{request.COOKIES.get('csrftoken')}">
                        <button type="submit" style="color: red;">🗑️ Eliminar</button>
                    </form>
                </div>
            </div>
            '''

        return JsonResponse({'html': html})

    except Usuario.DoesNotExist:
        return JsonResponse({'html': '<p>Usuario no válido.</p>'}, status=404)    
    


def eliminar_producto(request, producto_id):
    if request.method == "POST":
        try:
            producto = ProductoEmpresa.objects.get(id=producto_id)
            producto.delete()
            return JsonResponse({'success': True})
        except ProductoEmpresa.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    return JsonResponse({'error': 'Método no permitido'}, status=405)




def form_editar_producto(request, producto_id):
    try:
        producto = ProductoEmpresa.objects.get(id=producto_id)
        categorias = Categoria.objects.all()  # Asegúrate de importar tu modelo Categoria

        # Generamos las opciones del select de categorías
        opciones_categoria = ""
        for categoria in categorias:
            selected = "selected" if categoria.id == producto.categoria.id else ""
            opciones_categoria += f'<option value="{categoria.id}" {selected}>{categoria.nombre}</option>'

        html = f'''
            <form method="POST" action="/marketplace/editar_producto/{producto_id}/" class="form-editar" enctype="multipart/form-data">
                <input type="hidden" name="csrfmiddlewaretoken" value="{request.COOKIES.get('csrftoken')}">

                <label>Nombre:</label>
                <input type="text" name="nombre" value="{producto.nombre}" required>

                <label>Precio:</label>
                <input type="number" step="0.01" name="precio" value="{producto.precio}" required>

                <label>Descuento (%):</label>
                <input type="number" step="0.01" name="descuento" value="{producto.descuento}" required>

                <label>Unidad de medida:</label>
                <input type="text" name="unidad_medida" value="{producto.unidad_medida}" required>

                <label>Cantidad disponible:</label>
                <input type="number" name="cantidad_disponible" value="{producto.cantidad_disponible}" required>

                <label>Nombre de la empresa:</label>
                <input type="text" name="nombre_empresa" value="{producto.nombre_empresa}" required>

                <label>Descripción:</label>
                <textarea name="descripcion" required>{producto.descripcion}</textarea>

                <label>Ubicación:</label>
                <textarea name="ubicacion" required>{producto.ubicacion}</textarea>

                <label>Categoría:</label>
                <select name="categoria" required>{opciones_categoria}</select>

                <label>Imágenes (agrega nuevas si deseas):</label>
                <input type="file" name="imagenes" multiple accept="image/*">

                <button type="submit">Guardar Cambios</button>
            </form>
        '''
        return JsonResponse({'html': html})
    except ProductoEmpresa.DoesNotExist:
        return JsonResponse({'html': '<p>Producto no encontrado.</p>'}, status=404)
    



def editar_producto(request, producto_id):
    if request.method == 'POST':
        try:
            producto = ProductoEmpresa.objects.get(id=producto_id)

            producto.nombre = request.POST.get('nombre')
            producto.precio = request.POST.get('precio')
            producto.descuento = request.POST.get('descuento')
            producto.unidad_medida = request.POST.get('unidad_medida')
            producto.cantidad_disponible = request.POST.get('cantidad_disponible')
            producto.nombre_empresa = request.POST.get('nombre_empresa')
            producto.descripcion = request.POST.get('descripcion')
            producto.ubicacion = request.POST.get('ubicacion')

            categoria_id = request.POST.get('categoria')
            if categoria_id:
                producto.categoria_id = categoria_id

            producto.save()

            # Si se suben nuevas imágenes
            for imagen in request.FILES.getlist('imagenes'):
                producto.imagenes.create(imagen=imagen)  # Asumiendo una relación ProductoEmpresa -> Imagen con .imagenes

            return JsonResponse({'success': True})
        except ProductoEmpresa.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    return JsonResponse({'error': 'Método no permitido'}, status=405)







#modulo para el panel de agricultor




def panel_agricultor(request):
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    productos_agricultores = ProductoAgricultor.objects.all()
    productos_empresas = ProductoEmpresa.objects.all()
    return render(request, 'panel_agricultor.html', {
        'usuario': usuario,
        'productos_agricultores': productos_agricultores,
        'productos_empresas': productos_empresas,
    })

def informacion3(request):
    return render(request, 'informacion3.html',{})



def publicar_producto_agricultor(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para acceder a esta página.")
        return redirect('login_usuario')

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        if usuario.tipo_usuario != 'Agricultor':
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect('login_usuario')
    except Usuario.DoesNotExist:
        messages.error(request, "Usuario no encontrado.")
        return redirect('login_usuario')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        unidad_medida = request.POST.get('unidad_medida')
        cantidad_disponible = request.POST.get('cantidad_disponible')
        ubicacion = request.POST.get('ubicacion')
        categoria_id = request.POST.get('categoria')
        imagenes = request.FILES.getlist('imagenes')

        try:
            categoria = Categoria.objects.get(id=categoria_id)

            producto = ProductoAgricultor.objects.create(
                usuario=usuario,
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                unidad_medida=unidad_medida,
                cantidad_disponible=cantidad_disponible,
                ubicacion=ubicacion,
                categoria=categoria
            )

            for imagen in imagenes:
                ImagenProducto.objects.create(producto_agricultor=producto, imagen=imagen)

            messages.success(request, "Producto publicado correctamente.")
            return redirect('panel_agricultor')

        except Categoria.DoesNotExist:
            messages.error(request, "Categoría no válida.")
        except Exception as e:
            messages.error(request, f"Error al guardar el producto: {str(e)}")

    categorias = Categoria.objects.all()
    return render(request, 'publicar_producto_agricultor.html', {'categorias': categorias})

def publicar_producto_form_A(request):
    categorias = Categoria.objects.all()
    return render(request, 'publicar_producto_form_A.html', {'categorias': categorias})


def mis_productos_agricultor(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return JsonResponse({'html': '<p>No has iniciado sesión.</p>'}, status=403)

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        productos = ProductoAgricultor.objects.filter(usuario=usuario)

        if not productos.exists():
            return JsonResponse({'html': '<p>No tienes productos publicados.</p>'})

        html = ""
        for producto in productos:
            html += f'''
                <div class="producto" id="producto-{producto.id}">
                    <p><strong>{escape(producto.nombre)}</strong> - ${producto.precio}</p>
            '''

            if producto.imagenes.all():
                html += '<div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px;">'
                for imagen in producto.imagenes.all():
                    html += f'<img src="{imagen.imagen.url}" alt="Imagen del producto" width="120px" height="120px" style="object-fit: cover; border-radius: 5px; border: 1px solid #ccc;" />'
                html += '</div>'

            html += f'''
                <div style="margin-top: 10px;">
                    <button class="btn-editar" data-id="{producto.id}">✏️ Editar</button>
                    <form action="/marketplace/eliminar_producto_agricultor/{producto.id}/" method="POST" class="form-eliminar" style="display:inline;">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{request.COOKIES.get('csrftoken')}">
                        <button type="submit" style="color: red;">🗑️ Eliminar</button>
                    </form>
                </div>
            </div>
            '''

        return JsonResponse({'html': html})

    except Usuario.DoesNotExist:
        return JsonResponse({'html': '<p>Usuario no válido.</p>'}, status=404)


def eliminar_producto_agricultor(request, producto_id):
    if request.method == "POST":
        try:
            producto = ProductoAgricultor.objects.get(id=producto_id)
            producto.delete()
            return JsonResponse({'success': True})
        except ProductoAgricultor.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def form_editar_producto_agricultor(request, producto_id):
    try:
        producto = ProductoAgricultor.objects.get(id=producto_id)
        categorias = Categoria.objects.all()

        opciones_categoria = ""
        for categoria in categorias:
            selected = "selected" if categoria.id == producto.categoria.id else ""
            opciones_categoria += f'<option value="{categoria.id}" {selected}>{categoria.nombre}</option>'

        html = f'''
            <form method="POST" action="/marketplace/editar_producto_agricultor/{producto_id}/" class="form-editar" enctype="multipart/form-data">
                <input type="hidden" name="csrfmiddlewaretoken" value="{request.COOKIES.get('csrftoken')}">

                <label>Nombre:</label>
                <input type="text" name="nombre" value="{producto.nombre}" required>

                <label>Precio:</label>
                <input type="number" step="0.01" name="precio" value="{producto.precio}" required>

                <label>Unidad de medida:</label>
                <input type="text" name="unidad_medida" value="{producto.unidad_medida}" required>

                <label>Cantidad disponible:</label>
                <input type="number" name="cantidad_disponible" value="{producto.cantidad_disponible}" required>

                <label>Descripción:</label>
                <textarea name="descripcion" required>{producto.descripcion}</textarea>

                <label>Ubicación:</label>
                <textarea name="ubicacion" required>{producto.ubicacion}</textarea>

                <label>Categoría:</label>
                <select name="categoria" required>{opciones_categoria}</select>

                <label>Imágenes (agrega nuevas si deseas):</label>
                <input type="file" name="imagenes" multiple accept="image/*">

                <button type="submit">Guardar Cambios</button>
            </form>
        '''
        return JsonResponse({'html': html})
    except ProductoAgricultor.DoesNotExist:
        return JsonResponse({'html': '<p>Producto no encontrado.</p>'}, status=404)



def editar_producto_agricultor(request, producto_id):
    if request.method == 'POST':
        try:
            producto = ProductoAgricultor.objects.get(id=producto_id)

            producto.nombre = request.POST.get('nombre')
            producto.precio = request.POST.get('precio')
            producto.unidad_medida = request.POST.get('unidad_medida')
            producto.cantidad_disponible = request.POST.get('cantidad_disponible')
            producto.descripcion = request.POST.get('descripcion')
            producto.ubicacion = request.POST.get('ubicacion')

            categoria_id = request.POST.get('categoria')
            if categoria_id:
                producto.categoria_id = categoria_id

            producto.save()

            for imagen in request.FILES.getlist('imagenes'):
                ImagenProducto.objects.create(producto_agricultor=producto, imagen=imagen)

            return JsonResponse({'success': True})
        except ProductoAgricultor.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    return JsonResponse({'error': 'Método no permitido'}, status=405)




#modulo para el carrito de compras
def separar_producto(request, producto_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if usuario.tipo_usuario != "Consumidor":
        return redirect('panel_consumidor')

    producto_agricultor = None
    producto_empresa = None
    vendedor = None

    try:
        producto_agricultor = ProductoAgricultor.objects.get(id=producto_id)
        vendedor = producto_agricultor.usuario  # Usuario vendedor agricultor
        producto = producto_agricultor
        tipo_producto = 'agricultor'
    except ProductoAgricultor.DoesNotExist:
        try:
            producto_empresa = ProductoEmpresa.objects.get(id=producto_id)
            vendedor = producto_empresa.usuario  # Usuario vendedor empresa
            producto = producto_empresa
            tipo_producto = 'empresa'
        except ProductoEmpresa.DoesNotExist:
            # Producto no existe
            return redirect('panel_consumidor')

    context = {
        'producto': producto,
        'vendedor': vendedor,
        'tipo_producto': tipo_producto,
        'usuario': usuario,
    }

    return render(request, 'separar_producto.html', context)



def separar_producto_agricultor(request, producto_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if usuario.tipo_usuario != "Agricultor":
        return redirect('panel_agricultor')

    producto_agricultor = None
    producto_empresa = None
    vendedor = None

    try:
        producto_agricultor = ProductoAgricultor.objects.get(id=producto_id)
        vendedor = producto_agricultor.usuario  # Usuario vendedor agricultor
        producto = producto_agricultor
        tipo_producto = 'agricultor'
    except ProductoAgricultor.DoesNotExist:
        try:
            producto_empresa = ProductoEmpresa.objects.get(id=producto_id)
            vendedor = producto_empresa.usuario  # Usuario vendedor empresa
            producto = producto_empresa
            tipo_producto = 'empresa'
        except ProductoEmpresa.DoesNotExist:
            # Producto no existe
            return redirect('panel_agricultor')

    context = {
        'producto': producto,
        'vendedor': vendedor,
        'tipo_producto': tipo_producto,
        'usuario': usuario,
    }

    return render(request, 'separar_producto_agricultor.html', context)



def separar_producto_empresa(request, producto_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if usuario.tipo_usuario != "Empresa":
        return redirect('panel_empresa')

    producto_agricultor = None
    producto_empresa = None
    vendedor = None

    try:
        producto_agricultor = ProductoAgricultor.objects.get(id=producto_id)
        vendedor = producto_agricultor.usuario  # Usuario vendedor agricultor
        producto = producto_agricultor
        tipo_producto = 'agricultor'
    except ProductoAgricultor.DoesNotExist:
        try:
            producto_empresa = ProductoEmpresa.objects.get(id=producto_id)
            vendedor = producto_empresa.usuario  # Usuario vendedor empresa
            producto = producto_empresa
            tipo_producto = 'empresa'
        except ProductoEmpresa.DoesNotExist:
            # Producto no existe
            return redirect('panel_empresa')

    context = {
        'producto': producto,
        'vendedor': vendedor,
        'tipo_producto': tipo_producto,
        'usuario': usuario,
    }

    return render(request, 'separar_producto_empresa.html', context)
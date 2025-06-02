from django.shortcuts import render, get_object_or_404, redirect  # Utilidades para vistas
from django.contrib import messages  # Sistema de mensajes para mostrar feedback al usuario
from .models import *  # Importa todos los modelos definidos en este archivo
from django.contrib.auth.decorators import login_required  # Decorador para vistas que requieren login
from .models import ProductoEmpresa, ImagenProducto, Categoria  # Importación específica de modelos
from django.http import JsonResponse  # Para devolver respuestas JSON
from django.template.loader import render_to_string  # Renderizar plantillas a cadenas
from django.utils.html import escape  # Escapar contenido HTML (por seguridad)

# Vista para la página de inicio del módulo Agromarket
def inicio_agromarket(request):
    return render(request, 'inicio_agromarket.html', {})

# Vista para mostrar la interfaz de login y registro
def login_registro_agromarket(request):
    return render(request, 'login_registro_agromarket.html', {})

# Vista para manejo de inicio de sesión de usuarios
def login_usuario(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')  # Obtiene el correo del formulario
        contrasena = request.POST.get('contraseña')  # Obtiene la contraseña

        try:
            usuario = Usuario.objects.get(correo=correo)  # Busca al usuario por correo
            if usuario.contraseña == contrasena:  # Verifica la contraseña
                request.session['usuario_id'] = usuario.id  # Guarda el ID del usuario en la sesión
                # Redirige según el tipo de usuario
                if usuario.tipo_usuario == 'Agricultor':
                    return redirect('panel_agricultor')
                elif usuario.tipo_usuario == 'Consumidor':
                    return redirect('panel_consumidor')
                elif usuario.tipo_usuario == 'Empresa':
                    return redirect('panel_empresa')
            else:
                messages.error(request, "Contraseña incorrecta.")  # Mensaje si la contraseña no coincide
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado. Verifique el correo.")  # Mensaje si el usuario no existe

    return render(request, 'login_registro_agromarket.html')  # Renderiza nuevamente el formulario

# Vista para registrar un nuevo usuario
def registro_usuario(request):
    if request.method == 'POST':
        try:
            correo = request.POST.get('correo')
            # Verifica si el correo ya está registrado
            if Usuario.objects.filter(correo=correo).exists():
                messages.error(request, "El correo ya está registrado.")
                return redirect('registro_usuario')

            # Crea el nuevo usuario con los datos del formulario
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
            return redirect('login_usuario')  # Redirige al login tras registrarse

        except Exception as e:
            messages.error(request, f"Error al registrar el usuario: {e}")  # Captura cualquier error
            return redirect('registro_usuario')

    return render(request, 'login_registro_agromarket.html')  # Muestra la vista en GET

# Vista para el panel del consumidor (usuario tipo "Consumidor")
def panel_consumidor(request):
    usuario = Usuario.objects.get(id=request.session['usuario_id'])  # Recupera el usuario actual desde sesión
    productos_agricultores = ProductoAgricultor.objects.all()  # Lista todos los productos de agricultores
    productos_empresas = ProductoEmpresa.objects.all()  # Lista todos los productos de empresas
    return render(request, 'panel_consumidor.html', {
        'usuario': usuario,
        'productos_agricultores': productos_agricultores,
        'productos_empresas': productos_empresas,
    })

# Vista para página informativa (genérica)
def informacion(request):
    return render(request, 'informacion.html', {})

# Vista para el panel de la empresa (usuario tipo "Empresa")
def panel_empresa(request):
    usuario = Usuario.objects.get(id=request.session['usuario_id'])  # Recupera el usuario actual desde sesión
    productos_agricultores = ProductoAgricultor.objects.all()  # Lista todos los productos de agricultores
    productos_empresas = ProductoEmpresa.objects.all()  # Lista todos los productos de empresas
    return render(request, 'panel_empresa.html', {
        'usuario': usuario,
        'productos_agricultores': productos_agricultores,
        'productos_empresas': productos_empresas,
    })

# Otra vista de información, posiblemente diferente de la anterior
def informacion2(request):
    return render(request, 'informacion2.html', {})


# Vista para que una empresa publique un producto
def publicar_producto_empresa(request):
    # Verificar si el usuario está autenticado mediante la sesión
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para acceder a esta página.")
        return redirect('login_usuario')

    try:
        # Obtener el usuario desde la base de datos
        usuario = Usuario.objects.get(id=usuario_id)
        # Validar que sea del tipo "Empresa"
        if usuario.tipo_usuario != 'Empresa':
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect('login_usuario')  # Redirección alternativa
    except Usuario.DoesNotExist:
        messages.error(request, "Usuario no encontrado.")
        return redirect('login_usuario')

    # Procesar datos del formulario si se hace POST
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
        imagenes = request.FILES.getlist('imagenes')  # Lista de archivos enviados

        try:
            # Obtener la categoría seleccionada
            categoria = Categoria.objects.get(id=categoria_id)

            # Crear el producto para la empresa
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

            # Guardar imágenes relacionadas al producto
            for imagen in imagenes:
                producto.imagenes.create(imagen=imagen)

            messages.success(request, "Producto publicado correctamente.")
            return redirect('panel_empresa')  # Redirige al panel

        # Si la categoría no existe
        except Categoria.DoesNotExist:
            messages.error(request, "Categoría no válida.")
        # Captura cualquier otro error inesperado
        except Exception as e:
            messages.error(request, f"Error al guardar el producto: {str(e)}")

    # Si es GET, obtener todas las categorías y mostrar el formulario
    categorias = Categoria.objects.all()
    return render(request, 'publicar_producto_empresa.html', {'categorias': categorias})

# Vista para renderizar un formulario separado para publicar productos
def publicar_producto_form(request):
    categorias = Categoria.objects.all()  # Obtener todas las categorías disponibles
    return render(request, 'publicar_producto_form.html', {'categorias': categorias})


# Vista para mostrar los productos publicados por la empresa
def mis_productos(request):
    usuario_id = request.session.get('usuario_id')
    # Verificar que el usuario haya iniciado sesión
    if not usuario_id:
        return JsonResponse({'html': '<p>No has iniciado sesión.</p>'}, status=403)

    try:
        # Obtener el usuario
        usuario = Usuario.objects.get(id=usuario_id)
        # Obtener los productos de la empresa asociada al usuario
        productos = ProductoEmpresa.objects.filter(usuario=usuario)

        # Verificar si no hay productos
        if not productos.exists():
            return JsonResponse({'html': '<p>No tienes productos publicados.</p>'})

        html = ""
        # Generar HTML dinámicamente para cada producto
        for producto in productos:
            html += f'''
                <div class="producto" id="producto-{producto.id}">
                    <p><strong>{escape(producto.nombre)}</strong> - ${producto.precio}</p>
            '''

            # Si el producto tiene imágenes asociadas, se muestran
            if producto.imagenes.all():
                html += '<div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px;">'
                for imagen in producto.imagenes.all():
                    html += f'<img src="{imagen.imagen.url}" alt="Imagen del producto" width="120px" height="120px" style="object-fit: cover; border-radius: 5px; border: 1px solid #ccc;" />'
                html += '</div>'

            # Botones para editar o eliminar el producto
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

        # Devolver el HTML generado como respuesta JSON
        return JsonResponse({'html': html})

    # Si el usuario no existe en la base de datos
    except Usuario.DoesNotExist:
        return JsonResponse({'html': '<p>Usuario no válido.</p>'}, status=404)

# Vista para eliminar un producto específico de la base de datos
def eliminar_producto(request, producto_id):
    # Verifica que la solicitud sea por método POST
    if request.method == "POST":
        try:
            # Busca el producto con el ID proporcionado
            producto = ProductoEmpresa.objects.get(id=producto_id)
            # Elimina el producto de la base de datos
            producto.delete()
            # Devuelve una respuesta JSON indicando éxito
            return JsonResponse({'success': True})
        except ProductoEmpresa.DoesNotExist:
            # Si el producto no existe, devuelve un error 404
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    # Si el método HTTP no es POST, devuelve un error 405
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Vista que devuelve un formulario HTML para editar un producto, renderizado como string
def form_editar_producto(request, producto_id):
    try:
        # Obtiene el producto que se desea editar
        producto = ProductoEmpresa.objects.get(id=producto_id)
        # Obtiene todas las categorías disponibles
        categorias = Categoria.objects.all()  # Asegúrate de importar tu modelo Categoria

        # Construye las opciones del <select> para categorías, marcando la seleccionada
        opciones_categoria = ""
        for categoria in categorias:
            selected = "selected" if categoria.id == producto.categoria.id else ""
            opciones_categoria += f'<option value="{categoria.id}" {selected}>{categoria.nombre}</option>'

        # Construye el formulario HTML con los datos actuales del producto
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
        # Devuelve el formulario HTML como parte de una respuesta JSON
        return JsonResponse({'html': html})
    except ProductoEmpresa.DoesNotExist:
        # Si no se encuentra el producto, devuelve un mensaje HTML con error 404
        return JsonResponse({'html': '<p>Producto no encontrado.</p>'}, status=404)


# Vista para procesar la edición de un producto cuando se envía el formulario
def editar_producto(request, producto_id):
    # Solo permite solicitudes POST
    if request.method == 'POST':
        try:
            # Obtener el producto que se desea editar
            producto = ProductoEmpresa.objects.get(id=producto_id)

            # Actualizar los campos del producto con los datos recibidos
            producto.nombre = request.POST.get('nombre')
            producto.precio = request.POST.get('precio')
            producto.descuento = request.POST.get('descuento')
            producto.unidad_medida = request.POST.get('unidad_medida')
            producto.cantidad_disponible = request.POST.get('cantidad_disponible')
            producto.nombre_empresa = request.POST.get('nombre_empresa')
            producto.descripcion = request.POST.get('descripcion')
            producto.ubicacion = request.POST.get('ubicacion')

            # Actualizar la categoría si se proporcionó
            categoria_id = request.POST.get('categoria')
            if categoria_id:
                producto.categoria_id = categoria_id

            # Guardar los cambios en la base de datos
            producto.save()

            # Si se subieron nuevas imágenes, se agregan al producto
            for imagen in request.FILES.getlist('imagenes'):
                producto.imagenes.create(imagen=imagen)  # Asumiendo una relación ProductoEmpresa -> Imagen con .imagenes

            # Respuesta JSON indicando éxito
            return JsonResponse({'success': True})
        except ProductoEmpresa.DoesNotExist:
            # Si no se encuentra el producto, devolver error 404
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    # Si el método HTTP no es POST, devolver error 405
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# módulo para el panel de agricultor

# Vista que muestra el panel principal del agricultor con sus productos y productos de empresas
def panel_agricultor(request):
    # Obtiene al usuario autenticado desde la sesión
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    # Obtiene todos los productos registrados por agricultores
    productos_agricultores = ProductoAgricultor.objects.all()
    # Obtiene todos los productos registrados por empresas
    productos_empresas = ProductoEmpresa.objects.all()
    # Renderiza el panel del agricultor con la información obtenida
    return render(request, 'panel_agricultor.html', {
        'usuario': usuario,
        'productos_agricultores': productos_agricultores,
        'productos_empresas': productos_empresas,
    })


# Vista auxiliar para mostrar una página informativa (informacion3.html)
def informacion3(request):
    return render(request, 'informacion3.html', {})


# Vista para permitir a un agricultor publicar un nuevo producto
def publicar_producto_agricultor(request):
    # Verifica si el usuario ha iniciado sesión
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para acceder a esta página.")
        return redirect('login_usuario')

    try:
        # Obtiene el usuario a partir del ID en la sesión
        usuario = Usuario.objects.get(id=usuario_id)
        # Verifica que el usuario tenga tipo "Agricultor"
        if usuario.tipo_usuario != 'Agricultor':
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect('login_usuario')
    except Usuario.DoesNotExist:
        # Maneja el caso en que el usuario no exista en la base de datos
        messages.error(request, "Usuario no encontrado.")
        return redirect('login_usuario')

    # Si el método de la solicitud es POST, procesar el formulario
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
            # Verifica que la categoría exista
            categoria = Categoria.objects.get(id=categoria_id)

            # Crea el nuevo producto con los datos recibidos
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

            # Guarda cada imagen subida para el producto
            for imagen in imagenes:
                ImagenProducto.objects.create(producto_agricultor=producto, imagen=imagen)

            # Mensaje de éxito y redirecciona al panel del agricultor
            messages.success(request, "Producto publicado correctamente.")
            return redirect('panel_agricultor')

        # Manejo de errores posibles
        except Categoria.DoesNotExist:
            messages.error(request, "Categoría no válida.")
        except Exception as e:
            messages.error(request, f"Error al guardar el producto: {str(e)}")

    # Si el método no es POST o hubo error, se vuelve a mostrar el formulario
    categorias = Categoria.objects.all()
    return render(request, 'publicar_producto_agricultor.html', {'categorias': categorias})


# Vista para cargar solo el formulario de publicación de producto para el agricultor
def publicar_producto_form_A(request):
    categorias = Categoria.objects.all()
    return render(request, 'publicar_producto_form_A.html', {'categorias': categorias})


# Vista que genera HTML dinámico con todos los productos del agricultor autenticado
def mis_productos_agricultor(request):
    # Verifica que el usuario esté autenticado
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return JsonResponse({'html': '<p>No has iniciado sesión.</p>'}, status=403)

    try:
        # Obtiene el usuario autenticado
        usuario = Usuario.objects.get(id=usuario_id)
        # Filtra los productos del agricultor correspondiente
        productos = ProductoAgricultor.objects.filter(usuario=usuario)

        # Si no hay productos publicados, se muestra un mensaje
        if not productos.exists():
            return JsonResponse({'html': '<p>No tienes productos publicados.</p>'})

        html = ""
        # Recorre cada producto y genera su representación HTML
        for producto in productos:
            html += f'''
                <div class="producto" id="producto-{producto.id}">
                    <p><strong>{escape(producto.nombre)}</strong> - ${producto.precio}</p>
            '''

            # Si el producto tiene imágenes, se muestran en un contenedor
            if producto.imagenes.all():
                html += '<div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px;">'
                for imagen in producto.imagenes.all():
                    html += f'<img src="{imagen.imagen.url}" alt="Imagen del producto" width="120px" height="120px" style="object-fit: cover; border-radius: 5px; border: 1px solid #ccc;" />'
                html += '</div>'

            # Agrega botones para editar o eliminar el producto
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

        # Devuelve el HTML generado como respuesta JSON
        return JsonResponse({'html': html})

    # Si el usuario no existe, se devuelve un mensaje de error
    except Usuario.DoesNotExist:
        return JsonResponse({'html': '<p>Usuario no válido.</p>'}, status=404)

# Vista para eliminar un producto de un agricultor
def eliminar_producto_agricultor(request, producto_id):
    # Verifica que el método de la solicitud sea POST
    if request.method == "POST":
        try:
            # Intenta obtener el producto por ID
            producto = ProductoAgricultor.objects.get(id=producto_id)
            # Elimina el producto
            producto.delete()
            # Retorna respuesta JSON de éxito
            return JsonResponse({'success': True})
        except ProductoAgricultor.DoesNotExist:
            # Si el producto no existe, retorna error 404
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    # Si no es POST, retorna error 405 (método no permitido)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Vista que devuelve el formulario HTML para editar un producto del agricultor
def form_editar_producto_agricultor(request, producto_id):
    try:
        # Obtiene el producto a editar
        producto = ProductoAgricultor.objects.get(id=producto_id)
        # Obtiene todas las categorías para el selector
        categorias = Categoria.objects.all()

        # Construye las opciones del select con preselección
        opciones_categoria = ""
        for categoria in categorias:
            selected = "selected" if categoria.id == producto.categoria.id else ""
            opciones_categoria += f'<option value="{categoria.id}" {selected}>{categoria.nombre}</option>'

        # Construye el formulario como HTML para retorno en JSON
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
        # Retorna el HTML en formato JSON
        return JsonResponse({'html': html})
    except ProductoAgricultor.DoesNotExist:
        # Si el producto no existe, retorna un mensaje de error en HTML
        return JsonResponse({'html': '<p>Producto no encontrado.</p>'}, status=404)


# Vista para procesar la edición de un producto de agricultor
def editar_producto_agricultor(request, producto_id):
    # Solo permite solicitudes POST
    if request.method == 'POST':
        try:
            # Obtiene el producto a editar
            producto = ProductoAgricultor.objects.get(id=producto_id)

            # Actualiza los campos con los valores del formulario
            producto.nombre = request.POST.get('nombre')
            producto.precio = request.POST.get('precio')
            producto.unidad_medida = request.POST.get('unidad_medida')
            producto.cantidad_disponible = request.POST.get('cantidad_disponible')
            producto.descripcion = request.POST.get('descripcion')
            producto.ubicacion = request.POST.get('ubicacion')

            # Asigna la nueva categoría si se proporciona
            categoria_id = request.POST.get('categoria')
            if categoria_id:
                producto.categoria_id = categoria_id

            # Guarda los cambios del producto
            producto.save()

            # Guarda nuevas imágenes si se subieron
            for imagen in request.FILES.getlist('imagenes'):
                ImagenProducto.objects.create(producto_agricultor=producto, imagen=imagen)

            # Retorna éxito en formato JSON
            return JsonResponse({'success': True})
        except ProductoAgricultor.DoesNotExist:
            # Si el producto no existe, retorna error 404
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    # Si no es POST, retorna error 405
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# Vista para separar un producto desde el punto de vista de un consumidor
def separar_producto(request, producto_id):
    # Verifica que el usuario esté autenticado
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    # Obtiene el usuario o retorna 404 si no existe
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Redirige si el usuario no es un consumidor
    if usuario.tipo_usuario != "Consumidor":
        return redirect('panel_consumidor')

    # Inicializa las variables del producto
    producto_agricultor = None
    producto_empresa = None
    vendedor = None

    try:
        # Intenta obtener el producto desde el modelo de agricultor
        producto_agricultor = ProductoAgricultor.objects.get(id=producto_id)
        vendedor = producto_agricultor.usuario  # Usuario vendedor agricultor
        producto = producto_agricultor
        tipo_producto = 'agricultor'
    except ProductoAgricultor.DoesNotExist:
        try:
            # Si no está en agricultores, busca en productos de empresa
            producto_empresa = ProductoEmpresa.objects.get(id=producto_id)
            vendedor = producto_empresa.usuario  # Usuario vendedor empresa
            producto = producto_empresa
            tipo_producto = 'empresa'
        except ProductoEmpresa.DoesNotExist:
            # Si no se encuentra en ninguno, redirige al panel
            return redirect('panel_consumidor')

    # Renderiza la vista con los datos del producto y usuario
    context = {
        'producto': producto,
        'vendedor': vendedor,
        'tipo_producto': tipo_producto,
        'usuario': usuario,
    }

    return render(request, 'separar_producto.html', context)


# Vista para separar un producto desde el punto de vista de un agricultor
def separar_producto_agricultor(request, producto_id):
    # Verifica autenticación
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    # Obtiene el usuario
    usuario = get_object_or_404(Usuario, id=usuario_id)

    # Verifica que sea agricultor
    if usuario.tipo_usuario != "Agricultor":
        return redirect('panel_agricultor')

    # Inicializa variables del producto
    producto_agricultor = None
    producto_empresa = None
    vendedor = None

    try:
        # Intenta obtener producto de agricultor
        producto_agricultor = ProductoAgricultor.objects.get(id=producto_id)
        vendedor = producto_agricultor.usuario
        producto = producto_agricultor
        tipo_producto = 'agricultor'
    except ProductoAgricultor.DoesNotExist:
        try:
            # Si no es de agricultor, busca en productos de empresa
            producto_empresa = ProductoEmpresa.objects.get(id=producto_id)
            vendedor = producto_empresa.usuario
            producto = producto_empresa
            tipo_producto = 'empresa'
        except ProductoEmpresa.DoesNotExist:
            # Producto no encontrado, redirige
            return redirect('panel_agricultor')

    # Renderiza el producto con su contexto
    context = {
        'producto': producto,
        'vendedor': vendedor,
        'tipo_producto': tipo_producto,
        'usuario': usuario,
    }

    return render(request, 'separar_producto_agricultor.html', context)


# Vista para separar un producto desde el punto de vista de una empresa
def separar_producto_empresa(request, producto_id):
    # Verifica autenticación
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    # Obtiene el usuario
    usuario = get_object_or_404(Usuario, id=usuario_id)

    # Verifica que sea empresa
    if usuario.tipo_usuario != "Empresa":
        return redirect('panel_empresa')

    # Inicializa variables
    producto_agricultor = None
    producto_empresa = None
    vendedor = None

    try:
        # Intenta obtener producto del agricultor
        producto_agricultor = ProductoAgricultor.objects.get(id=producto_id)
        vendedor = producto_agricultor.usuario
        producto = producto_agricultor
        tipo_producto = 'agricultor'
    except ProductoAgricultor.DoesNotExist:
        try:
            # Si no está en agricultores, busca en productos de empresa
            producto_empresa = ProductoEmpresa.objects.get(id=producto_id)
            vendedor = producto_empresa.usuario
            producto = producto_empresa
            tipo_producto = 'empresa'
        except ProductoEmpresa.DoesNotExist:
            # Producto no encontrado, redirige
            return redirect('panel_empresa')

    # Renderiza la plantilla correspondiente
    context = {
        'producto': producto,
        'vendedor': vendedor,
        'tipo_producto': tipo_producto,
        'usuario': usuario,
    }

    return render(request, 'separar_producto_empresa.html', context)









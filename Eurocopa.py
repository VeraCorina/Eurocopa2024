import requests
import json
import urllib.request
import random
import string
import atexit
import os
import matplotlib.pyplot as plt
from bokeh.plotting import figure, show # Inclusion de librerias necesarias para la ejecucion del proyecto

# Clase equipo, se guardan los datos capturados desde la API
class Equipo:
    def __init__(self, id, code, name, group):
        self.id = id
        self.code = code
        self.name = name
        self.group = group

# Clase stadium, se guardan los datos capturados desde la API
class Stadium:
    def __init__(self, id, name, city, capacity_general, capacity_vip, restaurants):
        self.id = id
        self.name = name
        self.city = city
        self.capacity_general = capacity_general
        self.capacity_vip = capacity_vip
        self.restaurants = restaurants
        self.asientos = [["Disponible" for _ in range(self.capacity_vip)] for _ in range(self.capacity_general)]

# Clase restaurant, se guardan los datos capturados desde la API
class Restaurant:
    def __init__(self, name, products):
        self.name = name
        self.products = products

# Clase product, se guardan los datos capturados desde la API
class Product:
    def __init__(self, name, quantity, price, adicional, stock):
        self.name = name
        self.quantity = quantity
        self.price = float(price) + float(price)*0.16 # Se guarda el precio incluido con el IVA
        self.adicional = adicional
        self.stock = stock

# Clase cliente, se guardan los datos capturados desde la API
class Cliente:
    def __init__(self, nombre, cedula, edad, tipo_entrada, nombre_estadio):
        self.nombre = nombre
        self.cedula = cedula
        self.edad = edad
        self.tipo_entrada = tipo_entrada
        self.nombre_estadio = nombre_estadio
        self.id_boleto = self.generar_id_boleto() # Se genera un id de boleto aleatorio cada vez que se crea un cliente

    def generar_id_boleto(self): # Funcion para generar un id aleatorio para el boleto
        caracteres = string.ascii_letters + string.digits
        id_boleto = ''.join(random.choice(caracteres) for _ in range(8))
        return id_boleto

# Clase match, se guardan los datos capturados desde la API
class Match:
    def __init__(self, match_data, equipos, estadios):
        self.id = match_data['id']
        self.number = match_data['number']
        self.home = self.get_equipo_by_id(match_data['home']['id'], equipos)
        self.away = self.get_equipo_by_id(match_data['away']['id'], equipos)
        self.date = match_data['date']
        self.group = match_data['group']
        self.estadio = self.get_estadio_by_id(match_data['stadium_id'], estadios)

    def get_equipo_by_id(self, equipo_id, equipos):
        for equipo in equipos:
            if equipo.id == equipo_id:
                return equipo
        return None

    def get_estadio_by_id(self, estadio_id, estadios):
        for estadio in estadios:
            if estadio.id == estadio_id:
                return estadio
        return None

# Funcion que carga todos los datos, hace tres llamadas a la API y captura todos los datos necesarios
def cargar_datos():
    # Cargar los equipos desde la API
    equipos = cargar_equipos("https://raw.githubusercontent.com/Algoritmos-y-Programacion/api-proyecto/main/teams.json")
    # Cargar los estadios y restaurantes desde la API
    estadios = cargar_estadios("https://raw.githubusercontent.com/Algoritmos-y-Programacion/api-proyecto/main/stadiums.json")
    # Cargar los partidos desde la API
    partidos = cargar_partidos("https://raw.githubusercontent.com/Algoritmos-y-Programacion/api-proyecto/main/matches.json", equipos, estadios)
    return equipos, estadios, partidos

def cargar_equipos(url): # Funcion que recibe como parametro la url de los equipos y captura sus datos
    try:
        response = requests.get(url)
        if response.status_code == 200:
            equipos_data = json.loads(response.text)
            equipos = []
            for equipo_data in equipos_data:
                equipo = Equipo(
                    id=equipo_data["id"],
                    code=equipo_data["code"],
                    name=equipo_data["name"],
                    group=equipo_data["group"]
                )
                equipos.append(equipo)
            return equipos
        else:
            print("Error en la solicitud HTTP:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error en la conexión:", str(e))
    return None

def cargar_estadios(url): # Funcion que recibe como parametro la url de los estadios y captura sus datos
    try:
        response = urllib.request.urlopen(url)
        data = json.load(response)
        stadiums = []
        for item in data:
            stadium_id = item["id"]
            stadium_name = item["name"]
            stadium_city = item["city"]
            stadium_capacity_general = item["capacity"][0] # Separar las entradas "General"
            stadium_capacity_vip = item["capacity"][1] # Entradas "VIP"

            restaurants = []
            for restaurant_data in item["restaurants"]:
                restaurant_name = restaurant_data["name"]
                products = []
                for product_data in restaurant_data["products"]:
                    product_name = product_data["name"]
                    product_quantity = product_data["quantity"]
                    product_price = product_data["price"]
                    product_adicional = product_data["adicional"]
                    product_stock = product_data["stock"]
                    product = Product(product_name, product_quantity, product_price, product_adicional, product_stock)
                    products.append(product)

                restaurant = Restaurant(restaurant_name, products)
                restaurants.append(restaurant)

            stadium = Stadium(stadium_id, stadium_name, stadium_city, stadium_capacity_general, stadium_capacity_vip, restaurants)
            stadiums.append(stadium)

        return stadiums
    except urllib.error.URLError as e:
        print("Error en la conexión:", str(e))
    return None

# Funcion que recibe como parametro la url de los partidos y captura sus datos
# Ademas se le pasa los equipos y los estadios para completar la informacion del partido
def cargar_partidos(url, equipos, estadios): 
    try:
        response = requests.get(url)
        if response.status_code == 200:
            partidos_data = response.json()
            partidos = []
            for match_data in partidos_data:
                partido = Match(match_data, equipos, estadios)
                partidos.append(partido)
            return partidos
        else:
            print("Error en la solicitud HTTP:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error en la conexión:", str(e))
    return None

# Funcion que verifica si el numero de cedula del ciente es un numero vampiro
def es_numero_vampiro(cedula):
    cedula_str = str(cedula)
    cedula_longitud = len(cedula_str)

    # Verificar si el número de dígitos de la cédula es par
    if cedula_longitud % 2 != 0:
        return False

    # Calcular los dos factores posibles
    for factor1 in range(1, 10**(cedula_longitud // 2)):
        if cedula % factor1 == 0:
            factor2 = cedula // factor1
            factor2_str = str(factor2)

            # Verificar si ambos factores tienen la misma cantidad de dígitos que la cédula original
            if len(str(factor1)) == cedula_longitud // 2 and len(factor2_str) == cedula_longitud // 2:
                # Verificar si los factores contienen todos los dígitos de la cédula original
                digitos_cedula = list(cedula_str)
                digitos_factores = list(str(factor1) + factor2_str)
                digitos_factores.sort()
                digitos_cedula.sort()

                if digitos_factores == digitos_cedula:
                    return True

    return False

# Funcion que verifica si el numero de cedula del cliente es un numero perfecto
def es_numero_perfecto(cedula):
    suma_divisores = sum(divisor for divisor in range(1, cedula) if cedula % divisor == 0)
    return suma_divisores == cedula

# Funcion de busqueda, retorna todos los partidos recibiendo un nombre de pais
def buscar_partidos_por_pais(pais, partidos):
    partidos_encontrados = [partido for partido in partidos if partido.home.name == pais or partido.away.name == pais]
    return partidos_encontrados

# Funcion de busqueda, retorna todos los partidos recibiendo un nombre de estadio
def buscar_partidos_por_estadio(estadio, partidos):
    partidos_encontrados = []
    for partido in partidos:
        if partido.estadio.name == estadio:
            partidos_encontrados.append(partido)
    return partidos_encontrados

# Funcion de busqueda, retorna todos los partidos recibiendo una fecha en especifico
def buscar_partidos_por_fecha(fecha, partidos):
    partidos_encontrados = []
    for partido in partidos:
        if partido.date == fecha:
            partidos_encontrados.append(partido)
    return partidos_encontrados

# Funcion que pide por pantalla todos los datos del cliente, y retorna sus datos
def solicitar_datos_cliente(partidos):
    print("Sistema de venta de entradas") # Solicitar los datos del cliente
    nombre = input("Nombre ")
    cedula = input("Cédula ")
    edad = int(input("Edad "))
    mostrar_partidos(partidos)  # Mostrar información de los partidos
    partido_id = input("ID del partido: ")
    tipo_entrada = input("Tipo de entrada que desea comprar (General/VIP): ")
    return nombre, cedula, edad, partido_id, tipo_entrada

# Funcion que muestra la informacion de todos los partidos disponibles
def mostrar_partidos(partidos):
    print("Partidos:")
    for partido in partidos:
        print(f"ID: {partido.id}")
        print(f"Fecha: {partido.date}")
        print(f"Local: {partido.home.name}")
        print(f"Visitante: {partido.away.name}")
        print(f"Estadio: {partido.estadio.name}")
        print()

# Funcion que calcula el costo de una entrada, aplicando el descuento si es necesario y dependiendo del tipo de la entrada
def calcular_costo_entrada(tipo_entrada, cedula):
    if cedula.isdigit() and es_numero_vampiro(int(cedula)):
        print("Cedula vampiro, 50% de descuento.")
        descuento = 0.5
    else:
        descuento = 0

    if tipo_entrada == "General":
        precio_base = 35 # Precio de la entrada General
    elif tipo_entrada == "VIP":
        precio_base = 75 # Precio de la entrada VIP
    else:
        print("Tipo de entrada inválido.")
        return None

    subtotal = precio_base
    iva = subtotal * 0.16
    total = subtotal - (subtotal * descuento) + iva

    return subtotal, descuento, iva, total

# Funcion que muestra un bosquejo o mapa del estadio seleccionado para seleccionar un asiento
def seleccionar_asiento(estadio):
    print("----- Mapa del Estadio -----")
    for i in range(estadio.capacity_general):
        fila = []
        for j in range(estadio.capacity_vip):
            fila.append("O")
        print(" ".join(fila))

    while True:
        fila = int(input("Número de fila: "))
        columna = int(input("Número de columna: "))

        if fila < 1 or fila > estadio.capacity_general or columna < 1 or columna > estadio.capacity_vip:
            print("Asiento inválido. Intente nuevamente.")
        else:
            asiento = estadio.asientos[fila - 1][columna - 1]
            if asiento == "Ocupado":
                print("El asiento seleccionado está ocupado. Por favor, elija otro.")
            else:
                estadio.asientos[fila - 1][columna - 1] = "Ocupado"
                print("¡Asiento seleccionado correctamente!")
                return f"Fila {fila}, Columna {columna}"

clientes = [] # Lista de clientes, se guardan todos las instancias del cliente cada vez que compra una entrada
# Funcion que muestra la logica completa para la venta de una entrada
def vender_entrada(partidos, estadios):
    nombre, cedula, edad, partido_id, tipo_entrada = solicitar_datos_cliente(partidos)
    partido = None
    for p in partidos:
        if p.id == partido_id:
            partido = p
            break
    if partido is None:
        print("Partido no encontrado.")
        return
    estadio = partido.estadio
    asiento = seleccionar_asiento(estadio)
    costo_entrada = calcular_costo_entrada(tipo_entrada, cedula)
    if costo_entrada is None:
        return
    subtotal, descuento, iva, total = costo_entrada

    # Mostrar información al cliente
    print("Informacion de la Entrada: ")
    print(f"Cliente: {nombre}")
    print(f"Cédula: {cedula}")
    print(f"Edad: {edad}")
    print(f"Partido: {partido.home.name} vs {partido.away.name}")
    print(f"Estadio: {estadio.name}")
    print(f"Asiento: {asiento}")
    print("Costo del Boleto: ")
    print(f"Subtotal: ${subtotal:.2f}")
    print(f"Descuento: ${subtotal * descuento:.2f}")
    print(f"IVA (16%): ${iva:.2f}")
    print(f"Total: ${total:.2f}")

    opcion_pagar = input("¿Quiere pagar la entrada? (Si/No): ")
    if opcion_pagar == "Si":
        # Realizar el proceso de pago y ocupar el asiento  
        print("Pago exitoso. Su entrada ha sido reservada.")       
        cliente = Cliente(nombre, cedula, edad, tipo_entrada, estadio.name) # Creacion de una instancia cliente
        clientes.append(cliente)
        print("Su ID de entrada es: ", cliente.id_boleto)
    else:
        print("Venta de entrada cancelada.")

# Funcion para realizar la compra de los productos en el restaurante
def realizar_compra_restaurante(cedula, estadios):
    cliente = None
    for c in clientes:
        if c.cedula == cedula:
            cliente = c
            break
            
    if cliente is None: # Si el cliente no se encuentra registrado o no tiene entrada VIP se retorna la funcion
        print("Cliente no encontrado o no es VIP.")
        return

    nombre_estadio = cliente.nombre_estadio
    if cliente is not None:
        if cliente.tipo_entrada == "VIP":
            print("Productos disponibles en: ", nombre_estadio)
            for estadio in estadios:
                if estadio.name == nombre_estadio:
                    for restaurant in estadio.restaurants:
                        for product in restaurant.products:
                            imprimir_producto(product)

    productos_seleccionados = []
    monto_total = 0.0

    while True:
        nombre_producto = input("Nombre del producto que desea comprar ('fin' para finalizar): ")
        if nombre_producto.lower() == "fin":
            break

        producto_encontrado = False

        for estadio in estadios:
            if estadio.name == nombre_estadio:
                for restaurant in estadio.restaurants:
                    for product in restaurant.products:
                        if product.name.lower() == nombre_producto.lower():
                            producto_encontrado = True
                            if cliente.edad < 18 and product.adicional.lower() == "alcoholic": # Si el cliente es menor de edad, no deja comprar bebidas alcohólicas
                                print("No puedes comprar bebidas alcohólicas.")
                            else:
                                productos_seleccionados.append(product)
                                monto_total += product.price
                            break

                    if producto_encontrado:
                        break

            if producto_encontrado:
                break

        if not producto_encontrado:
            print("Producto no encontrado.")

    print("Productos seleccionados:")
    for producto in productos_seleccionados:
        imprimir_producto(producto)
        producto.stock -= 1 # Restando el producto del stock
    
    subtotal = monto_total
    
    if es_numero_perfecto(int(cliente.cedula)):
        print("Cédula perfecto. Obtendrá un 15% de descuento.")
        descuento = monto_total * 0.15
        monto_total -= descuento
    else:
        descuento = 0
    
    print("Monto total:", monto_total)
    
    opcion_pagar = input("¿Desea proceder con la compra? (Si/No): ")
    if opcion_pagar == "Si":
        # Realizar el proceso de pago de los productos  
        print("Pago exitoso:")       
        print("Subtotal: $", subtotal)
        print("Descuento: $", descuento)
        print("Total: $", monto_total)
        for producto in productos_seleccionados:
            imprimir_producto(producto)
    else:
        print("Venta cancelada.")

# Funcion para verificar si un boleto fue vendido y es valido para su uso
def validar_boleto(clientes, id_boleto):
    cliente_asistido = None
    # Buscar el cliente correspondiente al ID del boleto
    for cliente in clientes:
        if cliente.id_boleto == id_boleto:
            cliente_asistido = cliente
            break

    if cliente_asistido is None:
        print("El ID del boleto no es válido.")
        print("El boleto es falso.")
        return
    print("El boleto es válido. Cliente:", cliente_asistido.nombre)

# Funcion para buscar productos de los restaurantes dependiendo del criterio de busqueda
def buscar_productos(estadios, criterio, valor_busqueda=None, precio_minimo=None, precio_maximo=None):
    for estadio in estadios:
        for restaurant in estadio.restaurants:
            for product in restaurant.products:
                if criterio == "nombre" and valor_busqueda in product.name:
                    imprimir_producto(product)
                elif criterio == "tipo":
                    if valor_busqueda.lower() in product.adicional.lower():
                        imprimir_producto(product)
                elif criterio == "rango":
                    if precio_minimo is not None and precio_maximo is not None:
                        if precio_minimo <= product.price <= precio_maximo:
                            imprimir_producto(product)

# Funcion que imprime todos los productos seleccionados
def imprimir_producto(producto):
    print(f"Nombre: {producto.name}")
    print(f"Cantidad: {producto.quantity}")
    print(f"Precio (con IVA): ${producto.price:.2f}")
    print(f"Adicional: {producto.adicional}")
    print(f"Stock: {producto.stock}")
    print()

def guardar_datos_actuales(clientes, equipos, estadios, partidos): # Funcion para guardar los archivos actuales en un TXT
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(directorio_actual, "datos_actuales.txt") # Ruta del archivo donde se guardan los datos
    with open(ruta, "w") as archivo: # Abrir el archivo en modo escritura, crea el TXT en la ruta del .py
        archivo.write("Clientes:\n") # Guarda la informacion actual de todos los clientes, se actualiza de forma dinamica en la ejecucion del programa
        for cliente in clientes:
            archivo.write(f"Nombre: {cliente.nombre}\n")
            archivo.write(f"Cédula: {cliente.cedula}\n")
            archivo.write(f"Edad: {cliente.edad}\n")
            archivo.write(f"Tipo de entrada: {cliente.tipo_entrada}\n")
            archivo.write(f"ID del boleto: {cliente.id_boleto}\n")
            archivo.write("-------------------------\n")

        archivo.write("Estadios:\n") # Guarda la informacion actual de todos los estadios
        for estadio in estadios:
            archivo.write(f"Estadio: {estadio.name}\n")
            archivo.write(f"Ciudad: {estadio.city}\n")
            archivo.write(f"Capacidad general: {estadio.capacity_general}\n")
            archivo.write(f"Capacidad vip: {estadio.capacity_vip}\n")
            archivo.write("Restaurantes:\n")
            for restaurant in estadio.restaurants: # Guarda la informacion actual de los restaurantes
                archivo.write(f"- Nombre: {restaurant.name}\n")
                archivo.write("  Productos:\n")
                for product in restaurant.products: # Guarda la informacion actual de los productos
                    archivo.write(f"  - Nombre: {product.name}\n")
                    archivo.write(f"    Cantidad: {product.quantity}\n")
                    archivo.write(f"    Precio: {product.price}\n")
                    archivo.write(f"    Adicional: {product.adicional}\n")
                    archivo.write(f"    Stock: {product.stock}\n") # Atributo importante ya que el stock se actualiza 
                archivo.write("\n")
            archivo.write("\n")

# Funcion que saca el promedio de gastos de un cliente entre el ticket vip y productos consumidos en el restaurante
def promedio_gasto_clientes_vip(partidos, estadios):
    total_gastos = 0
    cantidad_clientes_vip = 0

    for cliente in clientes:
        if cliente.tipo_entrada == "VIP":
            # Calcular el gasto total del cliente (ticket + restaurante)
            gasto_total = 0
            
            # Calcular el costo del ticket
            costo_ticket = calcular_costo_entrada(cliente.tipo_entrada, cliente.cedula)
            if costo_ticket is not None:
                subtotal, descuento, iva, _ = costo_ticket
                gasto_total += subtotal - (subtotal * descuento) + iva
            
            # Calcular el gasto en el restaurante
            nombre_estadio = cliente.nombre_estadio
            for estadio in estadios:
                if estadio.name == nombre_estadio:
                    for restaurant in estadio.restaurants:
                        for product in restaurant.products:
                            gasto_total += product.price

            total_gastos += gasto_total
            cantidad_clientes_vip += 1

    if cantidad_clientes_vip > 0:
        promedio = total_gastos / cantidad_clientes_vip
        print("El promedio de gasto de un cliente VIP en un partido es de: $", promedio)
    else:
        print("No hay clientes VIP registrados.")

# Funcion que muestra la asistencia a los partidos
def mostrar_asistencia_partidos(partidos):
    asistencia_partidos = []

    for partido in partidos:
        boletos_vendidos = 0
        personas_asistieron = 0

        for cliente in clientes:
            if cliente.nombre_estadio == partido.estadio.name and cliente.tipo_entrada != "":
                boletos_vendidos += 1
                personas_asistieron += 1

        relacion_asistencia_venta = 0
        if boletos_vendidos > 0:
            relacion_asistencia_venta = personas_asistieron / boletos_vendidos

        asistencia_partidos.append((partido, boletos_vendidos, personas_asistieron, relacion_asistencia_venta))

    # Ordenar la lista de asistencia de mejor a peor
    asistencia_partidos.sort(key=lambda x: x[3], reverse=True)

    # Mostrar la tabla de asistencia
    print("----- Tabla de Asistencia a los Partidos -----")
    print("{:<30} {:<20} {:<15} {:<15} {:<25}".format("Partido", "Estadio", "Boletos Vendidos", "Personas Asistieron", "Relación Asistencia/Venta"))
    for partido, boletos_vendidos, personas_asistieron, relacion_asistencia_venta in asistencia_partidos:
        print("{:<30} {:<20} {:<15} {:<15} {:<25}".format(partido.home.name + " vs " + partido.away.name, partido.estadio.name, boletos_vendidos, personas_asistieron, relacion_asistencia_venta))
   
# Funcion que busca el partido con mayor asistencia y muestra los rivales
def encontrar_partido_mayor_asistencia(partidos):
    partido_mayor_asistencia = None
    mayor_asistencia = 0

    for partido in partidos:
        boletos_vendidos = 0
        personas_asistieron = 0

        for cliente in clientes:
            if cliente.nombre_estadio == partido.estadio.name and cliente.tipo_entrada != "":
                boletos_vendidos += 1
                personas_asistieron += 1

        if personas_asistieron > mayor_asistencia:
            mayor_asistencia = personas_asistieron
            partido_mayor_asistencia = partido

    if partido_mayor_asistencia is not None:
        print("El partido con mayor asistencia fue:", partido_mayor_asistencia.home.name, "vs", partido_mayor_asistencia.away.name)
    else:
        print("No hay partidos registrados.")

# Funcion que busca el partido con mayor boletos vendidos
def encontrar_partido_mayor_boletos_vendidos(partidos):
    partido_mayor_boletos = None
    mayor_boletos_vendidos = 0

    for partido in partidos:
        boletos_vendidos = 0

        for cliente in clientes:
            if cliente.nombre_estadio == partido.estadio.name and cliente.tipo_entrada != "":
                boletos_vendidos += 1

        if boletos_vendidos > mayor_boletos_vendidos:
            mayor_boletos_vendidos = boletos_vendidos
            partido_mayor_boletos = partido

    if partido_mayor_boletos is not None:
        print("El partido con mayor número de boletos vendidos fue:", partido_mayor_boletos.home.name, "vs", partido_mayor_boletos.away.name)
    else:
        print("No hay partidos registrados.")

# Funcion que muestra el top 3 de productos mas vendidos
def obtener_top_productos_vendidos(estadios):
    productos_vendidos = {}

    for estadio in estadios:
        for restaurant in estadio.restaurants:
            for producto in restaurant.products:
                total_vendidos = 0

                for cliente in clientes:
                    for item in cliente.orden:
                        if item == producto.nombre:
                            total_vendidos += 1

                if producto in productos_vendidos:
                    productos_vendidos[producto] += total_vendidos
                else:
                    productos_vendidos[producto] = total_vendidos

    top_productos = sorted(productos_vendidos.items(), key=lambda x: x[1], reverse=True)[:3]

    if top_productos:
        print("Los tres productos más vendidos en el restaurante son:")
        for producto, cantidad_vendida in top_productos:
            print("- Producto:", producto.name)
            print("  Cantidad vendida:", cantidad_vendida)
        return top_productos
    else:
        print("No hay productos registrados.")

# Funcion que muestra el top 3 de los clientes que mas compraron productos en el restaurante
def obtener_top_clientes_compradores(clientes):
    clientes_boletos = {}

    for cliente in clientes:
        boletos_comprados = 0

        for item in cliente.tipo_entrada:
            if item != "":
                boletos_comprados += 1

        clientes_boletos[cliente] = boletos_comprados

    top_clientes = sorted(clientes_boletos.items(), key=lambda x: x[1], reverse=True)[:3]

    if top_clientes:
        print("Los tres clientes que más compraron boletos son:")
        for cliente, boletos_comprados in top_clientes:
            print("- Cliente:", cliente.nombre)
            print("  Boletos comprados:", boletos_comprados)
        return top_clientes
    else:
        print("No hay clientes registrados.")

# Funcion que grafica las estadisticas de los productos
def graficar_top_productos_vendidos(top_productos):
    if top_productos:
        productos = [producto[0].name for producto in top_productos]
        cantidades = [producto[1] for producto in top_productos]

        plt.bar(productos, cantidades)
        plt.xlabel('Productos')
        plt.ylabel('Cantidad vendida')
        plt.title('Top 3 productos más vendidos')
        plt.show()
    else:
        print("No hay productos registrados.")

# Funcion que grafica las estadisticas de los clientes mas compradores de productos
def graficar_top_clientes_compradores(top_clientes):
    if top_clientes:
        clientes = [cliente[0].nombre for cliente in top_clientes]
        boletos = [cliente[1] for cliente in top_clientes]

        p = figure(x_range=clientes, plot_height=350, title='Top 3 clientes que más compraron boletos')
        p.vbar(x=clientes, top=boletos, width=0.9)
        p.xaxis.axis_label = 'Clientes'
        p.yaxis.axis_label = 'Boletos comprados'

        show(p)
    else:
        print("No hay clientes registrados.")

# Funcion principal con el flujo total del programa
def main():
    # Cargar los datos desde la API, esta opción se ejecuta como una precarga al iniciar el programa
    equipos, estadios, partidos = cargar_datos()
    print("Gestion de Entradas. Euro 2024")
   
    while(True): # Ciclo con el flujo principal del programa
   
        print("Menú: ")
        print("1. Buscar partidos.")
        print("2. Venta de entradas.")
        print("3. Validar boleto.")
        print("4. Buscar productos.")
        print("5. Comprar productos.")
        print("6. Mostrar estadísticas (completo).")
        print("7. Salir.")

        opcion = int(input("Elija una opcion: "))
        print()

        if opcion == 1:
            op = ""
            op = input("Elija el filtro (pais, estadio, fecha): ")
            if op == "pais":
                pais = input("Nombre del pais: ")
                partidos_pais = buscar_partidos_por_pais(pais, partidos)
                if partidos_pais:
                    print(f"Partidos de {pais}:")
                    for partido in partidos_pais:
                        print(f"Equipo local: {partido.home.name} vs Equipo visitante: {partido.away.name}")
                else:
                    print(f"No se encontraron partidos de {pais}.")
            elif op == "estadio":
                estadio = input("Nombre del estadio: ")
                partidos_estadio = buscar_partidos_por_estadio(estadio, partidos)
                if partidos_estadio:
                    print(f"Partidos en {estadio}")
                    for partido in partidos_estadio:
                        print(f"Equipo local: {partido.home.name} vs Equipo visitante: {partido.away.name}")
                else:
                    print(f"No se encontraron partidos en el estadio {estadio}.")
            elif op == "fecha":
                fecha = input("Fecha del partido (aaaa-mm-dd): ")
                partidos_fecha = buscar_partidos_por_fecha(fecha, partidos)
                if partidos_fecha:
                    print(f"Partidos en la fecha {fecha}:")
                    for partido in partidos_fecha:
                        print(f"ID: {partido.id}")
                        print(f"Equipo local: {partido.home.name}")
                        print(f"Equipo visitante: {partido.away.name}")
                        print(f"Estadio: {partido.estadio.name}")
                        print("-----")
                else:
                    print(f"No se encontraron partidos en la fecha {fecha}.")
            else:
                print("Opcion incorrecta.")
        elif opcion == 2:
            vender_entrada(partidos, estadios)
        elif opcion == 3:
            id_boleto = input("Ingrese ID del Boleto: ")
            validar_boleto(clientes, id_boleto)
        elif opcion == 4:
            op = ""
            op = input("Elija el filtro (nombre, tipo, rango): ")
            if op == "nombre":
                name = input("Nombre del producto: ")
                buscar_productos(estadios, "nombre", name)
            elif op == "tipo":
                tipo = input("Tipo: (alcoholic, non-alcoholic, package, plate): ")
                buscar_productos(estadios, "tipo", tipo)
            elif op == "rango":
                print("Introduce el rango de precio: ")
                inf = float(input("Rango inferior: "))
                sup = float(input("Rango superior: "))
                buscar_productos(estadios, "rango", "", inf, sup)
            else:
                print("Opcion incorrecta.")
        elif opcion == 5:
            cedula = input("Ingrese cedula del cliente: ")
            realizar_compra_restaurante(cedula, estadios)
        elif opcion == 6:
            promedio_gasto_clientes_vip(partidos, estadios) # Llamada de todas las funciones que muestran estadisticas
            mostrar_asistencia_partidos(partidos)
            encontrar_partido_mayor_asistencia(partidos)
            encontrar_partido_mayor_boletos_vendidos(partidos)
            top_productos = obtener_top_productos_vendidos(estadios)
            top_clientes = obtener_top_clientes_compradores(clientes)
            graficar_top_productos_vendidos(top_productos)
            graficar_top_clientes_compradores(top_clientes)
        elif opcion == 7:
            guardar_datos_actuales(clientes, equipos, estadios, partidos) # Llamada de la funcion para guardar los datos en un TXT
            print("Saliendo. Presione ENTER.")
            input()
            break
        else:
            print("Opcion incorrecta.")

# Llamada de la funcion principal
main()
# EXPORTAR: gráfica de barras horizontales
        
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path
import matplotlib.ticker as mticker
from matplotlib.ticker import FuncFormatter
from statistics import mode
import subprocess
from matplotlib.patches import Patch
import os

from funciones import limpiar_svg_con_scour, formato_fechas, get_text_color_for_bg, unir_barras, num_decimales, elimina_ceros_no_significativos, cambiar_color
import matplotlib.patheffects as path_effects 


def barras_horizontales(

    # --- GRÁFICA GENERAL ---
    df,                         # DataFrame de entrada
    nombre="barras_verticales", # Nombre base para archivos de salida
    tipo_letra='Montserrat',    # Tipo de letra para todo el texto en la gráfica
    colores=None,        # Lista de colores para las barras
    ancho=23,             # Ancho de la figura 
    alto=10,              # Alto de la figura
    grillas=True,               # Muestra u oculta las grillas horizontales
    fondo='transparent',        # Color de fondo de la figura ('transparent', 'white')
    decimales=None,             # Número de decimales a mostrar en los valores

    # --- DATOS Y ESTRUCTURA ---
    agregar_datos=None,         # Datos extra para agregar como barras
    ordenar='x',        # Ordenar las barras de acuerdo al eje X (valor), eje Y (etiqueta) o None (orden del DF).
    ascendente=False,        # Ordena las barras de forma ascendente (True) o descendente (False).
    unir_sup=0,                # Cantidad de barras a unir en la parte superior (primeras barras).
    unir_inf=0,                # Cantidad de barras a unir en la parte inferior (últimas barras).
    columna_categorias=None, # Entero que indica la posición (empezando por 1) de la columna para categorizar colores

    # --- BARRAS ---
    ancho_barra=0.85,            # Ancho de cada barra
    tam_valor_barra=11,   # Tamaño de letra para valores dentro de las barras
    peso_valor_barra='bold',  # Grosor de letra para valores dentro de las barras
    color_valor_barra=None,     # Color del texto de valor en barra
    tam_porce_barra=11,   # Tamaño de letra para porcentajes dentro de las barras
    peso_porce_barra='bold',  # Grosor de letra para porcentajes dentro de las barras
    color_porce_barra=None,     # Color de letra para porcentajes dentro de las barras
    valor_barra=True,           # Mostrar valor numérico en la barra
    porce_barra=False,           # Mostrar porcentaje en la barra
    porce_al_lado=True,         # Mostrar porcentaje al lado del valor dentro de la barra
    porce_diver=False,          # Porcentaje respecto a suma absoluta (divergente)
    alinear_texto_barra=True,   # Alinear el texto dentro de la barra horizontalmente

   # --- CÁPSULAS ---
    valor_capsu=True,           # Muestra u oculta la cápsula arriba de la barra
    tam_valor_capsu=12,   # Tamaño de letra para valores dentro de las cápsulas
    peso_valor_capsu='bold',  # Grosor de letra para valores dentro de las cápsulas
    color_valor_capsu=None,# Color de letra para valores dentro de las cápsulas
    color_fondo_capsu='#FFFFFF', # Color de fondo de la cápsula
    color_borde_capsu=None,# Color del borde de la cápsula
    peso_borde_capsu=1.8,     # Grosor del borde de la cápsula
    curvatura_capsu=0.7,         # Redondez de las cápsulas (float, 0 a 1)
    quitar_capsu=False,         # Quitar la cápsula y deja solo el valor dentro de la ella.
    activar_cambiar_color=True, # Agrega un contorno al texto si el color del texto y el fondo son muy similares
    capsu_cero=True,            # Mostrar cápsula aunque el valor sea cero
    asignar_etiquetas=None,     # Columna del dataframe df con las nuevas etiquetas que sustituiran las que se encuentran en la parte superior de las barras.
    alinear_capsu=True,        # Alinear la cápsula verticalmente, en la misma dirección de las barras. 
    ajustar_pos_capsu=0.00,      # Ajusta la posición de la cápsula respecto a la barra.
    ajustar_pos_capsu_areamin=0.026,   # Desplazamiento extra para la cápsula cuando hay etiquetas fuera.
    simbolo_negativo_capsu=False, # Si es True, agrega el signo negativo a las cápsulas de valores negativos.

    # --- OCULTAR ETIQUETAS CUANDO LAS BARRAS SON MUY PEQUEÑAS ---
    areamin=0,               # Área mínima para mostrar texto en barra
    opcion_areamin='fuera', # Opción para mostrar texto fuera o no mostrarlo al usar areamin ('sin etiquetas', 'fuera')
    ajustar_sep_valor_barra=1.0, # Multiplicador para el espaciado entre etiquetas desplazadas (fuera)
    color_valor_barra_fuera=None, # Color del texto de los valores desplazados fuera de la barra. Acepta un color fijo (str) o un dict {nombre_columna: color} para asignar por categoría. Si es None (o la columna no está en el dict), usa el color de la barra correspondiente.
    color_contorno_valor_barra=None, # Color fijo del contorno (stroke) de los valores desplazados fuera de la barra. Si es None, se calcula automáticamente según el fondo.

    # --- PORCENTAJES TOTALES ---
    porce_total=False,           # Muestra el valor del porcentaje respecto al total general arriba de la capsula
    porce_total_inicio=False,   # Cuando es True, hace lo mismo que porce_total pero lo muestra al inicio de la barra en lugar de arriba de la cápsula.
    ajustar_pos_porce_total=-0.09,      # Ajusta la posicion del porcentaje total
    tam_porce_total=11,         # Tamaño de letra para porcentaje total
    peso_porce_total='semibold', # Grosor de letra para porcentaje total
    color_porce_total='#434343',   # Color de letra para porcentaje total

    # --- LEYENDA ---
    leyenda=None,               # Título de la leyenda
    posicion_leyenda=(0.5, -0.2), # Coordenadas (x,y) relativas a la gráfica (ej: 0=izq, 1=der, y<0 la baja), string 'loc' (ej: 'best'), o dict con kwargs
    ajustar_pos_leyenda=0.0,    # Espacio extra para la leyenda
    num_columnas_leyenda=None,          # Número de columnas en la leyenda
    tam_letra_leyenda=12,       # Tamaño de letra para la leyenda
    peso_letra_leyenda='medium', # Grosor de letra para la leyenda
    color_letra_leyenda='#434343', # Color de letra para la leyenda

    # --- EJE Y (ETIQUETAS) ---
    tam_valor_ejey=14,          # Tamaño de letra para etiquetas eje Y
    peso_valor_ejey='medium', # Grosor de letra para etiquetas eje Y
    color_valor_ejey="#434343", # Color de letra para etiquetas eje Y
    espacio_inicio=0,           # Espacio extra al inicio del eje Y
    nombre_ejey=None,          # Nombre del eje Y
    tam_nombre_ejey=14,  # Tamaño de letra para nombre del eje Y
    peso_nombre_ejey='medium', # Grosor de letra para nombre del eje Y (posibles valores: 'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black')
    color_nombre_ejey='#434343', # Color de letra para nombre del eje Y.
    sustituir_valor_ejey=None,   # Lista para sustituir etiquetas del eje Y
    orientacion_valor_ejey=0,    # Grados de inclinación de etiquetas eje Y (ej. 0, 45, 90)
    ajustar_sep_izquierda_ejey=0.0,      # Aumenta separación en eje Y
    resaltar_valor_ejey=None,    # Lista de etiquetas a resaltar
    color_resaltado_ejey="#a3173e", # Color para el resaltado de etiquetas
    color_borde_resaltado_ejey='none',  # Color del borde de resaltado de etiquetas
    ejey_der=False,             # Colocar el eje Y a la derecha

    # --- EJE X (VALORES) ---
    tam_valor_ejex=14,          # Tamaño de letra para etiquetas eje X
    peso_valor_ejex='medium', # Grosor de letra para etiquetas eje X
    color_valor_ejex="#434343", # Color de letra para etiquetas eje X
    nombre_ejex=None,          # Nombre del eje X
    tam_nombre_ejex=14,  # Tamaño de letra para nombre del eje X
    peso_nombre_ejex='medium', # Grosor de letra para nombre del eje X
    color_nombre_ejex='#434343', # Color de letra para nombre del eje X
    limites_ejex=None,              # Límites del eje X
    solo_ejex_positivo=True,        # Eje X solo muestra valores positivos
    simbolo_porce_ejex=False,      # Añade el símbolo de porcentaje a los números del eje X
    divisiones_ejex=False,             # División personalizada del eje X
    respecto_porce=False,      # Graficar con respecto al porcentaje en el eje X
    modalidad_fechas=1,      # Argumento para la función formato_fechas
    mostrar_solo_fechas=None,   # Argumento para la función formato_fechas

    # --- GRÁFICA DE LÍNEAS ---
    columnas_lineas=None,       # Lista de nombres de columnas que serán graficadas como líneas verticales
    colores_lineas=None, # Lista de colores para las líneas
    capsu_final_lineas=False,     # Mostrar cápsula con el valor al final de cada línea
    espacio_entre_grupos=0.0,   # Espaciado adicional entre grupos de barras

    # ---- GAURDADO Y VISUALIZACIÓN -----
    guardar_fig=False,           # Guardar la figura en disco
    mostrar_fig=True,           # Mostrar la figura en pantalla
    svg_trazos=False,           # True: texto del SVG como trazos (no depende de la fuente instalada)
    tamano_exacto=False,        # True: la imagen final mide exactamente ancho x alto (cm)
):
    """
    Genera un gráfico de barras horizontales (apiladas si hay múltiples columnas) altamente personalizable.
    Ideal para comparar cantidades entre diferentes categorías, mostrar clasificaciones o visualizar la 
    composición de un total mediante barras apiladas a lo largo del eje Y.

    INFORMACIÓN PARA LA IA Y USUARIOS:
    Esta función está optimizada para generar gráficos de calidad de publicación. Las etiquetas, colores
    y tamaños son totalmente ajustables. Las cápsulas (rectángulos redondeados) al final de cada barra
    suman el total de sus componentes en la pila. Existen parámetros para resolver la colisión de etiquetas.

    ESTRUCTURA DEL DATAFRAME `df`:
    1. La primera columna SIEMPRE debe ser el eje Y (las categorías de las barras o etiquetas).
    2. Las columnas siguientes serán consideradas como los valores apilados (segmentos) de las barras 
       que se proyectarán a lo largo del eje X.
    3. Excepciones: columnas indicadas en `asignar_etiquetas` o `columnas_lineas` serán procesadas
       de manera independiente a los datos numéricos de las barras.
       
    Parámetros:
    
    --- GRÁFICA GENERAL ---
    df (pandas.DataFrame) : DataFrame de entrada con la estructura especificada arriba.
    nombre (str) : Nombre base para archivos de salida (.png y .svg se exportarán).
    tipo_letra (str) : Tipo de letra, por defecto 'Montserrat'.
    colores (list) : Lista de colores en HEX o nombres CSS para las series a apilar.
    ancho (float/int) : Ancho de la figura en centímetros.
    alto (float/int) : Alto de la figura en centímetros.
    grillas (bool) : Activar/desactivar grillas horizontales/verticales (alineadas al eje X).
    fondo (str) : Color de fondo. Puede ser 'transparent', 'white' o cualquier código HEX.
    decimales (int) : Número de decimales forzados en los valores dentro y fuera de la barra.

    --- DATOS Y ESTRUCTURA ---
    agregar_datos (list) : Permite insertar barras comparativas o de contexto sin añadirlas al DataFrame.
        Recibe una lista de tuplas con 2 a 5 elementos: `(categoria, [etiqueta], valor, [texto_barra], [opciones_extra])`.
        - `categoria`: El índice en X (Ej: 2018, 'Ene').
        - `etiqueta` (Opcional): Texto a mostrar en el eje X para esta barra.
        - `valor`: Cantidad a graficar (lista proporcional si son múltiples barras apiladas, ej. `[10, 20]`).
        - `texto_barra` (Opcional): Texto customizado para el interior de las barras agregadas.
        - `opciones_extra` (Opcional): Diccionario para estilos dict={
            'colores_fondo': ['#hex', 'none'], 'colores_borde': ['black'], 
            'estilos_borde': ['--'], 'grosores_borde': [2], 'colores_texto': ['blue'],
            'separador_derecha': '...', 'separador_izquierda': 'espacio' }
        Ejemplo 1 (Comparativa histórica anclada a la izquierda con separador):
           agregar_datos=[(2015, "Año Base", [50, 40], None, {'colores_fondo': ['#CCC', '#DDD'], 'separador_derecha': '...'})]
        Ejemplo 2 (Proyección futura transparente con borde punteado):
           agregar_datos=[("2027", "Proy.", [80, 90], "80/90 Est.", {'colores_fondo': ['none', 'none'], 'estilos_borde': ['--', '--']})]
    ordenar (str/None) : 'x' ordena por suma total del valor de la barra, 'y' por los nombres de las categorías, None preserva orden del DataFrame.
    ascendente (bool) : Si es True ordena los nuumeros o las etiquetas de forma ascendente, de lo contrario los ordena de forma descendente.
    unir_sup / unir_inf (int) : Agrupa las primeras (sup) o últimas (inf) 'n' filas y las condensa en una sola barra "Otros", reduciendo el ruido visual.
    columna_categorias (int) : Índice 1-based de la columna de agrupamiento. Modifica el color por categoría general.

    --- BARRAS ---
    ancho_barra (float) : 0 a 1 indicando grosor relativo de las barras (0.85 default).
    tam_valor_barra (int/float) : Tamaño letra etiqueta valor barra.
    peso_valor_barra (str) : Grosor fuente del valor numérico dentro de la barra. Puede ser 'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black'.
    color_valor_barra (str/None) : Color del texto para el valor o texto dentro de la barra.
    tam_porce_barra (int/float) : Tamaño de la letra exclusivamente para el texto del porcentaje mostrado en la barra.
    peso_porce_barra (str) : Grosor de la fuente del porcentaje. Puede ser 'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black'.
    color_porce_barra (str/None) : Color de la fuente del porcentaje.
    valor_barra (bool) : Muestra el valor numérico correspondiente a la barra o al segmento apilado.
    porce_barra (bool) : Muestra porcentaje respecto a la barra total apilada.
    porce_al_lado (bool) : Pone el porcentaje al lado del valor numérico.
    porce_diver (bool) : Porcentaje calculado respecto a la suma absoluta de los segmentos, útil en casos de barras bidireccionales.
    alinear_texto_barra (bool) : Cuando es True alinea el texto dentro de la barra horizontalmente, en la misma dirección de la barra.

    --- CÁPSULAS (Total al final de la barra) ---
    valor_capsu (bool) : Muestra el valor dentro de la capsula, la suma total de las barras apiladas para cada valor del eje Y.
    tam_valor_capsu (int/float) : Tamaño de letra para valores dentro de las cápsulas.
    peso_valor_capsu (str) : Grosor o estilo de la fuente para el texto de la cápsula. Puede ser 'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black'.
    color_valor_capsu (str/None) : Color en HEX del texto dentro de la cápsula.
    color_fondo_capsu (str) : Color en HEX de relleno interno de la cápsula.
    color_borde_capsu (str/None) : Color en HEX del borde de la cápsula.
    peso_borde_capsu (float/None) : Grosor del borde de la cápsula.
    curvatura_capsu (float) : 0 a 1 que redondea los bordes.
    quitar_capsu (bool) : Elimina la cápsula manteniendo solo el número dentro de la cápsula.
    activar_cambiar_color (bool) : Si es True, garantiza que el texto contraste bien con su fondo interior.
    capsu_cero (bool) : Mostrar cápsula aunque el total sume 0.
    asignar_etiquetas (str) : Columna del DataFrame (nombre) con las nuevas etiquetas para sustituir las mostradas en las cápsulas.
    alinear_capsu (bool) : Alinear la cápsula, siguiendo la dirección de las barras.
    ajustar_pos_capsu (float) : Ajusta la posición horizontal u offset de la cápsula respecto a la barra.
    ajustar_pos_capsu_areamin (float) : Desplazamiento extra de la capsula en aquellas barras donde los valores dentro de la barras tuvieron que ser sacadas de la barra (areamin).
    simbolo_negativo_capsu (bool) : Agregar símbolo negativo a las cápsulas con valor negativo.

    --- OCULTAR ETIQUETAS CUANDO LAS BARRAS SON MUY PEQUEÑAS ---
    areamin (int/float) : Área o tamaño mínimo necesario para mostrar un número dentro de la porción de barra. 
    opcion_areamin (str) : 'fuera' para sacar los números fuera de la barra cuando no haya espacio o 'sin etiquetas' para ocultarlos.
    ajustar_sep_valor_barra (float) : Multiplicador para acomodar las etiquetas que fueron empujadas fuera de la barra.
    color_valor_barra_fuera (str/dict/None) : Color en HEX para el texto de los valores desplazados fuera de la barra. Puede ser un color fijo (str) o un dict {nombre_columna: color} para definir un color distinto por categoría. Si es None (o la columna no está en el dict), usa el color de relleno de la barra correspondiente.
    color_contorno_valor_barra (str/None) : Color fijo en HEX para el contorno de los valores desplazados fuera de la barra. Si es None, se calcula automáticamente para contrastar con el fondo.

    --- PORCENTAJES TOTALES ---
    porce_total (bool) : Muestra el valor porcentual comparado contra la suma global de todas las barras de la gráfica.
    porce_total_inicio (bool) : Mostrar dicho porcentaje en el inicio o base de la barra en vez de junto a la cápsula final.
    ajustar_pos_porce_total (float) : Modifica la posición espacial de estas etiquetas porcentuales globales.
    tam_porce_total (int/float) : Tamaño de la letra o numero asociado a porce_total.
    peso_porce_total (str) : Grosor de la letra o numero asociada a porce_total.
    color_porce_total (str) : Color del texto para este porcentaje total.

    --- LEYENDA (Series / Segmentos apilados) ---
    leyenda (str/bool/None) : Título o indicador para la leyenda de las variables.
    posicion_leyenda (tuple/str/dict) : Define la ubicación de la leyenda. Principalmente se usa una tupla `(x, y)` donde las coordenadas corresponden a dimensiones relativas a la gráfica (`x=0` es izquierda, `x=1` derecha, `x=0.5` centro). Valores de `y<0` bajan la leyenda por debajo del gráfico para que no estorbe. También admite un string 'loc' clásico de `plt.legend` (ej. 'best', 'upper right') o un dict con kwargs para configuración avanzada.
    ajustar_pos_leyenda (float) : Espacio extra adicional.
    num_columnas_leyenda (int) : Número de columnas en la leyenda.
    tam_letra_leyenda (int/float) : Tamaño de letra para la leyenda.
    peso_letra_leyenda (str) : Grosor de letra para la leyenda.
    color_letra_leyenda (str) : Color de letra para la leyenda.

    --- EJE Y (ETIQUETAS) ---
    tam_valor_ejey (int/float) : Estilos de los textos principales recostados en el eje Y.
    peso_valor_ejey (str) : Grosor de la fuente en el eje Y.
    color_valor_ejey (str) : Color del texto en el eje Y.
    espacio_inicio (float) : Espacio extra en la base de la gráfica cerca del eje Y.
    nombre_ejey (str) : Título específico para el eje Y.
    tam_nombre_ejey (int/float) : Tamaño de fuente para este título de eje Y.
    peso_nombre_ejey (str) : Grosor de fuente para este título de eje Y.
    color_nombre_ejey (str) : Color de fuente para este título de eje Y.
    sustituir_valor_ejey (list) : Lista explícita de nombres alternos para las categorías del eje Y.
    orientacion_valor_ejey (int/float) : Rota las etiquetas del eje Y.
    ajustar_sep_izquierda_ejey (float) : Alejamiento / separación del gráfico.
    resaltar_valor_ejey (list) : Destacar palabras o variables específicas de la etiqueta.
    color_resaltado_ejey (str) : Color especial de resaltado.
    color_borde_resaltado_ejey (str) : Color para el borde de texto resaltado.
    ejey_der (bool) : Cambia las etiquetas categorizadas del eje Y hacia el extremo derecho de la visualización.

    --- EJE X (VALORES) ---
    tam_valor_ejex (int/float) : Formato de la escala numérica horizontal (eje X).
    peso_valor_ejex (str) : Grosor de la fuente del eje X.
    color_valor_ejex (str) : Color del texto en el eje X.
    nombre_ejex (str) : Título a mostrar debajo del eje numérico.
    tam_nombre_ejex (int/float) : Tamaño de la fuente para el texto del título X.
    peso_nombre_ejex (str) : Grosor de la fuente para el texto del título X.
    color_nombre_ejex (str) : Color para el texto del título X.
    limites_ejex (tuple/None) : Forzar la escala de representación (min, max).
    solo_ejex_positivo (bool) : Visualizar únicamente el dominio > 0, ocultando la parte negativa.
    simbolo_porce_ejex (bool) : Incluir un marcador '%' en los labels numéricos de la escala.
    divisiones_ejex (int/bool) : Controlar el conteo de divisiones numéricas (ticks).
    respecto_porce (bool) : Si True, grafica de 0 a 100% de manera normalizada (share de porciones).
    modalidad_fechas (int) : Modalidad formato de fecha.
    mostrar_solo_fechas (list) : Restringir subsample temporal de etiquetas en el eje.

    --- GRÁFICA DE LÍNEAS ---
    columnas_lineas (list) : Nombres de la columna para representar una serie de línea vertical superpuesta a la visualización.
    colores_lineas (list) : Paleta de color para dicha serie lineal.
    capsu_final_lineas (bool) : Globos o cápsulas extra mostrando el número a la altura final de la línea.
    espacio_entre_grupos (float) : Espacio intermedio extra aplicado entre la segmentación de grupos en las barras.

    EJEMPLO DE DATAFRAME VÁLIDO:
    | Región | Ventas_A | Ventas_B | Otros_ingresos |
    |--------|----------|----------|----------------|
    | Norte  | 150.5    | 80.2     |      45.96     | 
    | Sur    | 165.0    | 90.5     |      56.72     |
    
    NOTAS DE EJECUCIÓN IA (Accionables):
    1. Agrupar categorías pequeñas usando int `unir_sup` o `unir_inf` para consolidar en "Otros".
    2. Cuando las barras son muy aplastadas y `areamin` desplaza el texto fuera de las divisiones con `opcion_areamin='fuera'`.
    3. Para comparar por share, utiliza `respecto_porce=True` (todo sumará 1 o 100).
    4. Las columnas nombradas en parámetros especiales como `asignar_etiquetas` no se computan en las longitudes de las barras.
    """
    # --- 1. CONFIGURACIÓN INICIAL ---
    hay_annotations_externas = False
    espacio = "\u00A0"

    # --- 2. PREPARACIÓN DE DATOS ---
    if not isinstance(df, pd.DataFrame):
        raise ValueError("El argumento df debe ser un DataFrame de pandas.")

    # Copia inicial del DataFrame para evitar modificar el original en cualquier operación.
    df = df.copy()

    font_config = {
        'family': tipo_letra,
        'variable_y': {'size': tam_valor_ejey, 'weight': peso_valor_ejey, 'color': color_valor_ejey},
        'variable_x': {'size': tam_valor_ejex, 'weight': peso_valor_ejex, 'color': color_valor_ejex},
        'nombre_ejey': {'size': tam_nombre_ejey, 'weight': peso_nombre_ejey, 'color': color_nombre_ejey},
        'nombre_ejex': {'size': tam_nombre_ejex, 'weight': peso_nombre_ejex, 'color': color_nombre_ejex},
        'valor_capsula': {'size': tam_valor_capsu, 'weight': peso_valor_capsu, 'color': color_valor_capsu},
        'valor_porcentaje_barra': {'size': tam_valor_barra, 'weight': peso_valor_barra, 'color': color_valor_barra},
        'valor_porcentaje_barra_porcentaje': {'size': tam_porce_barra, 'weight': peso_porce_barra, 'color': color_porce_barra},
        'porcentaje_total': {'size': tam_porce_total, 'weight': peso_porce_total, 'color': color_porce_total},
        'leyenda': {'size': tam_letra_leyenda, 'weight': peso_letra_leyenda, 'color': color_letra_leyenda}
    }

    plt.rcParams['svg.fonttype'] = 'path' if svg_trazos else 'none'
    current_dir = Path(__file__).resolve().parent
    font_dirs = [current_dir.parent / "0_fonts"]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

    colores_asignados = colores or ["#10302C", "#4C6A67", "#8FA8A6", "#A3C9A8"]

    # --- 2. PREPARACIÓN DE DATOS ---
    if not isinstance(df, pd.DataFrame):
        raise ValueError("El argumento df debe ser un DataFrame de pandas.")
    
    if ordenar not in ['x', 'y', None]:
        raise ValueError("El argumento 'ordenar' solo acepta 'x', 'y' o None.")

    # Validación de ascendente.
    if not isinstance(ascendente, bool):
        raise ValueError("El argumento 'ascendente' solo acepta True o False.")
        
    df = df.copy()

    # --- LÓGICA DE CATEGORIZACIÓN POR COLOR ---
    mapa_color_categoria = None
    if columna_categorias is not None:
        if not isinstance(columna_categorias, int):
            raise ValueError("El argumento 'columna_categorias' debe ser un entero.")
        if columna_categorias < 1 or columna_categorias > len(df.columns):
            raise ValueError(f"El índice 'columna_categorias' ({columna_categorias}) está fuera de rango. Debe estar entre 1 y {len(df.columns)}.")
        
        col_categorias_nombre = df.columns[columna_categorias - 1]
        
        # Validar que si también se usan 'unir_sup' o 'unir_inf', la columna no interfiera o sea manejada
        # (Dependiendo de la lógica deseada, pero por ahora solo extraemos colores)
        
        categorias_unicas = df[col_categorias_nombre].unique()
        # Generar colores para las categorías
        colores_categorias = plt.cm.get_cmap('tab20', len(categorias_unicas)) if len(categorias_unicas) > 10 else plt.cm.get_cmap('tab10', len(categorias_unicas))
        mapa_color_categoria = {cat: colores_categorias(i) for i, cat in enumerate(categorias_unicas)}
        
        # Asignar color a cada fila
        df['__color_categoria'] = df[col_categorias_nombre].map(mapa_color_categoria)
        
        # Eliminar la columna de categorías del dataframe para que no se grafique como dato
        df = df.drop(columns=[col_categorias_nombre])

    categorias_y = df.columns[0]
    if pd.api.types.is_integer_dtype(df[categorias_y]) and df[categorias_y].between(1900, 2100).all():
        df[categorias_y] = pd.to_datetime(df[categorias_y], format='%Y')
    df = df.set_index(categorias_y)

    # Extraer la columna de color si existe y luego eliminarla
    colores_por_barra = None
    if '__color_categoria' in df.columns:
        colores_por_barra = df['__color_categoria'].copy()
        df = df.drop(columns=['__color_categoria'])

    df, etiqueta_union_sup = unir_barras(df, unir_sup, 'izquierda') # 'izquierda' en vertical es 'arriba' en horizontal
    df, etiqueta_union_inf = unir_barras(df, unir_inf, 'derecha')   # 'derecha' en vertical es 'abajo' en horizontal

    etiquetas_personalizadas = {}
    textos_barra_personalizados = {}
    colores_fondo_personalizados = {}
    colores_borde_personalizados = {}
    estilos_borde_personalizados = {}
    grosores_borde_personalizados = {}
    colores_texto_personalizados = {}
    datos_para_separadores = []

    if agregar_datos:
        filas_a_agregar = []
        for item in agregar_datos:
            etiqueta, texto_barra, opciones_extra = None, None, {}
            if len(item) == 2: categoria, valor = item
            elif len(item) == 3: categoria, etiqueta, valor = item
            elif len(item) == 4: categoria, etiqueta, valor, texto_barra = item
            elif len(item) == 5: categoria, etiqueta, valor, texto_barra, opciones_extra = item

            if etiqueta: etiquetas_personalizadas[categoria] = etiqueta
            if texto_barra: textos_barra_personalizados[categoria] = texto_barra
            if isinstance(opciones_extra, dict):
                if 'colores_fondo' in opciones_extra: colores_fondo_personalizados[categoria] = opciones_extra['colores_fondo']
                if 'colores_borde' in opciones_extra: colores_borde_personalizados[categoria] = opciones_extra['colores_borde']
                if 'estilos_borde' in opciones_extra: estilos_borde_personalizados[categoria] = opciones_extra['estilos_borde']
                if 'grosores_borde' in opciones_extra: grosores_borde_personalizados[categoria] = opciones_extra['grosores_borde']
                if 'colores_texto' in opciones_extra: colores_texto_personalizados[categoria] = opciones_extra['colores_texto']
                if 'separador_derecha' in opciones_extra: datos_para_separadores.append({'posicion': 'despues', 'referencia': categoria, 'texto': opciones_extra['separador_derecha']})
                if 'separador_izquierda' in opciones_extra: datos_para_separadores.append({'posicion': 'antes', 'referencia': categoria, 'texto': opciones_extra['separador_izquierda']})

            fila = pd.Series(dict(zip(df.columns, valor)) if isinstance(valor, (list, tuple, np.ndarray)) else {col: valor if i == 0 else 0 for i, col in enumerate(df.columns)}, name=categoria)
            filas_a_agregar.append(fila)

        if filas_a_agregar:
            df_agregado = pd.DataFrame(filas_a_agregar)
            df = pd.concat([df, df_agregado])

    etiquetas_finales = None
    if asignar_etiquetas and asignar_etiquetas in df.columns:
        etiquetas_finales = df[asignar_etiquetas].copy()
        df = df.drop(columns=[asignar_etiquetas])

    categorias = df.columns

    # --- 3. ORDENAMIENTO DE DATOS ---
    # Calcular suma por fila/grupo para ordenamiento
    # Excluir columnas de líneas y cápsulas internas para la suma
    cols_excluir = columnas_lineas if columnas_lineas is not None else []
    lista_cols_suma = [c for c in df.columns if c not in cols_excluir and c != '__capsule_values__' and c != '__color_categoria']
    
    # Crear columna temporal para ordenamiento
    df['_sum_for_sort'] = df[lista_cols_suma].sum(axis=1)

    # Identificar filas fijas (extremos)
    # En horizontal: sup está al inicio (index 0 visualmente si no invertido, pero invertimos y)
    # Etiquetas de unión
    lista_sup = [etiqueta_union_sup] if etiqueta_union_sup else []
    lista_inf = [etiqueta_union_inf] if etiqueta_union_inf else []

    # Obtener índices únicos preservando ascendente de aparición
    seen = set()
    unique_indices = []
    for idx in df.index:
        if idx not in seen:
            unique_indices.append(idx)
            seen.add(idx)

    # Filtrar fijos
    u_sup = [idx for idx in lista_sup if idx in seen]
    u_inf = [idx for idx in lista_inf if idx in seen]
    u_center = [idx for idx in unique_indices if idx not in u_sup and idx not in u_inf]

    if ordenar == 'x':
        # Calcular suma TOTAL por grupo
        group_sums = df.groupby(level=0)['_sum_for_sort'].sum()
        # Ordenar u_center basado en sumas
        sums_center = group_sums.loc[u_center]
        # En barras horizontales, el "top" es el inicio.
        # Si ascendente False (descendente, mayor a menor): Mayor suma arriba.
        u_center_sorted = sums_center.sort_values(ascending=ascendente).index.tolist()
        
    elif ordenar == 'y':
        # Ordenar por etiqueta
        centro_ser = pd.Series(u_center)
        # Intentar parsing de fecha como en vertical
        try:
            parsed = pd.to_datetime(centro_ser, errors='coerce') # pandas > 2.0 format no necesario
        except:
            parsed = pd.to_datetime(centro_ser, errors='coerce', infer_datetime_format=True)
            
        if parsed.notna().any():
            filled = parsed.fillna(pd.Timestamp.max)
            u_center_sorted = [x for _, x in sorted(zip(filled, u_center), key=lambda t: t[0])]
            if not ascendente:
                u_center_sorted.reverse()
        else:
            tipos = set(type(idx) for idx in u_center)
            reverse_sort = not ascendente
            if len(tipos) > 1:
                u_center_sorted = sorted(u_center, key=lambda x: str(x), reverse=reverse_sort)
            else:
                u_center_sorted = sorted(u_center, reverse=reverse_sort)
    elif ordenar is None:
        # Mantener orden original
        u_center_sorted = u_center
    else:
        # Mantener orden original
        u_center_sorted = u_center

    # Reconstruir índice final
    final_order_indices = u_sup + u_center_sorted + u_inf
    
    # Reordenar DataFrame
    # IMPORTANTE: Usar loc con índices ÚNICOS agrupa las filas de cada índice.
    df = df.loc[final_order_indices]
    
    # Limpiar columna temporal
    if '_sum_for_sort' in df.columns:
        df = df.drop(columns=['_sum_for_sort'])
    
    if colores_por_barra is not None:
         # Reindexar colores requiere manejo cuidadoso si hay duplicados
         # Pero colores_por_barra venía de df original.
         # Al hacer df.loc[final_order], duplicamos filas si hay indices duplicados en df?
         # NO, df.loc[['A']] devuelve todas las filas A.
         # El objeto colores_por_barra debe alinearse.
         # Mejor estrategia: volver a extraer colores de df si es posible, o reindexar.
         # Como colores_por_barra se extrajo ANTES de borrar la columna en df, 
         # y ahora df ha sido reordenado (y potencialmente "grouped" visualmente),
         # Lo más seguro es que colores_por_barra se pierda sincronicidad si no tenemos cuidado.
         # PERO, en barras_horizontales (original), colores_por_barra se reindexaba.
         # Si colores_por_barra tiene índice único (el original tenía índices posiblemente duplicados),
         # reindexar con duplicados funciona.
         try:
            colores_por_barra = colores_por_barra.loc[df.index]
         except:
            pass 

    if datos_para_separadores:
        datos_para_separadores.sort(key=lambda x: x['posicion'] == 'antes', reverse=True)
        # Convertir a lista de tuplas para inserción, como estaba antes
        # Pero ahora df puede tener indice duplicado. iterrows() estaria bien.
        df_list = list(df.iterrows())
        # current_indices necesita ser tracking de la lista, no del index de pandas
        current_indices_labels = [item[0] for item in df_list]

        offset = 0
        for sep_info in datos_para_separadores:
            try:
                # Buscar primera ocurrencia de la referencia
                try:
                    idx_pos = current_indices_labels.index(sep_info['referencia'])
                except ValueError:
                    continue

                idx_separador = f"__espaciador__{sep_info['referencia']}_{sep_info['posicion']}_{np.random.randint(1000)}"
                fila_separador = pd.Series({col: 0 for col in df.columns}, name=idx_separador)
                etiquetas_personalizadas[idx_separador] = sep_info['texto']
                
                # Si es 'antes', insertar en idx_pos. Si 'despues', buscar el final del grupo.
                # Simplificación: insertar antes o después de la PRIMERA aparición (que es el grupo entero si usamos loc)
                # Pero si loc agrupa AAA, index devuelve el primero.
                # Si queremos despues del grupo AAA:
                if sep_info['posicion'] == 'despues':
                    # Contar cuantos hay de este grupo
                    count = current_indices_labels.count(sep_info['referencia'])
                    insert_at = idx_pos + count 
                else:
                    insert_at = idx_pos
                
                df_list.insert(insert_at, (idx_separador, fila_separador))
                current_indices_labels.insert(insert_at, idx_separador)
            except ValueError:
                pass
        
        # Reconstruir DF
        # Nota: from_dict con orient='index' puede fallar si hay claves duplicadas en diccionario? 
        # Dict no permite claves duplicadas.
        # df_list es [(idx, series), ...].
        # Pasarlo a DataFrame:
        df = pd.DataFrame([x[1] for x in df_list])
        df.index = [x[0] for x in df_list]
        df.columns = categorias

    # --- 4. CÁLCULOS PARA LA GRÁFICA ---
    # Determinar el número de decimales a usar y formato (MOVIDO DESDE SECCIÓN 7)
    todos_los_valores = df.select_dtypes(include=[np.number]).values.flatten()
    num_dec = num_decimales(todos_los_valores, determinado=decimales)
    
    formato_decimal = f"{{:,.{num_dec}f}}"

    # Crear copia redondeada para cálculos de sumas (consistencia visual con etiquetas)
    df_rounded = df.copy()
    numeric_cols = df_rounded.select_dtypes(include=[np.number]).columns
    df_rounded[numeric_cols] = df_rounded[numeric_cols].round(num_dec)

    if columnas_lineas is None: columnas_lineas = []
    
    columnas_barras = [col for col in df.columns if col not in columnas_lineas]
    
    suma_total_real = df[columnas_barras].sum(axis=1) if columnas_barras else pd.Series(0, index=df.index)
    suma_total = df_rounded[columnas_barras].sum(axis=1) if columnas_barras else pd.Series(0, index=df.index)
    total_general = suma_total.sum()

    df_plot = df.copy()
    if respecto_porce:
        suma_total_no_cero = suma_total_real.replace(0, np.nan)
        for col in columnas_barras:
            df_plot[col] = df[col].div(suma_total_no_cero, axis=0).multiply(100).fillna(0)
    
    es_divergente = (any(df[columnas_barras].min() < 0) if columnas_barras else False) or \
                   (any(df[columnas_lineas].min() < 0) if columnas_lineas else False)
    
    suma_positivos_por_barra, suma_negativos_por_barra, suma_absoluta_por_barra, total_general_absoluto, total_general_positivos = None, None, None, None, None
    if es_divergente:
        suma_negativos_por_barra = df_rounded[columnas_barras][df_rounded[columnas_barras] < 0].sum(axis=1)
        suma_positivos_por_barra = df_rounded[columnas_barras][df_rounded[columnas_barras] > 0].sum(axis=1)
        if porce_diver:
            total_general_positivos = suma_positivos_por_barra.sum()
        else:
            suma_absoluta_por_barra = df_rounded[columnas_barras].abs().sum(axis=1)
            total_general_absoluto = suma_absoluta_por_barra.sum()

    x_max_pos = df[df > 0].sum(axis=1).max()
    x_max_neg = df[df < 0].sum(axis=1).min()
    min_lineas = df[columnas_lineas].min().min() if columnas_lineas else 0
    x_max = max(x_max_pos, abs(x_max_neg), abs(min_lineas) if min_lineas < 0 else 0) * 1.15
    if pd.isna(x_max): x_max = suma_total.max() * 1.15
    if respecto_porce: x_max = 100 * 1.15

    # --- 5. FORMATEO DE ETIQUETAS DEL EJE Y ---
    entidades = df.index.values
    es_fecha = any(isinstance(idx, (pd.Timestamp, np.datetime64)) for idx in df.index if idx not in [etiqueta_union_sup, etiqueta_union_inf])
    if es_fecha:
        fechas_a_formatear = [idx for idx in df.index if isinstance(idx, (pd.Timestamp, np.datetime64))]
        mapa_fechas = dict(zip(fechas_a_formatear, formato_fechas(fechas_a_formatear, modalidad=modalidad_fechas, mostrar_solo=mostrar_solo_fechas)))
        entidades_formateadas = [mapa_fechas.get(idx, str(idx)) for idx in df.index]
    else:
        entidades_formateadas = [str(idx) for idx in df.index]

    if sustituir_valor_ejey:
        if len(sustituir_valor_ejey) != len(entidades_formateadas):
            raise ValueError("La longitud de 'sustituir_valor_ejey' debe coincidir con el número de barras.")
        entidades_formateadas = list(sustituir_valor_ejey)

    for i, entidad in enumerate(df.index):
        if entidad in etiquetas_personalizadas and etiquetas_personalizadas[entidad]:
            entidades_formateadas[i] = etiquetas_personalizadas[entidad]

    for i, entidad in enumerate(entidades_formateadas):
        if "__espaciador__" in str(df.index[i]):
            entidades_formateadas[i] = etiquetas_personalizadas.get(df.index[i], "...")

    # --- 6. CREACIÓN DE LA FIGURA Y EJES ---
    
    # --- CÁLCULO DE POSICIONES Y AGRUPAMIENTOS (Barras Horizontales) ---
    posiciones = []
    
    # En barh, 'ancho_barra' es el grosor vertical de la barra (height en matplotlib)
    # Usaremos 'alturas_barras' para pasar al parámetro 'height' de barh (confuso, pero así es matplotlib)
    alturas_barras = [] 
    
    tick_positions = []
    tick_labels = []
    
    # Detectar grupos de etiquetas consecutivas idénticas
    # (El ordenamiento ya ocurrió en la sección 3)

    if len(df) > 0:
        grouped_counts = [] # list of (label, count)
        last_label = None
        count = 0
        
        for label in df.index:
            if label != last_label and last_label is not None:
                grouped_counts.append((last_label, count))
                count = 0
            last_label = label
            count += 1
        grouped_counts.append((last_label, count))
        
        # Calcular posiciones Y
        # En horizontal, empezamos desde arriba (índice 0 visualmente arriba pero en Matplotlib 0 es abajo)
        # Pero luego hacemos invert_yaxis(), así que 0 estará arriba.
        # Vamos a calcular posiciones incrementales 0, 1, 2... y luego mapero.
        
        y_cursor = 0
        df_row_idx = 0
        
        # Tamaño máximo de grupo
        max_group_count = max([c for _, c in grouped_counts]) if grouped_counts else 1
        
        # Alto base del grupo (espacio vertical disponible)
        alto_grupo_base = max(ancho_barra, 0.85)

        # Paso entre centros de barras dentro del grupo
        step = alto_grupo_base / max_group_count
        
        # Alto visual (grosor) de cada barra individual
        alto_individual = ancho_barra / max_group_count
        
        for label, count in grouped_counts:
            # Centro del grupo en el eje Y
            center_y = y_cursor
            tick_positions.append(center_y)
            tick_labels.append(entidades_formateadas[df_row_idx])
            
            # Calcular posiciones de barras dentro del grupo
            total_group_height = count * step
            start_y = center_y - (total_group_height / 2) + (step / 2)
            
            for i in range(count):
                pos = start_y + (i * step)
                posiciones.append(pos)
                alturas_barras.append(alto_individual)
            
            y_cursor += 1 + espacio_entre_grupos
            df_row_idx += count

    else:
        # Caso vacío o fallback
        posiciones = []
        alturas_barras = []
        tick_positions = []
        tick_labels = []

    posiciones = np.array(posiciones)
    alturas_barras = np.array(alturas_barras)
    
    # Cálculo dinámico del alto de la figura
    longitudes = [len(str(e)) for e in entidades_formateadas]
    moda_etiqueta_len = mode(longitudes) if longitudes else 10
    extra_height = moda_etiqueta_len * 0.1
    
    # Factor de expansión vertical por espacio entre grupos
    factor_espacio = 1 + max(0, espacio_entre_grupos)
    
    base_height = max(8, len(tick_labels) * 0.5 * factor_espacio)
    fig_height = alto / 2.54 if alto is not None else base_height
    fig_width = ancho / 2.54 if ancho is not None else fig_height * 2
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)

    if fondo == 'transparent':
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
    else:
        fig.patch.set_alpha(1)
        ax.patch.set_alpha(1)
        fig.patch.set_facecolor(fondo)
        ax.patch.set_facecolor(fondo)

    # --- 7. DIBUJO DE BARRAS Y TEXTOS ---
    line_handles, line_labels = [], []
    etiquetas_fuera = [] # Para etiquetas fuera por areamin
    
    # Usamos enumerate(zip(...)) para tener índice de fila (idx_row) y propiedades calculadas
    for idx_row, (pos, entidad, total_valor, alto_indiv) in enumerate(zip(posiciones, entidades, suma_total, alturas_barras)):
        left_pos, left_neg = 0, 0
        annotations_externas_pos = []
        annotations_externas_neg = []
        last_non_zero_idx = 0
        last_non_zero_idx_neg = 0
        
        for i, col in enumerate(columnas_barras):
            current_val = df_plot[col].iloc[idx_row]
            if current_val == 0: continue
            
            if current_val > 0:
                last_non_zero_idx = i
            else:
                last_non_zero_idx_neg = i

            color_fondo_personalizado = colores_fondo_personalizados.get(entidad)
            color_borde_personalizado = colores_borde_personalizados.get(entidad)
            estilo_borde_personalizado = estilos_borde_personalizados.get(entidad)
            grosor_borde_personalizado = grosores_borde_personalizados.get(entidad)
            color_texto_personalizado = colores_texto_personalizados.get(entidad)

            color = color_fondo_personalizado[i] if color_fondo_personalizado and i < len(color_fondo_personalizado) and color_fondo_personalizado[i] else colores_asignados[i % len(colores_asignados)]
            if colores_por_barra is not None:
                # Acceso seguro por índice posicional (ya que df está ordenado igual que el loop)
                try: 
                    c_cat = colores_por_barra.iloc[idx_row] 
                    if isinstance(c_cat, (str, tuple, list, np.ndarray)):
                        color = c_cat
                except IndexError: pass

            edge_color = color_borde_personalizado[i] if color_borde_personalizado and i < len(color_borde_personalizado) and color_borde_personalizado[i] else 'none'
            line_style = estilo_borde_personalizado[i] if estilo_borde_personalizado and i < len(estilo_borde_personalizado) and estilo_borde_personalizado[i] else '-'
            line_width = grosor_borde_personalizado[i] if grosor_borde_personalizado and i < len(grosor_borde_personalizado) and grosor_borde_personalizado[i] is not None else 1.5
            custom_text_color = color_texto_personalizado[i] if color_texto_personalizado and i < len(color_texto_personalizado) and color_texto_personalizado[i] else None
            
            text_color_valor = custom_text_color or color_valor_barra or get_text_color_for_bg(color)
            text_color_porcentaje = custom_text_color or color_porce_barra or get_text_color_for_bg(color)
            
            bar_left = left_pos if current_val > 0 else left_neg
            
            # USAMOS alto_indiv PARA EL PARAMETRO height (grosor vertical)
            ax.barh(pos, current_val, height=alto_indiv, left=bar_left, color=color, edgecolor=edge_color, linestyle=line_style, linewidth=line_width, zorder=2, label=col if idx_row == 0 else "")
            
            if current_val > 0: left_pos += current_val
            else: left_neg += current_val

            # --- INICIO DE LA LÓGICA DE ETIQUETAS EXTERNAS ---
            # Calcular area basada en el alto individual actual
            area_barra = abs(current_val) * alto_indiv
            debe_dibujar_dentro = area_barra >= areamin
            debe_dibujar_fuera = not debe_dibujar_dentro and opcion_areamin == 'fuera'

            # Solo procesar si se debe dibujar algo
            if debe_dibujar_dentro or debe_dibujar_fuera:
                # --- Cálculo de porcentaje y texto ---
                if es_divergente:
                    if porce_diver:
                        base_porcentaje = suma_positivos_por_barra.iloc[idx_row] if current_val > 0 else suma_negativos_por_barra.iloc[idx_row]
                    else:
                        base_porcentaje = suma_absoluta_por_barra.iloc[idx_row]
                else:
                    base_porcentaje = total_valor
                porcentaje_valor = (current_val / base_porcentaje) * 100 if base_porcentaje != 0 else 0

                texto_final, texto_valor, texto_porcentaje = "", "", ""
                es_texto_personalizado = False

                if entidad in textos_barra_personalizados:
                    textos_barra = textos_barra_personalizados[entidad]
                    if i < len(textos_barra) and textos_barra[i] is not None:
                        texto_final = textos_barra[i]
                        es_texto_personalizado = True
                
                if not es_texto_personalizado:
                    if valor_barra:
                        texto_valor = elimina_ceros_no_significativos(formato_decimal.format(abs(current_val)))
                    if porce_barra:
                        texto_porcentaje = f"({abs(porcentaje_valor):.1f}%)" if not porce_al_lado else f"{abs(porcentaje_valor):.1f}%"

                # --- Dibujo o almacenamiento de la etiqueta ---
                if debe_dibujar_dentro:
                    text_pos_x = bar_left + current_val / 2
                    rotacion_texto_barra = 0 if alinear_texto_barra else 270
                    va_texto_barra = 'center'
                    ha_texto_barra_valor = 'right' if porce_al_lado else 'center'
                    ha_texto_barra_porce = 'left' if porce_al_lado else 'center'
                    ha_texto_barra_unificado = 'center'

                    if activar_cambiar_color:
                        c_bord_val = cambiar_color(text_color_valor, color)
                        eff_val = [path_effects.withStroke(linewidth=1.5, foreground=c_bord_val)] if c_bord_val else None
                        c_bord_por = cambiar_color(text_color_porcentaje, color)
                        eff_por = [path_effects.withStroke(linewidth=1.5, foreground=c_bord_por)] if c_bord_por else None
                    else:
                        eff_val = None
                        eff_por = None

                    if es_texto_personalizado:
                        ax.text(text_pos_x, pos, texto_final, va=va_texto_barra, ha=ha_texto_barra_unificado, rotation=rotacion_texto_barra, fontsize=font_config['valor_porcentaje_barra']['size'], fontfamily=font_config['family'], fontweight=font_config['valor_porcentaje_barra']['weight'], color=text_color_valor, linespacing=1.2, path_effects=eff_val)
                    elif porce_al_lado and valor_barra and porce_barra:
                        ax.text(text_pos_x, pos, texto_valor, va=va_texto_barra, ha=ha_texto_barra_valor, rotation=rotacion_texto_barra, fontsize=font_config['valor_porcentaje_barra']['size'], fontfamily=font_config['family'], fontweight=font_config['valor_porcentaje_barra']['weight'], color=text_color_valor, linespacing=1.5, path_effects=eff_val)
                        ax.text(text_pos_x, pos, texto_porcentaje, va=va_texto_barra, ha=ha_texto_barra_porce, rotation=rotacion_texto_barra, fontsize=font_config['valor_porcentaje_barra_porcentaje']['size'], fontfamily=font_config['family'], fontweight=font_config['valor_porcentaje_barra_porcentaje']['weight'], color=text_color_porcentaje, linespacing=1.5, path_effects=eff_por)
                    else:
                        if porce_al_lado:
                            texto_final = f"{texto_valor} {texto_porcentaje}".strip()
                        else:
                            texto_final = f"{texto_valor}\n{texto_porcentaje}".strip()
                        
                        font_size_a_usar = font_config['valor_porcentaje_barra_porcentaje']['size'] if not valor_barra and porce_barra else font_config['valor_porcentaje_barra']['size']
                        color_a_usar = text_color_porcentaje if not valor_barra and porce_barra else text_color_valor
                        eff_unificado = eff_por if not valor_barra and porce_barra else eff_val

                        ax.text(text_pos_x, pos, texto_final, va=va_texto_barra, ha=ha_texto_barra_unificado, rotation=rotacion_texto_barra, fontsize=font_size_a_usar, fontfamily=font_config['family'], fontweight=font_config['valor_porcentaje_barra']['weight'], color=color_a_usar, linespacing=1.2, path_effects=eff_unificado)

                elif debe_dibujar_fuera:
                    hay_annotations_externas = True
                    if not es_texto_personalizado:
                        texto_final = f"{texto_valor} {texto_porcentaje}".strip()
                    
                    if isinstance(color_valor_barra_fuera, dict):
                        color_texto_fuera = color_valor_barra_fuera.get(col, color)
                    else:
                        color_texto_fuera = color_valor_barra_fuera or color

                    annotation_info = {
                        'texto': texto_final,
                        'color': color_texto_fuera,
                        'font_size': font_config['valor_porcentaje_barra']['size'],
                        'font_weight': font_config['valor_porcentaje_barra']['weight']
                    }
                    if current_val > 0:
                        annotations_externas_pos.append(annotation_info)
                    else:
                        annotations_externas_neg.append(annotation_info)
            # --- FIN DE LA LÓGICA DE ETIQUETAS EXTERNAS ---

        # Almacenar las anotaciones de la barra actual
        if annotations_externas_pos or annotations_externas_neg:
            etiquetas_fuera.append({
                'pos': pos,
                'left_pos': left_pos,
                'left_neg': left_neg,
                'positivas': annotations_externas_pos,
                'negativas': annotations_externas_neg
            })

        debe_dibujar_capsu_pos = valor_capsu and "__espaciador__" not in str(entidad)
        
        is_simple_or_divergent = len(columnas_barras) == 1 or (es_divergente and len(columnas_barras) == 2)  # definido aquí para que exista también en la cápsula negativa
        if debe_dibujar_capsu_pos:
            if es_divergente:
                 # En divergente, dibujar si hay valores positivos, o si capsu_cero es True
                 if suma_positivos_por_barra.iloc[idx_row] <= 0 and not capsu_cero:
                     debe_dibujar_capsu_pos = False
            else:
                 # En normal, dibujar si total > 0, o si capsu_cero es True
                 if total_valor <= 0 and not capsu_cero:
                     debe_dibujar_capsu_pos = False

        if debe_dibujar_capsu_pos:
            valor_a_mostrar = total_valor
            if es_divergente:
                valor_a_mostrar = suma_positivos_por_barra.iloc[idx_row]

            if etiquetas_finales is not None and not pd.isna(etiquetas_finales.iloc[idx_row]):
                texto_a_mostrar = str(etiquetas_finales.iloc[idx_row])
            else:
                texto_a_mostrar = elimina_ceros_no_significativos(formato_decimal.format(valor_a_mostrar))
            
            es_cero_visual = False
            try:
                if float(texto_a_mostrar.replace(',', '')) == 0:
                    es_cero_visual = True
            except ValueError:
                pass

            if capsu_cero or not es_cero_visual:
                texto_capsula = f"{espacio*2}{texto_a_mostrar}{espacio*2}"
                base_pos_x = left_pos if es_divergente else (100 if respecto_porce else total_valor)

                # --- INICIO: Lógica de desplazamiento de cápsula ---
                desplazamiento_extra_capsula = 0
                if hay_annotations_externas and annotations_externas_pos:
                    num_etiquetas_fuera = len(annotations_externas_pos)
                    desplazamiento_extra_capsula = x_max * ajustar_pos_capsu_areamin * num_etiquetas_fuera
                
                text_x_pos = base_pos_x + x_max * ajustar_pos_capsu + desplazamiento_extra_capsula
                # --- FIN: Lógica de desplazamiento de cápsula ---
                
                color_una_barra_capsu = None
                is_simple_or_divergent = len(columnas_barras) == 1 or (es_divergente and len(columnas_barras) == 2)
                if is_simple_or_divergent:
                    color_fondo_pers_capsu = colores_fondo_personalizados.get(entidad)
                    c_pos = color_fondo_pers_capsu[last_non_zero_idx] if color_fondo_pers_capsu and last_non_zero_idx < len(color_fondo_pers_capsu) and color_fondo_pers_capsu[last_non_zero_idx] else colores_asignados[last_non_zero_idx % len(colores_asignados)]
                    if colores_por_barra is not None:
                        try:
                            ccat = colores_por_barra.iloc[idx_row]
                            if pd.notna(ccat):
                                c_pos = ccat
                        except IndexError:
                            pass
                    color_una_barra_capsu = c_pos

                rotacion_capsula = 0 if alinear_capsu else 270
                ha_capsula, va_capsula = 'left', 'center'
                pos_x_capsula, pos_y_capsula = text_x_pos, pos
                
                if isinstance(color_valor_capsu, list):
                    col_idx_para_color = last_non_zero_idx
                    c_val_capsu = color_valor_capsu[col_idx_para_color % len(color_valor_capsu)]
                else:
                    if color_valor_capsu is None:
                        c_val_capsu = color_una_barra_capsu if is_simple_or_divergent else '#434343'
                    else:
                        c_val_capsu = color_valor_capsu
                
                if isinstance(color_borde_capsu, list):
                    col_idx_para_borde = last_non_zero_idx
                    c_borde_capsu = color_borde_capsu[col_idx_para_borde % len(color_borde_capsu)]
                else:
                    if color_borde_capsu is None:
                        c_borde_capsu = color_una_barra_capsu if is_simple_or_divergent else '#434343'
                    else:
                        c_borde_capsu = color_borde_capsu
                
                color_texto_capsula = c_val_capsu

                bbox_dict = dict(boxstyle=f"round,pad=0.15,rounding_size={curvatura_capsu}", facecolor=color_fondo_capsu, edgecolor=c_borde_capsu, linewidth=peso_borde_capsu)
                font_dict = {'family': font_config['family'], 'size': font_config['valor_capsula']['size'], 'weight': font_config['valor_capsula']['weight'], 'color': color_texto_capsula}
                
                if activar_cambiar_color:
                    c_bord_cap = cambiar_color(color_texto_capsula, color_fondo_capsu if not quitar_capsu else (fondo if fondo != 'transparent' else '#ffffff'))
                    eff_cap = [path_effects.withStroke(linewidth=1.5, foreground=c_bord_cap)] if c_bord_cap else None
                else:
                    eff_cap = None

                if not quitar_capsu:
                    ax.text(pos_x_capsula, pos_y_capsula, texto_capsula, bbox=bbox_dict, ha=ha_capsula, va=va_capsula, rotation=rotacion_capsula, fontdict=font_dict, path_effects=eff_cap)
                else:
                    ax.text(pos_x_capsula, pos_y_capsula, texto_a_mostrar, ha=ha_capsula, va=va_capsula, rotation=rotacion_capsula, fontdict=font_dict, path_effects=eff_cap)

        # Mostrar cápsula negativa solo si hay valores negativos
        if es_divergente and valor_capsu and left_neg < 0:
            valor_negativo_total = suma_negativos_por_barra.iloc[idx_row]
            
            # Agrega el signo "-" manualmente
            prefijo_neg = "-" if simbolo_negativo_capsu else ""
            texto_a_mostrar_neg = f"{prefijo_neg}{elimina_ceros_no_significativos(formato_decimal.format(abs(valor_negativo_total)))}"
            
            es_cero_visual_neg = False
            try:
                if float(texto_a_mostrar_neg.replace(',', '').replace('-', '')) == 0:
                    es_cero_visual_neg = True
            except ValueError:
                pass

            if capsu_cero or not es_cero_visual_neg:
                texto_capsula_neg = f"{espacio*2}{texto_a_mostrar_neg}{espacio*2}"
                
                # --- INICIO: Lógica de desplazamiento de cápsula negativa ---
                desplazamiento_extra_capsula_neg = 0
                if hay_annotations_externas and annotations_externas_neg:
                    num_etiquetas_fuera_neg = len(annotations_externas_neg)
                    desplazamiento_extra_capsula_neg = x_max * ajustar_pos_capsu_areamin * num_etiquetas_fuera_neg
                # --- FIN: Lógica de desplazamiento de cápsula negativa ---

                text_x_pos_neg = left_neg - x_max * ajustar_pos_capsu - desplazamiento_extra_capsula_neg
                
                color_una_barra_capsu_neg = None
                if is_simple_or_divergent:
                    color_fondo_pers_capsu = colores_fondo_personalizados.get(entidad)
                    c_neg = color_fondo_pers_capsu[last_non_zero_idx_neg] if color_fondo_pers_capsu and last_non_zero_idx_neg < len(color_fondo_pers_capsu) and color_fondo_pers_capsu[last_non_zero_idx_neg] else colores_asignados[last_non_zero_idx_neg % len(colores_asignados)]
                    if colores_por_barra is not None:
                        try:
                            ccat = colores_por_barra.iloc[idx_row]
                            if pd.notna(ccat):
                                c_neg = ccat
                        except IndexError:
                            pass
                    color_una_barra_capsu_neg = c_neg

                if isinstance(color_valor_capsu, list):
                    col_idx_para_color_neg = last_non_zero_idx_neg
                    c_val_capsu = color_valor_capsu[col_idx_para_color_neg % len(color_valor_capsu)]
                else:
                    if color_valor_capsu is None:
                        c_val_capsu = color_una_barra_capsu_neg if is_simple_or_divergent else '#434343'
                    else:
                        c_val_capsu = color_valor_capsu

                if isinstance(color_borde_capsu, list):
                    col_idx_para_borde_neg = last_non_zero_idx_neg
                    c_borde_capsu = color_borde_capsu[col_idx_para_borde_neg % len(color_borde_capsu)]
                else:
                    if color_borde_capsu is None:
                        c_borde_capsu = color_una_barra_capsu_neg if is_simple_or_divergent else '#434343'
                    else:
                        c_borde_capsu = color_borde_capsu

                color_texto_capsula_neg = c_val_capsu
                bbox_dict = dict(boxstyle=f"round,pad=0.15,rounding_size={curvatura_capsu}", facecolor=color_fondo_capsu, edgecolor=c_borde_capsu, linewidth=peso_borde_capsu)
                font_dict = {'family': font_config['family'], 'size': font_config['valor_capsula']['size'], 'weight': font_config['valor_capsula']['weight'], 'color': color_texto_capsula_neg}

                if activar_cambiar_color:
                    c_bord_cap_neg = cambiar_color(color_texto_capsula_neg, color_fondo_capsu if not quitar_capsu else (fondo if fondo != 'transparent' else '#ffffff'))
                    eff_cap_neg = [path_effects.withStroke(linewidth=1.5, foreground=c_bord_cap_neg)] if c_bord_cap_neg else None
                else:
                    eff_cap_neg = None

                if not quitar_capsu:
                    ax.text(text_x_pos_neg, pos, texto_capsula_neg, bbox=bbox_dict, ha='right', va='center', fontdict=font_dict, path_effects=eff_cap_neg)
                else:
                    ax.text(text_x_pos_neg, pos, texto_a_mostrar_neg, ha='right', va='center', fontdict=font_dict, path_effects=eff_cap_neg)

        if porce_total_inicio:
            valor_numerador = total_valor
            valor_denominador = total_general
            if es_divergente:
                if not porce_diver: valor_numerador, valor_denominador = suma_absoluta_por_barra.iloc[idx_row], total_general_absoluto
                else: valor_numerador, valor_denominador = suma_positivos_por_barra.iloc[idx_row], total_general_positivos
            
            porcentaje = round((valor_numerador / valor_denominador) * 100, 1) if valor_denominador != 0 else 0
            etiqueta_actual = entidades_formateadas[pos]

            if resaltar_valor_ejey and etiqueta_actual in resaltar_valor_ejey:
                texto_a_mostrar = f"{espacio*1}{etiqueta_actual}   {porcentaje}%{espacio*1}"
                color_texto_resaltado = get_text_color_for_bg(color_resaltado_ejey)
                bbox_capsula = dict(facecolor=color_resaltado_ejey, edgecolor=color_borde_resaltado_ejey, boxstyle=f"round,pad=0.15,rounding_size={curvatura_capsu}")
                pos_x_resaltado = x_max * 1.02 if ejey_der else -x_max * 0.02
                ha_resaltado = 'left' if ejey_der else 'right'
                ax.text(pos_x_resaltado, pos, texto_a_mostrar, ha=ha_resaltado, va='center', bbox=bbox_capsula, fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight'], 'color': color_texto_resaltado})
            else:
                texto_a_mostrar = f"{espacio*1}{porcentaje}%{espacio*1}"
                ax.text(0, pos, texto_a_mostrar, ha='left', va='bottom', color=font_config['porcentaje_total']['color'], fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight']})

        if porce_total:
            valor_numerador = total_valor
            valor_denominador = total_general
            if es_divergente:
                if not porce_diver: valor_numerador, valor_denominador = suma_absoluta_por_barra.iloc[idx_row], total_general_absoluto
                else: valor_numerador, valor_denominador = suma_positivos_por_barra.iloc[idx_row], total_general_positivos

            porcentaje = round((valor_numerador / valor_denominador) * 100, 1) if valor_denominador != 0 else 0
            desplazamiento_x = x_max * (0.15 if valor_capsu and not quitar_capsu else 0.08)
            base_pos_x = left_pos if es_divergente else (100 if respecto_porce else total_valor)
            
            # --- INICIO: Lógica de desplazamiento de porcentaje total ---
            desplazamiento_extra_porcentaje = 0
            if hay_annotations_externas and annotations_externas_pos:
                num_etiquetas_fuera = len(annotations_externas_pos)
                desplazamiento_extra_porcentaje = x_max * ajustar_pos_capsu_areamin * num_etiquetas_fuera
            
            desplazamiento_final = base_pos_x + desplazamiento_x + (x_max * ajustar_pos_porce_total) + desplazamiento_extra_porcentaje
            # --- FIN: Lógica de desplazamiento de porcentaje total ---
            ax.text(desplazamiento_final, pos, f"{porcentaje}%", ha='center', va='center', color=font_config['porcentaje_total']['color'], fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight']})

    # --- DIBUJO DE ETIQUETAS EXTERNAS ---
    if hay_annotations_externas:
        for data in etiquetas_fuera:
            pos = data['pos']
            
            # Etiquetas positivas (a la derecha)
            if data['positivas']:
                start_x = data['left_pos']
                for i, annot in enumerate(data['positivas']):
                    # Modifica la siguiente línea para un espaciado no lineal
                    spacing = ((i + 1)**1.5) * (x_max * 0.01) * ajustar_sep_valor_barra
                    
                    if activar_cambiar_color:
                        if color_contorno_valor_barra:
                            c_bord_ext = color_contorno_valor_barra
                        else:
                            color_fondo_efectivo_ext = fondo if fondo != 'transparent' else '#ffffff'
                            c_bord_ext = cambiar_color(annot['color'], color_fondo_efectivo_ext)
                        eff_ext = [path_effects.withStroke(linewidth=1.5, foreground=c_bord_ext)] if c_bord_ext else None
                    else:
                        eff_ext = None
                    
                    ax.text(start_x + spacing, pos, annot['texto'],
                            ha='left', va='center',
                            color=annot['color'],
                            fontsize=annot['font_size'],
                            fontweight=annot['font_weight'],
                            path_effects=eff_ext,
                            fontfamily=font_config['family'])
            
            # Etiquetas negativas (a la izquierda)
            if data['negativas']:
                start_x = data['left_neg']
                for i, annot in enumerate(data['negativas']):
                    # Modifica la siguiente línea para un espaciado no lineal
                    spacing = ((i + 1)**1.5) * (x_max * 0.01) * ajustar_sep_valor_barra

                    if activar_cambiar_color:
                        if color_contorno_valor_barra:
                            c_bord_ext_neg = color_contorno_valor_barra
                        else:
                            color_fondo_efectivo_ext_neg = fondo if fondo != 'transparent' else '#ffffff'
                            c_bord_ext_neg = cambiar_color(annot['color'], color_fondo_efectivo_ext_neg)
                        eff_ext_neg = [path_effects.withStroke(linewidth=1.5, foreground=c_bord_ext_neg)] if c_bord_ext_neg else None
                    else:
                        eff_ext_neg = None

                    ax.text(start_x - spacing, pos, annot['texto'],
                            ha='right', va='center',
                            color=annot['color'],
                            fontsize=annot['font_size'],
                            fontweight=annot['font_weight'],
                            path_effects=eff_ext_neg,
                            fontfamily=font_config['family'])

    for i, col in enumerate(columnas_lineas):
        if colores_lineas and i < len(colores_lineas): line_color = colores_lineas[i]
        else: line_color = colores_asignados[(i + len(columnas_barras)) % len(colores_asignados)]
        valores_linea = df_plot[col].values
        line, = ax.plot(valores_linea, posiciones, marker='o', markersize=6, linewidth=2, color=line_color, label=col, zorder=5)
        line_handles.append(line)
        line_labels.append(col)
        
        if capsu_final_lineas and len(valores_linea) > 0:
            ultimo_pos, ultimo_valor = posiciones[-1], valores_linea[-1]
            if capsu_cero or ultimo_valor != 0:
                texto_a_mostrar = elimina_ceros_no_significativos(formato_decimal.format(abs(ultimo_valor)))
                texto_capsula = f"{espacio*2}{texto_a_mostrar}{espacio*2}"
                pos_x_capsula, pos_y_capsula = ultimo_valor, ultimo_pos
                
                # Reutilizando colores configurados
                color_texto_capsula = color_valor_capsu if color_valor_capsu is not None else '#434343'
                color_borde_capsula = color_borde_capsu if color_borde_capsu is not None else '#434343'

                bbox_dict = dict(boxstyle=f"round,pad=0.15,rounding_size={curvatura_capsu}", facecolor=color_fondo_capsu, edgecolor=color_borde_capsula, linewidth=peso_borde_capsu)
                font_dict = {'family': font_config['family'], 'size': font_config['valor_capsula']['size'], 'weight': font_config['valor_capsula']['weight'], 'color': color_texto_capsula}
                ha_val = 'left' if ultimo_valor >= 0 else 'right'
                if not quitar_capsu:
                    ax.text(pos_x_capsula, pos_y_capsula, texto_capsula, bbox=bbox_dict, ha=ha_val, va='center', fontdict=font_dict)
                else:
                    ax.text(pos_x_capsula, pos_y_capsula, texto_a_mostrar, ha=ha_val, va='center', fontdict=font_dict)

    # --- 8. AJUSTES FINALES DE LA GRÁFICA ---
    if (porce_total_inicio or resaltar_valor_ejey) and resaltar_valor_ejey:
        # Modificación para usar tick_labels original en lugar de entidades_formateadas si se resalta
        tick_labels = ["" if e in resaltar_valor_ejey else e for e in tick_labels]

    ax.set_yticks(tick_positions)
    
    # Manejo de la rotación basada en grados numéricos (-90 a 90)
    try:
        rotation_val = float(orientacion_valor_ejey)
        # Limitar entre -90 y 90
        rotation_val = max(-90.0, min(90.0, rotation_val))
    except (ValueError, TypeError):
        rotation_val = 0.0

    # Ajuste de alineación horizontal según rotación y lado del eje Y
    if rotation_val == 0:
        ha_val = 'left' if ejey_der else 'right'
    elif abs(rotation_val) == 90:
        ha_val = 'center'
    else:
        # Para rotaciones intermedias, se ajusta según la inclinación y el lado
        if ejey_der:
            ha_val = 'left' if rotation_val > 0 else 'right'
        else:
            ha_val = 'right' if rotation_val > 0 else 'left'

    ax.set_yticklabels(tick_labels, fontsize=font_config['variable_y']['size'], fontweight=font_config['variable_y']['weight'], fontfamily=font_config['family'], color=font_config['variable_y']['color'], rotation=rotation_val, ha=ha_val)
    
    if resaltar_valor_ejey and not porce_total_inicio:
        # Usar tick_positions y tick_labels
        for pos_y, etiqueta_actual in zip(tick_positions, tick_labels):
            if etiqueta_actual in resaltar_valor_ejey:
                texto_capsula = f"{espacio*1}{etiqueta_actual}{espacio*1}"
                color_texto_resaltado = get_text_color_for_bg(color_resaltado_ejey)
                bbox_capsula = dict(facecolor=color_resaltado_ejey, edgecolor=color_borde_resaltado_ejey, boxstyle=f"round,pad=0.15,rounding_size={curvatura_capsu}")
                pos_x_resaltado = x_max * 1.02 if ejey_der else -x_max * 0.02
                ha_resaltado = 'left' if ejey_der else 'right'
                ax.text(pos_x_resaltado, pos_y, texto_capsula, ha=ha_resaltado, va='center', bbox=bbox_capsula, fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight'], 'color': color_texto_resaltado})

    bottom_y_limit = -0.5
    # Actualizar límite superior usando la última posición + margen
    if len(posiciones) > 0:
        max_pos_y = posiciones[-1] # En horizontal, esto está "abajo" visualmente si invertimos ejes... 
        # Espera, ax.invert_yaxis() hace que 0 esté arriba.
        # Las posiciones crecen hacia abajo. Entonces el "top" visual es index 0.
        # bottom limit de la grafica (valores bajos de Y) es arriba visualmente.
        # top limit (valores altos de Y) es abajo visualmente.
        
        # Con invert_yaxis():
        # y=0 es Top. y=max es Bottom.
        
        # Mis posiciones van de 0 a N.
        # bottom_y_limit = -0.5 (un poco arriba de la primera barra)
        # top_y_limit debería ser max_pos + algo.
        
        # Con mis nuevos calculos, 'y_cursor' avanza.
        # La ultima position es max(posiciones).
        
        top_y_limit = max(posiciones) + 0.5 + (0.8 if hay_annotations_externas else 0)
    else:
        top_y_limit = 0.5

    ax.set_ylim(bottom_y_limit, top_y_limit)
    ax.invert_yaxis()
    
    if limites_ejex and not respecto_porce: ax.set_xlim(limites_ejex)
    else:
        x_min = (-x_max * (1 + ajustar_sep_izquierda_ejey)) if es_divergente and not respecto_porce else 0
        x_max_val = 100 if respecto_porce else x_max
        ax.set_xlim(x_min, x_max_val)
        
    if divisiones_ejex: ax.xaxis.set_major_locator(mticker.MultipleLocator(divisiones_ejex))
    else: ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins='auto', steps=[1, 2, 5, 10]))
    
    if respecto_porce or simbolo_porce_ejex:
        formatter = FuncFormatter(lambda x, _: f'{int(x)}%')
        if not respecto_porce and num_dec > 0:
            formatter = FuncFormatter(lambda x, _: f"{elimina_ceros_no_significativos(formato_decimal.format(abs(x) if solo_ejex_positivo else x))}%")
        elif not respecto_porce:
            formatter = FuncFormatter(lambda x, _: f"{int(abs(x)) if solo_ejex_positivo else int(x):,}%")
        ax.xaxis.set_major_formatter(formatter)
    else:
        formatter = FuncFormatter(lambda x, _: elimina_ceros_no_significativos(formato_decimal.format(abs(x) if solo_ejex_positivo else x)))
        ax.xaxis.set_major_formatter(formatter)
    
    plt.setp(ax.get_xticklabels(), fontsize=font_config['variable_x']['size'], fontweight=font_config['variable_x']['weight'], color=font_config['variable_x']['color'], fontfamily=font_config['family'])
    
    ax.set_axisbelow(True)
    ax.grid(visible=grillas, axis='x', color='#B9B9B9', linewidth=0.75, linestyle='-', zorder=0)
    if porce_total_inicio: ax.tick_params(axis='y', pad=espacio_inicio)
        
    if nombre_ejey: ax.set_ylabel(nombre_ejey, labelpad=18, **font_config['nombre_ejey'])
    if nombre_ejex: ax.set_xlabel(nombre_ejex, labelpad=18, **font_config['nombre_ejex'])

    for label, entidad_formateada in zip(ax.get_yticklabels(), entidades_formateadas):
        try:
            mapa_formato_a_original = {ent_fmt: ent_orig for ent_fmt, ent_orig in zip(entidades_formateadas, df.index)}
            original_index = mapa_formato_a_original.get(entidad_formateada)
            if original_index and "__espaciador__" in str(original_index):
                label.set_rotation(0)
                label.set_ha('center')
        except (ValueError, IndexError, KeyError): pass

    if ejey_der:
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")
        ax.invert_xaxis()

    if leyenda:
        handles, labels = ax.get_legend_handles_labels()
        by_label = {lbl: h for h, lbl in zip(handles, labels)}
        
        all_labels, final_handles = [], []
        
        if mapa_color_categoria:
            final_handles = [Patch(color=color) for color in mapa_color_categoria.values()]
            all_labels = list(mapa_color_categoria.keys())
            
            for i, lbl in enumerate(columnas_lineas):
                all_labels.append(lbl)
                if colores_lineas and i < len(colores_lineas): line_color = colores_lineas[i]
                else: line_color = colores_asignados[(i + len(columnas_barras)) % len(colores_asignados)]
                final_handles.append(by_label.get(lbl, plt.Line2D([0], [0], color=line_color, marker='o', markersize=6, linewidth=2)))
        else:
            for i, lbl in enumerate(columnas_barras):
                all_labels.append(lbl)
                final_handles.append(by_label.get(lbl, Patch(color=colores_asignados[i % len(colores_asignados)])))
            for i, lbl in enumerate(columnas_lineas):
                all_labels.append(lbl)
                if colores_lineas and i < len(colores_lineas): line_color = colores_lineas[i]
                else: line_color = colores_asignados[(i + len(columnas_barras)) % len(colores_asignados)]
                final_handles.append(by_label.get(lbl, plt.Line2D([0], [0], color=line_color, marker='o', markersize=6, linewidth=2)))
        
        num_cols_leyenda = num_columnas_leyenda if num_columnas_leyenda is not None else len(all_labels)
        
        # Configuración base de la leyenda
        kwargs_leyenda = {
            'title': leyenda if isinstance(leyenda, str) else None,
            'fontsize': font_config['leyenda']['size'],
            'title_fontsize': font_config['leyenda']['size'],
            'frameon': False,
            'ncol': num_cols_leyenda,
            'handlelength': 1,
            'handleheight': 1
        }

        # Lógica flexible para posicionar la leyenda
        if isinstance(posicion_leyenda, dict):
            kwargs_leyenda.update(posicion_leyenda)
        elif isinstance(posicion_leyenda, (tuple, list)):
            kwargs_leyenda['loc'] = 'center'
            kwargs_leyenda['bbox_to_anchor'] = posicion_leyenda
        else:
            kwargs_leyenda['loc'] = posicion_leyenda

        ax.legend(final_handles, all_labels, **kwargs_leyenda)
        
    ax.spines[['top', 'bottom']].set_visible(False)
    ax.spines['left'].set_visible(not ejey_der)
    ax.spines['right'].set_visible(ejey_der)

    if es_divergente and not respecto_porce: ax.axvline(0, color='black', linewidth=1)

    # --- 9. GUARDADO Y VISUALIZACIÓN ---
    from funciones import mostrar_guardar_figura

    mostrar_guardar_figura(
        fig=fig,
        ax=ax,
        nombre_df=nombre,
        guardar_fig=guardar_fig,
        mostrar_fig=mostrar_fig,
        limpiar_svg_con_scour=True,
        exact_dim=tamano_exacto
    )
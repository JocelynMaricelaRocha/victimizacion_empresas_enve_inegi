import subprocess
import pandas as pd
import numpy as np
import re
from matplotlib.colors import to_rgb, to_hex
import matplotlib.pyplot as plt
import decimal
import os

MESES_ES_ABREV = {
    1: 'ene', 2: 'feb', 3: 'mar', 4: 'abr', 5: 'may', 6: 'jun',
    7: 'jul', 8: 'ago', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dic'
}
MESES_ES_COMPLETO = {
    1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
    7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
}

def elimina_ceros_no_significativos(valor):
    valor_str = str(valor)
    if '.' in valor_str:
        valor_str = valor_str.rstrip('0').rstrip('.')
    return valor_str

def num_decimales(valores, determinado=None):
    """
    Determina el número de decimales adecuado para mostrar en una gráfica según los valores dados.
    Reglas:
    - Busca el valor absoluto mínimo distinto de cero.
    - Calcula el promedio de los valores absolutos distintos de cero.
    - Si el mínimo > 1: 0 decimales.
    - Si el mínimo < 1 y el promedio >= 100: 0 decimales.
    - Si el mínimo < 1 y el promedio >= 10 y < 100: 1 decimal.
    - Si el mínimo < 1 y el promedio >= 1 y < 10: 2 decimales.
    - Si el promedio < 1: decimales según el mínimo (cuántos decimales tiene, incluyendo ceros a la izquierda).
    - Si 'determinado' es distinto de None, devuelve ese valor ignorando el resto.
    """
    if determinado is not None:
        return determinado

    serie = pd.Series(valores).dropna()
    serie_no_cero = serie[serie != 0].abs()
    if len(serie_no_cero) == 0:
        return 0

    min_abs = serie_no_cero.min()
    promedio = serie_no_cero.mean()

    if min_abs > 1:
        return 0
    elif min_abs < 1:
        if promedio >= 100:
            return 0
        elif promedio >= 10:
            return 1
        elif promedio >= 1:
            return 2
        else:
            # Cuenta todos los decimales después del punto, incluyendo ceros a la izquierda
            min_str = f"{min_abs:.16f}".rstrip('0')
            if '.' in min_str:
                decimales = len(min_str.split('.')[1])
                return decimales
            else:
                return 0
    else:
        return 0

def limpiar_svg_con_scour(archivo_entrada, archivo_salida):
    """
    Optimiza un archivo SVG utilizando la herramienta de línea de comandos 'scour'.

    Reduce el tamaño del archivo SVG eliminando datos innecesarios, acortando IDs
    y aplicando otras optimizaciones sin afectar la apariencia visual.

    Args:
        archivo_entrada (str): Ruta al archivo SVG original.
        archivo_salida (str): Ruta donde se guardará el archivo SVG optimizado.
    """
    subprocess.run([
        'scour', '-i', archivo_entrada, '-o', archivo_salida,
        '--enable-viewboxing', '--enable-id-stripping',
        '--shorten-ids', '--remove-descriptive-elements'
    ], check=True)

def formato_fechas(fechas, modalidad=1, mostrar_solo=None):
    """
    Formatea una lista de fechas a un formato de cadena de texto legible y conciso.

    Args:
        fechas (list): Una lista de objetos de fecha (ej. pd.Timestamp).
        mostrar_solo (str, optional): "años", "meses", "dias", "dias_meses", "dias_años" o "meses_años".
        modalidad (int, optional): Diferentes modalidades con las cuales se pueden expresar las fechas".


    Returns:
        list: Una lista de cadenas de texto con las fechas formateadas.
    """
    fechas = pd.to_datetime(fechas)

    opciones_mostrar_solo = ["años", "meses", "dias", "dias_meses", "dias_años", "meses_años"]

    if mostrar_solo is not None and mostrar_solo not in opciones_mostrar_solo:
        raise ValueError(f"Opción '{mostrar_solo}' no válida para 'mostrar_solo'. Opciones disponibles: {opciones_mostrar_solo}.")

    if modalidad not in [1, 2]:
        raise ValueError("Las opciones válidas para 'modalidad' son 1 y 2.")

    dias = set(f.day for f in fechas)
    meses = set(f.month for f in fechas)
    anios = set(f.year for f in fechas)

    if modalidad == 2:
        es_solo_meses = (mostrar_solo == "meses") or (
            mostrar_solo is None and len(dias) == 1 and len(anios) == 1 and len(meses) > 1
        )
        if not es_solo_meses:
            raise ValueError("La modalidad 2 solo está disponible para formatos que muestran únicamente los meses.")

    if mostrar_solo:
        if mostrar_solo == "años":
            labels = [str(f.year) for f in fechas]
        elif mostrar_solo == "meses":
            diccionario_meses = MESES_ES_COMPLETO if modalidad == 2 else MESES_ES_ABREV
            labels = [diccionario_meses[f.month] for f in fechas]
        elif mostrar_solo == "dias":
            labels = [f"{f.day:02d}" for f in fechas]
        elif mostrar_solo == "dias_meses":
            labels = [f"{f.day:02d}\n{MESES_ES_ABREV[f.month]}" for f in fechas]
        elif mostrar_solo == "dias_años":
            labels = [f"{f.day:02d}\n{f.year}" for f in fechas]
        elif mostrar_solo == "meses_años":
            labels = [f"{MESES_ES_ABREV[f.month]}\n{f.year}" for f in fechas]
        else:
            labels = []

        if labels:
            resultado = []
            ultimo = None
            for label in labels:
                if label != ultimo:
                    resultado.append(label)
                    ultimo = label
                else:
                    resultado.append("")
            return resultado

    # Si solo el mes es igual y difieren en día y año
    if len(meses) == 1 and len(anios) > 1 and len(dias) > 1:
        return [f"{f.day:02d}\n{f.year}" for f in fechas]

    # Si solo difieren en el día (mismo mes y año)
    if len(meses) == 1 and len(anios) == 1 and len(dias) > 1:
        return [f"{f.day:02d}" for f in fechas]

    # Si tienen el mismo año pero difieren en mes y día
    if len(anios) == 1 and len(meses) > 1 and len(dias) > 1:
        return [f"{f.day:02d}\n{MESES_ES_ABREV[f.month]}" for f in fechas]

    # Detectar si las fechas difieren exactamente por tres meses
    if len(fechas) > 1:
        diferencias = [(fechas[i+1] - fechas[i]).days for i in range(len(fechas)-1)]
        if all(d in [89, 90, 91, 92] for d in diferencias):
            return [f"T{((f.month-1)//3)+1} {f.year}" for f in fechas]

    # Si solo difieren en el año (mismo día y mes)
    if len(dias) == 1 and len(meses) == 1 and len(anios) > 1:
        return [str(f.year) for f in fechas]
    # Si solo difieren en el mes (mismo día y año)
    elif len(dias) == 1 and len(anios) == 1 and len(meses) > 1:
        diccionario_meses = MESES_ES_COMPLETO if modalidad == 2 else MESES_ES_ABREV
        return [diccionario_meses[f.month] for f in fechas]
    elif len(dias) == 1 and (len(meses) > 1 or len(anios) > 1):
        # mes abreviado en minúsculas + salto de línea + año
        return [MESES_ES_ABREV[f.month] + "\n" + str(f.year) for f in fechas]
    else:
        return [f"{f.day:02d}\n{MESES_ES_ABREV[f.month]}\n{f.year}" for f in fechas]


def get_text_color_for_bg(bg_color):
    """
    Determina si el color del texto debe ser blanco o negro para un contraste adecuado.

    Calcula la luminosidad del color de fondo y devuelve negro ('#000000') para
    fondos claros y blanco ('#ffffff') para fondos oscuros.

    Args:
        bg_color (str): El color de fondo en un formato reconocido por Matplotlib 
                        (ej. '#RRGGBB', 'red', 'yellow').

    Returns:
        str: El código hexadecimal del color de texto ('#000000' o '#ffffff').
    """
    if bg_color is None:
        return '#000000'
        
    if isinstance(bg_color, str) and bg_color.lower() == 'none':
        return '#000000'

    # Si el color es exactamente '8d78c3ff', devolver blanco
    if isinstance(bg_color, str) and bg_color.lower() == '8d78c3ff':
        return '#ffffff'

    try:
        # Convertir el color de fondo a RGB
        rgb = to_rgb(bg_color)
        
        # Calcular la luminosidad usando la fórmula estándar (YIQ)
        # 0.299*R + 0.587*G + 0.114*B
        luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        
        # Devolver negro para fondos claros (luminance > 0.5), blanco para oscuros
        return '#000000' if luminance > 0.5 else '#ffffff'
    except (ValueError, TypeError):
        # Si el color no es válido, devolver negro por defecto
        return '#000000'
    
def unir_barras(df, num_barras, lado):
    """
    Une un número específico de barras de un DataFrame en una sola barra sumada.

    Toma las primeras o las últimas 'num_barras' filas del DataFrame, las suma
    para crear una nueva fila consolidada y la reemplaza en el DataFrame original.
    La etiqueta de la nueva fila se genera a partir del rango de las etiquetas originales.

    Args:
        df (pd.DataFrame): El DataFrame de entrada con las barras a procesar.
        num_barras (int): El número de barras a unir desde el borde especificado.
        lado (str): El lado desde el cual unir las barras ('izquierda' o 'derecha').

    Returns:
        tuple: Un tuple conteniendo:
            - pd.DataFrame: El DataFrame modificado con las barras unidas.
            - str or None: La etiqueta de la nueva barra unida, o None si no se unió nada.
    """
    if num_barras <= 1 or len(df) < num_barras:
        return df, None
        
    if lado == 'izquierda':
        seleccion = df.iloc[:num_barras]
        df_resto = df.iloc[num_barras:]
    else: # derecha
        seleccion = df.iloc[-num_barras:]
        df_resto = df.iloc[:-num_barras]

    union = seleccion.sum()
    idxs = seleccion.index
        
    if np.issubdtype(type(idxs[0]), np.datetime64) or isinstance(idxs[0], pd.Timestamp):
        start_date, end_date = idxs[0], idxs[-1]
        
        if start_date == end_date:
            etiqueta_union = formato_fechas([start_date])[0]
        elif start_date.year == end_date.year:
            # Si los días son diferentes, muestra día y mes
            if start_date.day != end_date.day:
                start_format = f"{start_date.day:02d} de {MESES_ES_ABREV[start_date.month]}"
                end_format = f"{end_date.day:02d} de {MESES_ES_ABREV[end_date.month]}"
            # Si solo los meses son diferentes, muestra solo el mes
            else:
                start_format = MESES_ES_ABREV[start_date.month].capitalize()
                end_format = MESES_ES_ABREV[end_date.month].capitalize()
            
            etiqueta_union = f"{start_format} a {end_format} de {start_date.year}"
        else:
            # Si los años son diferentes, usa el formato completo
            formatted_dates = formato_fechas(idxs)
            etiqueta_union = f"{formatted_dates[0]}-{formatted_dates[-1]}"
    else:
        if idxs[0] == idxs[-1]:
            etiqueta_union = str(idxs[0])
        else:
            etiqueta_union = f"{idxs[0]}-{idxs[-1]}"
        
    df_union = pd.DataFrame([union], index=[etiqueta_union])

    if lado == 'izquierda':
        return pd.concat([df_union, df_resto]), etiqueta_union
    else:
        return pd.concat([df_resto, df_union]), etiqueta_union
    
    
def renombra_y_ordena_col(df, nuevos_nom_col, nuevas_pos_col):
    """
    Renombra y reordena las columnas de un DataFrame, mostrando los cambios realizados.
    Incluye validaciones y mensajes de error para los argumentos.
    """
    print("--------------------- FUNCIÓN: renombra_y_ordena_col -----------------------\n")
    df = df.copy()
    antiguos_nombres = list(df.columns)

    # Validaciones
    if not isinstance(nuevos_nom_col, (list, tuple)):
        raise ValueError("El argumento 'nuevos_nom_col' debe ser una lista o tupla de nombres de columnas.")
    if not isinstance(nuevas_pos_col, (list, tuple)):
        raise ValueError("El argumento 'nuevas_pos_col' debe ser una lista o tupla de posiciones (enteros).")
    if len(nuevos_nom_col) != len(antiguos_nombres):
        raise ValueError(f"El número de nuevos nombres ({len(nuevos_nom_col)}) no coincide con el número de columnas del DataFrame ({len(antiguos_nombres)}).")
    if len(nuevas_pos_col) != len(antiguos_nombres):
        raise ValueError(f"El número de posiciones ({len(nuevas_pos_col)}) no coincide con el número de columnas del DataFrame ({len(antiguos_nombres)}).")
    if not all(isinstance(i, int) for i in nuevas_pos_col):
        raise ValueError("Todos los elementos de 'nuevas_pos_col' deben ser enteros.")
    if not all(1 <= i <= len(antiguos_nombres) for i in nuevas_pos_col):
        raise ValueError(f"Todas las posiciones en 'nuevas_pos_col' deben estar entre 1 y {len(antiguos_nombres)} (inclusive).")
    if len(set(nuevas_pos_col)) != len(nuevas_pos_col):
        raise ValueError("Las posiciones en 'nuevas_pos_col' no deben repetirse.")

    # Renombrar columnas
    df.columns = nuevos_nom_col
    # Mostrar cambios de nombre
    print("Las siguientes columnas cambiaron de nombre:")
    for ant, nue in zip(antiguos_nombres, nuevos_nom_col):
        if ant != nue:
            print(f"{ant} -> {nue}")
    # print("\n Dimensiones del dataframe resultante:")
    # print(df.shape)
    # Reordenar columnas (ajustar a 0-based)
    nuevas_pos_col = [i-1 for i in nuevas_pos_col]
    df = df.iloc[:, nuevas_pos_col]
    #print("\n Las primeras 5 filas del dataframe resultante:")
    #print(df.head())
    print("\n----------------------------------------------------------------------------\n")
    return df

def exportar_grafica(nombre, limpiar_svg_con_scour_func, exact_dim=False):
    """
    Guarda la gráfica actual en SVG y PNG, optimiza el SVG y elimina el original.
    """
    base_path = f"output/{nombre}"
    output_dir = os.path.dirname(base_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    original_svg_path = f"{base_path}.svg"
    scour_svg_path = f"{base_path}_scour.svg"
    bbox_val = None if exact_dim else 'tight'
    plt.savefig(original_svg_path, format='svg', bbox_inches=bbox_val, dpi=300)
    plt.savefig(f"{base_path}.png", format='png', bbox_inches=bbox_val, dpi=300)
    
    # Comprueba si se proporcionó una función de limpieza válida antes de llamarla
    if callable(limpiar_svg_con_scour_func):
        try:
            limpiar_svg_con_scour_func(original_svg_path, scour_svg_path)
            os.remove(original_svg_path)
        except Exception as e:
            print(f"Error al optimizar o eliminar el SVG: {e}")
            # Si falla la optimización, renombra el original para no perderlo
            if os.path.exists(scour_svg_path):
                os.remove(scour_svg_path)
            os.rename(original_svg_path, scour_svg_path)
    else:
        # Si no hay función de limpieza, simplemente renombra el archivo original
        if os.path.exists(scour_svg_path):
            os.remove(scour_svg_path)
        os.rename(original_svg_path, scour_svg_path)


def mostrar_guardar_figura(fig=None, ax=None, nombre_df=None, guardar_fig=True, mostrar_fig=True, limpiar_svg_con_scour=True, exact_dim=False):
    """
    Guarda y/o muestra una figura de Matplotlib.
    Parámetros:
        fig: figura de matplotlib (opcional, si no se pasa se usa plt.gcf())
        ax: eje de matplotlib (opcional, si no se pasa se usa plt.gca())
        nombre_df: nombre para exportar la gráfica (str)
        guardar_fig: bool, si True guarda la figura
        mostrar_fig: bool, si True muestra la figura
        limpiar_svg_con_scour: bool o función. Si es True, usa la función por defecto.
                               Si es una función, la usa. Si es False/None, no hace nada.
        exact_dim: bool, si es True, evita redimensionar la figura al guardar.
    Retorna:
        fig, ax
    """
    import matplotlib.pyplot as plt

    if exact_dim:
        plt.tight_layout()
    # plt.tight_layout() # Eliminado: tight_layout a veces recorta elementos muy externos o falla con múltiples leyendas manuales.
    # Confiamos en bbox_inches='tight' al guardar.
    
    if fig is None:
        fig = plt.gcf()
    if ax is None:
        ax = plt.gca()
    if guardar_fig and nombre_df is not None:
        from funciones import exportar_grafica, limpiar_svg_con_scour as scour_func
        
        # Determina qué función pasar a exportar_grafica
        func_a_pasar = None
        if limpiar_svg_con_scour is True:
            func_a_pasar = scour_func
        elif callable(limpiar_svg_con_scour):
            func_a_pasar = limpiar_svg_con_scour

        exportar_grafica(nombre_df, func_a_pasar, exact_dim=exact_dim)
    if mostrar_fig:
        plt.show()
    return fig, ax

def algoritmo_posicionamiento_1(x_coords, y_coords, espaciado_vertical=0.5):
    """
    Algoritmo 1 de posicionamiento de cápsulas.
    - No cambia las posiciones en el eje X.
    - Las cápsulas alineadas en un mismo X se apilan por arriba del punto más alto en ese X,
      con una distancia uniforme entre ellas.
    """
    import numpy as np
    
    # Crear un diccionario para agrupar las coordenadas (original indices) por valor X
    puntos_por_x = {}
    for i, (x_val, y) in enumerate(zip(x_coords, y_coords)):
        # Redondear por si hay errores de precisión en floats de Matplotlib
        try:
            x_rounded = round(float(x_val), 5)
        except (ValueError, TypeError):
            x_rounded = str(x_val) # Si es un Timestamp o string, agrupar por su representación como texto
        
        if x_rounded not in puntos_por_x:
            puntos_por_x[x_rounded] = []
        puntos_por_x[x_rounded].append((i, y))
        
    nuevas_y = list(y_coords)
    
    for x_rounded, items in puntos_por_x.items():
        # Apilar solo si hay más de 1 punto (opcional) pero apilaremos siempre o al menos los detectaremos
        max_y = max(item[1] for item in items)
        items_ordenados = sorted(items, key=lambda item: item[1])
        
        for i, (idx, y_original) in enumerate(items_ordenados):
            nuevas_y[idx] = max_y + (i + 1) * espaciado_vertical

    return list(x_coords), nuevas_y

def algoritmo_posicionamiento_2(x_coords, y_coords, espaciado_vertical=0.5, capsu_en_max=False):
    """
    Algoritmo 2 de posicionamiento de cápsulas.
    - No cambia las posiciones en el eje X.
    - Las cápsulas están alternadas entre puntos consecutivos. 
      El primer conjunto se coloca arriba del máximo, el segundo abajo del mínimo, etc.
    """
    import numpy as np
    
    # Crear un diccionario para agrupar las coordenadas (original indices) por valor X
    puntos_por_x = {}
    for i, (x_val, y) in enumerate(zip(x_coords, y_coords)):
        # Redondear por si hay errores de precisión en floats de Matplotlib
        try:
            x_rounded = round(float(x_val), 5)
        except (ValueError, TypeError):
            x_rounded = str(x_val) # Si es un Timestamp o string, agrupar por su representación como texto
        
        if x_rounded not in puntos_por_x:
            puntos_por_x[x_rounded] = []
        puntos_por_x[x_rounded].append((i, y))
        
    nuevas_y = list(y_coords)
    
    # Ordenar las claves para asegurar que iteramos en orden de X (cronológico/secuencial)
    # y así alternar correctamente. Si no son comparables, usamos el orden de inserción.
    try:
        claves_ordenadas = sorted(puntos_por_x.keys())
    except TypeError:
        claves_ordenadas = list(puntos_por_x.keys())
        
    # Encontrar la clave X donde se encuentra el valor Y máximo
    x_key_max_global = None
    if capsu_en_max and y_coords:
        max_y_global = max(y_coords)
        for x_key, items in puntos_por_x.items():
            if any(item[1] == max_y_global for item in items):
                x_key_max_global = x_key
                break
    
    for idx_x, x_key in enumerate(claves_ordenadas):
        items = puntos_por_x[x_key]
        
        va_arriba = (idx_x % 2 == 0)
        if capsu_en_max and x_key == x_key_max_global:
            va_arriba = True
            
        if va_arriba:
            # Arriba del punto más alto
            max_y = max(item[1] for item in items)
            items_ordenados = sorted(items, key=lambda item: item[1]) # de menor a mayor
            for i, (idx, y_original) in enumerate(items_ordenados):
                nuevas_y[idx] = max_y + (i + 1) * espaciado_vertical
        else:
            # Abajo del punto más bajo
            min_y = min(item[1] for item in items)
            # Ordenar de mayor a menor para que el más alto esté más cerca del punto
            items_ordenados = sorted(items, key=lambda item: item[1], reverse=True)
            for i, (idx, y_original) in enumerate(items_ordenados):
                nuevas_y[idx] = min_y - (i + 1) * espaciado_vertical

    return list(x_coords), nuevas_y

import colorsys

def cambiar_color(color, color_fondo='#ffffff', umbral_contraste=0.35):
    """
    Ajusta la luminosidad de 'color' para asegurar que destaque frente a 'color_fondo'.
    Conserva el tono original (por ejemplo, un amarillo claro se vuelve un amarillo oscuro).
    """
    try:
        rgb_c = to_rgb(color)
        rgb_f = to_rgb(color_fondo)
    except (ValueError, TypeError):
        return color

    def calcular_luminancia(rgb):
        return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]

    lum_c = calcular_luminancia(rgb_c)
    lum_f = calcular_luminancia(rgb_f)

    if abs(lum_c - lum_f) < umbral_contraste:
        h, l, s = colorsys.rgb_to_hls(*rgb_c)
        paso = -0.05 if lum_f >= 0.5 else 0.05
        
        while abs(calcular_luminancia(colorsys.hls_to_rgb(h, l, s)) - lum_f) < umbral_contraste:
            l += paso
            if l <= 0.0 or l >= 1.0:
                break
                
        l = max(0.0, min(1.0, l))
        nuevo_rgb = colorsys.hls_to_rgb(h, l, s)
        return to_hex(nuevo_rgb)
        
    return None

def agregar_saltos_linea(texto, saltos_linea_cada_x_palabras=4):
    """
    Agrega saltos de línea '\\n' a un texto cada X palabras.
    """
    if not isinstance(texto, str):
        return texto
    palabras = texto.split()
    lineas = []
    for i in range(0, len(palabras), saltos_linea_cada_x_palabras):
        lineas.append(" ".join(palabras[i:i + saltos_linea_cada_x_palabras]))
    return "\n".join(lineas)

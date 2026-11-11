# EXPORTAR: gráfica de barras verticales
        
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
from collections import defaultdict
import os

from funciones import limpiar_svg_con_scour
from funciones import formato_fechas 
from funciones import get_text_color_for_bg 
from funciones import unir_barras 
from funciones import renombra_y_ordena_col
from funciones import num_decimales
from funciones import elimina_ceros_no_significativos
from funciones import cambiar_color
import matplotlib.patheffects as path_effects

def barras_verticales(
        
    # --- GRÁFICA GENERAL ---
    df,     # DataFrame de entrada con la estructura especificada arriba.
    nombre="barras_verticales", # Nombre base para archivos de salida (.png y .svg se exportarán).
    tipo_letra='Montserrat',    # Tipo de letra, por defecto 'Montserrat'.
    colores=None,               # Lista de colores en HEX o nombres CSS para las series a apilar.
    ancho=23,                 # Ancho de la figura en centímetros.
    alto=10,                  # Alto de la figura en centímetros.
    grillas=True,               # Activar/desactivar grillas horizontales de fondo.
    fondo='transparent',        # Color de fondo. Puede ser 'transparent', 'white' o cualquier código HEX (ej. '#FF0000').
    decimales=None,             # Número de decimales forzados en los valores dentro y fuera de la barra.
    mostrar=True,               # Si True, usa plt.show() al final.
    guardar=True,               # Si True, guarda los resultados vía savefig().
     

    # --- MODIFICACIONES ÚTILES ---
    ordenar='y',                # 'x' ordena la variable independiente, 'y' por suma total de barra, None preserva orden.
    ascendente=False,           # Dirección del orden si `ordenar` es 'x' o 'y'.
    agregar_datos=None,         # Permite insertar barras comparativas o de contexto sin añadirlas al DataFrame. Recibe una lista de tuplas con 2 a 5 elementos: `(categoria, [etiqueta], valor, [texto_barra], [opciones_extra])`. - `categoria`: El índice en X (Ej: 2018, 'Ene'). - `etiqueta` (Opcional): Texto a mostrar en el eje X para esta barra. - `valor`: Cantidad a graficar (lista proporcional si son múltiples barras apiladas, ej. `[10, 20]`). - `texto_barra` (Opcional): Texto customizado para el interior de las barras agregadas. - `opciones_extra` (Opcional): Diccionario para estilos dict={ 'colores_fondo': ['#hex', 'none'], 'colores_borde': ['black'], 'estilos_borde': ['--'], 'grosores_borde': [2], 'colores_texto': ['blue'], 'separador_derecha': '...', 'separador_izquierda': 'espacio' } Ejemplo 1 (Comparativa histórica anclada a la izquierda con separador): agregar_datos=[(2015, "Año Base", [50, 40], None, {'colores_fondo': ['#CCC', '#DDD'], 'separador_derecha': '...'})] Ejemplo 2 (Proyección futura transparente con borde punteado): agregar_datos=[("2027", "Proy.", [80, 90], "80/90 Est.", {'colores_fondo': ['none', 'none'], 'estilos_borde': ['--', '--']})]
    asignar_etiquetas=None,     # Nombre de columna para sustituir las etiquetas base de X con textos listos para display.
    unir_izq=0,                 # Unir barras a la izquierda
    unir_der=0,                 # Unir barras a la derecha
    nombres_columnas=None,      # Lista para renombrar las columnas tras remover metadatos.
    posiciones_columnas=None,   # Índices 1-based para reordenar cómo se apilan las barras de abajo hacia arriba.
    respecto_porce=False,       # Si True, convierte las barras apiladas al 100% de la altura, representando share (participación).


    # --- CATEGORIAS Y AGRUPACIÓN ---
    columna_categorias=None, # Índice 1-based de la columna de categorías de agrupamiento para las barras. Modifica el color por categoría.
    colores_categorias=None,    # Paleta de colores aplicada a los grupos de columnas cuando `columna_categorias` está activo.
    leyenda_categorias=False,      # Activa o nombra la leyenda de categorías.
    posicion_leyenda_categorias=None, # (x, y) de la leyenda.
    num_columnas_categorias=None,     # Columnas de leyenda.
    ajustar_sep_grupos=0.0, # Espacio artificial creado entre cambios de categoría grupal.


    # --- BARRAS ---
    ancho_barra=0.85,            # 0 a 1 indicando grosor relativo de las barras (0.85 default).
    estilo_grafica='apiladas',   # 'apiladas' (default) dibuja las columnas una sobre otra; 'agrupadas' las dibuja una al lado de otra, cada una desde cero, repartiendo el espacio de la barra.
    sep_barras_agrupadas=0.0,    # Solo con estilo_grafica='agrupadas' y más de una columna: separación entre las barras de un mismo grupo, de 0 (pegadas, default) a 1 (máxima). Es la fracción del espacio de cada barra que se convierte en hueco; el grupo conserva su ancho total.
    capsulas_alineadas=False,    # Solo con estilo_grafica='agrupadas': si es True, centra todas las cápsulas de un grupo en el mismo punto del eje X y las apila verticalmente, en el orden de las columnas, midiendo su alto real para que no se superpongan.
    tam_valor_barra=11,   # Tamaño letra etiqueta valor barra.
    peso_valor_barra='bold',  # Grosor de la fuente del valor numérico absoluto mostrado en la barra. Puede ser 'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black'.
    color_valor_barra=None, # Color del texto para el valor absoluto. Puede pasarse como nombre, HEX (ej. '#FFFFFF') o None para cálculo de contraste automático con el fondo.
    tam_porce_barra=11,   # Tamaño de la letra exclusivamente para el texto del porcentaje mostrado en la barra.
    peso_porce_barra='bold',  # Grosor de la fuente del porcentaje. Admite valores de matplotlib como 'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black'.
    color_porce_barra=None,# Color del texto para el porcentaje. Puede ser None (usará el predeterminado) o un código HEX/CSS.
    areamin=0,                 # Umbral mínimo para ocultar u obligar al texto posicionarse afuera de la barras por falta de espacio dentro de ellas.
    opcion_areamin='fuera',  # 'fuera' para mover el texto asociado a valor_barra y porce_barra afuera de la barra, entre la barra y la cápsula. 'sin etiquetas' para ocultar el texto dentro de las barras.
    valor_barra=True,           # Muestra el valor numérico correspondiente a la barra o al segmento de barra apilado.
    valor_barra_cero=False,     # Muestra los ceros de los valores dentro de las barras aunque sea cero en todos los valores.
    porce_barra=False,           # Muestra porcentaje que representa el segmento de barra respecto a la barra total apilada en la que se encuentra.
    porce_abajo=True,           # Pone el porcentaje debajo del valor (si ambos están activos).
    porce_diver=False,          # Porcentaje divergente. En este caso el porcentaje se calcula respecto a suma absoluta de los segmentos de barras positivas (arriba del eje X) y negativas (abajo del eje Y).
    alinear_texto_barra=False,   # Cuando es True alinea el texto dentro de la barra verticalmente (en la misma direccion a la que apunta la barra).
    simbolo_porce_barra=False, # Cuando es True añade el símbolo de porcentaje a los valores de las barra.
    simbolo_negativo=False,      # Cuando es True añade símbolo negativo a texto.
    sustituir_valores_barra=None,  # Lista de strings (nombres de columnas) en el DataFrame que contienen textos personalizados para sobreescribir las etiquetas predeterminadas dentro de las barras. Al declarar estas columnas aquí, la función las extraerá previniendo que se interpreten erróneamente como barras apilables y las usará como etiquetas.
    sustituir_valores_capsu=None, # Índice (1-based) de una columna en el DataFrame que contiene los valores o textos que se desean mostrar en la cápsula superior. Si se proporciona, la función extraerá esta columna, evitará que se grafique como una barra apilada y en su lugar la usará directamente para etiquetar la cápsula (anulando el cálculo automático de suma).
    activar_cambiar_color=True,  # Si es True, aplica automáticamente un contorno o ajuste de color al texto interno para garantizar contraste y máxima legibilidad contra el respectivo fondo.
    opcion_cambiar_color='cambio', # Modalidad para el ajuste de contraste: 'margen' aplica un contorno alrededor del texto y 'cambio' modifica directamente el color de los números para aumentar contraste.
    


   # --- CÁPSULAS ---
    valor_capsu=True,           # Mostrar globo que encapsula la suma total de apilados arriba de la barra.
    tam_valor_capsu=12,   # Tamaño de la fuente (letras o números) para el texto mostrado dentro de la cápsula.
    peso_valor_capsu='bold',  # Grosor o estilo de la fuente para el texto dentro de la cápsula. Admite valores como 'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black'.
    color_valor_capsu=None,# Color del texto dentro de la cápsula. Puede pasarse como nombre, código HEX o None (default).
    color_borde_capsu=None,# Color del borde de la cápsula.
    peso_borde_capsu=1.8,     # Grosor del borde de la cápsula. Admite valores como 'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black'.
    curvatura_capsu=0.7,         # 0 a 1 que redondea los bordes.
    color_fondo_capsu='#FFFFFF', # Color de relleno o fondo interno de la cápsula (ej. '#FFFFFF', 'white' o 'none' para transparente).
    quitar_capsu=False,         # Elimina la visualización de la cápsula.
    capsu_cero=True,            # Mantener el '0' si la barra mide cero.
    ajustar_pos_capsu=0.00,      # Ajusta la posición vertical de la cápsula respecto al tope de la barra. Es un multiplicador que se calcula como una proporción de la escala máxima del gráfico para desplazar la cápsula más arriba o más abajo.
    ajustar_pos_capsu_areamin=0.026,  # Ajuste vertical adicional que desplaza la cápsula (lado positivo) cuando `opcion_areamin='fuera'` mueve etiquetas fuera de la barra. Este desplazamiento es acumulativo y proporcional al número de etiquetas desplazadas por estar debajo del área mínima, previniendo sobreposiciones.
    ajustar_pos_capsu_neg=None,  # Ajuste de posición vertical exclusivo para las cápsulas de valores negativos (parte inferior del eje cero). Permite separación independiente de la positiva. Si es None, adoptará automáticamente el valor de `ajustar_pos_capsu`.
    ajustar_pos_capsu_neg_areamin=None, # Ajuste vertical adicional para evitar sobreposiciones de la cápsula negativa con etiquetas desplazadas hacia afuera (`opcion_areamin='fuera'`). Si es None, tomará el valor definido en `ajustar_pos_capsu_areamin`.
    alinear_capsu=False,        # Alinear la cápsula verticalmente
    simbolo_porce_capsu=False,  # Añadir símbolo de porcentaje a los valores dentro de las cápsulas
    ajustar_sep_valor_barra=1.0,  # Multiplicador para el espaciado entre etiquetas desplazadas (fuera)
    ajustar_pos_valor_barra=None, # Ajuste vertical adicional para valores fuera de las barras


    # --- PORCENTAJES TOTALES ---
    porce_total=False,           # Muestra cuánto aporta cada conjunto de barras apiladas en un mismo valor (o posición) del eje X respecto a la suma de todas las barras (en todas las posiciones del eje X) de la gráfica.
    porce_total_inicio=False,   # Mostrar el valor asociado a porce_total en el inicio de la barra (abajo del eje X) en lugar de la parte superior de la barra.
    ajustar_pos_porce_total=-0.09,      # Separación extra para porcentaje total
    tam_porce_total=11,         # Tamaño de letra para porcentaje total
    peso_porce_total='semibold', # Grosor de letra para porcentaje total
    color_porce_total='#434343',   # Color de letra para porcentaje total
    

    # --- LEYENDA ---
    leyenda=False,             # Cuando es True, muestra la leyenda de las variables.
    posicion_leyenda=(0.5, -0.2),    # Posición de la leyenda (x, y) o 'loc' de matplotlib
    ajustar_pos_leyenda=0.0,    # Espacio extra para la leyenda
    num_columnas_leyenda=None,          # Cantidad de columnas en las que se organiza la leyenda.
    tam_letra_leyenda=12,       # Tamaño de letra para la leyenda
    peso_letra_leyenda='medium', # Grosor de letra para la leyenda
    color_letra_leyenda='#434343', # Color de letra para la leyenda
    ascendente_leyenda=True,    # Orden ascendente de la leyenda (True) o invertido (False)


    # --- EJE X ---
    tam_valor_ejex=14,          # Controla el tamaño de la fuente para las etiquetas de los valores o categorías del eje X (tick labels).
    peso_valor_ejex='medium', # Define el grosor o estilo de la fuente para las etiquetas del eje X. Admite valores típicos de Matplotlib como 'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black'.
    color_valor_ejex="#434343", # Establece el color del texto para las etiquetas del eje X. Acepta nombres de colores de Matplotlib, colores CSS o códigos HEX (ej. '#434343').
    espacio_inicio=0,           # Margen artificial izquierdo en el plot para no pisar el eje Y.
    nombre_ejex=None,          # Título de eje X/Y.
    tam_nombre_ejex=14,  # Tamaño de letra para nombre del eje x
    peso_nombre_ejex='medium', # Grosor de letra para nombre del eje x
    color_nombre_ejex='#434343', # Color de letra para nombre del eje x
    sustituir_valor_ejex=None,   # Lista para sustituir etiquetas del eje x
    orientacion_valor_ejex=0,    # Grados (-90, -45, 0, 45, 90) para valores o texto mostrado en el eje X. 0 para horizontal y 90 para vertical. Cuando las etiquetas no caben de forma horizontal un angulo de 35 grados suele ser una buena opción.
    ajustar_sep_abajo_ejex=0.0,      # Aumenta separación en eje x
    resaltar_valor_ejex=None,    # Fechas/Keywords en el eje X para colorear ticklabels especiales de otro color.
    color_resaltado_ejex="#a3173e", # Color para el resaltado de etiquetas
    color_borde_resaltado_ejex='none', # Color del borde de resaltado de etiquetas
    modalidad_fechas=1,      # Modalidad con la que se muestran las fechas. El valor de 1 corresponde a una fecha con formato corto (ej. "ene"). El valor de 2 corresponde a una fecha con formato largo (ej. "enero"). El valor 2 no esta disponible para todos los formatos de fechas.
    mostrar_solo_fechas=None,   # Aplicar un subsample en fechas continuas, ej. año par.


    # --- EJE Y ---
    tam_valor_ejey=14,          # Tamaño de letra para etiquetas eje Y
    peso_valor_ejey='medium', # Grosor de letra para etiquetas eje Y
    color_valor_ejey="#434343", # Color de letra para etiquetas eje Y
    nombre_ejey=None,          # Nombre del eje y
    tam_nombre_ejey=14,  # Tamaño de letra para nombre del eje y
    peso_nombre_ejey='medium', # Grosor de letra para nombre del eje y
    color_nombre_ejey='#434343', # Color de letra para nombre del eje y
    limites_ejey=None,              # (min, max). Forzar límites del eje Y. Si es None, se ajusta automáticamente.
    solo_ejey_positivo=True,        # Eje Y solo muestra valores positivos
    divisiones_ejey=False,             # Forzar número de divisiones en el eje Y. Es util para cuando los valores son muy grandes y no caben en el eje Y.
    simbolo_porce_ejey=False,      # Añadir símbolo de porcentaje en el eje Y
    sustituir_etiquetas_ejey=None, # Lista para sustituir etiquetas del eje y


    # --- LÍNEAS ---
    columnas_lineas=None,       # Posiciones de las columnas (iniciando en 1) mapeadas como series Plot/Line que atraviesan los centros top de las barras.
    colores_lineas=None, # Colores de estas líneas de tendencia superpuestas.
    capsu_fin_lineas=False,     # Agrega una capsula al final de la linea con el valor del ultimo punto de la linea.
    poligono_zoom=False,        # Dibujar un polígono de zoom al final de la gráfica
    posiciones_poligono_zoom=None, # Personalizar vértices del polígono: [(vertice, x, y), ...]
    opacidad_poligono_zoom=None, # Controlar la opacidad del polígono de zoom
):
    """
    Genera un gráfico de barras verticales (apiladas si hay múltiples columnas) altamente personalizable.
    Ideal para comparar cantidades a lo largo del tiempo, por categorías, o para mostrar la composición
    de un total mediante barras apiladas.

    INFORMACIÓN PARA LA IA Y USUARIOS:
    Esta función está optimizada para generar gráficos de calidad de publicación. Las etiquetas, colores
    y tamaños son totalmente ajustables. Las cápsulas (rectángulos redondeados) en la cima de cada barra
    suman el total de sus componentes en la pila. Existen parámetros para resolver la colisión de etiquetas.

    ESTRUCTURA DEL DATAFRAME `df`:
    1. La primera columna SIEMPRE debe ser el eje X (las categorías de las barras o las fechas).
       Si son fechas/años, pueden ser procesadas para formato si se envían como tipo entero o datetime.
    2. Las columnas siguientes serán consideradas como los valores apilados (segmentos) de las barras.
    3. Excepciones: columnas indicadas en `sustituir_valores_barra`, `sustituir_valores_capsu`, o
       `columnas_lineas` serán extraidas antes de calcular las sumas, por lo que no deben ser 
       confundidas con valores regulares a apilar.

    FORMATO DE COLUMNA DE FECHAS (EJE X):
    - Puede ser enteros (ej. 2018, 2019, 2020) en el rango 1900-2100. La función los convertirá a datetime internamente.
    - Pueden ser cadenas o Timestamp, que interactúan con `modalidad_fechas` y `mostrar_solo_fechas`
      usando la función externa `formato_fechas`.
    
    Parámetros:
    
    --- GRÁFICA GENERAL ---
    df (pandas.DataFrame) : DataFrame de entrada con la estructura especificada arriba.
    nombre (str) : Nombre base para archivos de salida (.png y .svg se exportarán).
    tipo_letra (str) : Tipo de letra, por defecto 'Montserrat'.
    colores (list) : Lista de colores en HEX o nombres CSS para las series a apilar.
    ancho (float/int) : Ancho de la figura en centímetros.
    alto (float/int) : Alto de la figura en centímetros. 
    grillas (bool) : Activar/desactivar grillas horizontales de fondo.
    fondo (str) : Color de fondo. Puede ser 'transparent', 'white' o cualquier código HEX (ej. '#FF0000').
    decimales (int) : Número de decimales forzados en los valores dentro y fuera de la barra.
    mostrar (bool) : Si True, usa plt.show() al final.
    guardar (bool) : Si True, guarda los resultados vía savefig().

    --- MODIFICACIONES ÚTILES ---
    ordenar (str/None) : 'x' ordena la variable independiente, 'y' por suma total de barra, None preserva orden.
    ascendente (bool) : Si es True ordena los nuumeros o las etiquetas de forma ascendente, de lo contrario los ordena de forma descendente.
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
    asignar_etiquetas (str) : Nombre de columna para sustituir las etiquetas base de X con textos listos para display.
    unir_izq / unir_der (int) : Suma (agrupa) las primeras (izq) o últimas (der) 'n' filas y las condensa en una barra "Otros", reduciendo ruido.
    nombres_columnas (list) : Lista para renombrar las columnas tras remover metadatos.
    posiciones_columnas (list) : Índices 1-based para reordenar cómo se apilan las barras de abajo hacia arriba.
    respecto_porce (bool) : Si True, convierte las barras apiladas al 100% de la altura, representando share (participación).

    --- CATEGORÍAS Y AGRUPACIÓN ---
    columna_categorias (int) : Índice 1-based de la columna de categorías de agrupamiento para las barras. Modifica el color por categoría.
    colores_categorias (list) : Paleta de colores aplicada a los grupos de columnas cuando `columna_categorias` está activo.
    leyenda_categorias (bool/str) : Activa o nombra la leyenda de categorías.
    posicion_leyenda_categorias (tuple) : (x, y) de la leyenda.
    num_columnas_categorias (int) : Columnas de leyenda.
    ajustar_sep_grupos (float) : Espacio artificial creado entre cambios de categoría grupal.

    --- BARRAS ---
    ancho_barra (float) : 0 a 1 indicando grosor relativo de las barras (0.85 default).
    estilo_grafica (str) : Forma de dibujar las columnas del DataFrame.
        - 'apiladas' (default): cada columna se apila sobre la anterior y la cápsula muestra el total de la pila.
        - 'agrupadas': cada columna se dibuja como una barra independiente, una al lado de otra, repartiendo
          el espacio que ocuparía la barra apilada (`ancho_barra`). Todas arrancan desde cero, el eje Y se
          escala al valor individual mayor y se dibuja una cápsula por barra con su propio valor (en lugar
          de una sola cápsula con el total). `sustituir_valores_capsu` no aplica en este modo porque su
          valor corresponde al total de la fila.
    sep_barras_agrupadas (float) : Separación entre las barras de un mismo grupo, de 0 a 1. Solo tiene efecto
        con `estilo_grafica='agrupadas'` y más de una columna de barras; en cualquier otro caso se ignora.
        Es la fracción del espacio asignado a cada barra que se convierte en hueco: 0 (default) las deja
        pegadas, 0.2 deja un hueco pequeño, 0.5 adelgaza las barras a la mitad. Los centros de las barras
        no se mueven, así que el grupo conserva su ancho total y no invade a los grupos vecinos.
    capsulas_alineadas (bool) : Solo tiene efecto con `estilo_grafica='agrupadas'`; en cualquier otro caso
        se ignora. Con False (default) cada cápsula se coloca encima de su propia barra. Con True todas las
        cápsulas de un grupo se centran en el mismo punto del eje X (el centro del grupo) y se apilan una
        sobre otra, leyéndose de arriba hacia abajo en el orden de las columnas del DataFrame. El alto de
        cada cápsula se mide sobre la figura ya renderizada, así que el apilado no se superpone sea cual sea
        el tamaño de letra; el eje Y se amplía automáticamente para que la pila quepa dentro de la gráfica
        (salvo que se hayan fijado `limites_ejey` o `sustituir_etiquetas_ejey`). Cada cápsula conserva el
        color de su barra, que es lo que permite identificarlas al perder la referencia horizontal.
    tam_valor_barra (int/float) : Tamaño letra etiqueta valor barra.
    peso_valor_barra (str) : Grosor de la fuente del valor numérico absoluto mostrado en la barra. Puede ser 'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black'.
    color_valor_barra (str/None) : Color del texto para el valor absoluto. Puede pasarse como nombre, HEX (ej. '#FFFFFF') o None para cálculo de contraste automático con el fondo.
    tam_porce_barra (int/float) : Tamaño de la letra exclusivamente para el texto del porcentaje mostrado en la barra.
    peso_porce_barra (str) : Grosor de la fuente del porcentaje. Admite valores de matplotlib como 'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black'.
    color_porce_barra (str/None) : Color del texto para el porcentaje. Puede ser None (usará el predeterminado) o un código HEX/CSS.
    areamin (int/float) : Umbral mínimo para ocultar u obligar al texto posicionarse afuera de la barras por falta de espacio dentro de ellas.
    opcion_areamin (str) : 'fuera' para mover el texto asociado a valor_barra y porce_barra afuera de la barra, entre la barra y la cápsula. 'sin etiquetas' para ocultar el texto dentro de las barras.
    valor_barra (bool) : Muestra el valor numérico correspondiente a la barra o al segmento de barra apilado.
    valor_barra_cero (bool) : Muestra los ceros de los valores dentro de las barras aunque sea cero en todos los valores.
    porce_barra (bool) : Muestra porcentaje que representa el segmento de barra respecto a la barra total apilada en la que se encuentra.
    porce_abajo (bool) : Pone el porcentaje debajo del valor (si ambos están activos).
    porce_diver (bool) : Porcentaje divergente. En este caso el porcentaje se calcula respecto a suma absoluta de los segmentos de barras positivas (arriba del eje X) y negativas (abajo del eje Y).
    alinear_texto_barra (bool) : Cuando es True alinea el texto dentro de la barra verticalmente (en la misma direccion a la que apunta la barra).
    simbolo_porce_barra (bool) : Cuando es True añade el símbolo de porcentaje a los valores de las barra.
    simbolo_negativo (bool) : Cuando es True añade símbolo negativo a texto.
    sustituir_valores_barra (list/None) : Lista de strings (nombres de columnas) en el DataFrame que contienen textos personalizados para sobreescribir las etiquetas predeterminadas dentro de las barras. Al declarar estas columnas aquí, la función las extraerá previniendo que se interpreten erróneamente como barras apilables y las usará como etiquetas.
    sustituir_valores_capsu (int/None) : Índice (1-based) de una columna en el DataFrame que contiene los valores o textos que se desean mostrar en la cápsula superior. Si se proporciona, la función extraerá esta columna, evitará que se grafique como una barra apilada y en su lugar la usará directamente para etiquetar la cápsula (anulando el cálculo automático de suma).

    --- CÁPSULAS (Total encima de la barra) ---
    valor_capsu (bool) : Mostrar globo que encapsula la suma total de apilados arriba de la barra.
    tam_valor_capsu (int/float) : Tamaño de la fuente (letras o números) para el texto mostrado dentro de la cápsula.
    peso_valor_capsu (str) : Grosor o estilo de la fuente para el texto dentro de la cápsula. Admite valores como 'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black'.
    color_valor_capsu (str/None) : Color del texto dentro de la cápsula. Puede pasarse como nombre, código HEX o None (default).
    color_borde_capsu (str/None) : Color del borde de la cápsula.
    peso_borde_capsu (float/None) : Grosor del borde de la cápsula. Admite valores como 'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black'.
    curvatura_capsu (float) : 0 a 1 que redondea los bordes.
    color_fondo_capsu (str) : Color de relleno o fondo interno de la cápsula (ej. '#FFFFFF', 'white' o 'none' para transparente).
    activar_cambiar_color (bool) : Si es True, aplica automáticamente un contorno o ajuste de color al texto interno para garantizar contraste y máxima legibilidad contra el respectivo fondo.
    opcion_cambiar_color (str) : 'margen' para aplicar un contorno alrededor del texto o 'cambio' para modificar directamente el color del texto aumentando su contraste.
    quitar_capsu (bool) : Elimina la visualización de la cápsula.
    capsu_cero (bool) : Mantener el '0' si la barra mide cero.
    ajustar_pos_capsu (float) : Ajusta la posición vertical de la cápsula respecto al tope de la barra. Es un multiplicador que se calcula como una proporción de la escala máxima del gráfico para desplazar la cápsula más arriba o más abajo.
    ajustar_pos_capsu_areamin (float) : Ajuste vertical adicional que desplaza la cápsula (lado positivo) cuando `opcion_areamin='fuera'` mueve etiquetas fuera de la barra. Este desplazamiento es acumulativo y proporcional al número de etiquetas desplazadas por estar debajo del área mínima, previniendo sobreposiciones.
    ajustar_pos_capsu_neg (float/None) : Ajuste de posición vertical exclusivo para las cápsulas de valores negativos (parte inferior del eje cero). Permite separación independiente de la positiva. Si es None, adoptará automáticamente el valor de `ajustar_pos_capsu`.
    ajustar_pos_capsu_neg_areamin (float/None) : Ajuste vertical adicional para evitar sobreposiciones de la cápsula negativa con etiquetas desplazadas hacia afuera (`opcion_areamin='fuera'`). Si es None, tomará el valor definido en `ajustar_pos_capsu_areamin`.

    --- PORCENTAJES TOTALES ---
    porce_total (bool) : Muestra cuánto aporta cada conjunto de barras apiladas en un mismo valor (o posición) del eje X respecto a la suma de todas las barras (en todas las posiciones del eje X) de la gráfica.
    porce_total_inicio (bool): Mostrar el valor asociado a porce_total en el inicio de la barra (abajo del eje X) en lugar de la parte superior de la barra.

    --- LEYENDA (Series / Segmentos apilados) ---
    leyenda (bool/str) : Cuando es True, muestra la leyenda de las variables.
    posicion_leyenda (tuple/str/dict) : Define la ubicación de la leyenda. Principalmente se usa una tupla `(x, y)` donde las coordenadas corresponden a la ubicación espacial relativa a la figura (axes fraction): `x=0` es el borde izquierdo, `x=1` el borde derecho, `x=0.5` el centro horizontal. De manera similar `y=1` es el tope superior, `y=0` la base (eje X) y valores negativos bajan la leyenda por debajo del gráfico (útil para que no estorbe el contenido). También admite un string 'loc' clásico de `plt.legend` (ej. 'best', 'upper right') o un dict con kwargs.
    num_columnas_leyenda (int) : Cantidad de columnas en las que se organiza la leyenda.

    --- EJES X y Y ---
    tam_valor_ejex (int/float) : Controla el tamaño de la fuente para las etiquetas de los valores o categorías del eje X (tick labels).
    color_valor_ejex (str) : Establece el color del texto para las etiquetas del eje X. Acepta nombres de colores de Matplotlib, colores CSS o códigos HEX (ej. '#434343').
    peso_valor_ejex (str) : Define el grosor o estilo de la fuente para las etiquetas del eje X. Admite valores típicos de Matplotlib como 'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black'.
    espacio_inicio (float) : Margen artificial izquierdo en el plot para no pisar el eje Y.
    nombre_ejex/ejey ... : Título de eje X/Y.
    orientacion_valor_ejex (float) : Grados (-90, -45, 0, 45, 90) para valores o texto mostrado en el eje X. 0 para horizontal y 90 para vertical. Cuando las etiquetas no caben de forma horizontal un angulo de 35 grados suele ser una buena opción.
    resaltar_valor_ejex (list) : Fechas/Keywords en el eje X para colorear ticklabels especiales de otro color.
    modalidad_fechas (int) : Modalidad con la que se muestran las fechas. El valor de 1 corresponde a una fecha con formato corto (ej. "ene"). El valor de 2 corresponde a una fecha con formato largo (ej. "enero"). El valor 2 no esta disponible para todos los formatos de fechas. 
    mostrar_solo_fechas (list) : Aplicar un subsample en fechas continuas, ej. año par.
    limites_ejey (tuple/None) : (min, max). Forzar límites del eje Y. Si es None, se ajusta automáticamente.
    divisiones_ejey (int/bool) : Forzar número de divisiones en el eje Y. Es util para cuando los valores son muy grandes y no caben en el eje Y.

    --- LÍNEAS SUPERPUESTAS ---
    columnas_lineas (list) : Posiciones de las columnas (iniciando en 1) mapeadas como series Plot/Line que atraviesan los centros top de las barras.
    colores_lineas (list) : Colores de estas líneas de tendencia superpuestas.
    capsu_fin_lineas (bool) : Agrega una capsula al final de la linea con el valor del ultimo punto de la linea.
    poligono_zoom (bool) : Dibuja un polígono gris que une la última barra con el borde derecho de la figura, como guía visual hacia un detalle o acercamiento colocado a un lado de la gráfica.
    posiciones_poligono_zoom (list) : Personaliza los vértices del polígono con una lista de tuplas `(vertice, x, y)`. Los vértices 1, 2 y 3 (los que tocan la última barra) van en coordenadas de los datos; los vértices 4 y 5 (los del lado derecho) en proporciones de la figura, de 0.0 a 1.0.
    opacidad_poligono_zoom (float) : Opacidad del polígono, de 0.0 a 1.0. Por defecto 0.4.
    
    EJEMPLO DE DATAFRAME VÁLIDO:
    | Año  | Ingresos | Costos | Otros_gastos |
    |------|----------|--------|--------------|
    | 2021 | 150.5    | 80.2   |     45.96    | 
    | 2022 | 165.0    | 90.5   |     56.72    |
    
    NOTAS DE EJECUCIÓN IA (Accionables):
    1. Usar `asignar_etiquetas` para modificar los labels del eje X sin alterar los datos crudos.
    2. Agrupar ruido visual (variables irrelevantes o muy pequeñas) usando int `unir_der=N` para condensar.
    3. Cuando `areamin` detecta poco espacio para el texto, `opcion_areamin='fuera'` colocará los números en el exterior.
    4. Cuidar qué columnas se incluyen en el DataFrame. Las referenciadas como metadatos explícitos no se apilarán.
    """
    # --- 1. CONFIGURACIÓN INICIAL ---
    # Variable para detectar si se añaden anotaciones que requieran espacio extra.
    hay_annotations_externas = False
    # Espacio sin ruptura para el formato de texto.
    espacio = "\u00A0"

    #     # --- INTEGRACIÓN DE RENOMBRADO Y REORDENAMIENTO ---
    # if nuevos_nom_col is not None and posiciones_columnas is not None:
    #     df = renombra_y_ordena_col(df, nuevos_nom_col, posiciones_columnas)

    # Diccionario para centralizar la configuración de fuentes.
    font_config = {
        'family': tipo_letra,
        'variable_x': {'size': tam_valor_ejex, 'weight': peso_valor_ejex, 'color': color_valor_ejex},
        'variable_y': {'size': tam_valor_ejey, 'weight': peso_valor_ejey, 'color': color_valor_ejey},
        'nombre_ejex': {'size': tam_nombre_ejex, 'weight': peso_nombre_ejex, 'color': color_nombre_ejex},
        'nombre_ejey': {'size': tam_nombre_ejey, 'weight': peso_nombre_ejey, 'color': color_nombre_ejey},
        'valor_capsula': {'size': tam_valor_capsu, 'weight': peso_valor_capsu, 'color': color_valor_capsu},
        'valor_porcentaje_barra': {'size': tam_valor_barra, 'weight': peso_valor_barra, 'color': color_valor_barra},
        'valor_porcentaje_barra_porcentaje': {'size': tam_porce_barra, 'weight': peso_porce_barra, 'color': color_porce_barra},
        'porcentaje_total': {'size': tam_porce_total, 'weight': peso_porce_total, 'color': color_porce_total},
        'leyenda': {'size': tam_letra_leyenda, 'weight': peso_letra_leyenda, 'color': color_letra_leyenda}
    }

    import matplotlib.pyplot as plt
    # Configuración para que el texto en SVG sea editable.
    plt.rcParams['svg.fonttype'] = 'none'
    # Carga de fuentes personalizadas desde la carpeta de fuentes.
    import inspect
    try:
        current_dir = Path(__file__).resolve().parent
    except NameError:
        try:
            current_dir = Path(inspect.getfile(inspect.currentframe())).resolve().parent
        except TypeError:
            current_dir = Path.cwd() / "1_funciones"
            
    font_dirs = [current_dir.parent / "0_fonts"]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

    # Asignación de paleta de colores por defecto si no se proporciona una.
    colores_asignados = list(colores) if colores is not None else ["#10302C", "#4C6A67", "#8FA8A6", "#A3C9A8"]

    # --- 2. PREPARACIÓN DE DATOS ---
    # Validación de que el input es un DataFrame.
    if not isinstance(df, pd.DataFrame):
        raise ValueError("El argumento df debe ser un DataFrame de pandas.")

    if ordenar not in ['x', 'y', None]:
        raise ValueError("El argumento 'ordenar' solo acepta 'x', 'y' o None.")

    if not isinstance(ascendente, bool):
        raise ValueError("El argumento 'ascendente' solo acepta True o False.")

    if opcion_cambiar_color not in ['margen', 'cambio']:
        raise ValueError("El argumento 'opcion_cambiar_color' solo acepta 'margen' o 'cambio'.")

    # Copia inicial del DataFrame para evitar modificar el original en cualquier operación.
    # En Jupyter Notebooks, usar copy(deep=True) asegura que no haya referencias mutables residuales.
    df = df.copy(deep=True)

    # --- RESOLVER NOMBRES DE COLUMNAS LÍNEAS ---
    columnas_lineas_indices = []
    if columnas_lineas is not None:
        if isinstance(columnas_lineas, int):
            columnas_lineas = [columnas_lineas]
        nuevas_lineas = []
        for pos in columnas_lineas:
            if not isinstance(pos, int) or pos < 1:
                raise ValueError("Las posiciones en columnas_lineas deben ser enteros mayores o iguales a 1.")
            if pos > len(df.columns):
                raise ValueError(f"El índice {pos} en columnas_lineas está fuera de rango para el DataFrame con {len(df.columns)} columnas.")
            nuevas_lineas.append(df.columns[pos - 1])
            columnas_lineas_indices.append(pos - 1)
        columnas_lineas = nuevas_lineas

    # Para aislar problemas de ejecución repetida, creamos la figura explícitamente nueva aquí
    # en lugar de depender del caché subyacente.
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    
    plt.rcParams['svg.fonttype'] = 'none'

    # --- RESOLVER NOMBRE DE COLUMNA PARA CATEGORIZACIÓN ---
    # Se hace al inicio para usar el índice del DF original antes de que otras operaciones (como sustituir_valores_capsu) eliminen columnas
    nom_col_categoria = None
    if columna_categorias is not None:
        if not isinstance(columna_categorias, int) or columna_categorias < 1:
            raise ValueError("columna_categorias debe ser un entero mayor o igual a 1.")
        if columna_categorias > len(df.columns):
            raise ValueError(f"El índice {columna_categorias} está fuera de rango para el DataFrame con {len(df.columns)} columnas.")
        
        # Obtener el nombre de la columna usando el índice (ajustado a 0-based)
        nom_col_categoria = df.columns[columna_categorias - 1]

    # --- LÓGICA PARA SUSTITUIR VALORES CÁPSULA ---
    capsule_series = None
    if sustituir_valores_capsu is not None:
        if not isinstance(sustituir_valores_capsu, int) or sustituir_valores_capsu < 1:
             raise ValueError("sustituir_valores_capsu debe ser un entero mayor o igual a 1.")
        if sustituir_valores_capsu > len(df.columns):
             raise ValueError(f"El índice {sustituir_valores_capsu} está fuera de rango para el DataFrame con {len(df.columns)} columnas.")
        
        col_idx = sustituir_valores_capsu - 1
        # Extraer la serie con el índice del dataframe original
        capsule_series = df.iloc[:, col_idx].copy()
        
        # Si NO se va a renombrar/reordenar, eliminamos la columna ya
        if nombres_columnas is None and posiciones_columnas is None:
            # Eliminar por nombre para ser seguro
            col_name = df.columns[col_idx]
            df = df.drop(columns=[col_name])

    # --- PRIMERO: Extraer categorías para colorear antes de cualquier otra manipulación ---
    mapa_color_categoria = None
    if nom_col_categoria and nom_col_categoria in df.columns:
        # Obtener categorías únicas y asignarles un color de la paleta
        if colores_categorias:
            colores_cat_asignados = list(colores_categorias)
        else:
            colores_cat_asignados = [
                "#1F618D", "#A04000", "#117864", "#7D3C98", "#B7950B", "#34495E", 
                "#922B21", "#2874A6", "#5B2C6F", "#717D7E", "#1B4F72", "#239B56"
            ]
        
        categorias_unicas = df[nom_col_categoria].unique()
        # Ordenar categorías para asegurar consistencia en los colores entre ejecuciones
        try:
            categorias_unicas = sorted(categorias_unicas)
        except TypeError:
            categorias_unicas = sorted(categorias_unicas, key=lambda x: str(x))
            
        mapa_color_categoria = {cat: colores_cat_asignados[i % len(colores_cat_asignados)] for i, cat in enumerate(categorias_unicas)}
        
        # Crear un mapeo del índice del DataFrame a su color de categoría
        df['__color_categoria'] = df[nom_col_categoria].map(mapa_color_categoria)
        
        # Eliminar la columna de categorías original para que no se grafique
        df = df.drop(columns=[nom_col_categoria])

    # --- SEGUNDO: Aplicar renombrado y reordenamiento si se especifica ---
    if posiciones_columnas is not None:
        if nombres_columnas is None:
            nombres_columnas = list(df.columns)

        # Si tenemos capsule_series, necesitamos saber si la columna original sobrevivió para borrarla
        col_survived_name = None
        if sustituir_valores_capsu is not None:
             col_idx = sustituir_valores_capsu - 1
             # Verificar si el índice (1-based) está en posiciones_columnas
             if (col_idx + 1) in posiciones_columnas:
                 col_survived_name = nombres_columnas[col_idx]

        # Actualizar nombres en columnas_lineas a los nuevos nombres correspondientes a sus posiciones originales
        if columnas_lineas is not None and nombres_columnas is not None:
            columnas_lineas = [nombres_columnas[idx] for idx in columnas_lineas_indices]

        df = renombra_y_ordena_col(df, nombres_columnas, posiciones_columnas)
        
        if col_survived_name and col_survived_name in df.columns:
            df = df.drop(columns=[col_survived_name])

    # AÑADIR LA SERIE DE CÁPSULAS AL DATAFRAME (para que se alinee con el índice)
    if capsule_series is not None:
        # Aseguramos que el índice coincida si no se ha cambiado
        df['__capsule_values__'] = capsule_series

    # Se asume que la primera columna es el eje X.
    categorias_x = df.columns[0]
    # Conversión de años (enteros) a formato de fecha si aplica.
    if pd.api.types.is_integer_dtype(df[categorias_x]) and df[categorias_x].between(1900, 2100).all():
        df[categorias_x] = pd.to_datetime(df[categorias_x], format='%Y')
    # Establecer la primera columna como índice del DataFrame.
    df = df.set_index(categorias_x)

    # --- ELIMINAR COLUMNAS DE sustituir_valores_barra ANTES DE CÁLCULOS NUMÉRICOS ---
    textos_personalizados_barra = None
    if sustituir_valores_barra is not None:
        # Verificar qué columnas existen realmente en el DataFrame
        columnas_existentes = [col for col in sustituir_valores_barra if col in df.columns]
        # Guardar los textos personalizados antes de eliminar las columnas
        textos_personalizados_barra = df[columnas_existentes].copy()
        # Eliminar esas columnas del DataFrame ANTES de cualquier cálculo numérico
        df = df.drop(columns=columnas_existentes)

    # Extraer la columna de color si existe y luego eliminarla
    colores_por_barra = None
    if '__color_categoria' in df.columns:
        colores_por_barra = df['__color_categoria'].copy()
        df = df.drop(columns=['__color_categoria'])

    # Unión de barras si se especifica.
    df, etiqueta_union_izq = unir_barras(df, unir_izq, 'izquierda')
    df, etiqueta_union_der = unir_barras(df, unir_der, 'derecha')

    # Diccionarios para almacenar personalizaciones de datos agregados.
    etiquetas_personalizadas = {}
    textos_barra_personalizados = {}
    colores_fondo_personalizados = {}
    colores_borde_personalizados = {}
    estilos_borde_personalizados = {}
    grosores_borde_personalizados = {}
    colores_texto_personalizados = {}
    datos_para_separadores = []

    # Diccionarios para almacenar categorías agregadas que deben ir a los extremos.
    categorias_agregadas_izq = []
    categorias_agregadas_der = []

    # Procesamiento de datos adicionales para agregar a la gráfica.
    if agregar_datos:
        filas_izq = []
        filas_der = []
        for item in agregar_datos:
            etiqueta, texto_barra, opciones_extra = None, None, {}
            
            # Desempaquetado flexible de los datos adicionales.
            if len(item) == 2:
                categoria, valor = item
            elif len(item) == 3:
                categoria, etiqueta, valor = item
            elif len(item) == 4:
                categoria, etiqueta, valor, texto_barra = item
            elif len(item) == 5:
                categoria, etiqueta, valor, texto_barra, opciones_extra = item

            # Almacenamiento de las opciones de personalización.
            if etiqueta:
                etiquetas_personalizadas[categoria] = etiqueta
            if texto_barra:
                textos_barra_personalizados[categoria] = texto_barra
            if isinstance(opciones_extra, dict):
                if 'colores_fondo' in opciones_extra:
                    colores_fondo_personalizados[categoria] = opciones_extra['colores_fondo']
                if 'colores_borde' in opciones_extra:
                    colores_borde_personalizados[categoria] = opciones_extra['colores_borde']
                if 'estilos_borde' in opciones_extra:
                    estilos_borde_personalizados[categoria] = opciones_extra['estilos_borde']
                if 'grosores_borde' in opciones_extra:
                    grosores_borde_personalizados[categoria] = opciones_extra['grosores_borde']
                if 'colores_texto' in opciones_extra:
                    colores_texto_personalizados[categoria] = opciones_extra['colores_texto']
                # separador_derecha significa: poner separador a la derecha de esta barra (después de ella visualmente)
                # Por eso la posición debe ser 'despues' para que se inserte después de esta categoría
                if 'separador_derecha' in opciones_extra:
                    datos_para_separadores.append({'posicion': 'despues', 'referencia': categoria, 'texto': opciones_extra['separador_derecha']})
                # separador_izquierda significa: poner separador a la izquierda de esta barra (antes de ella visualmente)
                if 'separador_izquierda' in opciones_extra:
                    datos_para_separadores.append({'posicion': 'antes', 'referencia': categoria, 'texto': opciones_extra['separador_izquierda']})

            # --- REORDENAMIENTO DE VALORES AGREGADOS ---
            if posiciones_columnas is not None and isinstance(valor, (list, tuple, np.ndarray)):
                # Reordenar valor según posiciones_columnas
                try:
                    valor = [valor[i-1] for i in posiciones_columnas]
                except IndexError:
                    pass
                
                # Si hay una columna de cápsula que fue eliminada del DF, también debemos eliminarla de valor
                if sustituir_valores_capsu is not None and sustituir_valores_capsu in posiciones_columnas:
                    try:
                        idx_capsu = posiciones_columnas.index(sustituir_valores_capsu)
                        if isinstance(valor, tuple): valor = list(valor)
                        elif isinstance(valor, np.ndarray): valor = valor.tolist()
                        valor.pop(idx_capsu)
                    except (ValueError, IndexError):
                        pass

            # Creación de la fila de datos como una Serie de pandas.
            fila = pd.Series(dict(zip(df.columns, valor)) if isinstance(valor, (list, tuple, np.ndarray)) else {col: valor if i == 0 else 0 for i, col in enumerate(df.columns)}, name=categoria)
            
            # Decidir si va a la izquierda o derecha basado en el separador.
            if isinstance(opciones_extra, dict) and 'separador_derecha' in opciones_extra:
                categorias_agregadas_izq.append(categoria)
                filas_izq.append(fila)
            else:
                categorias_agregadas_der.append(categoria)
                filas_der.append(fila)

        # Concatenación de las nuevas filas al DataFrame principal.
        if filas_izq:
            df_izq = pd.DataFrame(filas_izq)
            df = pd.concat([df_izq, df])
        if filas_der:
            df_der = pd.DataFrame(filas_der)
            df = pd.concat([df, df_der])

    # Manejo de etiquetas personalizadas para las cápsulas.
    etiquetas_finales = None
    if asignar_etiquetas and asignar_etiquetas in df.columns:
        etiquetas_finales = df[asignar_etiquetas].copy()
        df = df.drop(columns=[asignar_etiquetas])

    # Guardar los nombres de las categorías (columnas de valores).
    categorias = df.columns

    # --- 3. ORDENAMIENTO Y AGRUPAMIENTO DE DATOS ---
    # Calcular suma por fila para ordenamiento
    cols_lineas_safe = columnas_lineas if columnas_lineas is not None else []
    lista_cols_suma = [c for c in df.columns if c not in cols_lineas_safe and c != '__capsule_values__' and c != '__color_categoria']
    df['_sum_for_sort'] = df[lista_cols_suma].sum(axis=1)

    # Identificar filas fijas (extremos)
    izq_fijos = ([etiqueta_union_izq] if etiqueta_union_izq else []) + categorias_agregadas_izq
    der_fijos = [cat for cat in categorias_agregadas_der if any(d['referencia'] == cat and d['posicion'] == 'antes' for d in datos_para_separadores)] + ([etiqueta_union_der] if etiqueta_union_der else [])
    
    # Obtener etiquetas únicas preservando orden de aparición (para stable sort)
    # y evitar explosión de datos por duplicados en .loc
    unique_indices = []
    seen = set()
    for idx in df.index:
        if idx not in seen:
            unique_indices.append(idx)
            seen.add(idx)
            
    # Filtrar etiquetas fijas que realmente existen en el DF
    u_izq = [idx for idx in izq_fijos if idx in seen]
    u_der = [idx for idx in der_fijos if idx in seen]    
    
    # Etiquetas centrales (no fijas)
    u_center = [idx for idx in unique_indices if idx not in u_izq and idx not in u_der]

    # Ordenar grupos centrales
    if ordenar == 'y':
        # Calcular suma TOTAL por grupo (etiqueta) para ordenar los grupos
        group_sums = df.groupby(level=0)['_sum_for_sort'].sum()
        # Ordenar lista de etiquetas u_center basada en sus sumas totales
        # Reindexamos group_sums solo con u_center para asegurar 1:1
        sums_center = group_sums.loc[u_center]
        u_center_sorted = sums_center.sort_values(ascending=ascendente).index.tolist()
        
    elif ordenar == 'x':
        # Ordenamiento robusto de etiquetas
        centro_ser = pd.Series(u_center)
        parsed = pd.to_datetime(centro_ser, errors='coerce')
        
        if parsed.notna().any():
            filled = parsed.fillna(pd.Timestamp.max)
            u_center_sorted = [x for _, x in sorted(zip(filled, u_center), key=lambda t: t[0])]
        else:
            tipos = set(type(idx) for idx in u_center)
            reverse_sort = not ascendente
            if len(tipos) > 1:
                u_center_sorted = sorted(u_center, key=lambda x: str(x), reverse=reverse_sort)
            else:
                u_center_sorted = sorted(u_center, reverse=reverse_sort)
    elif ordenar is None:
        # Mantener orden original (tal cual se proporciona en el dataframe df)
        u_center_sorted = u_center
    else:
        # Mantener orden original (opción no reconocida)
        u_center_sorted = u_center

    # Construir lista final de etiquetas de GRUPOS
    final_group_order = u_izq + u_center_sorted + u_der
    
    # Reconstruir el DataFrame agrupado y ordenado
    # Al hacer loc[lista_unica], Pandas trae TODAS las filas para cada etiqueta.
    # Esto agrupa visualmente las filas con mismo índice y evita duplicación exponencial.
    df = df.loc[final_group_order]
    
    # Limpieza columna temporal
    if '_sum_for_sort' in df.columns:
        df = df.drop(columns=['_sum_for_sort'])
    
    if colores_por_barra is not None:
        # Reordenar colores también (colores_por_barra tiene el mismo índice que df original)
        colores_por_barra = colores_por_barra.loc[final_group_order]

    # Inserción de filas espaciadoras si se definieron.
    if datos_para_separadores:
        # Nota: Con agrupamiento, los separadores se insertan entre grupos
        datos_para_separadores.sort(key=lambda x: x['posicion'] == 'antes', reverse=True)
        
        # Trabajamos sobre la lista de grupos (etiquetas únicas)
        groups_list = final_group_order.copy()
        
        separadores_to_add = [] # (index_pos, key, etiqueta)
        
        for sep_info in datos_para_separadores:
            try:
                if sep_info['referencia'] in groups_list:
                    idx_pos = groups_list.index(sep_info['referencia'])
                    insert_at = idx_pos if sep_info['posicion'] == 'antes' else idx_pos + 1
                    
                    idx_separador = f"__espaciador__{sep_info['referencia']}_{sep_info['posicion']}_{np.random.randint(1000)}"
                    etiquetas_personalizadas[idx_separador] = sep_info['texto']
                    
                    separadores_to_add.append((insert_at, idx_separador))
            except Exception as e:
                print(f"Advertencia: Error al añadir separador: {e}")
        
        # Ordenar inserciones por posición descendente para no alterar índices previos
        separadores_to_add.sort(key=lambda x: x[0], reverse=True)
        
        # Para insertar en el DF, lo más fácil es dividir y concatenar o usar append
        # Dado que ya ordenamos DF, podemos iterar e insertar.
        # Pero DF no es lista.
        # Estrategia: Crear dataframes de separadores y usar concat.
        
        df_list_chunks = []
        last_idx = 0
        
        # Mapa de label -> posiciones en final_group_order
        # No es trivial slicing directo por etiqueta en DF porque loc devuelve N filas.
        # Mejor estrategia: iterar unique groups y construir nuevo DF.
        
        new_df_parts = []
        
        # Re-scan groups list with separators inserted conceptually
        augmented_groups = list(final_group_order)
        for idx, key in separadores_to_add:
            augmented_groups.insert(idx, key)
            
        for group_key in augmented_groups:
            if "__espaciador__" in str(group_key):
                # Crear fila separadora
                fila_sep = pd.DataFrame({col: [0] for col in df.columns}, index=[group_key])
                new_df_parts.append(fila_sep)
            else:
                # Extraer grupo del DF actual (ya ordenado)
                # Usamos slice seguro o filtro. 
                # Como df ya está ordenado por final_group_order, podemos consumir iterador?
                # No, df.loc[group_key] funciona bien.
                parts = df.loc[[group_key]]
                new_df_parts.append(parts)
        
        df = pd.concat(new_df_parts)
        # Actualizar lista de categorías únicas visuales
        final_group_order = augmented_groups

    # --- 4. CÁLCULOS PARA LA GRÁFICA ---
    # Estilo de dibujo de las barras: 'apiladas' (una sobre otra) o 'agrupadas' (una al lado de otra).
    es_agrupada = str(estilo_grafica).strip().lower() in ('agrupadas', 'agrupada', 'agrupado', 'agrupados')

    # --- CÁLCULO DE DECIMALES ---
    # Recopilar todos los valores numéricos para determinar los decimales
    todos_los_valores = df.select_dtypes(include=np.number).values.flatten().tolist()
    
    # Determinar el número de decimales a usar
    num_dec = num_decimales(todos_los_valores, determinado=decimales)
    
    # Crear el formato de string basado en los decimales
    formato_decimal = f"{{:,.{num_dec}f}}"

    # Inicializar columnas_lineas como lista vacía si es None
    if columnas_lineas is None:
        columnas_lineas = []
    
    # Separar las columnas en barras y líneas
    columnas_barras = [col for col in df.columns if col not in columnas_lineas and col != '__capsule_values__']

    # Separación entre barras de un mismo grupo. Solo aplica en 'agrupadas' y cuando hay algo que separar.
    sep_agrupadas = min(max(float(sep_barras_agrupadas), 0.0), 0.95) if (es_agrupada and len(columnas_barras) > 1) else 0.0

    # Alineación de las cápsulas en el centro del grupo. Solo aplica en 'agrupadas'.
    capsulas_alineadas_activo = bool(capsulas_alineadas) and es_agrupada
    
    # Suma de valores por barra y total general (solo considerando columnas de barras)
    suma_total = df[columnas_barras].sum(axis=1) if columnas_barras else pd.Series(0, index=df.index)
    total_general = suma_total.sum()

    # Si se grafica respecto al porcentaje, se normalizan los datos a 100.
    df_plot = df.copy()
    if respecto_porce:
        suma_total_no_cero = suma_total.replace(0, np.nan)
        for col in columnas_barras:
            df_plot[col] = df[col].div(suma_total_no_cero, axis=0).multiply(100).fillna(0)
    
    # Detección y manejo de gráficos divergentes (con valores negativos).
    # Modificamos para considerar TODAS las columnas, no solo las barras
    es_divergente = (any(df[columnas_barras].min() < 0) if columnas_barras else False) or \
                   (any(df[columnas_lineas].min() < 0) if columnas_lineas else False)
    
    suma_positivos_por_barra = None
    suma_negativos_por_barra = None
    suma_absoluta_por_barra = None
    total_general_absoluto = None
    total_general_positivos = None
    if es_divergente:
        suma_negativos_por_barra = df[columnas_barras][df[columnas_barras] < 0].sum(axis=1)
        # --- INICIO DE CAMBIOS ---
        # Se calcula siempre que el gráfico sea divergente, para la lógica de las cápsulas.
        suma_positivos_por_barra = df[columnas_barras][df[columnas_barras] > 0].sum(axis=1)
        # --- FIN DE CAMBIOS ---
        if porce_diver:
            total_general_positivos = suma_positivos_por_barra.sum()
        else:
            suma_absoluta_por_barra = df[columnas_barras].abs().sum(axis=1)
            total_general_absoluto = suma_absoluta_por_barra.sum()

    # Cálculo de los límites del eje Y para escalar la gráfica correctamente.
    # Modificamos para considerar todas las columnas, no solo las que tienen barras
    todas_columnas = df.columns
    if es_agrupada:
        # En 'agrupadas' cada barra arranca desde cero, así que el tope lo marca el valor individual mayor.
        x_max_pos = df[df > 0].max().max()
        x_max_neg = df[df < 0].min().min()
    else:
        x_max_pos = df[df > 0].sum(axis=1).max()
        x_max_neg = df[df < 0].sum(axis=1).min()
    
    # También consideramos los valores mínimos de las líneas para el cálculo del mínimo
    min_lineas = df[columnas_lineas].min().min() if columnas_lineas else 0
    
    x_max = max(x_max_pos, abs(x_max_neg), abs(min_lineas) if min_lineas < 0 else 0) * 1.15
    if pd.isna(x_max):
        x_max = (df[columnas_barras].max().max() if es_agrupada and columnas_barras else suma_total.max()) * 1.15

    if respecto_porce:
        x_max = 100 * 1.15

    # --- 5. FORMATEO DE ETIQUETAS DEL EJE X ---
    entidades = df.index.values
    # Detección y formateo de fechas en el índice.
    es_fecha = any(isinstance(idx, (pd.Timestamp, np.datetime64)) for idx in df.index if idx not in [etiqueta_union_izq, etiqueta_union_der])
    if es_fecha:
        fechas_a_formatear = [idx for idx in df.index if isinstance(idx, (pd.Timestamp, np.datetime64))]
        mapa_fechas = dict(zip(fechas_a_formatear, formato_fechas(fechas_a_formatear, modalidad=modalidad_fechas, mostrar_solo=mostrar_solo_fechas)))
        entidades_formateadas = [mapa_fechas.get(idx, str(idx)) for idx in df.index]
    else:
        entidades_formateadas = [str(idx) for idx in df.index]

    # Sustitución de etiquetas del eje X si se proporciona una lista.
    if sustituir_valor_ejex:
        if len(sustituir_valor_ejex) != len(entidades_formateadas):
            raise ValueError("La longitud de 'sustituir_valor_ejex' debe coincidir con el número de barras.")
        entidades_formateadas = list(sustituir_valor_ejex)

    # Aplicación de etiquetas personalizadas de datos agregados.
    for i, entidad in enumerate(df.index):
        if entidad in etiquetas_personalizadas and etiquetas_personalizadas[entidad]:
            entidades_formateadas[i] = etiquetas_personalizadas[entidad]

    # Formateo de etiquetas para espaciadores.
    for i, entidad in enumerate(entidades_formateadas):
        if "__espaciador__" in str(df.index[i]):
            entidades_formateadas[i] = etiquetas_personalizadas.get(df.index[i], "...")

    # --- 6. CREACIÓN DE LA FIGURA Y EJES ---
    
    # --- CÁLCULO DE POSICIONES Y AGRUPAMIENTOS ---
    # Detectar grupos de etiquetas consecutivas idénticas
    posiciones = []
    anchos_barras = []
    grupos_visuales = [] # (label, [indices_originales])
    
    # Como el DF está ordenado de forma agrupada, podemos iterar secuencialmente
    if len(df) > 0:
        current_group_label = df.index[0]
        current_group_idx = 0
        current_group_count = 0
        
        # Primero identificamos los grupos y sus tamaños
        grouped_counts = [] # list of (label, count)
        
        last_label = None
        count = 0
        
        # Iterar sobre las etiquetas originales del DF (ya ordenadas)
        for label in df.index:
            if label != last_label and last_label is not None:
                grouped_counts.append((last_label, count))
                count = 0
            
            last_label = label
            count += 1
        grouped_counts.append((last_label, count))
        
        # Ahora calculamos posiciones
        x_cursor = 0
        tick_positions = []
        tick_labels = []
        
        # Iterador global para alinear con filas del DF
        df_row_idx = 0
        
        # Calcular el tamaño máximo de grupo para determinar el ancho fijo de barra individual
        max_group_count = max([c for _, c in grouped_counts]) if grouped_counts else 1
        
        # Calcular el ancho base del grupo (espacio total disponible para el grupo)
        # Se fija en 0.85 (valor por defecto estándar) o el ancho_barra si es mayor
        ancho_grupo_base = max(ancho_barra, 0.85)
        
        # Calcular el paso (stride) entre los centros de las barras
        step = ancho_grupo_base / max_group_count
        # Calcular el ancho visual de cada barra individual
        ancho_individual = ancho_barra / max_group_count
        
        for label, count in grouped_counts:
            # Calcular posición central para el grupo
            center_x = x_cursor
            tick_positions.append(center_x)
            
            # Usar la etiqueta formateada correspondiente a la primera fila de este grupo
            tick_labels.append(entidades_formateadas[df_row_idx])
            
            # Calcular posiciones de barras dentro del grupo
            # Se centra el grupo completo de ancho (count * step) en center_x
            total_group_width = count * step
            start_x = center_x - (total_group_width / 2) + (step / 2)
            
            for i in range(count):
                pos = start_x + (i * step)
                posiciones.append(pos)
                anchos_barras.append(ancho_individual)
            
            x_cursor += 1 + ajustar_sep_grupos
            df_row_idx += count
            
    else:
        posiciones = []
        anchos_barras = []
        tick_positions = []
        tick_labels = []

    posiciones = np.array(posiciones)
    anchos_barras = np.array(anchos_barras)

    valores = [df_plot[col].values for col in df_plot.columns]
    # posiciones ya calculado

    # Cálculo dinámico del ancho de la figura basado en la longitud de las etiquetas.
    # Usamos tick_positions que representa el nÃºmero visual de grupos
    longitudes = [len(f"{espacio*4}{int(total_valor):,}{espacio*4}") for total_valor in suma_total]
    moda_capsula_len = mode(longitudes) if longitudes else 10
    extra_width = moda_capsula_len * 0.1
    
    # Factor de expansión por espacio entre grupos (solo si es positivo para ampliar)
    factor_espacio = 1 + max(0, ajustar_sep_grupos)
    
    base_width = max(12, len(tick_labels) * extra_width * factor_espacio) # Usamos tick_labels en vez de entidades (filas)
    fig_width = ancho / 2.54 if ancho is not None else base_width
    fig_height = alto / 2.54 if alto is not None else fig_width / 2
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)

    # Fondo para la figura y los ejes.
    fig.patch.set_alpha(0 if fondo == 'transparent' else 1)
    ax.patch.set_alpha(0 if fondo == 'transparent' else 1)
    if fondo != 'transparent':
        fig.patch.set_facecolor(fondo)
        ax.patch.set_facecolor(fondo)

    # --- 7. DIBUJO DE BARRAS Y TEXTOS ---
    # Almacenar líneas para la leyenda
    line_handles = []
    line_labels = []
    
    # Para etiquetas fuera por areamin
    etiquetas_fuera = []

    # Cápsulas a repartir verticalmente al final, cuando capsulas_alineadas está activo
    capsulas_para_alinear = []

    # Iteración sobre cada barra para dibujarla y añadir textos.
    # Usamos enumerate para mantener el índice de fila y zip para las propiedades calculadas
    for idx_row, (pos, entidad, total_valor, ancho_indiv) in enumerate(zip(posiciones, entidades, suma_total, anchos_barras)):
        bottom_pos = 0
        bottom_neg = 0
        annotations_externas = []
        last_non_zero_idx = 0
        last_non_zero_idx_neg = 0
        etiquetas_fuera_fila = []

        # --- AGRUPADAS: reparto del espacio de la barra entre las columnas ---
        # El espacio que ocuparía la barra apilada (ancho_indiv) se divide en partes iguales,
        # una por columna, y cada columna se desplaza a su propia franja.
        n_cols_barras = max(1, len(columnas_barras))
        paso_seg = ancho_indiv / n_cols_barras
        # `sep_agrupadas` adelgaza cada barra dentro de su franja sin mover su centro:
        # así aparece el hueco entre barras y el grupo conserva su ancho total.
        ancho_seg = paso_seg * (1 - sep_agrupadas) if es_agrupada else ancho_indiv
        offsets_agrupadas = [(-ancho_indiv / 2) + paso_seg * (i + 0.5) for i in range(n_cols_barras)] if es_agrupada else [0] * n_cols_barras

        # Colores por columna, precalculados para reutilizarlos en las cápsulas de 'agrupadas'.
        colores_segmentos = []
        for i_seg in range(n_cols_barras):
            cfp_seg = colores_fondo_personalizados.get(entidad)
            c_seg = cfp_seg[i_seg] if cfp_seg and i_seg < len(cfp_seg) and cfp_seg[i_seg] else colores_asignados[i_seg % len(colores_asignados)]
            if colores_por_barra is not None:
                try:
                    c_cat_seg = colores_por_barra.iloc[idx_row]
                    if pd.notna(c_cat_seg):
                        c_seg = c_cat_seg
                except IndexError:
                    pass
            colores_segmentos.append(c_seg)

        # Topes de la fila (tope de la pila completa y valor individual mayor/menor).
        valores_fila_plot = df_plot[columnas_barras].iloc[idx_row] if columnas_barras else pd.Series(dtype=float)
        tope_sup_fila = valores_fila_plot[valores_fila_plot > 0].sum() if len(valores_fila_plot) else 0
        tope_inf_fila = valores_fila_plot[valores_fila_plot < 0].sum() if len(valores_fila_plot) else 0
        tope_max_fila = valores_fila_plot.max() if len(valores_fila_plot) else 0
        tope_min_fila = valores_fila_plot.min() if len(valores_fila_plot) else 0
        
        # Iteración sobre cada segmento de la barra apilada (solo columnas de barras).
        for i, col in enumerate(columnas_barras):
            current_val = df_plot[col].iloc[idx_row]
            # Posición y ancho efectivos: en 'agrupadas' cada columna ocupa su propia franja.
            pos_barra = pos + offsets_agrupadas[i]
            ancho_barra_actual = ancho_seg
            if current_val == 0 and not valor_barra_cero:
                continue
            
            if current_val > 0:
                last_non_zero_idx = i
            else:
                last_non_zero_idx_neg = i

            # Personalización de colores y estilos de borde por barra/segmento.
            color_fondo_personalizado = colores_fondo_personalizados.get(entidad)
            # ... resto de personalizaciones igual
            color_borde_personalizado = colores_borde_personalizados.get(entidad)
            estilo_borde_personalizado = estilos_borde_personalizados.get(entidad)
            grosor_borde_personalizado = grosores_borde_personalizados.get(entidad)
            color_texto_personalizado = colores_texto_personalizados.get(entidad)

            color = color_fondo_personalizado[i] if color_fondo_personalizado and i < len(color_fondo_personalizado) and color_fondo_personalizado[i] else colores_asignados[i % len(colores_asignados)]
            
            # Ajuste para colores_por_barra: usamos idx_row porque el DF ya está ordenado
            if colores_por_barra is not None:
                try:
                    color_cat = colores_por_barra.iloc[idx_row]
                    if pd.notna(color_cat):
                        color = color_cat
                except IndexError:
                    pass

            borde_color = color_borde_personalizado[i] if color_borde_personalizado and i < len(color_borde_personalizado) else color
            estilo_borde = estilo_borde_personalizado[i] if estilo_borde_personalizado and i < len(estilo_borde_personalizado) else '-'
            grosor_borde = grosor_borde_personalizado[i] if grosor_borde_personalizado and i < len(grosor_borde_personalizado) else 0

            # Determinamos la posición base (bottom) dependiendo del signo.
            # En 'agrupadas' no hay apilamiento: todas las barras arrancan desde cero.
            previous_bottom = 0 if es_agrupada else (bottom_pos if current_val >= 0 else bottom_neg)

            # Dibujo de la barra.
            # Añadir etiqueta solo si es la primera fila para evitar duplicados en la leyenda (aunque matplotlib los agrupa)
            lbl = col if idx_row == 0 else ""
            
            ax.bar(pos_barra, current_val, bottom=previous_bottom, width=ancho_barra_actual, color=color, 
                   edgecolor=borde_color, linewidth=grosor_borde, linestyle=estilo_borde, align='center', label=lbl)

            # Actualización de la posición base para el siguiente segmento.
            if current_val >= 0:
                bottom_pos += current_val
            else:
                bottom_neg += current_val 

            # Texto dentro de la barra (valor y/o porcentaje).
            val = df[col].iloc[idx_row] # Usar valor original

            # Determinación del color del texto para asegurar contraste.
            custom_text_color = color_texto_personalizado[i] if color_texto_personalizado and i < len(color_texto_personalizado) and color_texto_personalizado[i] else None
            text_color_valor = custom_text_color or color_valor_barra or get_text_color_for_bg(color)
            text_color_porcentaje = custom_text_color or color_porce_barra or get_text_color_for_bg(color)
            
            # Lógica para añadir textos (valor y/o porcentaje) dentro de las barras.
            area_barra = abs(current_val) * ancho_barra_actual
            
            # Cálculo de porcentaje (maneja casos normales y divergentes).
            porcentaje_valor = 0
            if respecto_porce:
                porcentaje_valor = current_val
            elif es_divergente:
                if porce_diver:
                    if current_val > 0:
                        base_porcentaje = suma_positivos_por_barra.iloc[idx_row]
                        porcentaje_valor = (val / base_porcentaje) * 100 if base_porcentaje != 0 else 0
                    else: # current_val < 0
                        base_porcentaje = suma_negativos_por_barra.iloc[idx_row]
                        porcentaje_valor = (val / base_porcentaje) * 100 if base_porcentaje != 0 else 0
                else: # porce_diver es False
                    base_porcentaje = suma_absoluta_por_barra.iloc[idx_row]
                    porcentaje_valor = (val / base_porcentaje) * 100 if base_porcentaje != 0 else 0
            else: # no es divergente
                # Como suma_total ya contiene el total de la fila (zip) y current_val es el valor del segmento
                porcentaje_valor = (val / total_valor) * 100 if total_valor != 0 else 0

            text_pos_y = previous_bottom + (current_val / 2)
                
            texto_final = ""
            texto_a_dibujar = False  # Cambia a False por defecto

            # Configuración de la alineación del texto.
            rotacion_texto_barra = 90 if alinear_texto_barra else 0
            ha_texto_barra = 'center'
            va_texto_barra_valor = 'bottom' if porce_abajo else 'center'
            va_texto_barra_porce = 'top' if porce_abajo else 'center'
            va_texto_barra_unificado = 'center'


            # --- INICIO DE LA LÓGICA CORREGIDA ---
            # Determinar si se debe dibujar la etiqueta según el área
            debe_dibujar_dentro = area_barra >= areamin
            debe_dibujar_fuera = not debe_dibujar_dentro and opcion_areamin == 'fuera'

            texto_final = ""
            texto_valor = ""
            texto_porcentaje = ""
            es_texto_personalizado = False

            # 1. Revisar si hay texto personalizado
            if textos_personalizados_barra is not None and i < textos_personalizados_barra.shape[1]:
                texto_candidato = textos_personalizados_barra.iloc[idx_row, i]
                if pd.notna(texto_candidato):
                    texto_final = str(texto_candidato)
                    es_texto_personalizado = True
            elif entidad in textos_barra_personalizados:
                textos_barra = textos_barra_personalizados[entidad]
                if i < len(textos_barra) and textos_barra[i] is not None:
                    texto_final = textos_barra[i]
                    es_texto_personalizado = True
            
            # 2. Si no hay texto personalizado, construir el texto de valor/porcentaje
            if not es_texto_personalizado:
                if valor_barra:
                    val_original = df[col].iloc[idx_row]
                    # Si simbolo_negativo es True, usamos el valor original (con signo)
                    # Si simbolo_negativo es False, usamos el valor absoluto
                    val_to_format = val_original if simbolo_negativo else abs(val_original)
                    texto_valor = elimina_ceros_no_significativos(formato_decimal.format(val_to_format))
                    if simbolo_porce_barra:
                        texto_valor = f"{texto_valor}%"
                if porce_barra:
                    # Usar porcentaje_valor calculado previamente
                    porce_val_abs = abs(porcentaje_valor)
                    texto_porcentaje = f"({elimina_ceros_no_significativos(f'{porce_val_abs:.1f}')}%)" if not porce_abajo else f"{elimina_ceros_no_significativos(f'{porce_val_abs:.1f}')}%"

            # 3. Dibujar las etiquetas si corresponde
            if debe_dibujar_dentro:
                if activar_cambiar_color:
                    if opcion_cambiar_color == 'cambio':
                        c_nuevo_val = cambiar_color(text_color_valor, color)
                        if c_nuevo_val:
                            text_color_valor = c_nuevo_val
                        eff_val = None

                        c_nuevo_por = cambiar_color(text_color_porcentaje, color)
                        if c_nuevo_por:
                            text_color_porcentaje = c_nuevo_por
                        eff_por = None
                    else:
                        c_bord_val = cambiar_color(text_color_valor, color)
                        eff_val = [path_effects.withStroke(linewidth=1.5, foreground=c_bord_val)] if c_bord_val else None
                        c_bord_por = cambiar_color(text_color_porcentaje, color)
                        eff_por = [path_effects.withStroke(linewidth=1.5, foreground=c_bord_por)] if c_bord_por else None
                else:
                    eff_val = None
                    eff_por = None
                
                if es_texto_personalizado:
                    ax.text(pos_barra, text_pos_y, texto_final, 
                            va='center', ha='center', rotation=rotacion_texto_barra,
                            fontsize=tam_valor_barra,
                            fontfamily=font_config['family'],
                            fontweight=font_config['valor_porcentaje_barra']['weight'],
                            color=text_color_valor, path_effects=eff_val)
                elif porce_abajo and valor_barra and porce_barra:
                    ax.text(pos_barra, text_pos_y, texto_valor, va=va_texto_barra_valor, ha=ha_texto_barra, rotation=rotacion_texto_barra,
                            fontsize=font_config['valor_porcentaje_barra']['size'],
                            fontfamily=font_config['family'],
                            fontweight=font_config['valor_porcentaje_barra']['weight'],
                            color=text_color_valor,
                            linespacing=1.5, path_effects=eff_val)
                    ax.text(pos_barra, text_pos_y, texto_porcentaje, va=va_texto_barra_porce, ha=ha_texto_barra, rotation=rotacion_texto_barra,
                            fontsize=font_config['valor_porcentaje_barra_porcentaje']['size'],
                            fontfamily=font_config['family'],
                            fontweight=font_config['valor_porcentaje_barra_porcentaje']['weight'],
                            color=text_color_porcentaje,
                            linespacing=1.5, path_effects=eff_por)
                else:
                    # Unificar texto para otros casos (solo valor, solo porce, o ambos en una línea)
                    texto_final_unificado = f"{texto_valor} {texto_porcentaje}".strip()
                    if texto_final_unificado:
                        font_size_a_usar = font_config['valor_porcentaje_barra_porcentaje']['size'] if not valor_barra and porce_barra else font_config['valor_porcentaje_barra']['size']
                        color_a_usar = text_color_porcentaje if not valor_barra and porce_barra else text_color_valor
                        eff_unificado = eff_por if not valor_barra and porce_barra else eff_val
                        ax.text(pos_barra, text_pos_y, texto_final_unificado, va=va_texto_barra_unificado, ha=ha_texto_barra, rotation=rotacion_texto_barra,
                                fontsize=font_size_a_usar,
                                fontfamily=font_config['family'],
                                fontweight=font_config['valor_porcentaje_barra']['weight'],
                                color=color_a_usar,
                                linespacing=1.2, path_effects=eff_unificado)

            elif debe_dibujar_fuera:
                # Construir el texto para fuera si no se hizo antes
                if es_texto_personalizado:
                    texto_para_fuera = texto_final
                else:
                    texto_para_fuera = f"{texto_valor} {texto_porcentaje}".strip()

                if texto_para_fuera:
                    etq_fuera = {
                        'pos': pos_barra,
                        'entidad': entidad,
                        'col': col,
                        'texto': texto_para_fuera,
                        'color': color,
                        'text_color': text_color_valor,
                        'font_size': tam_valor_barra,
                        'font_weight': font_config['valor_porcentaje_barra']['weight'],
                        'font_family': font_config['family'],
                        'order': i,
                        'bottom_pos': previous_bottom + current_val,
                        # Altura desde la que se despega la etiqueta: la pila completa en 'apiladas',
                        # la propia barra en 'agrupadas'.
                        'tope_pos': current_val if es_agrupada else tope_sup_fila,
                        'tope_neg': current_val if es_agrupada else tope_inf_fila,
                    }
                    etiquetas_fuera.append(etq_fuera)
                    etiquetas_fuera_fila.append(etq_fuera)
            # --- FIN DE LA LÓGICA CORREGIDA ---
                    
        # Lógica para dibujar las cápsulas con el total sobre las barras (solo en 'apiladas').
        if valor_capsu and not es_agrupada and "__espaciador__" not in str(entidad):
            # --- INICIO DE CAMBIOS ---
            # Determinar si la cápsula positiva debe dibujarse
            valor_positivo_total = suma_positivos_por_barra.iloc[idx_row] if es_divergente else total_valor
            
            # Calcular valor y texto antes de decidir
            valor_a_mostrar = total_valor
            
            if '__capsule_values__' in df.columns:
                valor_a_mostrar = df['__capsule_values__'].iloc[idx_row]
            elif es_divergente:
                if not porce_diver:
                    valor_a_mostrar = suma_absoluta_por_barra.iloc[idx_row]
                else: # porce_diver es True
                    valor_a_mostrar = suma_positivos_por_barra.iloc[idx_row]

            if etiquetas_finales is not None and not pd.isna(etiquetas_finales.iloc[idx_row]):
                texto_a_mostrar = str(etiquetas_finales.iloc[idx_row])
            else:
                texto_a_mostrar = elimina_ceros_no_significativos(formato_decimal.format(valor_a_mostrar))

            # Verificar si es visualmente cero
            es_cero_visual = False
            try:
                if float(texto_a_mostrar.replace(',', '')) == 0:
                    es_cero_visual = True
            except ValueError:
                pass
            
            if valor_a_mostrar == 0:
                es_cero_visual = True

            # Condición para dibujar:
            # 1. capsu_cero=True (siempre se intenta dibujar, incluso si es 0)
            # O
            # 2. El valor NO es cero visualmente
            debe_dibujar_capsula_positiva = capsu_cero or not es_cero_visual

            if es_divergente:
                valor_negativo_total = suma_negativos_por_barra.iloc[idx_row]
                # Ocultar la cápsula positiva solo si la parte positiva es cero Y la parte negativa NO es cero.
                # Esto permite que se muestre la cápsula de "0" si ambas partes son cero.
                if valor_positivo_total <= 0 and valor_negativo_total != 0:
                    debe_dibujar_capsula_positiva = False

            if debe_dibujar_capsula_positiva:
                # valor_a_mostrar y texto_a_mostrar ya calculados arriba

                # --- NUEVO: Añadir símbolo de porcentaje si se solicita ---
                if simbolo_porce_capsu and not "__espaciador__" in str(entidad):
                     texto_a_mostrar = f"{texto_a_mostrar}%"
                # -------------------------------------------------------------
     
                texto_capsula = f"{espacio*2}{texto_a_mostrar}{espacio*2}"
                base_pos_y = bottom_pos if es_divergente else (100 if respecto_porce else total_valor)
                text_y_pos = base_pos_y + x_max * ajustar_pos_capsu

                # --- DESPLAZAMIENTO EXTRA SI HAY ETIQUETAS FUERA ---
                if opcion_areamin == 'fuera':
                    etiquetas_fuera_en_barra = [etq for etq in etiquetas_fuera if etq['pos'] == pos and etq['bottom_pos'] >= 0]
                    n_etqs = len(etiquetas_fuera_en_barra)
                    if n_etqs:
                        # El desplazamiento total es proporcional al número de etiquetas
                        text_y_pos += ajustar_pos_capsu_areamin * x_max * n_etqs
                # --- FIN DESPLAZAMIENTO EXTRA ---

                rotacion_capsula = 90 if alinear_capsu else 0
                ha_capsula = 'center'
                va_capsula = 'bottom'
                pos_x_capsula = pos
                pos_y_capsula = text_y_pos

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

                # --- Lógica de colores personalizada para cápsulas y bordes ---
                if isinstance(color_valor_capsu, list):
                    # Usar el índice de la última columna con valor para determinar el color
                    # Esto asegura que el color de la cápsula coincida con el segmento superior de la barra
                    col_idx_para_color = last_non_zero_idx
                    color_texto_capsula = color_valor_capsu[col_idx_para_color % len(color_valor_capsu)]
                else:
                    if color_valor_capsu is None:
                        color_texto_capsula = color_una_barra_capsu if is_simple_or_divergent else '#434343'
                    else:
                        color_texto_capsula = color_valor_capsu

                if isinstance(color_borde_capsu, list):
                    col_idx_para_borde = last_non_zero_idx
                    color_actual_borde_capsu = color_borde_capsu[col_idx_para_borde % len(color_borde_capsu)]
                else:
                    if color_borde_capsu is None:
                        color_actual_borde_capsu = color_una_barra_capsu if is_simple_or_divergent else '#434343'
                    else:
                        color_actual_borde_capsu = color_borde_capsu
                # -------------------------------------------------------------
        
                if activar_cambiar_color:
                    bg_capsula = color_fondo_capsu if not quitar_capsu else (fondo if fondo != 'transparent' else '#ffffff')
                    if opcion_cambiar_color == 'cambio':
                        c_nuevo_cap = cambiar_color(color_texto_capsula, bg_capsula)
                        if c_nuevo_cap:
                            color_texto_capsula = c_nuevo_cap
                        eff_cap = None
                    else:
                        c_bord_cap = cambiar_color(color_texto_capsula, bg_capsula)
                        eff_cap = [path_effects.withStroke(linewidth=1.5, foreground=c_bord_cap)] if c_bord_cap else None
                else:
                    eff_cap = None
                    
                if not quitar_capsu:
                    ax.text(pos_x_capsula, pos_y_capsula, texto_capsula,
                        bbox=dict(boxstyle=f"round,pad=0.15,rounding_size={curvatura_capsu}", facecolor=color_fondo_capsu, edgecolor=color_actual_borde_capsu, linewidth=peso_borde_capsu),
                        ha=ha_capsula, va=va_capsula, rotation=rotacion_capsula,
                        path_effects=eff_cap,
                        fontdict={'family': font_config['family'], 'size': font_config['valor_capsula']['size'], 'weight': font_config['valor_capsula']['weight'], 'color': color_texto_capsula})
                else:
                    ax.text(pos_x_capsula, pos_y_capsula, texto_a_mostrar, ha=ha_capsula, va=va_capsula, rotation=rotacion_capsula,
                        path_effects=eff_cap,
                        fontdict={'family': font_config['family'], 'size': font_config['valor_capsula']['size'], 'weight': font_config['valor_capsula']['weight'], 'color': color_texto_capsula})
            # --- FIN DE CAMBIOS ---

        # Lógica para cápsulas en la parte negativa de gráficos divergentes.
        if es_divergente and valor_capsu and not es_agrupada and bottom_neg < 0:
            valor_negativo_total = suma_negativos_por_barra.iloc[idx_row]
            
            # Si simbolo_negativo es True, mostramos el valor original (negativo).
            # Si es False, mostramos el valor absoluto.
            val_neg_to_format = valor_negativo_total if simbolo_negativo else abs(valor_negativo_total)

            texto_a_mostrar_neg = elimina_ceros_no_significativos(formato_decimal.format(val_neg_to_format))
            
            es_cero_visual_neg = False
            try:
                if float(texto_a_mostrar_neg.replace(',', '')) == 0:
                    es_cero_visual_neg = True
            except ValueError:
                pass
            
            if valor_negativo_total == 0:
                es_cero_visual_neg = True

            if capsu_cero or not es_cero_visual_neg:

                # --- NUEVO: Añadir símbolo de porcentaje si se solicita ---
                if simbolo_porce_capsu and not "__espaciador__" in str(entidad):
                     texto_a_mostrar_neg = f"{texto_a_mostrar_neg}%"
                # -------------------------------------------------------------

                texto_capsula_neg = f"{espacio*2}{texto_a_mostrar_neg}{espacio*2}"
                # Usa el nuevo parámetro si existe, si no, usa el original
                ajuste_neg = ajustar_pos_capsu_neg if ajustar_pos_capsu_neg is not None else ajustar_pos_capsu
                # Inicializa la posición base de la cápsula negativa
                text_y_pos_neg = bottom_neg - x_max * ajuste_neg

                # --- DESPLAZAMIENTO EXTRA SI HAY ETIQUETAS FUERA ABAJO ---
                if opcion_areamin == 'fuera':
                    etiquetas_fuera_en_barra_neg = [etq for etq in etiquetas_fuera if etq['pos'] == pos and etq['bottom_pos'] < 0]
                    n_etqs_neg = len(etiquetas_fuera_en_barra_neg)
                    if n_etqs_neg:
                        # Usa el nuevo parámetro si existe, si no, usa el original
                        ajuste_2_neg = ajustar_pos_capsu_neg_areamin if ajustar_pos_capsu_neg_areamin is not None else ajustar_pos_capsu_areamin
                        text_y_pos_neg -= ajuste_2_neg * x_max * n_etqs_neg
                # --- FIN DESPLAZAMIENTO EXTRA ---

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

                # --- Lógica de colores personalizada para cápsulas y bordes (negativos) ---
                if isinstance(color_valor_capsu, list):
                    col_idx_para_color_neg = last_non_zero_idx_neg
                    color_texto_capsula_neg = color_valor_capsu[col_idx_para_color_neg % len(color_valor_capsu)]
                else:
                    if color_valor_capsu is None:
                        color_texto_capsula_neg = color_una_barra_capsu_neg if is_simple_or_divergent else '#434343'
                    else:
                        color_texto_capsula_neg = color_valor_capsu

                if isinstance(color_borde_capsu, list):
                    col_idx_para_borde_neg = last_non_zero_idx_neg
                    color_actual_borde_capsu_neg = color_borde_capsu[col_idx_para_borde_neg % len(color_borde_capsu)]
                else:
                    if color_borde_capsu is None:
                        color_actual_borde_capsu_neg = color_una_barra_capsu_neg if is_simple_or_divergent else '#434343'
                    else:
                        color_actual_borde_capsu_neg = color_borde_capsu
                # -------------------------------------------------------------

                # --- INICIO DE CAMBIOS ---
                # Aplicar la misma lógica de alineación que en las cápsulas positivas
                rotacion_capsula_neg = 90 if alinear_capsu else 0
                ha_capsula_neg = 'center'
                # Para cápsulas negativas, la alineación vertical debe ser 'top'
                va_capsula_neg = 'top' 
                pos_x_capsula_neg = pos
                pos_y_capsula_neg = text_y_pos_neg

                if activar_cambiar_color:
                    bg_capsula_neg = color_fondo_capsu if not quitar_capsu else (fondo if fondo != 'transparent' else '#ffffff')
                    if opcion_cambiar_color == 'cambio':
                        c_nuevo_cap_neg = cambiar_color(color_texto_capsula_neg, bg_capsula_neg)
                        if c_nuevo_cap_neg:
                            color_texto_capsula_neg = c_nuevo_cap_neg
                        eff_cap_neg = None
                    else:
                        c_bord_cap_neg = cambiar_color(color_texto_capsula_neg, bg_capsula_neg)
                        eff_cap_neg = [path_effects.withStroke(linewidth=1.5, foreground=c_bord_cap_neg)] if c_bord_cap_neg else None
                else:
                    eff_cap_neg = None

                if not quitar_capsu:
                    ax.text(pos_x_capsula_neg, pos_y_capsula_neg, texto_capsula_neg,
                        bbox=dict(boxstyle=f"round,pad=0.15,rounding_size={curvatura_capsu}", facecolor=color_fondo_capsu, edgecolor=color_actual_borde_capsu_neg, linewidth=peso_borde_capsu),
                        ha=ha_capsula_neg, va=va_capsula_neg, rotation=rotacion_capsula_neg,
                        path_effects=eff_cap_neg,
                        fontdict={'family': font_config['family'], 'size': font_config['valor_capsula']['size'], 'weight': font_config['valor_capsula']['weight'], 'color': color_texto_capsula_neg})
                else:
                    ax.text(pos_x_capsula_neg, pos_y_capsula_neg, texto_a_mostrar_neg, 
                        ha=ha_capsula_neg, va=va_capsula_neg, rotation=rotacion_capsula_neg,
                        path_effects=eff_cap_neg,
                        fontdict={'family': font_config['family'], 'size': font_config['valor_capsula']['size'], 'weight': font_config['valor_capsula']['weight'], 'color': color_texto_capsula_neg})
                # --- FIN DE CAMBIOS ---

        # --- CÁPSULAS EN MODO 'AGRUPADAS': una cápsula por barra con su propio valor ---
        if es_agrupada and valor_capsu and "__espaciador__" not in str(entidad):
            for i_cap, col_cap in enumerate(columnas_barras):
                valor_cap_plot = df_plot[col_cap].iloc[idx_row]
                valor_cap = df[col_cap].iloc[idx_row]

                val_cap_a_formatear = valor_cap if simbolo_negativo else abs(valor_cap)
                texto_cap = elimina_ceros_no_significativos(formato_decimal.format(val_cap_a_formatear))

                es_cero_visual_cap = valor_cap == 0
                try:
                    if float(texto_cap.replace(',', '')) == 0:
                        es_cero_visual_cap = True
                except ValueError:
                    pass

                if not (capsu_cero or not es_cero_visual_cap):
                    continue

                if simbolo_porce_capsu:
                    texto_cap = f"{texto_cap}%"

                pos_x_cap = pos + offsets_agrupadas[i_cap]
                es_negativa_cap = valor_cap_plot < 0

                # Las barras negativas llevan la cápsula por debajo, con su propio ajuste.
                if es_negativa_cap:
                    ajuste_cap = ajustar_pos_capsu_neg if ajustar_pos_capsu_neg is not None else ajustar_pos_capsu
                    pos_y_cap = valor_cap_plot - x_max * ajuste_cap
                    va_cap = 'top'
                else:
                    pos_y_cap = valor_cap_plot + x_max * ajustar_pos_capsu
                    va_cap = 'bottom'

                # Desplazamiento extra si la etiqueta de esta barra se movió fuera.
                if opcion_areamin == 'fuera':
                    n_etqs_cap = len([etq for etq in etiquetas_fuera_fila if etq['pos'] == pos_x_cap])
                    if n_etqs_cap:
                        if es_negativa_cap:
                            ajuste_2_cap = ajustar_pos_capsu_neg_areamin if ajustar_pos_capsu_neg_areamin is not None else ajustar_pos_capsu_areamin
                            pos_y_cap -= ajuste_2_cap * x_max * n_etqs_cap
                        else:
                            pos_y_cap += ajustar_pos_capsu_areamin * x_max * n_etqs_cap

                # Con 'capsulas_alineadas' todas las cápsulas del grupo se centran en el mismo punto
                # del eje X y arrancan de una base común (el tope del grupo, no el de cada barra).
                # El reparto vertical se resuelve al final de la sección 8, midiendo su alto real.
                if capsulas_alineadas_activo:
                    pos_x_cap = pos
                    if es_negativa_cap:
                        pos_y_cap = min(tope_min_fila, 0) - x_max * ajuste_cap
                    else:
                        pos_y_cap = max(tope_max_fila, 0) + x_max * ajustar_pos_capsu

                    if opcion_areamin == 'fuera':
                        # Basta con despejar una vez: la pila ya se separa sola por encima de esa altura.
                        hay_fuera_cap = any((etq['bottom_pos'] < 0) == es_negativa_cap for etq in etiquetas_fuera_fila)
                        if hay_fuera_cap:
                            if es_negativa_cap:
                                ajuste_2_alin = ajustar_pos_capsu_neg_areamin if ajustar_pos_capsu_neg_areamin is not None else ajustar_pos_capsu_areamin
                                pos_y_cap -= ajuste_2_alin * x_max
                            else:
                                pos_y_cap += ajustar_pos_capsu_areamin * x_max

                # Cada cápsula pertenece a una sola barra, así que hereda su color.
                color_barra_cap = colores_segmentos[i_cap]

                if isinstance(color_valor_capsu, list):
                    color_texto_cap = color_valor_capsu[i_cap % len(color_valor_capsu)]
                else:
                    color_texto_cap = color_barra_cap if color_valor_capsu is None else color_valor_capsu

                if isinstance(color_borde_capsu, list):
                    color_borde_cap = color_borde_capsu[i_cap % len(color_borde_capsu)]
                else:
                    color_borde_cap = color_barra_cap if color_borde_capsu is None else color_borde_capsu

                if activar_cambiar_color:
                    bg_cap = color_fondo_capsu if not quitar_capsu else (fondo if fondo != 'transparent' else '#ffffff')
                    if opcion_cambiar_color == 'cambio':
                        c_nuevo_cap_ag = cambiar_color(color_texto_cap, bg_cap)
                        if c_nuevo_cap_ag:
                            color_texto_cap = c_nuevo_cap_ag
                        eff_cap_ag = None
                    else:
                        c_bord_cap_ag = cambiar_color(color_texto_cap, bg_cap)
                        eff_cap_ag = [path_effects.withStroke(linewidth=1.5, foreground=c_bord_cap_ag)] if c_bord_cap_ag else None
                else:
                    eff_cap_ag = None

                rotacion_cap_ag = 90 if alinear_capsu else 0

                if not quitar_capsu:
                    artista_cap = ax.text(pos_x_cap, pos_y_cap, f"{espacio*2}{texto_cap}{espacio*2}",
                        bbox=dict(boxstyle=f"round,pad=0.15,rounding_size={curvatura_capsu}", facecolor=color_fondo_capsu, edgecolor=color_borde_cap, linewidth=peso_borde_capsu),
                        ha='center', va=va_cap, rotation=rotacion_cap_ag,
                        path_effects=eff_cap_ag,
                        fontdict={'family': font_config['family'], 'size': font_config['valor_capsula']['size'], 'weight': font_config['valor_capsula']['weight'], 'color': color_texto_cap})
                else:
                    artista_cap = ax.text(pos_x_cap, pos_y_cap, texto_cap,
                        ha='center', va=va_cap, rotation=rotacion_cap_ag,
                        path_effects=eff_cap_ag,
                        fontdict={'family': font_config['family'], 'size': font_config['valor_capsula']['size'], 'weight': font_config['valor_capsula']['weight'], 'color': color_texto_cap})

                if capsulas_alineadas_activo:
                    capsulas_para_alinear.append({
                        'artista': artista_cap,
                        'x': pos_x_cap,
                        'fila': idx_row,
                        'orden': i_cap,
                        'negativa': es_negativa_cap,
                        'base': pos_y_cap,
                        'tam': font_config['valor_capsula']['size'],
                        'con_caja': not quitar_capsu,
                    })

        # Lógica para mostrar porcentajes totales al inicio del eje (debajo de las barras).
        if porce_total_inicio:
            valor_numerador = total_valor
            valor_denominador = total_general
            if es_divergente:
                if not porce_diver:
                    valor_numerador = suma_absoluta_por_barra.iloc[idx_row]
                    valor_denominador = total_general_absoluto
                else: # porce_diver es True
                    valor_numerador = suma_positivos_por_barra.iloc[idx_row]
                    valor_denominador = total_general_positivos
            
            porcentaje = round((valor_numerador / valor_denominador) * 100, 1) if valor_denominador != 0 else 0
            etiqueta_actual = entidades_formateadas[idx_row]

            # Resaltado de etiquetas si se especifica.
            if resaltar_valor_ejex and etiqueta_actual in resaltar_valor_ejex:
                texto_a_mostrar = f"{espacio*1}{etiqueta_actual}   {elimina_ceros_no_significativos(f'{porcentaje:.1f}')}%{espacio*1}"
                color_texto_resaltado = get_text_color_for_bg(color_resaltado_ejex)
                bbox_capsula = dict(facecolor=color_resaltado_ejex, edgecolor=color_borde_resaltado_ejex, boxstyle=f"round,pad=0.15,rounding_size={curvatura_capsu}")
                ax.text(pos, -x_max*0.02, texto_a_mostrar, ha='center', va='top', rotation=90,
                        bbox=bbox_capsula,
                        fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 
                                  'weight': font_config['porcentaje_total']['weight'], 'color': color_texto_resaltado})
            else:
                texto_a_mostrar = f"{espacio*1}{elimina_ceros_no_significativos(f'{porcentaje:.1f}')}%{espacio*1}"
                ax.text(pos, 0, texto_a_mostrar, ha='right', va='top', rotation=90,
                        color=font_config['porcentaje_total']['color'],
                        fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight']})

        # Lógica para mostrar porcentajes totales sobre las barras.
        if porce_total:
            valor_numerador = total_valor
            valor_denominador = total_general
            if es_divergente:
                if not porce_diver:
                    valor_numerador = suma_absoluta_por_barra.iloc[idx_row]
                    valor_denominador = total_general_absoluto
                else: # porce_diver es True
                    valor_numerador = suma_positivos_por_barra.iloc[idx_row]
                    valor_denominador = total_general_positivos

            porcentaje = round((valor_numerador / valor_denominador) * 100, 1) if valor_denominador != 0 else 0
            
            desplazamiento_y = x_max * (0.15 if valor_capsu and not quitar_capsu else 0.08)
            
            if es_agrupada:
                # No hay pila: el porcentaje se apoya sobre la barra más alta del grupo.
                base_pos_y = tope_max_fila
            else:
                base_pos_y = bottom_pos if es_divergente else (100 if respecto_porce else total_valor)
            desplazamiento_final = base_pos_y + desplazamiento_y + (x_max * ajustar_pos_porce_total)
            
            # --- DESPLAZAMIENTO EXTRA SI HAY ETIQUETAS FUERA ---
            if opcion_areamin == 'fuera':
                if es_agrupada:
                    # Las etiquetas fuera están una al lado de otra, no acumuladas en altura.
                    n_etqs = 1 if any(etq['bottom_pos'] >= 0 for etq in etiquetas_fuera_fila) else 0
                else:
                    etiquetas_fuera_en_barra = [etq for etq in etiquetas_fuera if etq['pos'] == pos and etq['bottom_pos'] >= 0]
                    n_etqs = len(etiquetas_fuera_en_barra)
                if n_etqs:
                    desplazamiento_final += ajustar_pos_capsu_areamin * x_max * n_etqs
            # --- FIN DESPLAZAMIENTO EXTRA ---

            ax.text(pos, desplazamiento_final, f"{elimina_ceros_no_significativos(f'{porcentaje:.1f}')}%", ha='center', va='bottom',
                    color=font_config['porcentaje_total']['color'],
                    fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight']})

    # Después, dibujar todas las líneas
    for i, col in enumerate(columnas_lineas):
        # Obtener un color para la línea
        # Usar colores_lineas si está definida, de lo contrario usar la paleta general
        if colores_lineas and i < len(colores_lineas):
            line_color = colores_lineas[i]
        else:
            line_color = colores_asignados[(i + len(columnas_barras)) % len(colores_asignados)]
    
        # Obtener los valores de la línea
        valores_linea = df_plot[col].values
    
        # Dibujar la línea
        line, = ax.plot(posiciones, valores_linea, marker='o', markersize=6, 
                      linewidth=2, color=line_color, label=col, zorder=5)
    
        # Almacenar para la leyenda
        line_handles.append(line)
        line_labels.append(col)
        
        # Añadir cápsula al final de la línea si se solicita
        if capsu_fin_lineas and len(valores_linea) > 0:
            # Obtener la posición y valor del último punto
            ultimo_pos = posiciones[-1]
            ultimo_valor = valores_linea[-1]
            
            texto_a_mostrar = elimina_ceros_no_significativos(formato_decimal.format(ultimo_valor))
            
            es_cero_visual = False
            try:
                if float(texto_a_mostrar.replace(',', '')) == 0:
                    es_cero_visual = True
            except ValueError:
                pass
            
            if ultimo_valor == 0:
                es_cero_visual = True

            # Solo mostrar cápsula si el valor no es cero o si se especificó capsu_cero=True
            if capsu_cero or not es_cero_visual:
                texto_capsula = f"{espacio*2}{texto_a_mostrar}{espacio*2}"
                
                # Colocar la cápsula ligeramente desplazada del último punto
                pos_x_capsula = ultimo_pos + ancho_barra * 0.5
                pos_y_capsula = ultimo_valor
                
                # Usar la misma configuración de las cápsulas de barras
                color_texto_capsula = color_valor_capsu if color_valor_capsu is not None else '#434343'
                color_borde_capsula = color_borde_capsu if color_borde_capsu is not None else '#434343'
                
                if not quitar_capsu:
                    ax.text(pos_x_capsula, pos_y_capsula, texto_capsula,
                        bbox=dict(boxstyle=f"round,pad=0.15,rounding_size={curvatura_capsu}", facecolor=color_fondo_capsu, 
                                edgecolor=color_borde_capsula, linewidth=peso_borde_capsu),
                        ha='left', va='center',
                        fontdict={'family': font_config['family'], 
                                'size': font_config['valor_capsula']['size'], 
                                'weight': font_config['valor_capsula']['weight'], 
                                'color': color_texto_capsula})
                else:
                    ax.text(pos_x_capsula, pos_y_capsula, texto_a_mostrar, 
                        ha='left', va='center',
                        fontdict={'family': font_config['family'], 
                                'size': font_config['valor_capsula']['size'], 
                                'weight': font_config['valor_capsula']['weight'], 
                                'color': color_texto_capsula})
                                
                # Si el valor es negativo, ajustar la alineación vertical
                if ultimo_valor < 0:
                    ax.texts[-1].set_va('center')

    # --- DIBUJAR ETIQUETAS FUERA DE LAS BARRAS SI opcion_areamin == 'fuera' ---
    if opcion_areamin == 'fuera' and etiquetas_fuera:
        etiquetas_por_barra = defaultdict(list)
        for etq in etiquetas_fuera:
            etiquetas_por_barra[etq['pos']].append(etq)
        for pos, lista_etqs in etiquetas_por_barra.items():
            lista_etqs.sort(key=lambda x: x['order'])
            # Agrupar por positivas y negativas
            positivas = [etq for etq in lista_etqs if etq['bottom_pos'] >= 0]
            negativas = [etq for etq in lista_etqs if etq['bottom_pos'] < 0]
            spacing = 0.025 * x_max * ajustar_sep_valor_barra  # Espaciado pequeño y uniforme
            
            # Ajuste extra definido por el usuario
            ajuste_extra_usuario = (ajustar_pos_valor_barra if ajustar_pos_valor_barra is not None else 0) * x_max

            # Etiquetas positivas: todas alineadas arriba de la barra apilada
            if positivas:
                separacion_etiqueta_barra = 0.008 * x_max
                
                # Tope desde el que se despega la etiqueta: la pila completa en 'apiladas',
                # la barra individual en 'agrupadas'.
                tope_superior = max(etq.get('tope_pos', 0) for etq in positivas)

                y_base = tope_superior
                for idx, etq in enumerate(positivas):
                    extra_spacing = spacing * idx
                    y = y_base + extra_spacing + separacion_etiqueta_barra + ajuste_extra_usuario
                    
                    if activar_cambiar_color:
                        color_fondo_efectivo_fuera = fondo if fondo != 'transparent' else '#ffffff'
                        if opcion_cambiar_color == 'cambio':
                            c_nuevo_fuera = cambiar_color(etq['color'], color_fondo_efectivo_fuera)
                            color_etq_fuera = c_nuevo_fuera if c_nuevo_fuera else etq['color']
                            eff_fuera = None
                        else:
                            c_bord_fuera = cambiar_color(etq['color'], color_fondo_efectivo_fuera)
                            color_etq_fuera = etq['color']
                            eff_fuera = [path_effects.withStroke(linewidth=1.5, foreground=c_bord_fuera)] if c_bord_fuera else None
                    else:
                        color_etq_fuera = etq['color']
                        eff_fuera = None

                    ax.text(
                        pos, y, etq['texto'],
                        ha='center', va='bottom',
                        fontsize=etq['font_size'],
                        fontweight=etq['font_weight'],
                        fontfamily=etq['font_family'],
                        color=color_etq_fuera,
                        path_effects=eff_fuera,
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.0, boxstyle='round,pad=0.1')
                    )
            # Etiquetas negativas: todas alineadas abajo de la barra apilada
            if negativas:
                separacion_etiqueta_barra = 0.008 * x_max
                
                tope_inferior = min(etq.get('tope_neg', 0) for etq in negativas)

                y_base = tope_inferior
                for idx, etq in enumerate(negativas):
                    extra_spacing = spacing * idx
                    y = y_base - extra_spacing - separacion_etiqueta_barra - ajuste_extra_usuario
                    
                    if activar_cambiar_color:
                        color_fondo_efectivo_fuera_neg = fondo if fondo != 'transparent' else '#ffffff'
                        if opcion_cambiar_color == 'cambio':
                            c_nuevo_fuera_neg = cambiar_color(etq['color'], color_fondo_efectivo_fuera_neg)
                            color_etq_fuera_neg = c_nuevo_fuera_neg if c_nuevo_fuera_neg else etq['color']
                            eff_fuera_neg = None
                        else:
                            c_bord_fuera_neg = cambiar_color(etq['color'], color_fondo_efectivo_fuera_neg)
                            color_etq_fuera_neg = etq['color']
                            eff_fuera_neg = [path_effects.withStroke(linewidth=1.5, foreground=c_bord_fuera_neg)] if c_bord_fuera_neg else None
                    else:
                        color_etq_fuera_neg = etq['color']
                        eff_fuera_neg = None

                    ax.text(
                        pos, y, etq['texto'],
                        ha='center', va='top',
                        fontsize=etq['font_size'],
                        fontweight=etq['font_weight'],
                        fontfamily=etq['font_family'],
                        color=color_etq_fuera_neg,
                        path_effects=eff_fuera_neg,
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.0, boxstyle='round,pad=0.1')
                    )

    # --- 8. AJUSTES FINALES DE LA GRÁFICA ---
    # Usar tick_positions y tick_labels calculados previamente para el eje X
    final_tick_labels = list(tick_labels)

    # Si se resaltan etiquetas, se borran las originales para evitar duplicados.
    if (porce_total_inicio or resaltar_valor_ejex) and resaltar_valor_ejex:
        entidades_formateadas_final = []
        for e in final_tick_labels:
            if e in resaltar_valor_ejex:
                entidades_formateadas_final.append("")
            else:
                entidades_formateadas_final.append(e)
        final_tick_labels = entidades_formateadas_final

    # Configuración de las etiquetas del eje X.
    ax.set_xticks(tick_positions)
    
    # Manejo de la rotación basada en grados numéricos (-90 a 90)
    try:
        rotation_val = float(orientacion_valor_ejex)
        # Limitar entre -90 y 90
        rotation_val = max(-90.0, min(90.0, rotation_val))
    except (ValueError, TypeError):
        rotation_val = 0.0

    # Ajuste de alineación horizontal (ha) según rotación
    if rotation_val == 0:
        ha_val = 'center'
    elif rotation_val > 0:
        ha_val = 'right'
    else:
        ha_val = 'left'

    ax.set_xticklabels(
        final_tick_labels,
        fontsize=font_config['variable_x']['size'],
        fontweight=font_config['variable_x']['weight'],
        fontfamily=font_config['family'],
        color=font_config['variable_x']['color'],
        rotation=rotation_val,
        ha=ha_val
    )
    
    # Lógica para resaltar etiquetas si no se usa `porce_total_inicio`.
    if resaltar_valor_ejex and not porce_total_inicio:
        # Usamos tick_positions y tick_labels
        for pos_x, etiqueta_actual in zip(tick_positions, tick_labels):
            if etiqueta_actual in resaltar_valor_ejex:
                texto_capsula = f"{espacio*1}{etiqueta_actual}{espacio*1}"
                color_texto_resaltado = get_text_color_for_bg(color_resaltado_ejex)
                bbox_capsula = dict(facecolor=color_resaltado_ejex, edgecolor=color_borde_resaltado_ejex, boxstyle=f"round,pad=0.15,rounding_size={curvatura_capsu}")
                ax.text(pos_x, -x_max*0.02, texto_capsula, ha='center', va='top', rotation=90,
                        bbox=bbox_capsula,
                        fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 
                                  'weight': font_config['porcentaje_total']['weight'], 'color': color_texto_resaltado})

    # Configuración de los límites de los ejes.
    # Ajustar el límite derecho si hay cápsulas al final de las líneas
    if len(tick_positions) > 0:
        max_pos_x = tick_positions[-1]
    else:
        max_pos_x = len(entidades) - 1
        
    right_x_limit = max_pos_x + 0.5 + (0.8 if hay_annotations_externas or capsu_fin_lineas else 0)
    ax.set_xlim(-0.5, right_x_limit)
    
    if limites_ejey and not respecto_porce:
        ax.set_ylim(limites_ejey)
    else:
        y_min = (-x_max * (1 + ajustar_sep_abajo_ejex)) if es_divergente and not respecto_porce else 0
        y_max_val = 100 if respecto_porce else x_max
        ax.set_ylim(y_min, y_max_val)
        
    # Configuración de los "ticks" (marcas) del eje Y.
    if divisiones_ejey:
        ax.yaxis.set_major_locator(mticker.MultipleLocator(divisiones_ejey))
    else:
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins='auto', steps=[1, 2, 5, 10]))

    # Formateo de los números en el eje Y (porcentaje o miles).
    if respecto_porce:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x)}%'))
    elif simbolo_porce_ejey:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{elimina_ceros_no_significativos(formato_decimal.format(abs(x) if solo_ejey_positivo else x))}%"))
    else:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: elimina_ceros_no_significativos(formato_decimal.format(abs(x) if solo_ejey_positivo else x))))

    # --- SUSTITUCIÓN DE ETIQUETAS DEL EJE Y ---
    if sustituir_etiquetas_ejey is not None:
        yticks = ax.get_yticks()
        # Si la longitud coincide, sustituye directamente
        if len(sustituir_etiquetas_ejey) == len(yticks):
            ax.set_yticklabels(sustituir_etiquetas_ejey,
                               fontsize=font_config['variable_y']['size'],
                               fontweight=font_config['variable_y']['weight'],
                               color=font_config['variable_y']['color'],
                               fontfamily=font_config['family'])
        else:
            print("Advertencia: La longitud de 'sustituir_etiquetas_ejey' no coincide con el número de ticks del eje Y.")

    # Correcto: incluye explícitamente la familia de fuente
    plt.setp(ax.get_yticklabels(), 
             fontsize=font_config['variable_y']['size'],
             fontweight=font_config['variable_y']['weight'], 
             color=font_config['variable_y']['color'],
             fontfamily=font_config['family'])  # Añadir familia de fuente
    
    # Configuración de la grilla y espaciado.
    ax.set_axisbelow(True)
    ax.grid(visible=grillas, axis='y', color='#B9B9B9', linewidth=0.75, linestyle='-', zorder=0)
    if porce_total_inicio:
        ax.tick_params(axis='x', pad=espacio_inicio)
        
    # Títulos de los ejes.
    if nombre_ejex:
        ax.set_xlabel(nombre_ejex, labelpad=18, **font_config['nombre_ejex'])
    if nombre_ejey:
        ax.set_ylabel(nombre_ejey, labelpad=18, **font_config['nombre_ejey'])

    # Ajuste para etiquetas de espaciadores.
    for label, entidad_formateada in zip(ax.get_xticklabels(), entidades_formateadas):
        try:
            mapa_formato_a_original = {ent_fmt: ent_orig for ent_fmt, ent_orig in zip(entidades_formateadas, df.index)}
            original_index = mapa_formato_a_original.get(entidad_formateada)
            
            if original_index and "__espaciador__" in str(original_index):
                label.set_rotation(0)
                label.set_ha('center')
        except (ValueError, IndexError, KeyError):
            pass

    # Configuración de la leyenda.
    
    # 1. Preparar handles/labels para Series (si se requiere)
    h_series, l_series = [], []
    if leyenda: # Si leyenda es True o tiene título
        handles, labels = ax.get_legend_handles_labels()
        by_label = {l: h for l, h in zip(labels, handles)}
        
        for i, lbl in enumerate(columnas_barras):
            l_series.append(lbl)
            c = colores_asignados[i % len(colores_asignados)]
            if mapa_color_categoria:
                h_series.append(Patch(color=c))
            else:
                h_series.append(by_label.get(lbl, Patch(color=c)))
                
        for i, lbl in enumerate(columnas_lineas):
            l_series.append(lbl)
            line_c = colores_lineas[i] if colores_lineas and i < len(colores_lineas) else colores_asignados[(i + len(columnas_barras)) % len(colores_asignados)]
            h_series.append(by_label.get(lbl, plt.Line2D([0], [0], color=line_c, marker='o', markersize=6, linewidth=2)))

    if not ascendente_leyenda:
        h_series.reverse()
        l_series.reverse()

    # 2. Preparar handles/labels para Categorías (si se requiere)
    h_cat, l_cat = [], []
    if leyenda_categorias and mapa_color_categoria:
        for cat, color_cat in mapa_color_categoria.items():
            l_cat.append(cat)
            h_cat.append(Patch(color=color_cat))

    # 3. Dibujar Leyendas
    # Si ambas están presentes
    if (leyenda and l_series) and (leyenda_categorias and l_cat):
        # Dibujar Series primero
        num_cols = num_columnas_leyenda if num_columnas_leyenda is not None else len(l_series)
        kwargs_leyenda = {
            'title': leyenda if isinstance(leyenda, str) else None,
            'prop': {'size': font_config['leyenda']['size'], 'weight': font_config['leyenda']['weight']},
            'title_fontsize': font_config['leyenda']['size'],
            'frameon': False,
            'ncol': num_cols,
            'handlelength': 1,
            'handleheight': 1
        }
        if isinstance(posicion_leyenda, dict): kwargs_leyenda.update(posicion_leyenda)
        elif isinstance(posicion_leyenda, (tuple, list)): 
            kwargs_leyenda['loc'] = 'center'
            kwargs_leyenda['bbox_to_anchor'] = posicion_leyenda
        else: kwargs_leyenda['loc'] = posicion_leyenda

        leg1 = ax.legend(h_series, l_series, **kwargs_leyenda)
        if color_letra_leyenda is None:
            for text, handle in zip(leg1.get_texts(), leg1.legend_handles):
                if isinstance(handle, plt.Line2D):
                    text.set_color(handle.get_color())
                elif isinstance(handle, Patch):
                    text.set_color(handle.get_facecolor())
        ax.add_artist(leg1) # Manually keep it

        # Dibujar Categorías después
        num_cols_cat = num_columnas_categorias if num_columnas_categorias is not None else len(l_cat)
        kwargs_cat = {
            'title': leyenda_categorias if isinstance(leyenda_categorias, str) else None,
            'prop': {'size': font_config['leyenda']['size'], 'weight': font_config['leyenda']['weight']},
            'title_fontsize': font_config['leyenda']['size'],
            'frameon': False,
            'ncol': num_cols_cat,
            'handlelength': 1,
            'handleheight': 1
        }
        pos_cat = posicion_leyenda_categorias if posicion_leyenda_categorias is not None else posicion_leyenda
        if isinstance(pos_cat, dict): kwargs_cat.update(pos_cat)
        elif isinstance(pos_cat, (tuple, list)): 
            kwargs_cat['loc'] = 'center'
            kwargs_cat['bbox_to_anchor'] = pos_cat
        else: kwargs_cat['loc'] = pos_cat
        
        leg_cat = ax.legend(h_cat, l_cat, **kwargs_cat)
        if color_letra_leyenda is None:
            for text, handle in zip(leg_cat.get_texts(), leg_cat.legend_handles):
                if isinstance(handle, plt.Line2D):
                    text.set_color(handle.get_color())
                elif isinstance(handle, Patch):
                    text.set_color(handle.get_facecolor())
        
        # --- AJUSTE DE ESPACIO PARA LEYENDAS DOBLES ---
        # Añade un artista invisible en la parte inferior para obligar a tight_layout a reservar espacio,
        # adaptando el tamaño del gráfico (ejes) sin cambiar el tamaño de la figura.
        try:
            # Obtener coordenada Y mínima de las posiciones dadas (asumiendo formato lista/tupla)
            y_coords = []
            if isinstance(posicion_leyenda, (list, tuple)) and len(posicion_leyenda) >= 2:
                y_coords.append(posicion_leyenda[1])
            if isinstance(posicion_leyenda_categorias, (list, tuple)) and len(posicion_leyenda_categorias) >= 2:
                y_coords.append(posicion_leyenda_categorias[1])
            elif posicion_leyenda_categorias is None and isinstance(posicion_leyenda, (list, tuple)):
                 # Si no se define posición para categorías, usualmente se pondría manualmente
                 # Pero aquí asumimos que el usuario da posiciones si usa dos leyendas.
                 pass

            if y_coords:
                min_y = min(y_coords)
                # Añadir un margen extra abajo de la posición más baja (ej. 0.1 unids de ejes)
                # El texto es invisible.
                ax.text(0.5, min_y - 0.1, '', transform=ax.transAxes)
        except Exception:
            pass

    # Si solo Series
    elif (leyenda and l_series):
        num_cols = num_columnas_leyenda if num_columnas_leyenda is not None else len(l_series)
        kwargs_leyenda = {
            'title': leyenda if isinstance(leyenda, str) else None,
            'prop': {'size': font_config['leyenda']['size'], 'weight': font_config['leyenda']['weight']},
            'title_fontsize': font_config['leyenda']['size'],
            'frameon': False,
            'ncol': num_cols,
            'handlelength': 1,
            'handleheight': 1
        }
        if isinstance(posicion_leyenda, dict): kwargs_leyenda.update(posicion_leyenda)
        elif isinstance(posicion_leyenda, (tuple, list)): 
            kwargs_leyenda['loc'] = 'center'
            kwargs_leyenda['bbox_to_anchor'] = posicion_leyenda
        else: kwargs_leyenda['loc'] = posicion_leyenda
        
        leg = ax.legend(h_series, l_series, **kwargs_leyenda)
        if color_letra_leyenda is None:
            for text, handle in zip(leg.get_texts(), leg.legend_handles):
                if isinstance(handle, plt.Line2D):
                    text.set_color(handle.get_color())
                elif isinstance(handle, Patch):
                    text.set_color(handle.get_facecolor())
        
    # Si solo Categorías
    elif (leyenda_categorias and l_cat):
        num_cols_cat = num_columnas_categorias if num_columnas_categorias is not None else len(l_cat)
        kwargs_cat = {
            'title': leyenda_categorias if isinstance(leyenda_categorias, str) else None,
            'prop': {'size': font_config['leyenda']['size'], 'weight': font_config['leyenda']['weight']},
            'title_fontsize': font_config['leyenda']['size'],
            'frameon': False,
            'ncol': num_cols_cat,
            'handlelength': 1,
            'handleheight': 1
        }
        pos_cat = posicion_leyenda_categorias if posicion_leyenda_categorias is not None else posicion_leyenda
        if isinstance(pos_cat, dict): kwargs_cat.update(pos_cat)
        elif isinstance(pos_cat, (tuple, list)): 
            kwargs_cat['loc'] = 'center'
            kwargs_cat['bbox_to_anchor'] = pos_cat
        else: kwargs_cat['loc'] = pos_cat
        
        leg = ax.legend(h_cat, l_cat, **kwargs_cat)
        if color_letra_leyenda is None:
            for text, handle in zip(leg.get_texts(), leg.legend_handles):
                if isinstance(handle, plt.Line2D):
                    text.set_color(handle.get_color())
                elif isinstance(handle, Patch):
                    text.set_color(handle.get_facecolor())
        
    # Limpieza de los bordes del gráfico.
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_visible(True)

    # Línea en cero para gráficos divergentes.
    if es_divergente and not respecto_porce:
        ax.axhline(0, color='black', linewidth=1)

    # --- APILADO VERTICAL DE LAS CÁPSULAS ALINEADAS ('agrupadas' + capsulas_alineadas=True) ---
    # Todas las cápsulas del grupo se dibujaron ya centradas y sobre una base común. Aquí se
    # reparten en vertical midiendo su alto real sobre la figura renderizada, que es la única
    # forma de garantizar que no se superpongan con cualquier tamaño de letra o de figura.
    if capsulas_alineadas_activo and capsulas_para_alinear:
        try:
            # El layout tiene que estar en su forma definitiva antes de medir: mostrar_guardar_figura
            # llama a tight_layout cuando se fijan 'ancho'/'alto', y eso cambia la escala del eje.
            fig.tight_layout()
            fig.canvas.draw()
            renderer_cap = fig.canvas.get_renderer()
        except Exception:
            renderer_cap = None

        if renderer_cap is not None:
            # Una pila independiente por grupo (fila) y signo.
            pilas_capsulas = defaultdict(list)
            for cap in capsulas_para_alinear:
                pilas_capsulas[(cap['fila'], cap['negativa'])].append(cap)
            for pila_cap in pilas_capsulas.values():
                pila_cap.sort(key=lambda c: c['orden'])

            def alto_capsula_px(cap):
                alto = cap['artista'].get_window_extent(renderer=renderer_cap).height
                # 'round,pad=0.15' añade 0.15 * tamaño de letra por arriba y por abajo.
                if cap['con_caja']:
                    alto += 2 * 0.15 * cap['tam'] * fig.dpi / 72.0
                # Aire entre cápsulas consecutivas.
                return alto + 0.30 * cap['tam'] * fig.dpi / 72.0

            def repartir_capsulas():
                """Coloca cada pila y devuelve hasta dónde llega (en unidades de datos)."""
                tope_req, piso_req = ax.get_ylim()[1], ax.get_ylim()[0]
                for (_, es_neg_pila), pila_cap in pilas_capsulas.items():
                    y_cursor_px = ax.transData.transform((0, pila_cap[0]['base']))[1]
                    # Se recorren al revés en la pila positiva para que, leyendo de arriba hacia
                    # abajo, las cápsulas queden en el orden de las columnas del DataFrame.
                    for cap in (pila_cap if es_neg_pila else list(reversed(pila_cap))):
                        y_dato = ax.transData.inverted().transform((0, y_cursor_px))[1]
                        cap['artista'].set_position((cap['x'], y_dato))
                        cap['artista'].set_va('top' if es_neg_pila else 'bottom')
                        y_cursor_px += -alto_capsula_px(cap) if es_neg_pila else alto_capsula_px(cap)
                    limite = ax.transData.inverted().transform((0, y_cursor_px))[1]
                    if es_neg_pila:
                        piso_req = min(piso_req, limite)
                    else:
                        tope_req = max(tope_req, limite)
                return tope_req, piso_req

            # No se toca el eje si el usuario fijó sus límites o sustituyó sus etiquetas.
            puede_ampliar_ejey = not (limites_ejey and not respecto_porce) and sustituir_etiquetas_ejey is None

            # El alto de una cápsula es fijo en píxeles, pero lo que ocupa en unidades de datos
            # depende del rango del eje Y: al ampliarlo hay que volver a repartir.
            for _ in range(8):
                tope_necesario, piso_necesario = repartir_capsulas()
                y_inf_actual, y_sup_actual = ax.get_ylim()
                if not puede_ampliar_ejey:
                    break
                if tope_necesario <= y_sup_actual + 1e-9 and piso_necesario >= y_inf_actual - 1e-9:
                    break
                ax.set_ylim(min(piso_necesario, y_inf_actual), max(tope_necesario, y_sup_actual))
                fig.canvas.draw()

    # ------------------ POLÍGONO ZOOM ------------------
    if poligono_zoom and len(posiciones) > 0:
        import matplotlib.patches as mpatches
        pos_ultima = posiciones[-1]
        ancho_ultima = anchos_barras[-1]

        x_izq = pos_ultima - ancho_ultima / 2
        x_der = pos_ultima + ancho_ultima / 2

        if respecto_porce:
            y_sup = 100
        else:
            y_sup = suma_total.iloc[-1] if hasattr(suma_total, 'iloc') else suma_total[-1]

        if es_divergente:
            y_inf = suma_negativos_por_barra.iloc[-1] if hasattr(suma_negativos_por_barra, 'iloc') else suma_negativos_por_barra[-1]
        else:
            y_inf = 0

        v1 = (x_izq, y_sup)
        v2 = (x_izq, y_inf)
        v3 = (x_der, y_inf)

        inv = ax.transData.inverted()
        v4 = tuple(inv.transform(fig.transFigure.transform((1.0, 0.25))))
        v5 = tuple(inv.transform(fig.transFigure.transform((1.0, 0.50))))

        if posiciones_poligono_zoom is not None:
            dic_vertices = {1: v1, 2: v2, 3: v3, 4: v4, 5: v5}
            for num_v, posx, posy in posiciones_poligono_zoom:
                if num_v in [4, 5]:
                    # Los vértices 4 y 5 se interpretan como proporciones de la figura (0.0 a 1.0)
                    dic_vertices[num_v] = tuple(inv.transform(fig.transFigure.transform((posx, posy))))
                elif num_v in dic_vertices:
                    # Los vértices 1, 2 y 3 quedan en coordenadas de los datos
                    dic_vertices[num_v] = (posx, posy)
            v1, v2, v3, v4, v5 = dic_vertices[1], dic_vertices[2], dic_vertices[3], dic_vertices[4], dic_vertices[5]

        alpha_poly = 0.4 if opacidad_poligono_zoom is None else opacidad_poligono_zoom
        poly = mpatches.Polygon([v1, v2, v3, v4, v5], closed=True, facecolor='#E3E3E3', edgecolor='none', alpha=alpha_poly, zorder=0, clip_on=False)
        ax.add_patch(poly)
    # ---------------------------------------------------

    # --- 9. GUARDADO Y VISUALIZACIÓN ---
    from funciones import mostrar_guardar_figura
    
    # Asegurar que todo el contenido del canvas (incluyendo leyendas externas)
    # se incluya en el guardado usando bbox_inches='tight' en la función de exportación
    # que es llamada internamente por mostrar_guardar_figura.
    
    # Adicionalmente, ajustamos el layout actual antes de pasar
    # fig.tight_layout() se llama dentro de mostrar_guardar_figura,
    # pero para casos extremos de leyendas muy afuera, bbox_inches='tight' es la clave.

    mostrar_guardar_figura(
        fig=fig,
        ax=ax,
        nombre_df=nombre,
        guardar_fig=guardar,
        mostrar_fig=mostrar,
        limpiar_svg_con_scour=True,
        exact_dim=True if (ancho is not None or alto is not None) else False
    )
    
    return fig, ax

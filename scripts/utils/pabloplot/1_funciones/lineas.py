from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.font_manager as font_manager
import subprocess
import pandas as pd
import os

from funciones import limpiar_svg_con_scour 
from funciones import formato_fechas
from funciones import mostrar_guardar_figura
from funciones import num_decimales
from funciones import elimina_ceros_no_significativos
from funciones import algoritmo_posicionamiento_1
from funciones import algoritmo_posicionamiento_2
from funciones import cambiar_color
import matplotlib.patheffects as path_effects

def lineas(
        
# --- GRÁFICA GENERAL --- 
df,                            # DataFrame de entrada con la estructura especificada arriba.
formato_long=False,            # Si es True, asume que el DataFrame está en formato largo (3 columnas: fecha, variable, valor). Si False (default), asume formato ancho.
nombre="lineas",               # Nombre base para archivos de salida (.png y .svg). Default: "lineas".
tipo_letra='Montserrat',       # Tipo de letra para la gráfica, por defecto 'Montserrat'.
colores=None,                  # Lista de colores en HEX o nombres CSS para aplicar cíclicamente a las líneas. Si es None usa una paleta predeterminada.
ancho=23,                      # Ancho de la figura en centímetros.
alto=10,                       # Alto de la figura en centímetros.
grillas=True,                  # Activar/desactivar grillas horizontales de fondo.
fondo='transparent',           # Color de fondo. Puede ser 'transparent', 'white' o un código HEX.
decimales=None,                # Número de decimales forzados en los valores y cápsulas. Si es None, se calcula automáticamente.
mostrar=True,                  # Si True, despliega la figura con plt.show().
guardar=True,                  # Si True, guarda los resultados vía savefig().
margen=False,                  # Mostrar los ejes o bordes contenedores del gráfico (spines).
margen_color='#434343',        # Color de los bordes del gráfico.
margen_ancho=1.5,              # Grosor de las líneas del borde del contenedor.
marcas_ejes=True,              # Mostrar pequeñas marcas (ticks) en los ejes X y Y.
marcas_graduacion_ejex=True,   # Mostrar pequeñas marcas (ticks) en el eje X.
lineas_verticales=None,        # Lista de diccionarios para insertar líneas verticales superpuestas (ej. para enmarcar hitos temporales). Ejemplo: [{'x': 2020, 'color': 'red', 'estilo': '--'}].

# --- DATOS Y ESTRUCTURA ---
escalonada=False,              # Si True, las líneas se dibujan escalonadas (step plot) en lugar de continuas punto a punto.
acumuladas=False,              # Si True, las variables se dibujarán apiladas (stacked line plot / area).
estilos_lineas=None,           # Personalización individual de las líneas. Diccionario por nombre de variable o índice. Ej: {'GDP': {'ancho': 2.5, 'estilo': 'dashed'}}.
puntos=True,                   # Si True, grafica marcadores (puntos) en las coordenadas reales, interconectados por las líneas.
estilos_puntos=None,           # Personaliza el tamaño y estilo de los puntos por serie. Ej: {'Var1': {'tamano': 50}}.

# --- EJE X ---
nombre_ejex=None,              # Título del eje X.
tam_nombre_ejex=12,            # Tamaño tipográfico para el título del eje X.
peso_nombre_ejex='medium',     # Grosor tipográfico del título ('medium', 'bold', etc.).
tam_valor_ejex=12,             # Tamaño de letra para los valores o etiquetas base del eje X (ticks).
peso_valor_ejex='medium',      # Grosor para los valores/etiquetas del eje X.
color_valor_ejex='#434343',    # Color del texto para las etiquetas del eje X.
sustituir_valor_ejex=None,     # Lista para sustituir etiquetas del eje x
orientacion_valor_ejex=0,      # Grados de rotación para las etiquetas del eje X (0 = horizontal, 45 diagonal, 90 = vertical).
modalidad_fechas=1,            # Nivel de formato de la fecha (1=corto "ene", 2=largo "enero").
mostrar_solo_fechas=None,      # Permite aplicar un subsample si hay muchas fechas (ej. "años" o "meses"), para evitar sobreposición.
reducir_ticks_ejex=False,      # Disminuye visualmente la cantidad de ticks en el eje horizontal si hay aglomeración (compatible con fechas).

# --- EJE Y ---
nombre_ejey=None,              # Título del eje Y.
tam_nombre_ejey=12,            # Tamaño del título del eje Y.
peso_nombre_ejey='medium',     # Grosor del título del eje Y.
sustituir_etiquetas_ejey=None, # Permite sobrescribir completamente las etiquetas de los ticks del eje Y por una lista dada de cadenas.
limites_ejey=None,             # (min, max). Restringe y fuerza los límites del eje Y.
reducir_ticks_ejey=False,      # Disminuye visualmente la cantidad de ticks en el eje vertical si hay aglomeración.
tam_valor_ejey=12,             # Tamaño de texto para el número/etiquetas del eje Y.
peso_valor_ejey='medium',      # Grosor de las etiquetas del eje Y.
color_valor_ejey='#434343',    # Color de texto de las etiquetas de Y.
simbolo_porce_ejey=False,      # Agregar '%' como sufijo en los valores mostrados sobre el eje Y.

# --- CÁPSULAS O TAGS ---
mostrar_capsu=None,            # Lista de posiciones (índices 0-based) de puntos clave en donde se mostrarán cápsulas o etiquetas obligatoriamente.
color_fondo_capsu="white",     # Color interno o relleno de la cápsula. Si es "white", tendrán fondo blanco; si es None, hereda color de la línea correspondiente.
color_borde_capsu=None,        # Color para delinear el borde exterior de las cápsulas de valores.
peso_borde_capsu=1.8,          # Grosor de línea de este borde para la cápsula.
tam_valor_capsu=13,            # Tamaño numérico o textual dibujado en la cápsula.
peso_valor_capsu='bold',       # Grosor ('bold', 'medium'...) del texto dentro de las cápsulas.
color_valor_capsu=None,        # Determina un color tipográfico fijo para la cápsula.
ajustar_posx_capsu_fin=0.0,    # Modificador para distanciar horizontalmente las cápsulas conectadas al último punto longitudinalmente.
ajustar_posy_capsu_fin=0.0,    # Modificador para distanciar verticalmente las cápsulas conectadas al último punto longitudinalmente.
ajustar_sep_capsu_fin=0.0,     # Desplazamiento extra vertical entre cada etiqueta de final de línea si llegasen a colisionar o empalmarse.
ajustar_pos_capsu=-0.04,       # Ajuste flotante (y base general) que separa o aproxima progresivamente en "Y" todas las cápsulas globales a los puntos.
simbolo_porce_capsu=False,     # Muestra e incrusta el símbolo '%' tras generar los valores impresos dentro de las cápsulas.
capsu_fin=True,                # Despliega una etiqueta en el extremo derecho final absoluto de cada serie o línea dibujada.
capsu_ini=True,                # Inserta cápsula al arranque primario o punto temporal inicial explícito de todas las líneas.
capsu_max=True,                # Encuentra y prioriza nombrar automáticamete con cápsulas aquellos valores picos superlativos por línea del set de datos.
mostrar_capsu_especificas=None,# Categorías exactas referenciadas temporalmente (fechas como eje X) para gatillar etiquetas de coyuntura general en esas abscisas para las series.
curvatura_capsu=0.7,           # Coeficiente normalizado referencial entre líneas rectas (0.0) a fuertemente curvos con efecto redondeado tipo esfera (1.0).
sin_capsu=1000000,             # Tasa métrica de despliegue automatizada para obviar o reducir render en etiquetas no-picos (por defecto el valor excesivo anula intermedias implícitamente).
espacio_capsu=False,           # Alternativa inyectora de prefijos y sufijos de espacio libre Unicode invisible "\u00A0" para separar o esponjar cápsulas minúsculas abriendo bordes artificialmente.
activar_cambiar_color=True,    # Detona algoritmo de contrastado: si se vuelve invisible frente a gráficas idénticas, auto-genera y realza bordes.

# --- ALGORITMOS DE POSICIONAMIENTO ---
algoritmo_posicionamiento="algoritmo_posicionamiento_2", # Disposición paramétrica ('algoritmo_posicionamiento_1' o 'algoritmo_posicionamiento_2') como solucionador inteligente en caso que colisiones en empalme existan entre etiquetas.
ajustar_sep_capsu=0.13,        # Espacio físico relativo extra de repulsión entre etiquetas del solucionador.
ajustar_sep_con_ejex=0.1,      # Tolerancia para despejar el algoritmo de etiquetas de las bases horizontales (el suelo del recuadro del eje X principal inferior).
capsu_en_max=True,             # Otorga derecho jerárquico inamovible (arriba del punto) en trazabilidad, si se le etiqueta como máximo en `algoritmo_posicionamiento_2`.

# --- LEYENDA ---
leyenda=False,                 # Despiega identificador nominal descriptivo visual centralizado por debajo en base a los identificadores variables de series detectadas.
posicion_leyenda=(0.5, -0.2),  # Orientación decimal fraccional con referenciales en Ejes Base x & y, ej. `(0.5, -0.2)` lo alinea céntricamente bajo la cuadrícula de origen.
num_columnas_leyenda=None,     # Número fraccional en tabla (cuántas columnas por renglón) listará el compendio explícito total del index de leyendas.
tam_letra_leyenda=12,          # Resolución tipográfica del cuadro leyenda completo.
peso_letra_leyenda='medium',   # Grosor o peso de letras de fuente.
color_letra_leyenda='#434343', # Tintado cromático principal (cadenas, listados HEX o css de matplotlib) para leyendas.
leyenda_fin=False,             # Si 'True', anula el compendio tradicional e inserta leyendas textuales con alusión remanente por nombre adheridas de extremo derecho a diestra del fin longitudinalmente de las rayas variables por serie graficada.
ajustar_posx_leyenda_fin=0.0,  # Empuje numérico paramétrico flotador sobre la distancia horizonal base inyectada hacia el final longitudinal si se ha seleccionado dictar leyendas a destajo remanentes finales `leyenda_fin=True`.

):
    """
    Genera un gráfico de líneas altamente personalizable para visualizar series de tiempo o variables continuas.
    Ideal para comparar tendencias, observar la evolución temporal de diferentes categorías y marcar puntos o valores importantes.

    INFORMACIÓN PARA LA IA Y USUARIOS:
    Esta función permite crear gráficos de líneas con calidad para reportes y publicaciones. Se puede personalizar el grosor
    de líneas, el tamaño y formato de los puntos, aplicar estilos diferenciados a cada serie, e insertar cápsulas (etiquetas de valores)
    en posiciones clave (inicio, fin, máximos) o mediante un posicionamiento algorítmico inteligente (algoritmo_posicionamiento_1 y 2) que 
    evita los solapamientos.

    ESTRUCTURA DEL DATAFRAME `df`:
    1. Si `formato_long=False` (por defecto):
       El DataFrame debe presentarse en formato ancho (wide). La primera columna será siempre el eje X (fechas o variables independientes),
       y las siguientes columnas representarán las diferentes series (líneas) a graficar, conteniendo sus respectivos valores.
    2. Si `formato_long=True`:
       El DataFrame debe estar en formato largo (melted), y tener exactamente 3 columnas en este orden estricto: [Fecha/X, Variable/Categoría, Valor/Y].

    FORMATO DE COLUMNA DE FECHAS (EJE X):
    - Pueden ser enteros (ej. 2018, 2019) u otra variable continua. 
    - Las fechas (cadenas, int o datetime) interactúan con `modalidad_fechas` y `mostrar_solo_fechas` usando las utilidades externas del paquete.
    
    Parámetros:
    
    --- GRÁFICA GENERAL ---
    df (pandas.DataFrame) : DataFrame de entrada con la estructura especificada arriba.
    formato_long (bool) : Si es True, asume que el DataFrame está en formato largo (3 columnas: fecha, variable, valor). Si False (default), asume formato ancho.
    nombre (str) : Nombre base para archivos de salida (.png y .svg). Default: "lineas".
    tipo_letra (str) : Tipo de letra para la gráfica, por defecto 'Montserrat'.
    colores (list/None) : Lista de colores en HEX o nombres CSS para aplicar cíclicamente a las líneas. Si es None usa una paleta predeterminada.
    ancho (float/int/None) : Ancho de la figura en centímetros.
    alto (float/int/None) : Alto de la figura en centímetros. 
    grillas (bool) : Activar/desactivar grillas horizontales de fondo.
    fondo (str) : Color de fondo. Puede ser 'transparent', 'white' o un código HEX.
    decimales (int/None) : Número de decimales forzados en los valores y cápsulas. Si es None, se calcula automáticamente.
    mostrar (bool) : Si True, despliega la figura con plt.show().
    guardar (bool) : Si True, guarda los resultados vía savefig().
    margen (bool) : Mostrar los ejes o bordes contenedores del gráfico (spines).
    margen_color (str) : Color de los bordes del gráfico.
    margen_ancho (float) : Grosor de las líneas del borde del contenedor.
    marcas_ejes (bool) : Mostrar pequeñas marcas (ticks) en los ejes X y Y.
    marcas_graduacion_ejex (bool) : Mostrar pequeñas marcas (ticks) en el eje X.
    lineas_verticales (list/None) : Lista de diccionarios para insertar líneas verticales superpuestas (ej. para enmarcar hitos temporales). Ejemplo: [{'x': 2020, 'color': 'red', 'estilo': '--'}].

    --- DATOS Y ESTRUCTURA ---
    escalonada (bool) : Si True, las líneas se dibujan escalonadas (step plot) en lugar de continuas punto a punto.
    estilos_lineas (dict/list/None) : Personalización individual de las líneas. Diccionario por nombre de variable o índice. Ej: {'GDP': {'ancho': 2.5, 'estilo': 'dashed', 'alpha': 0.5}}.
    puntos (bool) : Si True, grafica marcadores (puntos) en las coordenadas reales, interconectados por las líneas.
    estilos_puntos (dict/None) : Personaliza el tamaño y estilo de los puntos por serie. Ej: {'Var1': {'tamano': 50, 'alpha': 0.8}}.

    --- EJE X ---
    nombre_ejex (str/None) : Título del eje X.
    tam_nombre_ejex (int/float) : Tamaño tipográfico para el título del eje X.
    peso_nombre_ejex (str) : Grosor tipográfico del título ('medium', 'bold', etc.).
    tam_valor_ejex (int/float) : Tamaño de letra para los valores o etiquetas base del eje X (ticks).
    peso_valor_ejex (str) : Grosor para los valores/etiquetas del eje X.
    color_valor_ejex (str) : Color del texto para las etiquetas del eje X.
    sustituir_valor_ejex (list/None) : Lista para sustituir etiquetas del eje x.
    orientacion_valor_ejex (float) : Grados de rotación para las etiquetas del eje X (0 = horizontal, 45 diagonal, 90 = vertical).
    modalidad_fechas (int/None) : Nivel de formato de la fecha (1=corto "ene", 2=largo "enero").
    mostrar_solo_fechas (str/None) : Permite aplicar un subsample si hay muchas fechas (ej. "años" o "meses"), para evitar sobreposición.
    reducir_ticks_ejex (bool) : Disminuye visualmente la cantidad de ticks en el eje horizontal si hay aglomeración (es compatible con fechas).

    --- EJE Y ---
    nombre_ejey (str/None) : Título del eje Y.
    tam_nombre_ejey (int/float) : Tamaño del título del eje Y.
    peso_nombre_ejey (str) : Grosor del título del eje Y.
    sustituir_etiquetas_ejey (list/None) : Permite sobrescribir completamente las etiquetas de los ticks del eje Y por una lista dada de cadenas.
    limites_ejey (tuple/None) : (min, max). Restringe y fuerza los límites del eje Y.
    reducir_ticks_ejey (bool) : Disminuye visualmente la cantidad de ticks en el eje vertical si hay aglomeración.
    tam_valor_ejey (int/float) : Tamaño de texto para el número/etiquetas del eje Y.
    peso_valor_ejey (str) : Grosor de las etiquetas del eje Y.
    color_valor_ejey (str) : Color de texto de las etiquetas de Y.
    simbolo_porce_ejey (bool) : Agregar '%' como sufijo en los valores mostrados sobre el eje Y.

    --- CÁPSULAS O TAGS ---
    mostrar_capsu (list/None) : Lista de posiciones (índices 0-based) de puntos clave en donde se mostrarán cápsulas o etiquetas obligatoriamente.
    color_fondo_capsu (str/None) : Color interno o relleno de la cápsula. Si es "white", tendrán fondo blanco; si es None, hereda color de la línea correspondiente.
    color_borde_capsu (str/list/None) : Color para delinear el borde exterior de las cápsulas de valores.
    peso_borde_capsu (float) : Grosor de línea de este borde para la cápsula.
    tam_valor_capsu (int/float) : Tamaño numérico o textual dibujado en la cápsula.
    peso_valor_capsu (str) : Grosor ('bold', 'medium'...) del texto dentro de las cápsulas.
    color_valor_capsu (str/list/None) : Determina un color tipográfico fijo para la cápsula.
    ajustar_posx_capsu_fin (float) : Modificador para distanciar horizontalmente las cápsulas conectadas al último punto longitudinalmente.
    ajustar_posy_capsu_fin (float) : Modificador para distanciar verticalmente las cápsulas conectadas al último punto longitudinalmente.
    ajustar_sep_capsu_fin (float) : Desplazamiento extra vertical entre cada etiqueta de final de línea si llegasen a colisionar o empalmarse.
    ajustar_pos_capsu (float) : Ajuste flotante (y base general) que separa o aproxima progresivamente en "Y" todas las cápsulas globales a los puntos.
    simbolo_porce_capsu (bool) : Muestra e incrusta el símbolo '%' tras generar los valores impresos dentro de las cápsulas.
    capsu_fin (bool/str) : Despliega una etiqueta en el extremo derecho final absoluto de cada serie o línea dibujada.
    capsu_ini (bool) : Inserta cápsula al arranque primario o punto temporal inicial explícito de todas las líneas.
    capsu_max (bool) : Encuentra y prioriza nombrar automáticamete con cápsulas aquellos valores picos superlativos por línea del set de datos.
    mostrar_capsu_especificas (list/None) : Categorías exactas referenciadas temporalmente (fechas como eje X) para gatillar etiquetas de coyuntura general en esas abscisas para las series.
    curvatura_capsu (float) : Coeficiente normalizado referencial entre líneas rectas (0.0) a fuertemente curvos con efecto redondeado tipo esfera (1.0).
    sin_capsu (int) : Tasa métrica de despliegue automatizada para obviar o reducir render en etiquetas no-picos (por defecto el valor excesivo anula intermedias implícitamente).
    espacio_capsu (bool) : Alternativa inyectora de prefijos y sufijos de espacio libre Unicode invisible "\\u00A0" para separar o esponjar cápsulas minúsculas abriendo bordes artificialmente.
    activar_cambiar_color (bool) : Detona algoritmo de contrastado: si se vuelve invisible frente a gráficas idénticas, auto-genera y realza bordes.

    --- ALGORITMOS DE POSICIONAMIENTO ---
    algoritmo_posicionamiento (str) : Disposición paramétrica ('algoritmo_posicionamiento_1' o 'algoritmo_posicionamiento_2') como solucionador inteligente en caso que colisiones en empalme existan entre etiquetas.
    ajustar_sep_capsu (float) : Espacio físico relativo extra de repulsión entre etiquetas del solucionador.
    ajustar_sep_con_ejex (float) : Tolerancia para despejar el algoritmo de etiquetas de las bases horizontales (el suelo del recuadro del eje X principal inferior).
    capsu_en_max (bool) : Otorga derecho jerárquico inamovible (arriba del punto) en trazabilidad, si se le etiqueta como máximo en `algoritmo_posicionamiento_2`.

    --- LEYENDA ---
    leyenda (bool) : Despiega identificador nominal descriptivo visual centralizado por debajo en base a los identificadores variables de series detectadas.
    posicion_leyenda (tuple) : Orientación decimal fraccional con referenciales en Ejes Base x & y, ej. `(0.5, -0.2)` lo alinea céntricamente bajo la cuadrícula de origen.
    num_columnas_leyenda (int/None) : Número fraccional en tabla (cuántas columnas por renglón) listará el compendio explícito total del index de leyendas.
    tam_letra_leyenda (int/float) : Resolución tipográfica del cuadro leyenda completo.
    peso_letra_leyenda (str) : Grosor o peso de letras de fuente.
    color_letra_leyenda (str) : Tintado cromático principal (cadenas, listados HEX o css de matplotlib) para leyendas.
    leyenda_fin (bool) : Si 'True', anula el compendio tradicional e inserta leyendas textuales con alusión remanente por nombre adheridas de extremo derecho a diestra del fin longitudinalmente de las rayas variables por serie graficada.
    ajustar_posx_leyenda_fin (float) : Empuje numérico paramétrico flotador sobre la distancia horizonal base inyectada hacia el final longitudinal si se ha seleccionado dictar leyendas a destajo remanentes finales `leyenda_fin=True`.

    EJEMPLO DE DATAFRAME `df` (formato_long=False, default ancho):
    | Año o Categoría | Var_A  | Var_B |
    |-----------------|--------|-------|
    | 2021-Q1         | 30.2   | 55.4  | 
    | 2021-Q2         | 42.1   | 50.1  |
    
    NOTAS DE EJECUCIÓN IA (Accionables):
    1. Revisar formato Dataframe: Si el df viene "largo" (fecha, variable, valor), activa `formato_long=True`.
    2. Cuidado con excesos: Mostrar demasiados puntos + múltiples líneas usualmente produce una sobrescripción caótica de texto; prioriza `capsu_fin`, `capsu_ini` o `capsu_max` sobre intentar mostrar toda cifra con `mostrar_capsu`.
    3. Cuando hayan líneas superponiéndose, confía en el `algoritmo_posicionamiento_2` y usa un buen `ajustar_sep_capsu` para repeler dinámicamente las etiquetas.
    """
    # Transformar de wide a long si es necesario
    if not formato_long:
        col_x = df.columns[0]
        df = pd.melt(df, id_vars=[col_x], var_name="variable", value_name="valor")

    # Validar columnas
    if df.shape[1] != 3:
        raise ValueError("El DataFrame debe tener exactamente 3 columnas después de la transformación a long: fecha, variable y valor (en ese orden).")

    # Asignar nombres automáticos
    columna_fecha = df.columns[0]
    columna_variable = df.columns[1]
    columna_valor = df.columns[2]

    variables = df[columna_variable].unique()

    if acumuladas:
        df['__orden_var'] = df[columna_variable].map({v: idx for idx, v in enumerate(variables)})
        df = df.sort_values([columna_fecha, '__orden_var'])
        df['__cum'] = df.groupby(columna_fecha)[columna_valor].cumsum()
        df['__valor_prev'] = df.groupby(columna_fecha)['__cum'].shift(1).fillna(0)
        df[columna_valor] = df['__cum']
        df = df.drop(columns=['__cum', '__orden_var'])

    # --- CÁLCULO DE DECIMALES ---
    # Recopilar todos los valores numéricos para determinar los decimales
    todos_los_valores = df[columna_valor].dropna().values.tolist()
    
    # Determinar el número de decimales a usar
    num_dec = num_decimales(todos_los_valores, determinado=decimales)
    
    formato_decimal = f"{{:,.{num_dec}f}}"

    font_config = {
        'family': tipo_letra,
        'variable_x': {'size': tam_valor_ejex, 'weight': peso_valor_ejex, 'color': color_valor_ejex},
        'variable_y': {'size': tam_valor_ejey, 'weight': peso_valor_ejey, 'color': color_valor_ejey},
        'capsula_valor': {'size': tam_valor_capsu, 'weight': peso_valor_capsu, 'color': color_valor_capsu},
        'leyenda': {'size': tam_letra_leyenda, 'weight': peso_letra_leyenda, 'color': color_letra_leyenda}
    }

    plt.rcParams['svg.fonttype'] = 'none'
    current_dir = Path(__file__).resolve().parent
    font_dirs = [current_dir.parent / "0_fonts"]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

    # --- Ajuste de tamaño de figura ---
    if ancho is not None and alto is not None:
        fig, ax = plt.subplots(figsize=(ancho / 2.54, alto / 2.54))
    else:
        ancho_px = 1480
        alto_px = 520
        dpi = 100
        ancho_in = ancho_px / dpi
        alto_in = alto_px / dpi
        fig, ax = plt.subplots(figsize=(ancho_in, alto_in), dpi=dpi)
    
    # Aplicar color de fondo
    if fondo.lower() == 'transparent':
        fig.patch.set_facecolor('none')
        fig.patch.set_alpha(0.0)
        ax.set_facecolor('none')
        ax.set_alpha(0.0)
    else:
        fig.patch.set_facecolor(fondo)
        ax.set_facecolor(fondo)

    if colores is not None:
        colores_asignados = colores
    else:
        colores_asignados = ["#006157", "#767676", "#671435", "#9B2247", "#9D792A", "#D5B162"]
    color_map = {var: colores_asignados[i % len(colores_asignados)] for i, var in enumerate(variables)}

    # Graficar todas las líneas y puntos primero
    for i, var in enumerate(variables):
        datos = df[df[columna_variable] == var]
    
        # --- Lógica para estilos de línea personalizados (por nombre o posición) ---
        ancho_actual = 2
        estilo_actual = 'solid'
        estilo_personalizado = None
        alpha_actual = 1.0

        if estilos_lineas:
            # Opción 1: Es una lista, usar el índice 'i'
            if isinstance(estilos_lineas, list):
                if i < len(estilos_lineas):
                    estilo_personalizado = estilos_lineas[i]
            # Opción 2: Es un diccionario, usar el nombre de la variable 'var' o la posición de la columna (i+1)
            elif isinstance(estilos_lineas, dict):
                if var in estilos_lineas:
                    estilo_personalizado = estilos_lineas[var]
                elif (i + 1) in estilos_lineas:
                    estilo_personalizado = estilos_lineas[i + 1]
        
        if estilo_personalizado:
            ancho_actual = estilo_personalizado.get('ancho', ancho_actual)
            estilo_actual = estilo_personalizado.get('estilo', estilo_actual)
            alpha_actual = estilo_personalizado.get('alpha', alpha_actual)
        # --- FIN Lógica de estilos ---

        # --- Lógica para estilos de puntos personalizados ---
        tam_punto_actual = 10
        estilo_punto_personalizado = None
        alpha_punto_actual = 1.0
        
        if estilos_puntos:
            if isinstance(estilos_puntos, list):
                if i < len(estilos_puntos):
                    estilo_punto_personalizado = estilos_puntos[i]
            elif isinstance(estilos_puntos, dict):
                if var in estilos_puntos:
                    estilo_punto_personalizado = estilos_puntos[var]
                elif (i + 1) in estilos_puntos:
                    estilo_punto_personalizado = estilos_puntos[i + 1]
        
        if estilo_punto_personalizado:
            tam_punto_actual = estilo_punto_personalizado.get('tamano', tam_punto_actual)
            alpha_punto_actual = estilo_punto_personalizado.get('alpha', alpha_punto_actual)
        # --- FIN Lógica de estilos puntos ---

        if escalonada:
            ax.step(
                datos[columna_fecha],
                datos[columna_valor],
                label=var,
                color=color_map[var],
                linewidth=ancho_actual,
                linestyle=estilo_actual,
                where='mid',
                clip_on=False,
                alpha=alpha_actual
            )
        else:
            ax.plot(
                datos[columna_fecha],
                datos[columna_valor],
                label=var,
                color=color_map[var],
                linewidth=ancho_actual,
                linestyle=estilo_actual,
                clip_on=False,
                alpha=alpha_actual
            )
        
        # --- NUEVO: Lógica para dibujar el área bajo la curva ---
        if acumuladas:
            alpha_area = 0.5
            color_area = color_map[var]
            if estilo_personalizado and isinstance(estilo_personalizado.get('area'), dict):
                alpha_area = estilo_personalizado.get('area').get('alpha', alpha_area)
                color_area = estilo_personalizado.get('area').get('color_area', color_area)

            ax.fill_between(
                datos[columna_fecha],
                datos.get('__valor_prev', 0),
                datos[columna_valor],
                color=color_area,
                alpha=alpha_area,
                step='mid' if escalonada else None,
                zorder=0
            )
        elif estilo_personalizado and estilo_personalizado.get('area'):
            config_area = estilo_personalizado.get('area')
            
            # El color del área es 'color_area' si existe, si no, el color de la línea.
            color_area = estilo_personalizado.get('color_area', color_map[var])
            alpha_area = 0.2 # Alpha por defecto

            # Si 'area' es un diccionario, permite personalizar el alpha
            if isinstance(config_area, dict):
                alpha_area = config_area.get('alpha', alpha_area)
            
            ax.fill_between(
                datos[columna_fecha],
                datos[columna_valor],
                color=color_area,
                alpha=alpha_area,
                step='mid' if escalonada else None,
                zorder=0 # Asegura que el área esté detrás de las líneas y puntos
            )
        # --- FIN Lógica de área ---

        color_relleno = color_map[var]
        color_borde = color_map[var]
        grosor_borde = 1.0

        if estilo_punto_personalizado:
            color_relleno = estilo_punto_personalizado.get('color_relleno', color_relleno)
            color_borde = estilo_punto_personalizado.get('color_borde', color_borde)
            grosor_borde = estilo_punto_personalizado.get('grosor_borde', grosor_borde)

        if puntos:
            ax.scatter(
                datos[columna_fecha],
                datos[columna_valor],
                c=color_relleno,
                edgecolors=color_borde,
                linewidths=grosor_borde,
                s=tam_punto_actual,
                zorder=3,
                clip_on=False,
                alpha=alpha_punto_actual
            )

    # ...después de graficar las líneas y puntos...
    y_max = df[columna_valor].max()
    y_min = df[columna_valor].min()
    espacio_extra = abs(y_max - y_min) * 0.24  # 15% de espacio extra arriba
    ax.set_ylim(y_min - 0.5*espacio_extra, y_max + espacio_extra)

    # Calcular la escala global para el offset de etiquetas
    escala = df[columna_valor].max() - df[columna_valor].min()

    # Calcular la coordenada X máxima global para alinear todas las etiquetas finales
    if capsu_fin == 'derecha':
        x_final_global = df[columna_fecha].max()

    all_texts = []
    capsu_fin_texts = []  # Para guardar referencias a las etiquetas finales
    for i, var in enumerate(variables):
        if isinstance(color_valor_capsu, list):
            color_texto_capsula = color_valor_capsu[i % len(color_valor_capsu)]
        else:
            if color_valor_capsu is None:
                color_texto_capsula = colores_asignados[i % len(colores_asignados)]
            else:
                color_texto_capsula = color_valor_capsu
            
        if isinstance(color_borde_capsu, list):
            color_actual_borde_capsu = color_borde_capsu[i % len(color_borde_capsu)]
        else:
            if color_borde_capsu is None:
                color_actual_borde_capsu = colores_asignados[i % len(colores_asignados)]
            else:
                color_actual_borde_capsu = color_borde_capsu
            
        datos = df[df[columna_variable] == var].reset_index(drop=True)
        total_puntos = len(datos)
        max_index = datos[columna_valor].idxmax()
        color = color_map[var]
        fc_color = color_fondo_capsu if color_fondo_capsu else color
        bbox_props = dict(
            boxstyle=f"round,pad=0.25,rounding_size={curvatura_capsu}",
            fc=fc_color,
            ec=color_actual_borde_capsu, 
            lw=peso_borde_capsu, 
            alpha=1.0
        )
        espacio = "\u00A0" if espacio_capsu else ""
        va = 'bottom'
        escala = df[columna_valor].max() - df[columna_valor].min()
        offset = abs(escala) * 0.03 if escala else 10
        for j, row in datos.iterrows():
            # --- NUEVO: Mostrar tag si el valor de X está en mostrar_capsu_especificas ---
            if mostrar_capsu_especificas is not None and row[columna_fecha] in mostrar_capsu_especificas:
                mostrar_etiqueta = True
            else:
                # Si mostrar_capsu está definido, solo mostrar en esos índices
                if mostrar_capsu is not None:
                    mostrar_etiqueta = j in mostrar_capsu
                else:
                    mostrar_etiqueta = (total_puntos - j - 1) % (sin_capsu + 1) == 0

            tiene_etiqueta = mostrar_etiqueta
            es_ultimo = (j == total_puntos - 1) and (capsu_fin is True)
            es_primero = (j == 0) and capsu_ini
            es_maximo = (j == max_index) and capsu_max
            # --- NUEVO: mostrar_capsu_especificas tiene mayor jerarquía ---
            if mostrar_capsu_especificas is not None and row[columna_fecha] in mostrar_capsu_especificas:
                mostrar_tag = True
            else:
                # Evita mostrar la etiqueta en el último punto si capsu_fin es False
                if not capsu_fin and j == total_puntos - 1:
                    tiene_etiqueta = False
                # Evita mostrar la etiqueta en el primer punto si capsu_ini es False
                if not capsu_ini and j == 0:
                    tiene_etiqueta = False
                mostrar_tag = (tiene_etiqueta or es_ultimo or es_primero or es_maximo) and not (capsu_fin == 'derecha' and j == total_puntos - 1)

            if mostrar_tag:
                # Si es el máximo, aumenta el offset para evitar que se encime
                offset_actual = offset
                if es_maximo:
                    offset_actual += abs(escala) * 0.0  

                pos_y = row[columna_valor]

                # Formato inteligente de decimales
                valor_num = row[columna_valor]
                valor_capsula = elimina_ceros_no_significativos(formato_decimal.format(valor_num))
                
                # Añadir símbolo de porcentaje si se solicita
                if simbolo_porce_capsu:
                    valor_capsula = f"{valor_capsula}%"

                if activar_cambiar_color:
                    color_borde_texto = cambiar_color(color_texto_capsula, fc_color if fc_color and str(fc_color).lower() != 'none' else '#ffffff')
                    efectos_texto = [path_effects.withStroke(linewidth=1.5, foreground=color_borde_texto)] if color_borde_texto else None
                else:
                    efectos_texto = None

                x_pos_text = row[columna_fecha]
                if (j == total_puntos - 1):
                    if ajustar_posx_capsu_fin != 0.0:
                        x_pos_text = ax.convert_xunits(row[columna_fecha]) + ajustar_posx_capsu_fin
                    if ajustar_posy_capsu_fin != 0.0:
                        pos_y += ajustar_posy_capsu_fin

                txt = plt.text(
                    x_pos_text,
                    pos_y,
                    f"{espacio*2}{valor_capsula}{espacio*2}",
                    fontsize=font_config['capsula_valor']['size'],
                    color=color_texto_capsula,
                    weight=font_config['capsula_valor']['weight'],
                    ha='center',
                    va='center',
                    bbox=bbox_props,
                    fontname=font_config['family'],
                    path_effects=efectos_texto
                )
                txt.y_original = pos_y
                all_texts.append(txt)



        # Etiqueta final a la derecha, alineada para todas las líneas
        if capsu_fin == 'derecha':
            y_final = datos[columna_valor].iloc[-1]
            if ajustar_posy_capsu_fin != 0.0:
                y_final += ajustar_posy_capsu_fin

            valor_capsula = elimina_ceros_no_significativos(formato_decimal.format(datos[columna_valor].iloc[-1]))
            # Añadir símbolo de porcentaje si se solicita
            if simbolo_porce_capsu:
                valor_capsula = f"{valor_capsula}%"
            desplazamiento_tag = 0.2 + ajustar_posx_capsu_fin  # Usa el argumento para ajustar
            
            x_pos = ax.convert_xunits(x_final_global) + desplazamiento_tag
                
            if activar_cambiar_color:
                color_borde_texto_tag = cambiar_color(color_texto_capsula, fc_color if fc_color and str(fc_color).lower() != 'none' else '#ffffff')
                efectos_texto_tag = [path_effects.withStroke(linewidth=1.5, foreground=color_borde_texto_tag)] if color_borde_texto_tag else None
            else:
                efectos_texto_tag = None

            txt_tag = plt.text(
                x_pos,
                y_final,
                f"{espacio*2}{valor_capsula}{espacio*2}",
                fontsize=font_config['capsula_valor']['size'],
                color=color_texto_capsula,
                weight=font_config['capsula_valor']['weight'],
                ha='left',
                va='center',
                bbox=bbox_props,
                fontname=font_config['family'],
                path_effects=efectos_texto_tag
                )
            txt_tag.y_original = y_final
            all_texts.append(txt_tag)
            capsu_fin_texts.append(txt_tag)

    # Aplicar el algoritmo de posicionamiento
    if algoritmo_posicionamiento is not None and len(all_texts) > 0:
        x_coords = [t.get_position()[0] for t in all_texts]
        y_coords = [t.get_position()[1] for t in all_texts]
        
        # Calcular espaciado relativo al eje Y visible en vez de absoluto
        ymin, ymax = ax.get_ylim()
        espaciado_dinamico = (ymax - ymin) * ajustar_sep_capsu
        
        if algoritmo_posicionamiento == "algoritmo_posicionamiento_1" or algoritmo_posicionamiento == algoritmo_posicionamiento_1:
            _, nuevas_y = algoritmo_posicionamiento_1(x_coords, y_coords, espaciado_dinamico)
                
        elif algoritmo_posicionamiento == "algoritmo_posicionamiento_2" or algoritmo_posicionamiento == algoritmo_posicionamiento_2:
            _, nuevas_y = algoritmo_posicionamiento_2(x_coords, y_coords, espaciado_dinamico, capsu_en_max)
                
        elif callable(algoritmo_posicionamiento):
            # En caso de pasar otra función directamente
            _, nuevas_y = algoritmo_posicionamiento(x_coords, y_coords, espaciado_dinamico)
        else:
            nuevas_y = y_coords

        if ajustar_pos_capsu != 0.0:
            desplazamiento_global_dinamico = (ymax - ymin) * ajustar_pos_capsu
            for i, t in enumerate(all_texts):
                if nuevas_y[i] >= t.y_original:
                    nuevas_y[i] += desplazamiento_global_dinamico
                else:
                    nuevas_y[i] -= desplazamiento_global_dinamico

        for t, nuevo_y in zip(all_texts, nuevas_y):
            pos_x = t.get_position()[0]
            t.set_position((pos_x, nuevo_y))
    
    # --- Ajuste dinámico del límite inferior del eje Y ---
    # Asegura que las etiquetas más bajas no se superpongan con el eje X ni con sus valores
    if all_texts and algoritmo_posicionamiento in ["algoritmo_posicionamiento_2", algoritmo_posicionamiento_2]:
        min_y_text = min(t.get_position()[1] for t in all_texts)
        ymin_actual, ymax_actual = ax.get_ylim()
        
        # Consideramos un margen extra dinámico basado en el rango actual
        margen_inferior_necesario = (ymax_actual - ymin_actual) * ajustar_sep_con_ejex
        
        if (min_y_text - margen_inferior_necesario) < ymin_actual:
            ax.set_ylim(min_y_text - margen_inferior_necesario, ymax_actual)

    # Si capsu_fin == 'derecha', forzar alineación X de las etiquetas finales
    if capsu_fin == 'derecha':
        for txt in capsu_fin_texts:
            pos = txt.get_position()
            # Si el eje X son fechas (Timestamp de pandas u otros datetime), `pos[0]` puede seguir siendo referenciado como fecha 
            # internamente en get_position() antes de que se dibuje, por lo que usamos fechas sumando days, 
            # o si ya está traducido a número float por Matplotlib date2num le sumamos el float.
            import matplotlib.dates as mdates
            if isinstance(pos[0], pd.Timestamp) or 'datetime' in str(type(pos[0])):
                # Al convertir a número, 1 unidad = 1 día. Sumamos el desplazamiento como días.
                nuevo_x = mdates.num2date(mdates.date2num(pos[0]) + desplazamiento_tag * 100) # Escalado aproximado
            else:
                nuevo_x = pos[0] + desplazamiento_tag
            
            txt.set_position((nuevo_x, pos[1]))

    # Si capsu_fin == 'derecha' y leyenda_fin, extraer las coordenadas Y ajustadas
    if capsu_fin == 'derecha' and leyenda_fin:
        y_coords = [txt.get_position()[1] for txt in capsu_fin_texts]
    else:
        y_coords = None

     # Etiquetas y formato para el eje x (acepta fechas o enteros o cadenas)
    valores_x = df[columna_fecha].unique()
    original_len = len(valores_x)

    indices = None
    if reducir_ticks_ejex:
        n_ticks = len(valores_x)
        # Si es un entero, lo usamos como el número de divisiones (nbins), si no, usamos 5 por defecto
        nbins = reducir_ticks_ejex if (isinstance(reducir_ticks_ejex, int) and not isinstance(reducir_ticks_ejex, bool)) else 5
        if n_ticks > nbins:
            indices = [int(round(i * (n_ticks - 1) / (nbins - 1))) for i in range(nbins)]
            indices = sorted(list(set(indices)))
            valores_x = [valores_x[idx] for idx in indices]

    if pd.api.types.is_integer_dtype(df[columna_fecha]):
        etiquetas_x = [str(x) for x in valores_x]
    else:
        etiquetas_x = formato_fechas(valores_x, modalidad=modalidad_fechas, mostrar_solo=mostrar_solo_fechas)

    # Sustitución de etiquetas del eje X si se proporciona una lista.
    if sustituir_valor_ejex:
        if len(sustituir_valor_ejex) == original_len and indices is not None:
            etiquetas_x = [sustituir_valor_ejex[idx] for idx in indices]
        elif len(sustituir_valor_ejex) == len(etiquetas_x):
            etiquetas_x = list(sustituir_valor_ejex)
        else:
            raise ValueError(f"La longitud de 'sustituir_valor_ejex' ({len(sustituir_valor_ejex)}) debe coincidir con el número de etiquetas en X ({len(etiquetas_x)}).")

    # Manejo de la rotación basada en grados numéricos (-90 a 90)
    rotation_val = float(orientacion_valor_ejex)
    # Limitar entre -90 y 90
    rotation_val = max(-90.0, min(90.0, rotation_val))

    # Ajuste de alineación horizontal (ha) según rotación
    if rotation_val == 0:
        ha_val = 'center'
    elif rotation_val > 0:
        ha_val = 'right'
    else:
        ha_val = 'left'

    # Aplicar límites del eje y si se especifican
    if limites_ejey is not None:
        ax.set_ylim(limites_ejey)

    # Reducir el número de ticks en el eje Y si se solicita, priorizando enteros
    if reducir_ticks_ejey:
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='both', integer=True))

    # Etiquetas y formato para el eje y
    if sustituir_etiquetas_ejey is not None:
        min_tick = ax.get_ylim()[0]
        max_tick = ax.get_ylim()[1]
        n_etiquetas = len(sustituir_etiquetas_ejey)
        def y_formatter(x, _):
            idx = int(round((x - min_tick) / (max_tick - min_tick) * (n_etiquetas - 1)))
            if 0 <= idx < n_etiquetas:
                return sustituir_etiquetas_ejey[idx]
            return ""
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(y_formatter))
    else:
        # Formato con el número de decimales especificado y separador de miles
        if simbolo_porce_ejey:
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{elimina_ceros_no_significativos(formato_decimal.format(x))}%"))
        else:
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: elimina_ceros_no_significativos(formato_decimal.format(x))))
        #ax.ticklabel_format(style='plain', axis='y')  # <-- Evita notación científica


    # --- Graficar líneas verticales ---
    if lineas_verticales is not None:
        for linea in lineas_verticales:
            ax.axvline(
                x=linea.get('x', 0),
                color=linea.get('color', '#DC8F12'),
                linewidth=linea.get('linewidth', 2),
                linestyle=linea.get('linestyle', '--'),
                alpha=linea.get('alpha', 1),
                zorder=linea.get('zorder', 0)
            )

    plt.xticks(
        ticks=valores_x,
        labels=etiquetas_x,
        rotation=rotation_val,
        ha=ha_val,
        fontsize=font_config['variable_x']['size'],
        weight=font_config['variable_x']['weight'],
        color=font_config['variable_x']['color'],
        fontname=font_config['family']  
    )
    plt.yticks(
        fontsize=font_config['variable_y']['size'],
        weight=font_config['variable_y']['weight'],
        color=font_config['variable_y']['color'],
        fontname=font_config['family'] 
    )

    if nombre_ejex:
        ax.set_xlabel(nombre_ejex, fontsize=tam_nombre_ejex, weight=peso_nombre_ejex, color=font_config['variable_x']['color'], fontname=font_config['family'])
    
    if nombre_ejey:
        ax.set_ylabel(nombre_ejey, fontsize=tam_nombre_ejey, weight=peso_nombre_ejey, color=font_config['variable_y']['color'], fontname=font_config['family'])

    # --- Mostrar u ocultar las marcas de los ejes (ticks) ---
    if not marcas_ejes:
        ax.tick_params(axis='x', which='both', length=0)
        ax.tick_params(axis='y', which='both', length=0)

    if not marcas_graduacion_ejex:
        ax.tick_params(axis='x', which='both', length=0)


    if leyenda_fin:
        leyenda_texts = []
        for i, var in enumerate(variables):
            datos = df[df[columna_variable] == var]
            x_final = datos[columna_fecha].iloc[-1]
            # Si capsu_fin es 'derecha' y leyenda_fin, usar el mismo Y que la etiqueta final ajustada
            if capsu_fin == 'derecha' and y_coords is not None:
                y_final = y_coords[i]
            else:
                y_final = datos[columna_valor].iloc[-1]
                
            # Renderizamos primero en x_final para que Matplotlib lo traduzca a número float sin importar el tipo
            x_final_ajustado = x_final
            texto_leg = ax.text(
                x_final_ajustado, y_final,
                f"  {var}",
                color=color_map[var],
                fontsize=font_config['leyenda']['size'],
                fontweight=font_config['leyenda']['weight'],
                va='center',
                ha='left',
                fontname=font_config['family']
            )
            # Aplicar el desplazamiento iterativo en coordenadas reales del gráfico
            pos_leyenda = ax.convert_xunits(texto_leg.get_position()[0])
            texto_leg.set_position((pos_leyenda + ajustar_posx_leyenda_fin, texto_leg.get_position()[1]))
            leyenda_texts.append(texto_leg)
            
    if leyenda:
        from matplotlib.patches import Patch
        handles_leyenda = [Patch(color=color_map[var], label=var) for var in variables]
        leg = ax.legend(
            handles=handles_leyenda,
            loc='upper center',
            bbox_to_anchor=posicion_leyenda,
            ncol=num_columnas_leyenda if num_columnas_leyenda is not None else len(variables),
            frameon=False,
            handlelength=1.0,
            handleheight=1.0,
            prop={
                'size': font_config['leyenda']['size'],
                'weight': font_config['leyenda']['weight'],
                'family': font_config['family']
            }
        )
        for text in leg.get_texts():
            text.set_color(font_config['leyenda']['color'])  
            
    # Ajuste manual de separación vertical entre etiquetas finales (mayores arriba, menores abajo)
    if ajustar_sep_capsu_fin != 0.0 and len(capsu_fin_texts) > 1:
        posiciones = [txt.get_position() for txt in capsu_fin_texts]
        orden = sorted(range(len(posiciones)), key=lambda i: -posiciones[i][1])  # mayor Y arriba
        posiciones_ordenadas = [posiciones[i] for i in orden]
        textos_ordenados = [capsu_fin_texts[i] for i in orden]
        x_vals = [x for x, y in posiciones_ordenadas]
        y_centro = sum([y for x, y in posiciones_ordenadas]) / len(posiciones_ordenadas)
        for i, txt in enumerate(textos_ordenados):
            # Invertir el desplazamiento para que el primero (mayor) quede arriba
            nuevo_y = y_centro - ajustar_sep_capsu_fin * (i - (len(textos_ordenados)-1)/2)
            txt.set_position((x_vals[i], nuevo_y))

    if margen:
        for spine in ['top', 'right', 'left', 'bottom']:
            ax.spines[spine].set_visible(True)
            ax.spines[spine].set_linewidth(margen_ancho)
            ax.spines[spine].set_color(margen_color)
    else:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_linewidth(margen_ancho)
        ax.spines['bottom'].set_color(margen_color)


    if grillas:
        ax.grid(axis='y', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)
    
    ax.yaxis.set_ticks_position('left')
    
    exacto = True if (ancho is not None or alto is not None) else False
    return mostrar_guardar_figura(
        fig=fig, ax=ax, 
        nombre_df=nombre, 
        guardar_fig=guardar, 
        mostrar_fig=mostrar, 
        limpiar_svg_con_scour=limpiar_svg_con_scour,
        exact_dim=exacto
    )
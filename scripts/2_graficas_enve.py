# ————————————————————————————————————————————————————————— #
# Nombre: Jocelyn Rocha
# Contacto: jocelyn.flores@transformaciondigital.gob.mx
# Script: 2_graficas_enve.py
# Proyecto: Victimización de empresas | ENVE Principales resultados
# Fecha: 2026-11-11
# Propósito: Generar las gráficas de victimización de empresas (ENVE, INEGI) con las funciones de Pabloplot.
#            Se corre desde scripts/2_graficas_enve.R, que arma el manifiesto de gráficas.
# ————————————————————————————————————————————————————————— #
# PREÁMBULO -------
# ————————————————————————————————————————————————————————— #

import os
import sys
import locale
import math
import traceback
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                          # sin ventanas: corre desde R
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
import matplotlib.transforms as mtransforms
import pandas as pd

# barras_horizontales() llama plt.show(); con Agg solo genera este aviso.
warnings.filterwarnings("ignore", message=".*non-interactive.*")


# PARÁMETROS QUE LLEGAN DESDE R ______________ ----
def env(nombre, defecto=None):
    valor = os.environ.get(nombre, defecto)
    if valor is None or valor == "":
        sys.exit(f"ERROR: falta la variable de entorno {nombre}. Corre este script desde "
                 f"scripts/2_graficas_enve.R")
    return valor


RAIZ          = Path(env("ENVE_RAIZ")).resolve()
DIR_FUNCIONES = Path(env("ENVE_DIR_FUNCIONES")).resolve()
MANIFIESTO    = Path(env("ENVE_MANIFIESTO")).resolve()

# Pabloplot guarda en "output/<nombre>" RELATIVO a la carpeta actual.
# R lanza este proceso parado en la raíz; aquí solo se verifica (sin os.chdir).
if Path.cwd().resolve() != RAIZ:
    sys.exit(f"ERROR: el proceso corre en {Path.cwd()} y debe correr en {RAIZ}.")


# LOCALE A PRUEBA DE WINDOWS ______________ ----
# funciones.py pide locale 'es_ES.UTF-8', que no existe en Windows. Se prueban
# variantes y, si ninguna existe, se deja el locale actual sin tronar.
_setlocale_original = locale.setlocale


def _setlocale_seguro(categoria, loc=None):
    if loc is None:
        return _setlocale_original(categoria)
    for candidato in [loc, "es_MX.UTF-8", "es_ES.UTF-8", "es_MX", "es_ES",
                      "Spanish_Mexico.1252", "Spanish_Spain.1252", "Spanish"]:
        try:
            return _setlocale_original(categoria, candidato)
        except locale.Error:
            continue
    return _setlocale_original(categoria)


locale.setlocale = _setlocale_seguro


# FUNCIONES DE PABLOPLOT Y FUENTES  ______________ ----
sys.path.insert(0, str(DIR_FUNCIONES))
from barras_horizontales import barras_horizontales   # noqa: E402
from barras_verticales import barras_verticales       # noqa: E402
from lineas import lineas                             # noqa: E402
from funciones import exportar_grafica, limpiar_svg_con_scour   # noqa: E402

for archivo_fuente in font_manager.findSystemFonts(fontpaths=[str(DIR_FUNCIONES.parent / "0_fonts")]):
    font_manager.fontManager.addfont(archivo_fuente)

mpl.rcParams["font.family"] = "Montserrat"
mpl.rcParams["svg.fonttype"] = "none"              # texto editable en el SVG


# ————————————————————————————————————————————————————————— #
# ESTILO -------
# ————————————————————————————————————————————————————————— #

TAMANOS = {                       # cm, medidos de las imágenes de la PPT
    "barras_horizontales_slide_1": (10.6, 5.5),
    "barras_violencia_slide_2":    (19.02, 8.55),
    "barras_tamanio_slide_2_5":    (30.51, 13.08),   # provisional: ajustar a la PPT
    "flechas_percepcion_slide_3":  (10.05, 11.87),     # provisional: cada una de las 2 gráficas
    "lineas_costos_slide_4":       (24.48, 13.93),     # provisional: ajustar a la PPT
}

COLOR_TEXTO = "#434343"           # gris de textos de Pabloplot
COLOR_EJES = "#393939"            # líneas, marcas y textos de los ejes X y Y (slides 2 y 2.5)


def colorear_ejes(ax, color=COLOR_EJES):
    """Pinta de `color` las líneas de los ejes (spines), sus marcas y sus textos."""
    for lado in ("left", "bottom", "top", "right"):
        ax.spines[lado].set_color(color)
    ax.tick_params(axis="both", which="both", colors=color, labelcolor=color)

ANCHO_BARRA = 0.7

# Si una barra mide menos de esta fracción de la barra más larga, su valor se
# escribe fuera (no cabe adentro). Pabloplot compara área = valor * ancho_barra.
UMBRAL_VALOR_FUERA = 0.18

COLORES_TIPO = {
    "aumentos":      "#9B2247",   # rojo: la incidencia subió
    "disminuciones": "#006157",   # verde: la incidencia bajó
}


def paso_redondo(rango, n_marcas=4):
    """Paso 'redondo' (1, 2 o 5 x 10^k) para que el eje tenga ~n_marcas divisiones
    y las etiquetas (con signo) no se encimen."""
    crudo = abs(rango) / n_marcas
    if crudo == 0:
        return None
    magnitud = 10 ** math.floor(math.log10(crudo))
    return next(m * magnitud for m in (1, 2, 5, 10) if m * magnitud >= crudo)


COLORES_VIOLENCIA = {
    "Delitos sin violencia": "#002F2A",
    "Delitos con violencia": "#611232",
}


# Texto junto a la cápsula: "XXX" en negritas y debajo la unidad
UNIDAD_SLIDE_2 = "mil"

# Color de "XXX mil delitos": None = el color de su barra (COLORES_VIOLENCIA);
# o un HEX fijo para las tres barras, p. ej. COLOR_TEXTO ("#434343").
COLOR_MILES_SLIDE_2 = None

# Alto de la cápsula como fracción del grosor de la barra
ALTO_CAPSULA_SLIDE_2 = 0.4

# Etiquetas del eje Y con saltos de línea a mano (texto del tabulado -> como se muestra)
ETIQUETAS_EJEY_SLIDE_2 = {
    "Delitos con agresión física":      "Delitos con agresión\nfísica",
    "Delitos con amenaza de violencia": "Delitos con amenaza\nde violencia",
}

# ---- SLIDE 2.5 ---- #
# Paleta para los delitos; COLOR_EXTORSION queda reservado para "Extorsión" y
# el resto se asigna en el orden del tabulado (más frecuentes primero).
PALETA_SLIDE_2_5 = ["#161A1D", "#A57F2C", "#2F5D8C", "#851A36", "#6A93BF"]
COLOR_EXTORSION  = "#851A36"
ANCHO_BARRA_SLIDE_2_5 = 0.7      # < 0.85 deja un respiro entre barras del mismo grupo
PASO_EJEY_SLIDE_2_5 = 10         # marcas del eje Y cada 10%
TAM_EJEY_SLIDE_2_5 = 16          # tamaño de letra de las marcas del eje Y
COLOR_EJEY_SLIDE_2_5 = COLOR_EJES  # eje Y (texto, línea y remates); por defecto el de COLOR_EJES
PESO_EJEY_SLIDE_2_5 = "normal"   # grosor de las marcas del eje Y ("light", "normal", "medium"...)
LARGO_REMATE_EJEY_SLIDE_2_5 = 0.008  # largo de los remates (fracción del ancho del eje)
COLOR_GRID_SLIDE_2_5 = "#D9D9D9" # líneas horizontales de la cuadrícula (una por marca del eje Y)
# Etiqueta arriba de cada barra: "26.9%" (negritas) y debajo "708 mil" (más chico)
TAM_PCT_SLIDE_2_5 = 14           # tamaño del porcentaje
TAM_ABS_SLIDE_2_5 = 11           # tamaño de la cifra absoluta
SEP_ETIQUETA_SLIDE_2_5 = 4       # separación entre la barra y la etiqueta (puntos)
MARGEN_SUP_SLIDE_2_5 = 1.3       # tope del eje Y = barra más alta x este factor (espacio para la etiqueta)


def colores_delitos(delitos, paleta=PALETA_SLIDE_2_5, reservados={"Extorsión": COLOR_EXTORSION}):
    """Asigna un color a cada delito: los reservados primero; el resto toma los
    colores libres de la paleta en orden."""
    libres = [c for c in paleta if c not in reservados.values()]
    sin_reserva = [d for d in delitos if d not in reservados]
    if len(sin_reserva) > len(libres):
        raise ValueError(f"Hay {len(sin_reserva)} delitos sin color reservado y solo {len(libres)} colores libres")
    asignados = dict(zip(sin_reserva, libres))
    return {d: reservados.get(d, asignados.get(d)) for d in delitos}


def miles(valor):
    """453592.67 -> '453' (miles completos, sin redondear hacia arriba)."""
    return f"{math.floor(valor / 1000):,}"


def color_por_tipo(tipo):
    """Color de la barra según el tabulado de origen (top de aumentos o de disminuciones)."""
    try:
        return COLORES_TIPO[tipo]
    except KeyError:
        raise ValueError(f"Tipo '{tipo}' sin color. Opciones: {list(COLORES_TIPO)}") from None


# ————————————————————————————————————————————————————————— #
# GRÁFICAS -------
# ————————————————————————————————————————————————————————— #

def barras_horizontales_slide_1(fila):
    """Top 5 de entidades con mayor aumento o disminución en la tasa de
    incidencia delictiva (2023 vs 2025) para un tipo de delito."""
    df = pd.read_csv(fila.tabulado, encoding="utf-8-sig")
    df = df[df["tipo_de_delito"] == fila.tipo_de_delito]
    if df.empty:
        raise ValueError(f"'{fila.tipo_de_delito}' no tiene filas en {fila.tabulado}")

    # Se grafica la diferencia con su signo: las disminuciones son barras
    # negativas (hacia la izquierda) y su valor se escribe con "-".
    datos = (df.sort_values("posicion")
               .rename(columns={"diferencia_tasa_delictiva": "diferencia"})
               [["entidad_federativa", "diferencia"]]
               .reset_index(drop=True))
    es_disminucion = bool((datos["diferencia"] < 0).all())   # bool nativo: Pabloplot rechaza numpy.bool_

    ancho, alto = TAMANOS["barras_horizontales_slide_1"]
    areamin = UMBRAL_VALOR_FUERA * datos["diferencia"].abs().max() * ANCHO_BARRA
    # Con valores negativos Pabloplot hace un eje simétrico; se recorta a [mín, 0]
    # para que las barras usen todo el ancho.
    limites_ejex = (datos["diferencia"].min() * 1.1, 0) if es_disminucion else None

    barras_horizontales(
        datos,
        nombre=fila.grafica,
        ancho=ancho,
        alto=alto,
        ancho_barra=ANCHO_BARRA,
        colores=[color_por_tipo(fila.tipo)],
        ordenar="x",
        ascendente=es_disminucion,    # el cambio más grande (en valor absoluto) arriba
        decimales=0,
        tipo_letra="Montserrat",
        peso_nombre_ejey="light",
        tam_valor_ejex=12,
        tam_valor_ejey=11,
        tam_valor_capsu=9,
        ajustar_pos_capsu=0.015,
        valor_barra=True,
        simbolo_negativo_barra=True,
        porce_barra=False,
        porce_total=False,
        leyenda=False,
        valor_capsu=False,
        areamin=areamin,
        solo_ejex_positivo=False,     # el eje también muestra el signo
        limites_ejex=limites_ejex,
        divisiones_ejex=paso_redondo(datos["diferencia"].abs().max()),
        ajustar_sep_valor_barra=2.2,
    )
    plt.close("all")


def barras_violencia_slide_2(fila):
    """Delitos sin violencia (1 barra) vs con violencia (agresión física y
    amenaza), agrupadas en el eje Y.
    1) Pabloplot dibuja las barras y el porcentaje en cápsulas al final de cada barra.
    2) Sobre la figura ya hecha se agrega "XX mil delitos" a un lado de cada
       cápsula (número en negritas, unidad en letra normal) y se vuelve a guardar."""
    df = pd.read_csv(fila.tabulado, encoding="utf-8-sig")
    df = df[df["tipo_de_delito"] == fila.tipo_de_delito].sort_values("orden").reset_index(drop=True)
    if df.empty:
        raise ValueError(f"'{fila.tipo_de_delito}' no tiene filas en {fila.tabulado}")

    # Pabloplot: la 1a columna es el eje Y (una etiqueta por barra); una columna
    # de valores por grupo para que cada grupo tenga su color.
    grupos = list(COLORES_VIOLENCIA)
    datos = pd.DataFrame({"etiqueta": df["etiqueta"]})
    for g in grupos:
        datos[g] = df["porcentaje"].where(df["grupo"] == g, 0)
    colores = [COLORES_VIOLENCIA[g] for g in grupos]

    ancho, alto = TAMANOS["barras_violencia_slide_2"]
    barras_horizontales(
        datos,
        nombre=fila.grafica,
        ancho=ancho,
        alto=alto,
        fondo="transparent",
        colores=colores,
        ordenar=None,                       # respeta el orden del tabulado
        ancho_barra=ANCHO_BARRA,
        decimales=1,
        tipo_letra="Montserrat",
        grillas=False,
        valor_barra=False,                  # el % va en la cápsula, no dentro
        valor_capsu=True,
        simbolo_porce_capsu=True,
        tam_valor_capsu=11,
        color_valor_capsu=COLOR_TEXTO,
        color_borde_capsu=colores,          # borde del color de su barra
        ajustar_pos_capsu=0.045,             # separa la cápsula de la barra
        tam_valor_ejey=13,
        saltos_linea_cada_x_palabras=6,     # etiquetas en una sola línea
        peso_valor_ejey="medium",
        leyenda=False,
        limites_ejex=(0, df["porcentaje"].max() * 1.7),   # espacio para "xxx mil delitos"
    )

    # ---- Capa posterior: "XX mil delitos" a un lado de cada cápsula ----
    ax = plt.gca()

    # Saltos de línea propios en el eje Y (Pabloplot los re-arma por palabras)
    ax.set_yticks(ax.get_yticks(),
                  [ETIQUETAS_EJEY_SLIDE_2.get(t.get_text(), t.get_text())
                   for t in ax.get_yticklabels()])
    # Pabloplot reservó el margen izquierdo con las etiquetas en un renglón;
    # se recalcula para que las barras usen el espacio que liberan los saltos.
    plt.gcf().tight_layout()
    capsulas = sorted((t for t in ax.texts if t.get_bbox_patch() is not None),
                      key=lambda t: t.get_position()[1])      # mismo orden que df (de arriba abajo)
    if len(capsulas) != len(df):
        raise RuntimeError(f"Esperaba {len(df)} cápsulas y Pabloplot dibujó {len(capsulas)}")

    # Tamaño de letra de las cápsulas según el grosor de la barra (en puntos).
    # La cápsula mide ~1.3 veces el tamaño de letra (texto + relleno de Pabloplot).
    barra = next(p for p in ax.patches if p.get_width() > 0)
    y0, y1 = ax.transData.transform([(0, 0), (0, barra.get_height())])[:, 1]
    grosor_pt = abs(y1 - y0) * 72 / plt.gcf().dpi
    tam_capsula = ALTO_CAPSULA_SLIDE_2 * grosor_pt / 1.3

    for capsula, r in zip(capsulas, df.itertuples()):

        capsula.set_fontsize(tam_capsula)
        color_miles = COLOR_MILES_SLIDE_2 or COLORES_VIOLENCIA[r.grupo]

        # "XXX" en negritas y abajo "mil delitos", alineados a la izquierda
        numero = ax.annotate(miles(r.absolutos), xy=(1, 0.5), xycoords=capsula,
                             xytext=(10, -1), textcoords="offset points",
                             ha="left", va="bottom", fontsize=15, fontweight="bold",
                             color=color_miles)
        ax.annotate(UNIDAD_SLIDE_2, xy=(0, 0), xycoords=numero,
                    xytext=(0, 1), textcoords="offset points",
                    ha="left", va="top", fontsize=11, fontweight="normal", color=color_miles)

    ax.xaxis.set_visible(False)
    colorear_ejes(ax)

    with mpl.rc_context({"savefig.transparent": True}):
        exportar_grafica(fila.grafica, limpiar_svg_con_scour, exact_dim=True)
    plt.close("all")


def barras_tamanio_slide_2_5(fila):
    """Barras verticales agrupadas por tamaño de empresa; dentro de cada grupo,
    una barra por delito (% de los delitos ocurridos en ese tamaño).
    1) Pabloplot dibuja las barras, la cápsula con el % y la leyenda.
    2) Sobre la figura ya hecha se escribe "XXX mil delitos" dentro de cada
       barra (vertical, número en negritas y unidad normal) y se guarda."""
    df = (pd.read_csv(fila.tabulado, encoding="utf-8-sig")
            .sort_values(["orden_tamanio", "orden_delito"]))
    tamanios = df.drop_duplicates("tamanio_empresa")["tamanio_empresa"].tolist()
    delitos  = (df.sort_values("orden_delito")
                  .drop_duplicates("tipo_de_delito")["tipo_de_delito"].tolist())
    color_de = colores_delitos(delitos)

    # Pabloplot agrupa las filas consecutivas con la misma etiqueta en X y solo
    # dibuja las barras que existen (sin huecos). Una fila por barra y una
    # columna por delito (0 en las demás) para que cada barra tome su color.
    datos = pd.DataFrame({"tamanio_empresa": df["tamanio_empresa"].values})
    for d in delitos:
        datos[d] = df["porcentaje"].where(df["tipo_de_delito"] == d, 0).values
    colores = [color_de[d] for d in delitos]

    ancho, alto = TAMANOS["barras_tamanio_slide_2_5"]
    fig, ax = barras_verticales(
        datos,
        nombre=fila.grafica,
        ancho=ancho,
        alto=alto,
        fondo="transparent",
        colores=colores,
        ancho_barra=ANCHO_BARRA_SLIDE_2_5,
        ordenar=None,                     # respeta el orden del tabulado
        decimales=1,
        tipo_letra="Montserrat",
        grillas=False,
        valor_barra=False,
        valor_capsu=False,                # sin cápsulas: la etiqueta se pone después
        tam_valor_ejex=12,
        leyenda=False,
        num_columnas_leyenda=3,
        posicion_leyenda={"loc": "upper center", "bbox_to_anchor": (0.5, -0.12)},
        tam_letra_leyenda=9,
        guardar=False,
        mostrar=False,
    )

    # Eje Y discreto: "0% ... XX%" en gris, línea delgada que termina en la
    # última marca, con remates cortos arriba y abajo; cuadrícula horizontal atrás.
    ax.grid(False)
    ax.set_axisbelow(True)                 # la cuadrícula queda detrás de las barras
    ax.grid(True, axis="y", color=COLOR_GRID_SLIDE_2_5, linewidth=0.75, linestyle="-")
    ax.spines[["top", "right"]].set_visible(False)
    y_max = df["porcentaje"].max()
    ax.set_ylim(0, y_max * MARGEN_SUP_SLIDE_2_5)   # espacio para la etiqueta de arriba

    paso = PASO_EJEY_SLIDE_2_5
    tope_eje = paso * math.floor(ax.get_ylim()[1] / paso)
    marcas = [paso * i for i in range(int(tope_eje / paso) + 1)]
    ax.yaxis.set_visible(True)
    ax.set_yticks(marcas, [f"{m:g}%" for m in marcas])
    ax.tick_params(axis="y", which="major", length=0, pad=6, labelsize=TAM_EJEY_SLIDE_2_5,
                   labelcolor=COLOR_EJEY_SLIDE_2_5)
    for etiq in ax.get_yticklabels():
        etiq.set_fontweight(PESO_EJEY_SLIDE_2_5)
    ax.spines["left"].set_visible(True)
    ax.spines["left"].set_bounds(0, tope_eje)
    ax.spines["left"].set_color(COLOR_EJEY_SLIDE_2_5)
    ax.spines["left"].set_linewidth(0.8)
    # Remates cortos hacia adentro en 0% y en la última marca (como "[")
    trans = mtransforms.blended_transform_factory(ax.transAxes, ax.transData)
    for y in (0, tope_eje):
        ax.plot([0, LARGO_REMATE_EJEY_SLIDE_2_5], [y, y], transform=trans,
                color=COLOR_EJEY_SLIDE_2_5, linewidth=0.8, clip_on=False, zorder=3)

    # Recalcula márgenes con las etiquetas del eje Y ya puestas (si se agranda la
    # letra, "40%" no se corta). Va antes de la capa posterior: esa mide las barras.
    fig.tight_layout()

    # ---- Capa posterior: una etiqueta horizontal arriba de cada barra ----
    #   26.9%      <- porcentaje, negritas
    #   708 mil    <- cifra absoluta, más chica
    # Ambas en el color de su barra, sin cápsula ni contorno.
    barras = sorted((p for p in ax.patches if p.get_height() > 0), key=lambda b: b.get_x())
    filas = list(df.itertuples())                              # mismo orden: tamaño, delito
    if len(barras) != len(filas):
        raise RuntimeError(f"Esperaba {len(filas)} barras y Pabloplot dibujó {len(barras)}")

    etiquetas = []
    for barra, r in zip(barras, filas):
        x = barra.get_x() + barra.get_width() / 2
        color = color_de[r.tipo_de_delito]
        absoluto = ax.annotate(f"{miles(r.absolutos)} mil", xy=(x, barra.get_height()),
                               xytext=(0, SEP_ETIQUETA_SLIDE_2_5), textcoords="offset points",
                               ha="center", va="bottom", fontsize=TAM_ABS_SLIDE_2_5,
                               fontweight="normal", color=color)
        porcentaje = ax.annotate(f"{r.porcentaje:.1f}%", xy=(0.5, 1), xycoords=absoluto,
                                 xytext=(0, 1), textcoords="offset points",
                                 ha="center", va="bottom", fontsize=TAM_PCT_SLIDE_2_5,
                                 fontweight="bold", color=color)
        etiquetas.append((barra, porcentaje))

    # Avisos: etiquetas vecinas que se enciman (bajar TAM_PCT_SLIDE_2_5) o que
    # se salen por arriba (subir MARGEN_SUP_SLIDE_2_5).
    renderer = fig.canvas.get_renderer()
    tope_ejes = ax.get_window_extent(renderer).y1
    cajas = [porcentaje.get_window_extent(renderer) for _, porcentaje in etiquetas]
    for (_, izq), (_, der), c_izq, c_der in zip(etiquetas, etiquetas[1:], cajas, cajas[1:]):
        se_tocan_en_y = c_izq.y0 < c_der.y1 and c_der.y0 < c_izq.y1
        if se_tocan_en_y and c_izq.x1 > c_der.x0:
            print(f"  Aviso slide 2.5: '{izq.get_text()}' y '{der.get_text()}' se enciman; "
                  "baja TAM_PCT_SLIDE_2_5")
    for (_, porcentaje), caja in zip(etiquetas, cajas):
        if caja.y1 > tope_ejes:
            print(f"  Aviso slide 2.5: '{porcentaje.get_text()}' se sale por arriba; sube MARGEN_SUP_SLIDE_2_5")

    colorear_ejes(ax)

    with mpl.rc_context({"savefig.transparent": True}):
        exportar_grafica(fila.grafica, limpiar_svg_con_scour, exact_dim=True)
    plt.close("all")


# ---- SLIDE 3 ---- #
COLOR_ANTERIOR_SLIDE_3 = "#6B6B6B"   # cápsula y texto del año anterior (2024)
PESO_NUEVO_SLIDE_3 = "bold"          # grosor del número 2026 ("normal", "medium", "semibold", "bold")
PESO_ANTERIOR_SLIDE_3 = "bold"       # grosor del número 2024
ESPACIOS_CAPSULA_SLIDE_3 = 0         # espacios duros extra a cada lado del número (alargan la cápsula)
PAD_CAPSULA_SLIDE_3 = 0.45           # relleno de la cápsula (fracción del tamaño de letra): más = más gruesa
REDONDEO_CAPSULA_SLIDE_3 = 0.9       # radio de las esquinas (en tamaños de letra); ~1 = píldora
TAM_PUNTO_SLIDE_3 = 5                # diámetro (pt) del punto de inicio (valor 2024)
COLOR_NACIONAL_SLIDE_3 = "#9E9E9E"   # línea punteada del valor nacional 2026
TAM_ENTIDAD_SLIDE_3 = 9              # tamaño de los nombres de las entidades
TAM_CAPSULA_SLIDE_3 = 9            # tamaño del texto de las cápsulas
GROSOR_FLECHA_SLIDE_3 = 2.0          # grosor de la flecha
LIMITES_X_SLIDE_3 = (0, 100)         # marcas del eje X; el área se amplía sola para que quepan las cápsulas
PASO_X_SLIDE_3 = 20                  # marcas del eje X cada 20%


def flechas_percepcion_slide_3(fila):
    """Percepción de inseguridad por entidad: punto en el valor 2024 y flecha al
    2026; cápsula gris con 2024 y cápsula del color del cambio con 2026 (rojo si
    aumentó, verde si bajó). Una gráfica por panel (16 entidades cada una), con
    la línea punteada del valor nacional 2026. Pabloplot no tiene este tipo de
    gráfica (lineas() es para series en el tiempo): se dibuja con matplotlib en su estilo.
    Los dos paneles comparten márgenes y límites del eje X para alinearse en la slide."""
    todas = pd.read_csv(fila.tabulado, encoding="utf-8-sig").sort_values("orden")
    df = todas[todas["panel"] == int(fila.panel)].reset_index(drop=True)
    if df.empty:
        raise ValueError(f"El panel {fila.panel} no tiene filas en {fila.tabulado}")

    ancho, alto = TAMANOS["flechas_percepcion_slide_3"]
    fig, ax = plt.subplots(figsize=(ancho / 2.54, alto / 2.54), dpi=300)
    ys = list(range(len(df)))                       # 0 = arriba (eje invertido)
    espacio = "\u00A0" * ESPACIOS_CAPSULA_SLIDE_3   # espacios duros: ensanchan la cápsula
    sep_nuevo, sep_anterior = 4, 4 + TAM_PUNTO_SLIDE_3 / 2   # puntos entre punto y cápsula
    caja = {"boxstyle": f"round,pad={PAD_CAPSULA_SLIDE_3},rounding_size={REDONDEO_CAPSULA_SLIDE_3}",
            "facecolor": "#FFFFFF", "linewidth": 1.5}

    def texto_capsula(valor):
        return f"{espacio}{valor:.1f}%{espacio}"

    # ---- 1. Ejes y márgenes (antes de dibujar: de ellos depende la escala) ----
    ax.set_ylim(len(df) - 0.5, -0.6)
    ax.set_yticks(ys, df["entidad_federativa"])
    marcas = list(range(LIMITES_X_SLIDE_3[0], LIMITES_X_SLIDE_3[1] + 1, PASO_X_SLIDE_3))
    ax.set_xlim(*LIMITES_X_SLIDE_3)
    ax.set_xticks(marcas, [f"{m}%" for m in marcas])
    # Tamaños con tick_params (no con fontsize=): mover la línea del eje
    # (set_position) recrea las marcas y un fontsize= se perdería.
    ax.tick_params(axis="y", length=0, pad=8, labelsize=TAM_ENTIDAD_SLIDE_3)
    ax.tick_params(axis="x", length=0, pad=4, labelsize=TAM_ENTIDAD_SLIDE_3 - 1)
    ax.spines[["top", "right", "bottom"]].set_visible(False)
    ax.spines["left"].set_linewidth(0.8)

    # Mismo margen izquierdo en los dos paneles: el nombre más ANCHO de TODAS las
    # entidades (se miden todos; el de más letras no siempre es el más ancho)
    fig.tight_layout()
    renderer = fig.canvas.get_renderer()
    pruebas = [ax.text(0, 0, nombre, fontsize=TAM_ENTIDAD_SLIDE_3) for nombre in todas["entidad_federativa"]]
    ancho_nombre = max(t.get_window_extent(renderer).width for t in pruebas)
    for t in pruebas:
        t.remove()
    pad_px = (8 + 6) * fig.dpi / 72
    fig.subplots_adjust(left=(ancho_nombre + pad_px) / fig.bbox.width)

    # ---- 2. Límites del eje X para que quepan TODAS las cápsulas (de los dos
    # paneles, así ambos quedan con la misma escala). El ancho de una cápsula en
    # pixeles no depende de la escala, así que se mide una vez y se itera.
    pt_px = fig.dpi / 72
    temporales = []
    for r in todas.itertuples():
        sube = r.inseguro_2026 > r.inseguro_2024
        for valor, peso, sep, lado in ((r.inseguro_2026, PESO_NUEVO_SLIDE_3, sep_nuevo, "der" if sube else "izq"),
                                       (r.inseguro_2024, PESO_ANTERIOR_SLIDE_3, sep_anterior, "izq" if sube else "der")):
            t = ax.text(0, 0, texto_capsula(valor), fontsize=TAM_CAPSULA_SLIDE_3,
                        fontweight=peso, bbox={**caja, "edgecolor": "#000000"})
            temporales.append((t, valor, sep, lado))
    fig.canvas.draw()
    necesidades = [(valor, lado, t.get_bbox_patch().get_window_extent(renderer).width + sep * pt_px + 2)
                   for t, valor, sep, lado in temporales]
    if int(fila.panel) == 1:                       # tamaño típico de cápsula, para comparar con la PPT
        cajas = [t.get_bbox_patch().get_window_extent(renderer) for t, *_ in temporales]
        px_cm = fig.dpi / 2.54
        ancho_cm = sorted(c.width for c in cajas)[len(cajas) // 2] / px_cm
        alto_cm = cajas[0].height / px_cm
        print(f"  Slide 3 | cápsula típica: {ancho_cm:.2f} x {alto_cm:.2f} cm "
              f"(proporción {ancho_cm / alto_cm:.1f}:1)")
    for t, *_ in temporales:
        t.remove()

    ancho_ejes_px = ax.get_window_extent(renderer).width
    x_min, x_max = LIMITES_X_SLIDE_3
    for _ in range(20):
        datos_por_px = (x_max - x_min) / ancho_ejes_px
        x_min = min([LIMITES_X_SLIDE_3[0]] + [v - px * datos_por_px for v, lado, px in necesidades if lado == "izq"])
        x_max = max([LIMITES_X_SLIDE_3[1]] + [v + px * datos_por_px for v, lado, px in necesidades if lado == "der"])
    ax.set_xlim(x_min, x_max)
    ax.spines["left"].set_position(("data", x_min))

    # ---- 3. Flechas, puntos y cápsulas ----
    def capsula(x, y, valor, color, lado, peso, separacion):
        """Cápsula estilo Pabloplot pegada al punto, hacia `lado` ('izq' o 'der')."""
        ax.annotate(texto_capsula(valor), xy=(x, y),
                    xytext=(-separacion if lado == "izq" else separacion, 0),
                    textcoords="offset points",
                    ha="right" if lado == "izq" else "left", va="center",
                    fontsize=TAM_CAPSULA_SLIDE_3, fontweight=peso, color=color, zorder=4,
                    bbox={**caja, "edgecolor": color})

    for y, r in zip(ys, df.itertuples()):
        color = COLORES_TIPO[r.tipo]
        sube = r.inseguro_2026 > r.inseguro_2024
        # Flecha 2024 -> 2026
        ax.annotate("", xy=(r.inseguro_2026, y), xytext=(r.inseguro_2024, y),
                    arrowprops={"arrowstyle": "-|>", "color": color, "lw": GROSOR_FLECHA_SLIDE_3,
                                "mutation_scale": 10, "shrinkA": 0, "shrinkB": 0}, zorder=3)
        # Punto de inicio (2024), del color de la flecha
        ax.plot(r.inseguro_2024, y, marker="o", markersize=TAM_PUNTO_SLIDE_3,
                color=color, linestyle="none", zorder=3.5)
        # Cápsulas hacia afuera de la flecha: 2026 del lado al que apunta, 2024 del
        # otro (un poco más separada para no tapar el punto)
        capsula(r.inseguro_2026, y, r.inseguro_2026, color,
                "der" if sube else "izq", PESO_NUEVO_SLIDE_3, sep_nuevo)
        capsula(r.inseguro_2024, y, r.inseguro_2024, COLOR_ANTERIOR_SLIDE_3,
                "izq" if sube else "der", PESO_ANTERIOR_SLIDE_3, sep_anterior)

    # Línea punteada: valor nacional 2026
    ax.axvline(df["nacional_2026"].iloc[0], color=COLOR_NACIONAL_SLIDE_3,
               linestyle=(0, (4, 3)), linewidth=1, zorder=1)
    colorear_ejes(ax)

    with mpl.rc_context({"savefig.transparent": True}):
        exportar_grafica(fila.grafica, limpiar_svg_con_scour, exact_dim=True)
    plt.close("all")


# ---- SLIDE 4 ---- #
# Serie -> (nombre en la leyenda, color)
SERIES_SLIDE_4 = {
    "promedio_gastos":   ("Gasto promedio en medidas de protección", "#3E7D70"),
    "promedio_perdidas": ("Pérdida promedio a consecuencia del delito", "#9B2247"),
}
TAM_CAPSULA_SLIDE_4 = 11.5
SEP_CAPSULA_SLIDE_4 = 7              # separación (pt) entre el punto y su cápsula
TAM_EJEX_SLIDE_4 = 15                # tamaño de los años (eje X)
TAM_EJEY_SLIDE_4 = 12                # tamaño de los valores del eje Y
SEP_EJEX_SLIDE_4 = 8                 # distancia (pt) entre el eje X y los años; matplotlib usa 3.5
NOMBRE_EJEY_SLIDE_4 = None           # título del eje Y (None = sin título); valores en pesos de 2025


def lineas_costos_slide_4(fila):
    """Serie 2015-2025 (nacional) con Pabloplot lineas(): una línea por promedio,
    con puntos y el valor de cada año en cápsula."""
    df = pd.read_csv(fila.tabulado, encoding="utf-8-sig").sort_values("anio")
    faltan = [c for c in SERIES_SLIDE_4 if c not in df.columns]
    if faltan:
        raise ValueError(f"Faltan columnas en {fila.tabulado}: {faltan}")

    datos = df[["anio", *SERIES_SLIDE_4]].rename(
        columns={c: nombre for c, (nombre, _) in SERIES_SLIDE_4.items()})
    datos["anio"] = datos["anio"].astype(int)
    colores = [color for _, color in SERIES_SLIDE_4.values()]
    techo = df[list(SERIES_SLIDE_4)].to_numpy().max() * 1.25     # espacio para las cápsulas

    ancho, alto = TAMANOS["lineas_costos_slide_4"]
    fig, ax = lineas(
        datos,
        nombre=fila.grafica,
        ancho=ancho, alto=alto,
        colores=colores,
        puntos=True,
        mostrar_capsu=[],                             # cápsulas propias (abajo)
        capsu_ini=False, capsu_max=False, capsu_fin=False,
        decimales=0,
        marcas_graduacion_ejex=False,
        tam_valor_ejex=TAM_EJEX_SLIDE_4, tam_valor_ejey=TAM_EJEY_SLIDE_4,
        tam_valor_capsu=TAM_CAPSULA_SLIDE_4,
        color_valor_ejex=COLOR_EJES, color_valor_ejey=COLOR_EJES,
        nombre_ejey=NOMBRE_EJEY_SLIDE_4, tam_nombre_ejey=TAM_EJEY_SLIDE_4 - 1,
        limites_ejey=(0, techo),
        leyenda=False,
        num_columnas_leyenda=2,
        tam_letra_leyenda=TAM_EJEY_SLIDE_4 - 1,
        guardar=False, mostrar=False,
    )

    # ---- Cápsulas propias: en cada año, la serie más alta arriba de su punto
    # y la más baja abajo del suyo (así nunca se enciman ni se alejan del punto).
    # Las x se toman de las líneas que dibujó Pabloplot (una por serie, en orden).
    lineas_dibujadas = [l for l in ax.get_lines() if len(l.get_xdata()) == len(datos)][:len(SERIES_SLIDE_4)]
    if len(lineas_dibujadas) != len(SERIES_SLIDE_4):
        raise RuntimeError(f"Esperaba {len(SERIES_SLIDE_4)} líneas y encontré {len(lineas_dibujadas)}")
    xs = lineas_dibujadas[0].get_xdata()
    columnas = list(SERIES_SLIDE_4)
    for i, x in enumerate(xs):
        valores = {c: df[c].iloc[i] for c in columnas}
        mas_alta = max(valores, key=valores.get)
        for c, v in valores.items():
            arriba = c == mas_alta
            color = SERIES_SLIDE_4[c][1]
            ax.annotate(f"{v:,.0f}", xy=(x, v),
                        xytext=(0, SEP_CAPSULA_SLIDE_4 if arriba else -SEP_CAPSULA_SLIDE_4),
                        textcoords="offset points", ha="center",
                        va="bottom" if arriba else "top",
                        fontsize=TAM_CAPSULA_SLIDE_4, fontweight="bold", color=color, zorder=5,
                        bbox={"boxstyle": "round,pad=0.3,rounding_size=0.8",
                              "facecolor": "#FFFFFF", "edgecolor": color, "linewidth": 1.5})
    ax.tick_params(axis="x", pad=SEP_EJEX_SLIDE_4)    # distancia de los años al eje X
    colorear_ejes(ax)

    with mpl.rc_context({"savefig.transparent": True}):
        exportar_grafica(fila.grafica, limpiar_svg_con_scour, exact_dim=True)
    plt.close("all")


FUNCIONES = {
    "barras_horizontales_slide_1": barras_horizontales_slide_1,
    "barras_violencia_slide_2":    barras_violencia_slide_2,
    "barras_tamanio_slide_2_5":    barras_tamanio_slide_2_5,
    "flechas_percepcion_slide_3":  flechas_percepcion_slide_3,
    "lineas_costos_slide_4":       lineas_costos_slide_4,
}


# ————————————————————————————————————————————————————————— #
# EJECUCIÓN -------
# ————————————————————————————————————————————————————————— #

manifiesto = pd.read_csv(MANIFIESTO, encoding="utf-8-sig")
errores = []

for fila in manifiesto.itertuples(index=False):
    print(f"[slide {fila.slide}] {fila.grafica}")
    try:
        FUNCIONES[fila.funcion](fila)
    except Exception:
        traceback.print_exc()
        errores.append(fila.grafica)
        plt.close("all")

if errores:
    sys.exit(f"ERROR en {len(errores)} gráfica(s):\n  " + "\n  ".join(errores))

print(f"OK: {len(manifiesto)} gráficas en {RAIZ / 'output'}")

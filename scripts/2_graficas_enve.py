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

for archivo_fuente in font_manager.findSystemFonts(fontpaths=[str(DIR_FUNCIONES.parent / "0_fonts")]):
    font_manager.fontManager.addfont(archivo_fuente)

mpl.rcParams["font.family"] = "Montserrat"
mpl.rcParams["svg.fonttype"] = "none"              # texto editable en el SVG


# ————————————————————————————————————————————————————————— #
# ESTILO -------
# ————————————————————————————————————————————————————————— #

TAMANOS = {                       # cm, medidos de las imágenes de la PPT
    "barras_horizontales_slide_1": (10.6, 5.5),
}

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


FUNCIONES = {
    "barras_horizontales_slide_1": barras_horizontales_slide_1,
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

# ==============================================================================
# Autopartes -- graficas_081026.py
#
# Mismas gráficas que gráficas.ipynb (barras apiladas por partida y por país,
# y líneas definitivas vs temporales), pero con los insumos de
# 4_pd_partidas_paises_081026.R: PROMEDIO DIARIO (MDP reales) de
# 2022 a 2026 (ene a sep cuando el insumo trae mes).
#
# Se puede correr desde cualquier carpeta (las rutas salen de RAIZ). Las
# imágenes (PNG + SVG) se guardan en output/081026/plots/ del proyecto.
# ==============================================================================

import os
import sys
from pathlib import Path

import textwrap

import pandas as pd

# ---- RAÍZ DEL PROYECTO (ajusta si mueves la carpeta) ----
RAIZ = Path("/Users/ariadnamartinez/Desktop/ATDT/proyecto_autopartes")
# ----------------------------------------------------------

# Si la ruta fija no existe (otra máquina), busca la raíz hacia arriba desde
# este archivo o desde la carpeta donde estés parado.
if not (RAIZ / "output" / "081026").is_dir():
    try:
        inicio = Path(__file__).resolve().parent
    except NameError:                          # consola interactiva / notebook
        inicio = Path.cwd().resolve()
    for carpeta in [inicio, *inicio.parents]:
        if (carpeta / "output" / "081026").is_dir():
            RAIZ = carpeta
            break
    else:
        raise FileNotFoundError(
            "No encontré output/081026. Corre antes 4_pd_partidas_paises_081026.R "
            "o ajusta RAIZ arriba."
        )

CARPETA_FUNCIONES = RAIZ / "scripts" / "slide_1_pd_definitivas_temporales"   # barras_verticales.py
sys.path.insert(0, str(RAIZ / "scripts" / "1_funciones"))                      # lineas.py, funciones.py
sys.path.insert(0, str(CARPETA_FUNCIONES))
from barras_verticales import barras_verticales
from lineas import lineas

import matplotlib as mpl

# Montserrat en TODO el texto, incluida la leyenda: barras_verticales le pasa
# la fuente a etiquetas y ejes, pero la leyenda toma la fuente global de
# matplotlib (rcParams). Sin esto, en el SVG la leyenda sale en otra letra.
mpl.rcParams["font.family"] = "Montserrat"
mpl.rcParams["svg.fonttype"] = "none"          # texto editable en el SVG

CARPETA = RAIZ / "output" / "081026"
print(f"Leyendo insumos de: {CARPETA}")

# exportar_grafica() (funciones.py) guarda en "output/{nombre}" relativo a la
# carpeta actual; parándonos en RAIZ y con nombre "081026/plots/...", todo
# cae en RAIZ/output/081026/plots/.
os.chdir(RAIZ)
PLOTS = "081026/plots/"
print(f"Guardando gráficas en: {RAIZ / 'output' / PLOTS}")


def orden_apilado(df, flag, categoria):
    """Top de menor a mayor (abajo hacia arriba) y "Otras/Otros" hasta arriba,
    como en las slides. El orden se fija con el último año."""
    ultimo = df[df["year"] == df["year"].max()]
    top = ultimo[ultimo[flag] == 1].sort_values("valor2")[categoria].tolist()
    otros = ultimo[ultimo[flag] == 0][categoria].tolist()
    return top + otros


# Colores fijos por categoría (los mismos de las slides anteriores). Lo que no
# esté aquí toma un color de RESERVA, en orden.
# Partidas: colores POR POSICIÓN en la barra (de abajo hacia arriba), los
# mismos de la slide anterior, aunque las partidas hayan cambiado. El gris
# siempre es "Otras partidas" (va hasta arriba).
COLORES_PARTIDA_POSICION = ["#4f3a5eff", "#1e5b4fff", "#e6d194ff", "#611232ff", "#a57f2cff"]
COLOR_OTRAS = "#98989aff"
COLORES_PAIS = {
    "China": "#3e7a5fff", "Alemania": "#2f6e8cff", "Japón": "#6b3a5eff",
    "Corea del Sur": "#a35a3cff", "México": "#a5802fff",
    "Estados Unidos": "#6e5a3eff", "Otros países": "#98989aff",
}
RESERVA = ["#e6d194ff", "#1c4587ff", "#38761dff", "#1e5b4fff", "#4f3a5eff", "#611232ff"]


def colores_para(columnas, fijos):
    reserva = iter(RESERVA)
    return [fijos.get(c) or next(reserva) for c in columnas]


# Segmentos con participación menor a este % se quedan SIN número (para que no
# se amontonen). barras_verticales mide el "área" = valor * ancho_barra, así
# que el umbral se traduce a MDP con el total más alto de la gráfica.
UMBRAL_PCT_PARTIDAS = 4.5   # oculta las partidas chicas (2% a 4%)
UMBRAL_PCT_PAISES   = 3.0   # los países top pesan 5% o más: se ven todos
ANCHO_BARRA = 0.7
ALTO_BARRAS = 16.5   # cm; antes 11.83. Más alto = segmentos más altos y números menos apretados


def areamin_para(ancho, umbral_pct):
    total_max = ancho.drop(columns="year").sum(axis=1).max()
    return umbral_pct / 100 * total_max * ANCHO_BARRA


def a_ancho(df, categoria, valor, orden_categorias=None):
    """year x categoria, igual que los pivots del notebook."""
    ancho = df.pivot(index="year", columns=categoria, values=valor).reset_index()
    ancho.columns.name = None
    ancho["year"] = ancho["year"].astype(str)
    if orden_categorias is not None:
        ancho = ancho[["year"] + [c for c in orden_categorias if c in ancho.columns]]
    return ancho.fillna(0)


# ---- 1. Por partida (antes top5capitulos.csv) --------------------------------
partidas = pd.read_csv(CARPETA / "top_partidas_pd_081026.csv", dtype={"partida": str})
# La leyenda usa etiqueta_leyenda: "Descripción (clave)" y "Otras partidas
# (N partidas más; incluyen ...)", ambas armadas en el script 4.
orden_p = orden_apilado(partidas, partidas.columns[1], "etiqueta_leyenda")
partidas_ancho = a_ancho(partidas, "etiqueta_leyenda", "valor2", orden_p)
# Corta las etiquetas largas en renglones para que la leyenda quepa
ANCHO_ETIQUETA = 48
partidas_ancho.columns = ["year"] + [textwrap.fill(c, ANCHO_ETIQUETA) for c in partidas_ancho.columns[1:]]
n_top = partidas_ancho.shape[1] - 2          # columnas sin "year" ni "Otras partidas"
colores_p = COLORES_PARTIDA_POSICION[:n_top] + [COLOR_OTRAS]
print(partidas_ancho)

barras_verticales(partidas_ancho,
                  nombre=PLOTS + 'barras_partidas_pd_081026',
                  leyenda=True,
                  ancho=19.76,
                  alto=ALTO_BARRAS,
                  num_columnas_leyenda=2,   # 2 columnas: los nombres de partida son largos
                  # leyenda anclada por ARRIBA y bajo el eje x, para que al crecer
                  # (etiquetas de varios renglones) baje y no tape los años
                  posicion_leyenda={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                  tam_letra_leyenda=8,
                  quitar_capsu=True,
                  colores=colores_p,
                  porce_barra=True,
                  valor_barra=False,
                  ancho_barra=ANCHO_BARRA,
                  areamin=areamin_para(partidas_ancho, UMBRAL_PCT_PARTIDAS),
                  opcion_areamin='sin etiquetas',
                  ordenar='x',
                  )

# ---- 2. Por país (antes top6pais.csv) ----------------------------------------
pais = pd.read_csv(CARPETA / "top_paises_pd_081026.csv")
orden_c = orden_apilado(pais, pais.columns[1], "etiqueta_leyenda")
pais_ancho = a_ancho(pais, "etiqueta_leyenda", "valor2", orden_c)
# colores por nombre de país (la etiqueta de "Otros países" es larga: se mapea a gris)
nombre_de = dict(zip(pais["etiqueta_leyenda"], pais["pais"]))
colores_c = colores_para([nombre_de[c] for c in pais_ancho.columns[1:]], COLORES_PAIS)
pais_ancho.columns = ["year"] + [textwrap.fill(c, ANCHO_ETIQUETA) for c in pais_ancho.columns[1:]]
print(pais_ancho)

barras_verticales(pais_ancho,
                  nombre=PLOTS + 'barras_paises_pd_081026',
                  leyenda=True,
                  ancho=19.76,
                  alto=ALTO_BARRAS,
                  num_columnas_leyenda=2,
                  posicion_leyenda={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                  tam_letra_leyenda=8,
                  quitar_capsu=True,
                  colores=colores_c,
                  porce_barra=True,
                  valor_barra=False,
                  ancho_barra=ANCHO_BARRA,
                  areamin=areamin_para(pais_ancho, UMBRAL_PCT_PAISES),
                  opcion_areamin='sin etiquetas',
                  ordenar='x'
                  )

# ---- 3. Definitivas vs temporales (antes temp_definit.csv) -------------------
temp = pd.read_csv(CARPETA / "temp_definit_pd_081026.csv")
temp = temp[['year', 'temporal', 'valor']]
temp = temp.pivot(index='year', columns='temporal', values='valor').reset_index()
temp.columns.name = None
print(temp)

lineas(temp,
       nombre=PLOTS + 'lineas_definitivas_temporales_pd_081026',
       ancho=19.32,
       alto=9.74,
       sin_capsu=0,
       algoritmo_posicionamiento='algorimto_posicionamiento_1',
       ajustar_pos_capsu=0.1,
       leyenda=False,
       colores=['#9b2247ff', '#011738ff'],
       )

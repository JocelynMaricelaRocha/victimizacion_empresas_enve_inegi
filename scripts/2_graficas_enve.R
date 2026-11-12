# ————————————————————————————————————————————————————————— #
# Nombre: Jocelyn Rocha
# Contacto: jocelyn.flores@transformaciondigital.gob.mx
# Script: 2_graficas_enve.R
# Proyecto: Victimización de empresas | ENVE Principales resultados
# Fecha: 2026-11-11
# Propósito: Lanzar desde R las gráficas de Pabloplot (scripts/2_graficas_enve.py)
#            vía system2(), sin reticulate.
# ————————————————————————————————————————————————————————— #
# PREÁMBULO -------
# ————————————————————————————————————————————————————————— #

rm(list = ls())
cat("\014")

pacman::p_load(tidyverse, glue, crayon)

source(here::here("scripts", "utils", "funciones_enve.R"))

# PARÁMETROS _________________ -----
RAIZ              <- normalizePath(here::here(), winslash = "/")
DIR_FUNCIONES     <- file.path(RAIZ, "scripts", "utils", "pabloplot", "1_funciones")  # fuentes en ../0_fonts
SCRIPT_PY         <- file.path(RAIZ, "scripts", "2_graficas_enve.py")
CARPETA_TABULADOS <- file.path(RAIZ, "output", "tabulados")
CARPETA_GRAFICAS  <- "graficas"           # relativo a output/ (así guarda Pabloplot)
MANIFIESTO        <- file.path(CARPETA_TABULADOS, "manifiesto_graficas.csv")
SOLO_SLIDES       <- NULL                 # p. ej. c(1, 2) para rehacer solo esas; NULL = todas

# VALIDACIONES _______________ -----
if (!file.exists(SCRIPT_PY) || !dir.exists(DIR_FUNCIONES)) {
    stop("No encuentro ", SCRIPT_PY, " o ", DIR_FUNCIONES, ".\n  Raíz detectada: ", RAIZ)
}

# ————————————————————————————————————————————————————————— #
# MANIFIESTO -------
# ————————————————————————————————————————————————————————— #
# Una fila por gráfica. El .py solo recorre esta tabla: para agregar slides
# basta con sumar filas (y, si es otro tipo de gráfica, su función en el .py).

DELITOS_SLIDE_1 <- c("Extorsión", "Robo hormiga", "Robo/asalto de bienes o dinero")

manifiesto_slide_1 <- crossing(
    tipo           = c("aumentos", "disminuciones"),
    tipo_de_delito = DELITOS_SLIDE_1
) |>
    mutate(
        slide    = 1L,
        funcion  = "barras_horizontales_slide_1",
        tabulado = file.path(CARPETA_TABULADOS, glue("slide_1_top_{tipo}.csv")),
        grafica  = glue("{CARPETA_GRAFICAS}/slide_1/slide_1_{tipo}_{slug(tipo_de_delito)}")
    )

manifiesto <- bind_rows(manifiesto_slide_1) |>
    select(slide, funcion, grafica, tabulado, tipo, tipo_de_delito)

if (!is.null(SOLO_SLIDES)) manifiesto <- filter(manifiesto, slide %in% SOLO_SLIDES)

faltan_tab <- unique(manifiesto$tabulado[!file.exists(manifiesto$tabulado)])
if (length(faltan_tab) > 0) {
    stop("Faltan tabulados (corre antes scripts/1_tabulados.R):\n  ",
         paste(faltan_tab, collapse = "\n  "))
}

walk(unique(dirname(file.path(RAIZ, "output", manifiesto$grafica))),
     dir.create, recursive = TRUE, showWarnings = FALSE)
write_excel_csv(manifiesto, MANIFIESTO)
cat(cyan(glue("Manifiesto con {nrow(manifiesto)} gráficas: {MANIFIESTO}\n")))

# ————————————————————————————————————————————————————————— #
# PYTHON -------
# ————————————————————————————————————————————————————————— #

PYTHON <- encontrar_python()
cat(cyan(glue("Python: {PYTHON}\n")))

faltan <- c("pandas", "numpy", "matplotlib", "scour") |>
    keep(~ system2(PYTHON, c("-c", shQuote(glue("import {.x}"))), stdout = FALSE, stderr = FALSE) != 0)
if (length(faltan) > 0) {
    stop("A Python le faltan paquetes: ", paste(faltan, collapse = ", "), ".\n",
         "  Instálalos desde la terminal con:\n  ",
         shQuote(PYTHON), " -m pip install ", paste(faltan, collapse = " "))
}

# ————————————————————————————————————————————————————————— #
# GRÁFICAS -------
# ————————————————————————————————————————————————————————— #
# Los parámetros van por variables de entorno. Pabloplot guarda en
# "output/<grafica>" relativo a la carpeta de trabajo, así que el proceso de
# Python se lanza parado en la raíz del proyecto.

# Pabloplot llama al ejecutable `scour`, que vive en la carpeta Scripts de
# Python (no siempre está en el PATH).
DIR_SCRIPTS_PY <- file.path(dirname(PYTHON), "Scripts")

Sys.setenv(
    PATH               = paste(DIR_SCRIPTS_PY, Sys.getenv("PATH"), sep = .Platform$path.sep),
    ENVE_RAIZ          = RAIZ,
    ENVE_DIR_FUNCIONES = DIR_FUNCIONES,
    ENVE_MANIFIESTO    = MANIFIESTO,
    PYTHONUTF8         = "1",        # acentos bien en Windows
    PYTHONIOENCODING   = "utf-8",
    MPLBACKEND         = "Agg"
)

cat(cyan("Generando gráficas...\n"))
wd_original <- setwd(RAIZ)
estado <- system2(PYTHON, shQuote(SCRIPT_PY))
setwd(wd_original)

if (estado != 0) {
    stop("Python terminó con error (código ", estado, "). Revisa el mensaje de arriba.")
}
cat(green(glue("Listo. Gráficas en {file.path(RAIZ, 'output', CARPETA_GRAFICAS)}\n")))

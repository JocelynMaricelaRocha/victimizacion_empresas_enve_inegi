# ————————————————————————————————————————————————————————— #
# Nombre: Jocelyn Rocha
# Contacto: jocelyn.flores@transformaciondigital.gob.mx
# Script: 1_tabulados.R
# Proyecto: Victimización de empresas | ENVE Principales resultados
# Fecha: 2026-11-11
# Propósito: Tabulados por slide a partir de las bases procesadas en 0_procesamiento.R
# ————————————————————————————————————————————————————————— #
# PREÁMBULO -------
# ————————————————————————————————————————————————————————— #

rm(list = ls())
cat("\014")

pacman::p_load(tidyverse, glue, crayon, janitor)

source(here::here("scripts", "utils", "funciones_enve.R"))

# ————————————————————————————————————————————————————————— #
# DATOS -----------
# ————————————————————————————————————————————————————————— #

# INTAKES -------- #
CARPETA_PROCESADOS <- here::here("output", "procesados")
CARPETA_TABULADOS  <- here::here("output", "tabulados")
dir.create(CARPETA_TABULADOS, recursive = TRUE, showWarnings = FALSE)

NACIONAL <- "Estados Unidos Mexicanos"
N_TOP    <- 5

# Slide 1 ------ #
incidencia_slide_1_completo <- readRDS(file.path(CARPETA_PROCESADOS, "incidencia_slide_1_completo.rds"))

# ————————————————————————————————————————————————————————— #
# SLIDE 1 -----------
# ————————————————————————————————————————————————————————— #
# Top 5 de entidades con mayores aumentos y disminuciones en la tasa de
# incidencia delictiva (2023 vs 2025), por tipo de delito.

# REFERENCIA NACIONAL -- #
nacional_slide_1 <- incidencia_slide_1_completo |>
    filter(entidad_federativa == NACIONAL)

entidades_slide_1 <- incidencia_slide_1_completo |>
    filter(entidad_federativa != NACIONAL, !is.na(diferencia_tasa_delictiva))

# AUMENTOS ------ #
# Solo entidades que efectivamente aumentaron (diferencia > 0)
top_aumentos_slide_1 <- entidades_slide_1 |>
    filter(diferencia_tasa_delictiva > 0) |>
    group_by(tipo_de_delito) |>
    slice_max(diferencia_tasa_delictiva, n = N_TOP, with_ties = FALSE) |>
    mutate(posicion = row_number()) |>
    ungroup()

# DISMINUCIONES - #
# Solo entidades que efectivamente disminuyeron (diferencia < 0)
top_disminuciones_slide_1 <- entidades_slide_1 |>
    filter(diferencia_tasa_delictiva < 0) |>
    group_by(tipo_de_delito) |>
    slice_min(diferencia_tasa_delictiva, n = N_TOP, with_ties = FALSE) |>
    mutate(posicion = row_number()) |>
    ungroup()

# REVISIÓN ------ #
# Avisa si algún delito tiene menos de N_TOP entidades en alguno de los tabulados
bind_rows(aumentos = count(top_aumentos_slide_1, tipo_de_delito),
          disminuciones = count(top_disminuciones_slide_1, tipo_de_delito),
          .id = "tabulado") |>
    filter(n < N_TOP) |>
    pwalk(\(tabulado, tipo_de_delito, n) {
        cat(yellow(glue("Aviso: '{tipo_de_delito}' tiene solo {n} entidades en {tabulado}.\n")))
    })

# GUARDAR ------- #
write_excel_csv(top_aumentos_slide_1,
                file.path(CARPETA_TABULADOS, "slide_1_top_aumentos.csv"))
write_excel_csv(top_disminuciones_slide_1,
                file.path(CARPETA_TABULADOS, "slide_1_top_disminuciones.csv"))
write_excel_csv(nacional_slide_1,
                file.path(CARPETA_TABULADOS, "slide_1_nacional.csv"))

cat(green(glue("Tabulados del slide 1 guardados en {CARPETA_TABULADOS}\n")))

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

# ————————————————————————————————————————————————————————— #
# SLIDE 2 -----------
# ————————————————————————————————————————————————————————— #
# Extorsiones con y sin violencia: una fila por barra de la gráfica.
# El porcentaje es respecto a los delitos ocurridos.

extorsion_slide_2 <- readRDS(file.path(CARPETA_PROCESADOS, "extorsion_slide_2.rds"))

violencia_slide_2 <- extorsion_slide_2 |>
    select(tipo_de_delito, delitos_ocurridos,
           delitos_sin_violencia, delitos_agresion, delitos_amenaza) |>
    pivot_longer(c(delitos_sin_violencia, delitos_agresion, delitos_amenaza),
                 names_to = "categoria", values_to = "absolutos") |>
    mutate(
        grupo = if_else(categoria == "delitos_sin_violencia",
                        "Delitos sin violencia", "Delitos con violencia"),
        etiqueta = recode(categoria,
                          delitos_sin_violencia = "Delitos sin violencia",
                          delitos_agresion      = "Delitos con agresión física",
                          delitos_amenaza       = "Delitos con amenaza de violencia"),
        porcentaje = 100 * absolutos / delitos_ocurridos,
        orden = row_number(),
        .by = tipo_de_delito
    ) |>
    select(tipo_de_delito, orden, grupo, categoria, etiqueta, absolutos, porcentaje)

write_excel_csv(violencia_slide_2,
                file.path(CARPETA_TABULADOS, "slide_2_violencia_extorsion.csv"))

cat(green(glue("Tabulados del slide 2 guardados en {CARPETA_TABULADOS}\n")))

# ————————————————————————————————————————————————————————— #
# SLIDE 2.5 -----------
# ————————————————————————————————————————————————————————— #
# Delitos más frecuentes por tamaño de empresa: una fila por barra.
# El porcentaje es respecto a los delitos ocurridos en ese tamaño de empresa.

TAMANIOS_EMPRESA <- c("Micro", "Pequeña", "Mediana", "Grande")

extorsiones_por_tamanio <- readRDS(file.path(CARPETA_PROCESADOS, "extorsiones_por_tamanio_slide_2_5.rds"))

# Orden de los delitos (dentro de cada grupo y en la leyenda): primero los más
# frecuentes a nivel nacional; los que no aparecen en el nacional van al final.
orden_delitos <- extorsiones_por_tamanio |>
    summarise(absolutos = sum(delitos_ocurridos_absolutos[tamanio_empresa == NACIONAL]),
              .by = tipo_de_delito) |>
    arrange(desc(absolutos)) |>
    pull(tipo_de_delito)

tamanio_slide_2_5 <- extorsiones_por_tamanio |>
    filter(tamanio_empresa %in% TAMANIOS_EMPRESA) |>
    transmute(
        tamanio_empresa,
        tipo_de_delito,
        absolutos  = delitos_ocurridos_absolutos,
        porcentaje = delitos_ocurridos_relativos,
        orden_tamanio = match(tamanio_empresa, TAMANIOS_EMPRESA),
        orden_delito  = match(tipo_de_delito, orden_delitos)
    ) |>
    arrange(orden_tamanio, orden_delito)

write_excel_csv(tamanio_slide_2_5,
                file.path(CARPETA_TABULADOS, "slide_2_5_delitos_por_tamanio.csv"))

cat(green(glue("Tabulados del slide 2.5 guardados en {CARPETA_TABULADOS}\n")))

# ————————————————————————————————————————————————————————— #
# SLIDE 3 -----------
# ————————————————————————————————————————————————————————— #
# Percepción de inseguridad 2024 vs 2026 por entidad. Se ordena por la
# percepción de inseguridad 2026 (mayor primero) y se parte en dos gráficas de 16.

N_POR_PANEL_SLIDE_3 <- 16

percepcion_slide_3 <- readRDS(file.path(CARPETA_PROCESADOS, "percepcion_slide_3.rds"))
nacional_slide_3   <- readRDS(file.path(CARPETA_PROCESADOS, "percepcion_nacional_slide_3.rds"))

tabulado_slide_3 <- percepcion_slide_3 |>
    arrange(desc(inseguro_2026)) |>   # mayor percepción de inseguridad 2026 primero
    mutate(
        orden    = row_number(),
        panel    = if_else(orden <= N_POR_PANEL_SLIDE_3, 1L, 2L),
        tipo     = if_else(diferencia > 0, "aumentos", "disminuciones"),
        # Referencia nacional 2026 (línea punteada en la gráfica)
        nacional_2026 = nacional_slide_3$inseguro_2026
    )

write_excel_csv(tabulado_slide_3,
                file.path(CARPETA_TABULADOS, "slide_3_percepcion_inseguridad.csv"))

cat(green(glue("Tabulados del slide 3 guardados en {CARPETA_TABULADOS} ",
               "({sum(tabulado_slide_3$tipo == 'aumentos')} entidades con aumento, ",
               "{sum(tabulado_slide_3$tipo == 'disminuciones')} con disminución)\n")))

# ————————————————————————————————————————————————————————— #
# SLIDE 4 -----------
# ————————————————————————————————————————————————————————— #
# Serie 2015-2025 (nacional): promedio de gastos en medidas de protección y
# promedio de pérdidas a consecuencia del delito, por unidad económica (pesos
# constantes del año base, deflactor implícito; ver 0_procesamiento.R).

costos_slide_4 <- readRDS(file.path(CARPETA_PROCESADOS, "costos_slide_4.rds"))

write_excel_csv(costos_slide_4, file.path(CARPETA_TABULADOS, "slide_4_costos_promedio.csv"))

cat(green(glue("Tabulados del slide 4 guardados en {CARPETA_TABULADOS}\n")))

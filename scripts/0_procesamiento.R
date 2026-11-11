# ————————————————————————————————————————————————————————— #
# Nombre: Jocelyn Rocha
# Contacto: jocelyn.flores@transformaciondigital.gob.mx
# Script: 0_procesamiento.R
# Proyecto: Victimización de empresas | ENVE Principales resultados
# Fecha: 2026-11-11
# Propósito: Procesamiento de tabulados (carpeta en input/slide_n) que servirán de insumo para el script 1_tabulados
# ————————————————————————————————————————————————————————— #
# PREÁMBULO -------
# ————————————————————————————————————————————————————————— #

rm(list = ls())
cat("\014")

pacman::p_load(tidyverse, data.table, lubridate, glue, crayon, stringi, janitor)

source(here::here("scripts", "utils", "funciones_enve.R"))

# ————————————————————————————————————————————————————————— #
# DATOS -----------
# ————————————————————————————————————————————————————————— #

# INTAKES -------- #
CARPETA_SLIDE_1_2023 <- here::here("input", "slide_1", "incidencia_delictiva_2023.csv")
CARPETA_SLIDE_1_2025 <- here::here("input", "slide_1", "incidencia_delictiva_2025.csv")

# CATÁLOGOS ----- #
load(here::here("input", "catalogos", "cat_ent.R"))
cat_ent <- cat_ent |> clean_names()

# Slide 1 ------ #
incidencia_delictiva_2023 <- leer_csv_robusto(CARPETA_SLIDE_1_2023)
incidencia_delictiva_2025 <- leer_csv_robusto(CARPETA_SLIDE_1_2025)

# ————————————————————————————————————————————————————————— #
# SLIDE 1 -----------
# ————————————————————————————————————————————————————————— #

# INTAKES -------- #
# DELITOS PARA GRÁFICA
DELITOS_SLIDE_1 <- c("Extorsión", "Robo hormiga", "Robo/asalto de bienes o dinero")

# ORDENAR BASES -- #
# Una fila por entidad y tipo de delito (la fila de la entidad = "Total")
incidencia_delictiva_2023 <- incidencia_delictiva_2023 |>
    separar_entidad_delito(nombres_entidades = cat_ent$nom_ent) |>
    rename(tasa_de_incidencia = `tasa de incidencia`)

incidencia_delictiva_2025 <- incidencia_delictiva_2025 |>
    separar_entidad_delito(nombres_entidades = cat_ent$nom_ent) |>
    rename(tasa_de_incidencia = `tasa de incidencia`)

# FILTRAR DELITOS  #
incidencia_slide_1_2023 <- incidencia_delictiva_2023 |> filter(tipo_de_delito %in% DELITOS_SLIDE_1)
incidencia_slide_1_2025 <- incidencia_delictiva_2025 |> filter(tipo_de_delito %in% DELITOS_SLIDE_1)

incidencia_slide_1_2023 <- incidencia_slide_1_2023 |> 
  rename(tasa_de_incidencia_2023 = tasa_de_incidencia)
incidencia_slide_1_2025 <- incidencia_slide_1_2025 |> 
  rename(tasa_de_incidencia_2025 = tasa_de_incidencia)

# JUNTAR EN UNA BASE JUNTO VARIABLE DE DIFERENCIA_TASA_DELICTIVA
incidencia_slide_1_completo <- incidencia_slide_1_2023 |> 
  left_join(incidencia_slide_1_2025, by = c("entidad_federativa" = "entidad_federativa", "tipo_de_delito" = "tipo_de_delito")) |> 
  mutate(diferencia_tasa_delictiva = tasa_de_incidencia_2025 - tasa_de_incidencia_2023)

# GUARDAR -------- #
CARPETA_PROCESADOS <- here::here("output", "procesados")
dir.create(CARPETA_PROCESADOS, recursive = TRUE, showWarnings = FALSE)

saveRDS(incidencia_slide_1_completo,
        file.path(CARPETA_PROCESADOS, "incidencia_slide_1_completo.rds"))

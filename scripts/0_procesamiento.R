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

CARPETA_SLIDE_2_EXTORSIONES <- here::here("input", "slide_2", "extorsiones_absolutos_2026.csv")
CARPETA_SLIDE_2_TAMANIO_EMPRESA <- here::here("input", "slide_2", "extorsiones_por_tamanio_empresa.csv")

CARPETA_SLIDE_3_PERCEPCION_2024 <- here::here("input", "slide_3", "percepcion_seguridad_entidades_2024.csv")
CARPETA_SLIDE_3_PERCEPCION_2026 <- here::here("input", "slide_3", "percepcion_seguridad_entidades_2026.csv")

CARPETA_SLIDE_4_COSTOS_2015 <- here::here("input", "slide_4", "6.1_costosdelito_entidades_2015.csv")
CARPETA_SLIDE_4_COSTOS_2017 <- here::here("input", "slide_4", "6.1_costosdelito_entidades_2017.csv")
CARPETA_SLIDE_4_COSTOS_2019 <- here::here("input", "slide_4", "6.1_costosdelito_entidades_2019.csv")
CARPETA_SLIDE_4_COSTOS_2021 <- here::here("input", "slide_4", "6.1_costosdelito_entidades_2021.csv")
CARPETA_SLIDE_4_COSTOS_2023 <- here::here("input", "slide_4", "6.1_costosdelito_entidades_2023.csv")
CARPETA_SLIDE_4_COSTOS_2025 <- here::here("input", "slide_4", "6.1_costosdelito_entidades_2025.csv")

# CATÁLOGOS ----- #
load(here::here("input", "catalogos", "cat_ent.R"))
cat_ent <- cat_ent |> clean_names()

# Slide 1 ------ #
incidencia_delictiva_2023 <- leer_csv_robusto(CARPETA_SLIDE_1_2023)
incidencia_delictiva_2025 <- leer_csv_robusto(CARPETA_SLIDE_1_2025)

# Slide 2 ------ #
extorsiones_2026 <- leer_csv_robusto(CARPETA_SLIDE_2_EXTORSIONES)

# Slide 2.5 ----- #
extorsiones_por_tamanio <- leer_csv_robusto(CARPETA_SLIDE_2_TAMANIO_EMPRESA)

# Slide 3 ----- #
percepcion_2024 <- leer_csv_robusto(CARPETA_SLIDE_3_PERCEPCION_2024)
percepcion_2026 <- leer_csv_robusto(CARPETA_SLIDE_3_PERCEPCION_2026)

# Slide 4 ----- #
costos_2015 <-leer_csv_robusto(CARPETA_SLIDE_4_COSTOS_2015)
costos_2017 <-leer_csv_robusto(CARPETA_SLIDE_4_COSTOS_2017)
costos_2019 <-leer_csv_robusto(CARPETA_SLIDE_4_COSTOS_2019)
costos_2021 <-leer_csv_robusto(CARPETA_SLIDE_4_COSTOS_2021)
costos_2023 <-leer_csv_robusto(CARPETA_SLIDE_4_COSTOS_2023)
costos_2025 <-leer_csv_robusto(CARPETA_SLIDE_4_COSTOS_2025)

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

# ————————————————————————————————————————————————————————— #
# SLIDE 2 -----------
# ————————————————————————————————————————————————————————— #

# INTAKES -------- #
# Solo seleccionar tipo_de_delito == "Extorsión|Extorsiones"
DELITOS_SLIDE_2 <- c("Extorsión")

# Columnas de interés:
# `tipo_delito`
# `delitos ocurridos`
# `delitos en los que dueño y/o empleados no estuvieron presentes y pudieron observarlos`
# `condición de violencia2_delitos con agresión física3_absolutos`
# `condición de violencia2_delitos con amenaza de violencia4_absolutos`

# Crear columna de `condición de violencia atestiguado sin violencia`
# `delitos en los que dueño y/o empleados no estuvieron presentes y pudieron observarlos` - (`condición de violencia2_delitos con agresión física3_absolutos` + `condición de violencia2_delitos con amenaza de violencia4_absolutos`)

# De esta manera tendremos dos columnas:
# `delitos_sin_violencia` == `delitos en los que dueño y/o empleados no estuvieron presentes y pudieron observarlos` + `condición de violencia atestiguado sin violencia`
# `delitos_con_violencia` == `condición de violencia2_delitos con agresión física3_absolutos` + `condición de violencia2_delitos con amenaza de violencia4_absolutos`

# Donde `delitos_sin_violencia` + `delitos_con_violencia` == `delitos ocurridos`

# ORDENAR BASE --- #
extorsion_slide_2 <- extorsiones_2026 |>
    rename(
        tipo_de_delito       = `tipo de delito`,
        delitos_ocurridos    = `delitos ocurridos`,
        delitos_no_presentes = `delitos en los que dueño y/o empleados no estuvieron presentes y pudieron observarlos`,
        delitos_presentes    = `delitos en los que dueño y/o empleados estuvieron presentes y pudieron observarlos`,
        delitos_agresion     = `condición de violencia2_delitos con agresión física3_absolutos`,
        delitos_amenaza      = `condición de violencia2_delitos con amenaza de violencia4_absolutos`,
        delitos_agresion_o_amenaza = `condición de violencia2_delitos con agresión física3 o amenaza de violencia4_absolutos`
    ) |>
    filter(tipo_de_delito %in% DELITOS_SLIDE_2) |>
    select(tipo_de_delito, delitos_ocurridos, delitos_no_presentes, delitos_presentes,
           delitos_agresion, delitos_amenaza, delitos_agresion_o_amenaza) |>
    mutate(
        across(-tipo_de_delito, a_numero),   # acepta "786,802.53"
        delitos_con_violencia = delitos_agresion + delitos_amenaza,
        delitos_atestiguados_sin_violencia = delitos_presentes - delitos_con_violencia,
        delitos_sin_violencia = delitos_no_presentes + delitos_atestiguados_sin_violencia
    )

# VALIDACIONES --- #
stopifnot("Falta algún delito de DELITOS_SLIDE_2" = nrow(extorsion_slide_2) == length(DELITOS_SLIDE_2))
stopifnot("sin + con violencia no suma los delitos ocurridos" =
              with(extorsion_slide_2,
                   all(abs(delitos_sin_violencia + delitos_con_violencia - delitos_ocurridos) < 1)))

# Agresión y amenaza pueden ocurrir en el mismo delito: la suma puede ser un
# poco mayor que la columna "agresión física o amenaza" (que no duplica).
extorsion_slide_2 |>
    mutate(duplicados = delitos_con_violencia - delitos_agresion_o_amenaza) |>
    filter(duplicados > 0) |>
    pwalk(\(tipo_de_delito, duplicados, ...) {
        cat(yellow(glue("Aviso: en '{tipo_de_delito}' agresión + amenaza excede en ",
                        "{round(duplicados)} delitos a 'agresión o amenaza' (delitos con ambas).\n")))
    })

# GUARDAR -------- #
saveRDS(extorsion_slide_2, file.path(CARPETA_PROCESADOS, "extorsion_slide_2.rds"))

# ————————————————————————————————————————————————————————— #
# SLIDE 2.5 -----------
# ————————————————————————————————————————————————————————— #

# INTAKES -------- #
TAMANIOS_EMPRESA <- c("Micro", "Pequeña", "Mediana", "Grande")

# Seleccionar todos los delitos menos "Total"
DELITOS_SLIDE_2_5_EXCLUIR <- c("Total")

# ORDENAR BASES -- #
# Una fila por tamaño de empresa y tipo de delito (la fila del tamaño = "Total";
# "Estados Unidos Mexicanos" es el total de todos los tamaños)
extorsiones_por_tamanio <- extorsiones_por_tamanio |>
    separar_bloques(col_bloque = "tamanio_empresa", categorias = TAMANIOS_EMPRESA) |>
    rename(delitos_ocurridos_absolutos = `delitos ocurridos_absolutos`,
           delitos_ocurridos_relativos = `delitos ocurridos_relativos`)

# CORRECCIONES AL TABULADO DE INEGI -- #
# El relativo es % de los delitos ocurridos en ese tamaño ("Total" del bloque).
# 1) Absolutos que no se pudieron leer (p. ej. Mediana/Extorsión = "11,218,179",
#    que en realidad es 11,218.179): se reconstruyen con relativo * total / 100.
# 2) Relativos que no cuadran con absolutos / total (p. ej. Grande/Extorsión =
#    0.1077 en vez de 10.77): se recalculan.
extorsiones_por_tamanio <- extorsiones_por_tamanio |>
    mutate(
        total_bloque = delitos_ocurridos_absolutos[tipo_de_delito == "Total"],
        absoluto_reconstruido = is.na(delitos_ocurridos_absolutos) & !is.na(delitos_ocurridos_relativos),
        delitos_ocurridos_absolutos = if_else(absoluto_reconstruido,
                                              delitos_ocurridos_relativos * total_bloque / 100,
                                              delitos_ocurridos_absolutos),
        relativo_calculado = 100 * delitos_ocurridos_absolutos / total_bloque,
        relativo_corregido = tipo_de_delito != "Total" &
            abs(relativo_calculado - delitos_ocurridos_relativos) > 0.01,
        delitos_ocurridos_relativos = if_else(tipo_de_delito == "Total",
                                              delitos_ocurridos_relativos, relativo_calculado),
        .by = tamanio_empresa
    )

extorsiones_por_tamanio |>
    filter(absoluto_reconstruido | relativo_corregido) |>
    pwalk(\(tamanio_empresa, tipo_de_delito, absoluto_reconstruido, ...) {
        que <- if (absoluto_reconstruido) "absoluto reconstruido con el relativo" else "relativo recalculado"
        cat(yellow(glue("Corrección: {tamanio_empresa} / {tipo_de_delito}: {que}.\n")))
    })

extorsiones_por_tamanio <- extorsiones_por_tamanio |>
    select(-total_bloque, -relativo_calculado, -absoluto_reconstruido, -relativo_corregido)

extorsiones_por_tamanio <- extorsiones_por_tamanio |>
  filter(!tipo_de_delito %in% DELITOS_SLIDE_2_5_EXCLUIR)

# GUARDAR -------- #
saveRDS(extorsiones_por_tamanio, file.path(CARPETA_PROCESADOS, "extorsiones_por_tamanio_slide_2_5.rds"))

# ————————————————————————————————————————————————————————— #
# SLIDE 3 -----------
# ————————————————————————————————————————————————————————— #

percepcion_2024 <- percepcion_2024 |> clean_names()
percepcion_2026 <- percepcion_2026 |> clean_names()

# Interesa conocer el cambio porcentual entre la percepción relativa en cada entidad federativa.
# Para el valor nacional no debemos guardar en el tabulado final, solo obtener el número (se escribirá en la PPX a parte).
solo_valor <- "Estados Unidos Mexicanos"

# Columnas de interés:
# `entidad_federativa`
# `sensacion_de_seguridad_en_la_entidad_federativa1_inseguro_relativos`

# ORDENAR BASES -- #
seleccionar_inseguro <- function(df, anio) {
    df |>
        select(entidad_federativa,
               inseguro = sensacion_de_seguridad_en_la_entidad_federativa1_inseguro_relativos) |>
        filter(!is.na(entidad_federativa)) |>
        mutate(inseguro = a_numero(inseguro)) |>
        rename_with(~ glue("inseguro_{anio}"), inseguro)
}

percepcion_slide_3 <- seleccionar_inseguro(percepcion_2024, 2024) |>
    full_join(seleccionar_inseguro(percepcion_2026, 2026), by = "entidad_federativa") |>
    mutate(
        # Diferencia en puntos porcentuales: > 0 = aumentó la percepción de inseguridad
        diferencia = inseguro_2026 - inseguro_2024,
        # Nombres cortos para que quepan en la gráfica (los de cat_ent) y
        # "México" -> "Estado de México"
        entidad_federativa = recode(entidad_federativa,
                                    "México"                          = "Estado de México",
                                    "Veracruz de Ignacio de la Llave" = "Veracruz",
                                    "Michoacán de Ocampo"             = "Michoacán",
                                    "Coahuila de Zaragoza"            = "Coahuila")
    )

# VALIDACIONES --- #
faltantes_slide_3 <- percepcion_slide_3 |> filter(is.na(inseguro_2024) | is.na(inseguro_2026))
if (nrow(faltantes_slide_3) > 0) {
    stop("Entidades sin dato en algún año (¿nombres distintos entre 2024 y 2026?): ",
         paste(faltantes_slide_3$entidad_federativa, collapse = ", "))
}
stopifnot("Se esperaban 32 entidades + nacional" = nrow(percepcion_slide_3) == 33)

# VALOR NACIONAL (para escribirlo en la PPT; no va en el tabulado) -- #
nacional_slide_3 <- percepcion_slide_3 |> filter(entidad_federativa == solo_valor)
cat(cyan(glue("Slide 3 | Nacional: {round(nacional_slide_3$inseguro_2024, 1)}% (2024) -> ",
              "{round(nacional_slide_3$inseguro_2026, 1)}% (2026); ",
              "diferencia {sprintf('%+.1f', nacional_slide_3$diferencia)} pp\n")))

percepcion_slide_3 <- percepcion_slide_3 |> filter(entidad_federativa != solo_valor)

# GUARDAR -------- #
saveRDS(percepcion_slide_3, file.path(CARPETA_PROCESADOS, "percepcion_slide_3.rds"))
saveRDS(nacional_slide_3,   file.path(CARPETA_PROCESADOS, "percepcion_nacional_slide_3.rds"))

# ————————————————————————————————————————————————————————— #
# SLIDE 4 -----------
# ————————————————————————————————————————————————————————— #

costos_2015 <- costos_2015 |> clean_names()
costos_2017 <- costos_2017 |> clean_names()
costos_2019 <- costos_2019 |> clean_names()
costos_2021 <- costos_2021 |> clean_names()
costos_2023 <- costos_2023 |> clean_names()
costos_2025 <- costos_2025 |> clean_names()

# INTAKES -------- #
# Solo interesa la dimensión nacional en este caso
ENTIDAD_INTERES <- "Estados Unidos Mexicanos"

# Debido a que en cada levantamiento de la encuesta el número de unidades económicas cambia, 
# usemos solo columnas con promedios.
# `entidad_federativa`
# `unidades_economicas_victimas_del_delito1_promedio_de_gastos`
# `perdidas_a_consecuencia_del_delito_promedio_de_perdidas`

# OJO: en 2019-2025 los encabezados de INEGI están corridos: la columna
# `unidades_economicas_victimas_del_delito1_promedio_de_gastos` NO es un
# promedio, es el número de unidades víctimas (~1.3 millones). Los promedios
# correctos son:
#   - gasto en medidas de protección contra la delincuencia | promedio de gastos
#   - pérdidas a consecuencia del delito | promedio de pérdidas
# Se buscan por nombre (ya limpio) y se valida que haya exactamente una por año.

extraer_promedios_costos <- function(df, anio) {
    buscar <- function(patrones) {
        col <- names(df)[reduce(map(patrones, ~ str_detect(names(df), .x)), `&`)]
        if (length(col) != 1) {
            stop("Costos ", anio, ": se esperaba 1 columna con [", paste(patrones, collapse = " + "),
                 "] y hay ", length(col), ": ", paste(col, collapse = ", "))
        }
        col
    }
    col_gastos   <- buscar(c("gasto_en_medidas", "promedio_de_gastos"))
    col_perdidas <- buscar(c("perdidas_a_consecuencia", "promedio_de_perdidas"))

    df |>
        rename(entidad_federativa = 1) |>
        filter(entidad_federativa == ENTIDAD_INTERES) |>
        transmute(anio            = anio,
                  promedio_gastos   = a_numero(.data[[col_gastos]]),
                  promedio_perdidas = a_numero(.data[[col_perdidas]]))
}

costos_slide_4 <- list(`2015` = costos_2015, `2017` = costos_2017, `2019` = costos_2019,
                       `2021` = costos_2021, `2023` = costos_2023, `2025` = costos_2025) |>
    imap(~ extraer_promedios_costos(.x, as.integer(.y))) |>
    list_rbind() |>
    arrange(anio)

# VALIDACIONES --- #
stopifnot("Falta algún año o el nacional en costos" = nrow(costos_slide_4) == 6)
stopifnot("Hay promedios vacíos en costos" = !anyNA(costos_slide_4))
stopifnot("Algún 'promedio' parece un conteo (> 1 millón de pesos)" =
              all(costos_slide_4$promedio_gastos < 1e6 & costos_slide_4$promedio_perdidas < 1e6))

# DEFLACTAR ---- # 
# Base 100 siendo 2020
# Ciclo | Deflactor implícito
# 2015 | 77.056154163
# 2017 | 87.113807145
# 2019 | 95.612049638
# 2021 | 104.507486428
# 2023 | 116.653616175
# 2025 | 127.759054404

ANIO_BASE_SLIDE_4 <- 2025          # los valores quedan en pesos de este año

deflactor_slide_4 <- tribble(
    ~anio, ~deflactor,
    2015,  77.056154163,
    2017,  87.113807145,
    2019,  95.612049638,
    2021, 104.507486428,
    2023, 116.653616175,
    2025, 127.759054404
)

faltan_deflactor <- setdiff(c(costos_slide_4$anio, ANIO_BASE_SLIDE_4), deflactor_slide_4$anio)
if (length(faltan_deflactor) > 0) {
    stop("Falta el deflactor de: ", paste(faltan_deflactor, collapse = ", "))
}
deflactor_base <- deflactor_slide_4$deflactor[deflactor_slide_4$anio == ANIO_BASE_SLIDE_4]

# valor real = nominal x deflactor(base) / deflactor(año). Se conservan los nominales.
costos_slide_4 <- costos_slide_4 |>
    left_join(deflactor_slide_4, by = "anio") |>
    mutate(
        across(c(promedio_gastos, promedio_perdidas), list(nominal = identity), .names = "{.col}_nominal"),
        across(c(promedio_gastos, promedio_perdidas), ~ .x * deflactor_base / deflactor),
        anio_base = ANIO_BASE_SLIDE_4
    )

cat(cyan(glue("Slide 4 | valores deflactados a pesos de {ANIO_BASE_SLIDE_4} ",
              "(deflactor implícito, 2020 = 100)\n")))

# GUARDAR -------- #
saveRDS(costos_slide_4, file.path(CARPETA_PROCESADOS, "costos_slide_4.rds"))

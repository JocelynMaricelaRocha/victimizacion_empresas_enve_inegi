# ————————————————————————————————————————————————————————— #
# Nombre: Jocelyn Rocha
# Contacto: jocelyn.flores@transformaciondigital.gob.mx
# Script: funciones_enve.R
# Proyecto: Victimización de empresas | ENVE Principales resultados
# Fecha: 2026-11-11
# Propósito: Funciones útiles del repositorio.
# ————————————————————————————————————————————————————————— #

#' Detecta si un archivo es UTF-8 válido revisando una muestra de bytes.
#' Devuelve "UTF-8" o "Latin-1" (nombres que acepta data.table::fread).
detectar_encoding <- function(ruta, n_bytes = 5e6) {
    con <- file(ruta, "rb")
    on.exit(close(con))
    bytes <- readBin(con, "raw", n = n_bytes)
    if (length(bytes) >= 3 && identical(bytes[1:3], as.raw(c(0xEF, 0xBB, 0xBF)))) {
        bytes <- bytes[-(1:3)]
    }
    ult_nl <- max(which(bytes == as.raw(0x0A)), length(bytes))
    if (validUTF8(rawToChar(bytes[seq_len(ult_nl)]))) "UTF-8" else "Latin-1"
}

#' Quita las notas al pie numéricas pegadas al final de un texto
#' (p. ej. "Fraude3" -> "Fraude", "Tasa de incidencia1" -> "Tasa de incidencia").
#' Solo quita dígitos pegados a una letra, así "Delitos 2023" o "tasa_2023" no cambian.
quitar_notas_al_pie <- function(x) stringr::str_remove(x, "(?<=[[:alpha:]])\\d+$")

#' TRUE si la columna no contiene datos numéricos (todos sus valores no-NA fallan as.numeric).
es_texto_no_numerico <- function(x) {
    x <- x[!is.na(x)]
    length(x) > 0 && all(is.na(suppressWarnings(as.numeric(x))))
}

#' Lee un CSV con el encoding detectado y todo como texto.
#' En los nombres de columna y en las columnas de texto sin datos numéricos
#' elimina las notas al pie (números pegados al final).
leer_csv_robusto <- function(ruta) {
    if (!file.exists(ruta)) {
        stop("No existe ", ruta, ".\nArchivos en la carpeta:\n  ",
             paste(list.files(dirname(ruta)), collapse = "\n  "))
    }
    enc <- detectar_encoding(ruta)
    data.table::fread(ruta, encoding = enc, colClasses = "character",
                      na.strings = c("", "NA", "NULL")) |>
        tibble::as_tibble() |>
        dplyr::rename_with(~ quitar_notas_al_pie(stringr::str_to_lower(stringr::str_trim(.x)))) |>
        dplyr::mutate(dplyr::across(dplyr::where(is.character), enc2utf8)) |>
        dplyr::mutate(dplyr::across(dplyr::where(es_texto_no_numerico),
                                    ~ stringr::str_squish(quitar_notas_al_pie(.x))))
}

#' Separa los tabulados INEGI con formato "Entidad federativa_Tipo de delito":
#' bloques que inician con el nombre de la entidad (fila con el total) seguidos
#' de los delitos y separados por una fila de NAs.
#' Devuelve: entidad_federativa | tipo_de_delito | <columnas de valores (numéricas)>.
#' La fila de la entidad queda con tipo_de_delito = "Total".
#' La entidad se identifica por estructura (primera fila de cada bloque) y se
#' valida contra `nombres_entidades` (acepta nombres cortos del catálogo, p. ej.
#' "Coahuila" valida "Coahuila de Zaragoza").
separar_entidad_delito <- function(df, nombres_entidades,
                                   nacional = "Estados Unidos Mexicanos") {
    col_etq <- names(df)[1]

    out <- df |>
        dplyr::rename(etiqueta = dplyr::all_of(col_etq)) |>
        dplyr::mutate(
            vacia      = is.na(etiqueta),
            es_entidad = !vacia & (dplyr::row_number() == 1 | dplyr::lag(vacia, default = TRUE)),
            entidad_federativa = dplyr::if_else(es_entidad, etiqueta, NA_character_),
            tipo_de_delito     = dplyr::if_else(es_entidad, "Total", etiqueta)
        ) |>
        tidyr::fill(entidad_federativa, .direction = "down") |>
        dplyr::filter(!vacia) |>
        dplyr::select(entidad_federativa, tipo_de_delito, dplyr::everything(),
                      -etiqueta, -vacia, -es_entidad) |>
        dplyr::mutate(dplyr::across(-c(entidad_federativa, tipo_de_delito), as.numeric))

    # Validación contra el catálogo
    ents   <- unique(out$entidad_federativa)
    cat_n  <- normalizar(c(nacional, nombres_entidades))
    ok     <- vapply(normalizar(ents), function(e) any(startsWith(e, cat_n)), logical(1))
    sin_ent <- setdiff(nombres_entidades,
                       nombres_entidades[vapply(normalizar(nombres_entidades),
                                                function(c) any(startsWith(normalizar(ents), c)),
                                                logical(1))])
    if (!all(ok) || length(sin_ent) > 0) {
        warning("Revisar entidades.\n  Bloques que no están en el catálogo: ",
                paste(ents[!ok], collapse = ", "),
                "\n  Entidades del catálogo sin bloque: ", paste(sin_ent, collapse = ", "))
    }
    out
}

#' Normaliza texto para comparar (sin acentos, minúsculas, sin espacios extra).
normalizar <- function(x) stringr::str_squish(stringr::str_to_lower(stringi::stri_trans_general(x, "Latin-ASCII")))

#' Texto seguro para nombres de archivo ("Robo/asalto de bienes" -> "robo_asalto_de_bienes").
slug <- function(x) stringr::str_replace_all(normalizar(x), "[^a-z0-9]+", "_") |>
    stringr::str_remove_all("^_|_$")

# ————————————————————————————————————————————————————————— #
# PYTHON (para correr Pabloplot con system2, sin reticulate)
# ————————————————————————————————————————————————————————— #

#' Lee pares CLAVE=valor de un archivo .env (si existe).
leer_env <- function(ruta = here::here(".env")) {
    if (!file.exists(ruta)) return(character(0))
    lineas <- readLines(ruta, warn = FALSE, encoding = "UTF-8")
    lineas <- stringr::str_trim(lineas[stringr::str_detect(lineas, "^\\s*[A-Za-z_]+\\s*=")])
    stats::setNames(stringr::str_remove_all(stringr::str_remove(lineas, "^[^=]+=\\s*"), "^[\"']|[\"']$"),
                    stringr::str_trim(stringr::str_remove(lineas, "=.*$")))
}

#' Devuelve la ruta del ejecutable real de Python 3.
#' Orden: PYTHON_PATH del .env, variable de entorno PYTHON_PATH, python3/python/py del PATH.
#' Cada candidato se prueba ejecutándolo y se usa su sys.executable; así funcionan
#' los alias de WindowsApps del Python Install Manager y se descarta el alias
#' vacío de Microsoft Store (que no corre).
encontrar_python <- function() {
    candidatos <- c(leer_env()["PYTHON_PATH"], Sys.getenv("PYTHON_PATH"),
                    Sys.which("python3"), Sys.which("python"), Sys.which("py"))
    candidatos <- unique(candidatos[!is.na(candidatos) & candidatos != ""])
    for (py in candidatos) {
        exe <- suppressWarnings(tryCatch(
            system2(py, c("-c", shQuote("import sys; print(sys.version_info[0]); print(sys.executable)")),
                    stdout = TRUE, stderr = FALSE),
            error = function(e) character(0)))
        if (length(exe) >= 2 && exe[1] == "3" && file.exists(exe[2])) {
            return(normalizePath(exe[2], winslash = "/"))
        }
    }
    stop("No encontré Python 3. Instálalo (python.org) o pon su ruta en .env como PYTHON_PATH=...")
}

# glue() por defecto recorta el salto de línea final; aquí se conserva para
# que los mensajes de consola no queden pegados.
glue <- function(..., .envir = parent.frame(), .trim = FALSE) glue::glue(..., .envir = .envir, .trim = .trim)

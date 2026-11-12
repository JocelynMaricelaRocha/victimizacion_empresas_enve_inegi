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

#' Separa tabulados INEGI con formato "<Dimensión>_Tipo de delito": bloques que
#' inician con el nombre de la categoría (fila con el total) seguidos de los
#' delitos y separados por una fila de NAs. Sirve para entidad federativa,
#' tamaño de empresa, sector, etc.
#' Devuelve: <col_bloque> | tipo_de_delito | <columnas de valores (numéricas)>.
#' La fila de la categoría queda con tipo_de_delito = "Total".
#' La categoría se identifica por estructura (primera fila de cada bloque) y, si
#' se da `categorias`, se valida contra ellas (acepta nombres cortos: "Coahuila"
#' valida "Coahuila de Zaragoza"). `nacional` también se acepta como bloque.
separar_bloques <- function(df, col_bloque, categorias = NULL,
                            nacional = "Estados Unidos Mexicanos") {
    col_etq <- names(df)[1]

    out <- df |>
        dplyr::rename(etiqueta = dplyr::all_of(col_etq)) |>
        dplyr::mutate(
            vacia    = is.na(etiqueta),
            es_bloque = !vacia & (dplyr::row_number() == 1 | dplyr::lag(vacia, default = TRUE)),
            !!col_bloque    := dplyr::if_else(es_bloque, etiqueta, NA_character_),
            tipo_de_delito   = dplyr::if_else(es_bloque, "Total", etiqueta)
        ) |>
        tidyr::fill(dplyr::all_of(col_bloque), .direction = "down") |>
        dplyr::filter(!vacia) |>
        dplyr::select(dplyr::all_of(col_bloque), tipo_de_delito, dplyr::everything(),
                      -etiqueta, -vacia, -es_bloque)

    # Valores que no son número (p. ej. "11,218,179"): se avisa en vez de
    # convertirlos en NA en silencio.
    cols_valor <- setdiff(names(out), c(col_bloque, "tipo_de_delito"))
    for (col in cols_valor) {
        x <- out[[col]]
        num <- suppressWarnings(a_numero(x))
        malos <- !is.na(x) & is.na(num)
        if (any(malos)) {
            warning("Valores no numéricos en '", col, "' (quedan como NA):\n  ",
                    paste0(out[[col_bloque]][malos], " / ", out$tipo_de_delito[malos],
                           ": \"", x[malos], "\"", collapse = "\n  "), call. = FALSE)
        }
        out[[col]] <- num
    }

    # Validación contra las categorías esperadas
    if (!is.null(categorias)) {
        bloques <- unique(out[[col_bloque]])
        esperadas_n <- normalizar(c(nacional, categorias))
        ok <- vapply(normalizar(bloques), function(e) any(startsWith(e, esperadas_n)), logical(1))
        sin_bloque <- categorias[!vapply(normalizar(categorias),
                                         function(c) any(startsWith(normalizar(bloques), c)),
                                         logical(1))]
        if (!all(ok) || length(sin_bloque) > 0) {
            warning("Revisar '", col_bloque, "'.\n  Bloques que no están en las categorías: ",
                    paste(bloques[!ok], collapse = ", "),
                    "\n  Categorías sin bloque: ", paste(sin_bloque, collapse = ", "), call. = FALSE)
        }
    }
    out
}

#' Atajo de separar_bloques() para "Entidad federativa_Tipo de delito".
separar_entidad_delito <- function(df, nombres_entidades,
                                   nacional = "Estados Unidos Mexicanos") {
    separar_bloques(df, col_bloque = "entidad_federativa",
                    categorias = nombres_entidades, nacional = nacional)
}

#' Convierte texto a número aceptando comas de miles SOLO cuando no hay
#' ambigüedad: "786,802.53" -> 786802.53 (comas cada 3 dígitos + punto decimal).
#' "11,218,179" (sin punto) es ambiguo (¿miles o decimal mal puesto?): queda NA
#' y se avisa, para revisarlo a mano.
a_numero <- function(x) {
    x <- stringr::str_trim(as.character(x))
    con_miles <- !is.na(x) & stringr::str_detect(x, "^-?\\d{1,3}(,\\d{3})+\\.\\d+$")
    x[con_miles] <- stringr::str_remove_all(x[con_miles], ",")
    num <- suppressWarnings(as.numeric(x))
    malos <- !is.na(x) & x != "" & is.na(num)
    if (any(malos)) {
        warning("Valores no numéricos (quedan como NA): ",
                paste0("\"", unique(x[malos]), "\"", collapse = ", "), call. = FALSE)
    }
    num
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

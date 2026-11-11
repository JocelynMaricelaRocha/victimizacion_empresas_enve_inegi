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

#' Lee un CSV con el encoding detectado y todo como texto.
leer_csv_robusto <- function(ruta) {
    if (!file.exists(ruta)) {
        stop("No existe ", ruta, ".\nArchivos en la carpeta:\n  ",
             paste(list.files(dirname(ruta)), collapse = "\n  "))
    }
    enc <- detectar_encoding(ruta)
    data.table::fread(ruta, encoding = enc, colClasses = "character",
                      na.strings = c("", "NA", "NULL")) |>
        tibble::as_tibble() |>
        dplyr::rename_with(~ stringr::str_to_lower(stringr::str_trim(.x))) |>
        dplyr::mutate(dplyr::across(dplyr::where(is.character), enc2utf8))
}

#' Normaliza texto para comparar (sin acentos, minúsculas, sin espacios extra).
normalizar <- function(x) stringr::str_squish(stringr::str_to_lower(stringi::stri_trans_general(x, "Latin-ASCII")))

# glue() por defecto recorta el salto de línea final; aquí se conserva para
# que los mensajes de consola no queden pegados.
glue <- function(..., .envir = parent.frame(), .trim = FALSE) glue::glue(..., .envir = .envir, .trim = .trim)

# ============================================================================
# ARCHIVO: robot_banco_mundial.py   (el robot del equipo g02)   · VERSIÓN 2 · SEMANA 7
# QUÉ HACE:  Trae los dos indicadores del equipo desde el Banco Mundial, los revisa
#            con las reglas de calidad del equipo y SOLO si pasan los guarda.
# NOVEDADES DE LA SEMANA 7 («Avisa si falla»):
#   1. Reintentos con espera creciente (2 s, 4 s, 8 s...).
#   2. Control de calidad: si los datos no son creíbles, se detiene y no guarda.
#   3. Bitácora: una línea por evento en logs/bitacora_g02.jsonl
#   4. Salud: una fila por corrida en logs/salud_g02.csv (verde, amarillo o rojo).
#   5. Escritura atómica: el archivo de datos nunca queda cortado a medias.
#   6. Simulacro: con SIMULAR_FALLA=true finge que el Banco Mundial no contesta.
# ESTO PUEDEN CAMBIARLO: las reglas de la sección «REGLAS DEL EQUIPO».
# ============================================================================
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

EQUIPO = "g02"
INDICADORES = {"FS.AST.PRVT.GD.ZS": "Crédito al sector privado (% del PIB)", "FB.AST.NPER.ZS": "Morosidad bancaria (% de la cartera)"}

# --- REGLAS DEL EQUIPO (decididas en el cuaderno de la semana 7) ---
RANGOS = {"FS.AST.PRVT.GD.ZS": (5.0, 120.0), "FB.AST.NPER.ZS": (0.0, 25.0)}              # valor mínimo y máximo CREÍBLE de cada indicador
MIN_FILAS = 10                  # menos filas que esto = llegó incompleto
MAX_ANIOS_SIN_DATO = 4         # si el último año tiene más antigüedad, el dato está viejo
REINTENTOS = 3                # cuántas veces más intenta si la fuente no contesta
ESPERA_INICIAL = 2                # segundos de la primera espera; luego se duplica

DESDE, HASTA = 2015, 2025
SIMULAR_FALLA = os.environ.get("SIMULAR_FALLA", "false").lower() == "true"
CORRIDA = os.environ.get("GITHUB_RUN_ID") or datetime.now(timezone.utc).strftime("local-%Y%m%dT%H%M%S")
EN_GITHUB = os.environ.get("GITHUB_ACTIONS") == "true"

DATA, LOGS = Path("data"), Path("logs")
ARCHIVO_DATOS = DATA / f"indicadores_{EQUIPO}.csv"
BITACORA = LOGS / f"bitacora_{EQUIPO}.jsonl"
SALUD = LOGS / f"salud_{EQUIPO}.csv"
REINTENTOS_USADOS = []


class ErrorDeDatos(Exception):
    """Los datos llegaron, pero no son creíbles. Reintentar no lo arregla."""


def anotar(nivel, evento, **detalles):
    # Bitácora: una línea JSON por evento, siempre con los mismos campos.
    LOGS.mkdir(exist_ok=True)
    fila = {"momento_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "corrida": CORRIDA,
            "equipo": EQUIPO, "nivel": nivel, "evento": evento, **detalles}
    with open(BITACORA, "a", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False, default=str) + "\n")
    print(f"[{nivel:<7}] {evento}" + (" · " + ", ".join(f"{k}={v}" for k, v in detalles.items()) if detalles else ""))
    if EN_GITHUB and nivel in ("WARNING", "ERROR"):
        print(f"::{'warning' if nivel == 'WARNING' else 'error'} title=Robot {EQUIPO}::{evento}")


def traer(codigo):
    # Pide UN indicador. Si la fuente no contesta, espera cada vez más y reintenta.
    url = (f"https://api.worldbank.org/v2/country/ECU/indicator/{codigo}"
           f"?format=json&date={DESDE}:{HASTA}&per_page=100")
    for intento in range(1, REINTENTOS + 2):
        try:
            if SIMULAR_FALLA:
                raise ConnectionError("SIMULACRO: el Banco Mundial no contesta (falla provocada a propósito)")
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            datos = r.json()
            if len(datos) < 2 or not datos[1]:
                raise ErrorDeDatos(f"{codigo}: el Banco Mundial respondió, pero sin datos")
            return datos[1]
        except ErrorDeDatos:
            raise                                    # datos malos: no se reintenta
        except Exception as e:
            if intento > REINTENTOS:
                raise ConnectionError(f"{codigo}: no contestó después de {intento} intentos ({e})")
            pausa = ESPERA_INICIAL * 2 ** (intento - 1)
            REINTENTOS_USADOS.append(codigo)
            anotar("WARNING", f"{codigo}: intento {intento} falló; espero {pausa} s y reintento", error=str(e)[:150])
            time.sleep(pausa)


def revisar(tabla):
    # El control de calidad del equipo. Devuelve la lista de problemas (vacía = todo bien).
    problemas = []
    if tabla.empty:
        return ["no llegó ninguna fila"]
    if len(tabla) < MIN_FILAS:
        problemas.append(f"solo {len(tabla)} filas (mínimo {MIN_FILAS})")
    for codigo, nombre in INDICADORES.items():
        parte = tabla[tabla["codigo"] == codigo]
        if parte.empty:
            problemas.append(f"falta el indicador {nombre}")
            continue
        lo, hi = RANGOS[codigo]
        raros = parte[(parte["valor"] < lo) | (parte["valor"] > hi)]
        if len(raros):
            problemas.append(f"{nombre}: {len(raros)} valor(es) fuera de lo creíble ({lo} a {hi})")
        ultimo = int(parte["anio"].max())
        if ultimo < datetime.now(timezone.utc).year - MAX_ANIOS_SIN_DATO:
            problemas.append(f"{nombre}: el último dato es de {ultimo} (dato viejo)")
    return problemas


def guardar_atomico(tabla):
    # Escribe un borrador y lo cambia por el archivo de verdad en un solo movimiento.
    DATA.mkdir(exist_ok=True)
    borrador = ARCHIVO_DATOS.with_suffix(".tmp")
    tabla.to_csv(borrador, index=False)
    borrador.replace(ARCHIVO_DATOS)


def registrar_salud(estado, motivo, filas, segundos):
    # Una fila por corrida. Si GitHub repite la MISMA corrida, se reemplaza (idempotencia).
    LOGS.mkdir(exist_ok=True)
    fila = {"fecha_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "corrida": CORRIDA,
            "estado": estado, "motivo": motivo, "filas": filas, "segundos": round(segundos, 1)}
    salud = pd.read_csv(SALUD) if SALUD.exists() else pd.DataFrame(columns=list(fila))
    salud = salud[salud["corrida"].astype(str) != str(CORRIDA)]
    pd.concat([salud, pd.DataFrame([fila])], ignore_index=True).to_csv(SALUD, index=False)
    return salud


def resumen_en_github():
    # Escribe el tablero de salud en la pantalla de la corrida de GitHub.
    destino = os.environ.get("GITHUB_STEP_SUMMARY")
    if not destino or not SALUD.exists():
        return
    s = pd.read_csv(SALUD).tail(7).iloc[::-1]
    icono = {"verde": "🟢", "amarillo": "🟡", "rojo": "🔴"}
    filas = "\n".join(f"| {r.fecha_utc[:16].replace('T', ' ')} | {icono.get(r.estado, '')} {r.estado} | {r.motivo} |"
                      for r in s.itertuples())
    with open(destino, "a", encoding="utf-8") as f:
        f.write(f"## Salud del robot {EQUIPO}\n\n| Fecha (UTC) | Estado | Motivo |\n|---|---|---|\n{filas}\n")


def main():
    inicio = time.time()
    anotar("INFO", "inicio de la corrida", simulacro=SIMULAR_FALLA)
    filas_guardadas = 0
    try:
        filas = []
        for codigo, nombre in INDICADORES.items():
            for d in traer(codigo):
                if d.get("value") is not None:
                    filas.append({"anio": int(d["date"]), "codigo": codigo, "indicador": nombre, "valor": d["value"]})
            anotar("INFO", f"{codigo}: recibido")
        tabla = pd.DataFrame(filas, columns=["anio", "codigo", "indicador", "valor"]).sort_values(["codigo", "anio"])
        problemas = revisar(tabla)
        if problemas:
            raise ErrorDeDatos("; ".join(problemas))
        guardar_atomico(tabla)
        filas_guardadas = len(tabla)
        anotar("INFO", "datos aprobados y guardados", filas=filas_guardadas, archivo=str(ARCHIVO_DATOS))
        estado, motivo = ("amarillo", "funcionó, pero tuvo que reintentar") if REINTENTOS_USADOS else ("verde", "todo bien")
    except ErrorDeDatos as e:
        estado, motivo = "rojo", f"datos no confiables: {e}"
        anotar("ERROR", motivo)
    except Exception as e:
        estado, motivo = "rojo", f"la fuente falló: {e}"
        anotar("ERROR", motivo)
    if estado == "rojo" and ARCHIVO_DATOS.exists():
        anotar("INFO", "plan B: se conservan intactos los datos de la última corrida buena")
    registrar_salud(estado, motivo, filas_guardadas, time.time() - inicio)
    resumen_en_github()
    print(f"RESULTADO: {estado.upper()} · {motivo}")
    sys.exit(1 if estado == "rojo" else 0)


if __name__ == "__main__":
    main()

import json
import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd


def cargar_configuracion(raiz):
    archivo = raiz / ".config" / "settings.json"
    try:
        configuracion = json.loads(archivo.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError("Revisa la sintaxis de .config/settings.json.") from error
    if not isinstance(configuracion, dict) or not isinstance(configuracion.get("ruta_base_datos"), str):
        raise ValueError("Falta ruta_base_datos en .config/settings.json.")
    return configuracion


def conectar(ruta):
    # mode=ro impide modificar la base o crear una base vacía por una ruta errónea.
    return sqlite3.connect(Path(ruta).resolve().as_uri() + "?mode=ro", uri=True)


def comprobar_base(ruta):
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encontró la base de datos: {ruta.name}")
    with closing(conectar(ruta)) as conexion:
        conexion.execute("SELECT vuelo_id, apto_analisis FROM fact_analisis_vuelos LIMIT 1")
        conexion.execute("SELECT vuelo_id FROM vw_muestra_retrasos LIMIT 1")


def resumen_base(ruta):
    with closing(conectar(ruta)) as conexion:
        total, aptos, excluidos = conexion.execute(
            "SELECT COUNT(*), COALESCE(SUM(apto_analisis = 1), 0), "
            "COALESCE(SUM(apto_analisis = 0), 0) FROM fact_analisis_vuelos"
        ).fetchone()
        fecha_min, fecha_max = conexion.execute(
            "SELECT MIN(fecha_salida_local_id), MAX(fecha_salida_local_id) "
            "FROM vw_muestra_retrasos"
        ).fetchone()
    return dict(total=total, aptos=aptos, excluidos=excluidos,
                fecha_min=fecha_min or "Sin datos", fecha_max=fecha_max or "Sin datos")


def muestra_vuelos(ruta):
    consulta = """
        SELECT vuelo_id AS "ID vuelo", numero_vuelo AS "Número de vuelo",
               aeropuerto_origen_nombre AS "Aeropuerto de origen",
               aeropuerto_destino_nombre AS "Aeropuerto de destino",
               modelo_aeronave AS "Aeronave",
               salida_programada_local_origen AS "Salida programada (hora local origen)",
               salida_real_local_origen AS "Salida real (hora local origen)",
               retraso_salida_min AS "Retraso de salida (min)",
               retraso_llegada_min AS "Retraso de llegada (min)"
        FROM vw_muestra_retrasos
        ORDER BY salida_programada_utc, vuelo_id
        LIMIT 100
    """
    with closing(conectar(ruta)) as conexion:
        return pd.read_sql_query(consulta, conexion)


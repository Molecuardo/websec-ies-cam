# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 20:04:41 2025

@author: Javier Sánchez Zurdo

https://code.visualstudio.com/docs/python/environments
Creating environment command:
   Control + Shift + P
   Venv as a virtual environment
   Delete and recreate environment

   Control + Shift + P
    Python: Select Interpreter


pip install pandas requests openpyxl cryptography
"""

# %% --------------------------------------------------------------------------
# Librerias
# ----------------------------------------------------------------------------
import random
import datetime, time
import pandas as pd
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# %% --------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------
carpeta = "/home/pablo/Documentos/Institutos_Pablo/"
# carpeta = 'C:/Institutos_Pablo/'
fichero_excel = carpeta + "All_Institutos.xlsx"
pestana_excel = "Listado institutos"
carpeta_resultados = carpeta + "EscaneosNTP/"

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
]


# %% --------------------------------------------------------------------------
# Funciones
# ----------------------------------------------------------------------------
def leer_fichero_excel(fichero_excel: str, pestana_excel: str) -> pd.DataFrame:
    df = pd.read_excel(fichero_excel, sheet_name=pestana_excel, engine="openpyxl")
    return df


def pon_url_con_protocolo(url: str) -> str:
    if "http://" in url:
        return url
    if "https://" in url:
        return url
    resultado = "https://" + url
    return resultado


def haz_consulta_web(
    identificador_instituto: int, nombre_instituto: str, url: str, headers: str
):
    success = False
    retries = 1
    while (not success) and (retries < 5):
        try:
            response = requests.get(
                url_protocolo, timeout=100, verify=False, headers=headers
            )
            success = True
            return response
        except Exception as e:
            wait = retries * 30
            print(
                "\tError in "
                + str(identificador_instituto)
                + " "
                + nombre_instituto
                + " "
                + u
                + " Retry"
            )
            time.sleep(wait)
            retries += 1
    print("\tError not recovered")
    return None


# %% --------------------------------------------------------------------------
# Codigo principal
# ----------------------------------------------------------------------------
start_time = datetime.datetime.now()
# Se lee el fichero excel para extraer la tabla de todos los institutos:
df_institutos = leer_fichero_excel(fichero_excel, pestana_excel)

# Para cada instituto, vamos a hacer la consulta de tiempo y lo guardamos en fichero:
for index, raw in df_institutos.iterrows():
    headers = {"User-Agent": random.choice(user_agents)}
    identificador_instituto = raw["Codigo"]
    nombre_instituto = raw["Nombre"]
    url_web = raw["Web"]
    url_aula = raw["Aula_Virtual"]
    dict_urls_a_revisar = {}
    if url_web == url_web:  # is not nan
        dict_urls_a_revisar["url_web"] = url_web
    else:
        print(str(index) + "\t" + nombre_instituto + "\tSin URL en web")
    if url_aula == url_aula:  # is not nan
        dict_urls_a_revisar["url_aula"] = url_aula
    else:
        print(str(index) + "\t" + nombre_instituto + "\tSin URL aula")
    # dict_urls_a_revisar = {'url_web': url_web, 'url_aula': url_aula}
    for u in dict_urls_a_revisar:
        url_protocolo = pon_url_con_protocolo(dict_urls_a_revisar[u])
        # Sacamos la hora oficial:
        datetime_actual = datetime.datetime.utcnow()
        # Hacemos la consulta de la web con varios reintentos si falla:
        response = haz_consulta_web(
            url=url_protocolo,
            identificador_instituto=identificador_instituto,
            nombre_instituto=nombre_instituto,
            headers=headers,
        )
        if response is None:
            continue
        # Sacamos los datos de la consulta:
        codigo_respuesta = response.status_code
        cabeceras = dict(response.headers)
        if "Date" not in cabeceras:
            print(
                "\tError in "
                + str(identificador_instituto)
                + " "
                + nombre_instituto
                + " "
                + u
                + " Not date: "
                + str(cabeceras)
            )
            continue
        fecha_hora = cabeceras["Date"]  # RFC 9110
        datetime_web = datetime.datetime.strptime(
            fecha_hora, "%a, %d %b %Y %H:%M:%S %Z"
        )
        seg_dif = (datetime_web - datetime_actual).total_seconds()
        dict_data = {
            "test": "ntp_" + u,
            "url": url_protocolo,
            "delta_sg": seg_dif,
            "cabeceras": cabeceras,
        }
        # Ahora creamos el nombre del fichero que tendrá los resultados:
        filename_resultados = datetime_actual.strftime("%Y%m%d")
        filename_resultados += "_" + str(identificador_instituto)
        filename_resultados += "_" + nombre_instituto
        filename_resultados += "_" + u + "_NTP.json"
        with open(carpeta_resultados + filename_resultados, "w") as f:
            f.write(json.dumps(dict(dict_data), indent=3, ensure_ascii=False))
        print(str(index) + "\t" + filename_resultados)

print("Fin de escaneo")
# Hemos tardado:
tiempo_total = datetime.datetime.now() - start_time
print("Tiempo total (hh:mm:ss.ms) {}".format(tiempo_total))

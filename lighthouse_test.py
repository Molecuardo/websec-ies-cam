# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 20:04:41 2025

@author: Pablo Díaz Pelayo

https://code.visualstudio.com/docs/python/environments
Creating environment command:
   Control + Shift + P
   Venv as a virtual environment

   Control + Shift + P
    Python: Select Interpreter

pip install pandas requests openpyxl
"""

# Queremos utlizar light house para extraer las metricas de cada pagina web:

# %% --------------------------------------------------------------------------
# Librerias
# ----------------------------------------------------------------------------
import random
import subprocess
import datetime, time
import pandas as pd
import json

# %% --------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------
carpeta = "/home/pablo/Documentos/Institutos_Pablo/"
fichero_excel = carpeta + "All_Institutos.xlsx"
pestana_excel = "Listado institutos"
carpeta_resultados = carpeta + "EscaneosLightHouse/"
# usuario = 'morde'
# usuario = 'h70503'
# binario_lighthouse = f"C:/Users/{usuario}/AppData/Roaming/npm/lighthouse.cmd"
binario_lighthouse = f"/home/pablo/.nvm/versions/node/v20.19.1/bin/lighthouse"
light_house_output_file = carpeta + "lighthouse_report.json"

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


def run_lighthouse(url) -> dict:
    dict_return = {
        "test": "light_house_url_",
        "url": url,
        "fetchTime": None,
        "speed-index": None,
        "is-on-https": None,
        "redirects-http": None,
        "clickjacking-mitigation": None,
        "performance": 0.0,
        "accessibility": 0.0,
        "best-practices": 0.0,
        "seo": 0.0,
    }
    command = [
        binario_lighthouse,
        url,
        "--quiet",
        "--chrome-flags=--headless",
        "--output=json",
        f"--output-path={light_house_output_file}",
    ]
    performance = accessibility = best_practices = seo = 0.0
    fetchTime = speed_index = is_on_https = redirects_http = clickjacking_mitigation = (
        None
    )
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error en el análisis: {result.stderr}")
    with open(light_house_output_file, "r", encoding="utf8") as f:
        json_data = json.load(f)
        try:
            performance = json_data["categories"]["performance"]["score"]
        except KeyError:
            performance = None
        try:
            accessibility = json_data["categories"]["accessibility"]["score"]
        except KeyError:
            accessibility = None
        try:
            best_practices = json_data["categories"]["best-practices"]["score"]
        except KeyError:
            best_practices = None
        try:
            seo = json_data["categories"]["seo"]["score"]
        except KeyError:
            seo = None
        try:
            fetchTime = json_data["fetchTime"]
        except KeyError:
            fetchTime = None
        try:
            speed_index = json_data["audits"]["speed-index"]["score"]
        except KeyError:
            speed_index = None
        try:
            is_on_https = json_data["audits"]["is-on-https"]["score"]
        except KeyError:
            is_on_https = None
        try:
            redirects_http = json_data["audits"]["redirects-http"]["score"]
        except KeyError:
            redirects_http = None
        try:
            clickjacking_mitigation = json_data["audits"]["clickjacking-mitigation"][
                "score"
            ]
        except KeyError:
            clickjacking_mitigation = None
    dict_return["fetchTime"] = fetchTime
    dict_return["performance"] = performance
    dict_return["accessibility"] = accessibility
    dict_return["best-practices"] = best_practices
    dict_return["seo"] = seo
    dict_return["speed-index"] = speed_index
    dict_return["is-on-https"] = is_on_https
    dict_return["redirects-http"] = redirects_http
    dict_return["clickjacking-mitigation"] = clickjacking_mitigation
    return dict_return


# %% --------------------------------------------------------------------------
# Codigo principal
# ----------------------------------------------------------------------------
start_time = datetime.datetime.now()
# Se lee el fichero excel para extraer la tabla de todos los institutos:
df_institutos = leer_fichero_excel(fichero_excel, pestana_excel)
# Sacamos la hora oficial:
datetime_actual = datetime.datetime.now(datetime.timezone.utc)
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
        # Hacemos la consulta de la web con varios reintentos si falla:
        dict_results = run_lighthouse(url=url_protocolo)
        dict_results["test"] = "light_house_" + u
        # Ahora creamos el nombre del fichero que tendrá los resultados:
        filename_resultados = datetime_actual.strftime("%Y%m%d")
        filename_resultados += "_" + str(identificador_instituto)
        filename_resultados += "_" + nombre_instituto
        filename_resultados += "_" + u + "_LightHouse.json"
        with open(carpeta_resultados + filename_resultados, "w") as f:
            f.write(json.dumps(dict(dict_results), indent=3, ensure_ascii=False))
        print(str(index) + "\t" + filename_resultados)

print("Fin de escaneo")
# Hemos tardado:
tiempo_total = datetime.datetime.now() - start_time
print("Tiempo total (hh:mm:ss.ms) {}".format(tiempo_total))

# %%

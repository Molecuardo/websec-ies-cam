# -*- coding: utf-8 -*-
"""
Created on Sun Feb 16 18:28:39 2025

@author: Javier Sánchez Zurdo
"""

# %% --------------------------------------------------------------------------
# Librerias
# ----------------------------------------------------------------------------
import random
import ssl
import socket
import datetime, time
import pandas as pd
import json
import os

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, dsa

# %% --------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------
carpeta = "/home/pablo/Documentos/Institutos_Pablo/"
fichero_excel = carpeta + "All_Institutos.xlsx"
pestana_excel = "Listado institutos"
carpeta_resultados = carpeta + "EscaneosCertificados/"

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


def quitar_protocolo_de_url(url: str) -> str:
    return url.replace("http://", "").replace("https://", "")


def evaluar_calidad(dias_restantes, algoritmo_firma, algoritmo_clave, longitud_clave):
    # Evaluar días restantes
    if dias_restantes > 90:
        calidad_dias = "Bueno"
    elif dias_restantes >= 30:
        calidad_dias = "Aceptable"
    else:
        calidad_dias = "Deficiente"

    # Evaluar algoritmo de firma
    if algoritmo_firma in ["sha256", "sha384", "sha512"]:
        calidad_firma = "Bueno"
    elif algoritmo_firma in ["sha1"]:
        calidad_firma = "Aceptable"
    else:
        calidad_firma = "Deficiente"

    # Evaluar algoritmo de clave y longitud
    # Ahora para el algoritmo de la clave tipo RSA
    if algoritmo_clave == "RSA":
        if longitud_clave >= 3072:
            calidad_clave = "Bueno"
        elif longitud_clave >= 2048:
            calidad_clave = "Aceptable"
        else:
            calidad_clave = "Deficiente"
    # Ahora para el algoritmo de la clave tipo ECC
    elif algoritmo_clave == "ECC":
        if longitud_clave >= 256:
            calidad_clave = "Bueno"
        elif longitud_clave >= 224:
            calidad_clave = "Aceptable"
        else:
            calidad_clave = "Deficiente"
    # Ahora para el algoritmo de la clave tipo DSA
    elif algoritmo_clave == "DSA":
        if longitud_clave >= 2048:
            calidad_clave = "Bueno"
        elif longitud_clave >= 1024:
            calidad_clave = "Aceptable"
        else:
            calidad_clave = "Deficiente"
    # Para cualquier otro algoritmo:
    else:
        calidad_clave = "Deficiente"

    # Determinar calidad final (se toma la peor)
    if "Deficiente" in [calidad_dias, calidad_firma, calidad_clave]:
        return "Deficiente"
    elif "Aceptable" in [calidad_dias, calidad_firma, calidad_clave]:
        return "Aceptable"
    else:
        return "Buena"


def obtener_info_certificado(dominio, port=443):
    dict_return = {
        "dominio": dominio,
        "fecha_inicio": None,
        "fecha_expiracion": None,
        "dias_restantes": None,
        "emisor": None,
        "algoritmo_firma": None,
        "algoritmo_clave": None,
        "longitud_clave": None,
        "calidad": "Deficiente",
    }
    try:
        # Crear un contexto SSL
        context = ssl.create_default_context()

        # Conectar con el servidor y obtener el certificado en formato PEM
        with socket.create_connection((dominio, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=dominio) as ssock:
                cert_pem = ssl.DER_cert_to_PEM_cert(ssock.getpeercert(binary_form=True))

        # Cargar el certificado con cryptography
        cert_obj = x509.load_pem_x509_certificate(cert_pem.encode())

        # Extraer información relevante
        fecha_inicio = cert_obj.not_valid_before
        fecha_expiracion = cert_obj.not_valid_after
        dias_restantes = (fecha_expiracion - datetime.datetime.utcnow()).days

        # Obtener el emisor del certificado
        emisor = cert_obj.issuer.rfc4514_string()

        # Obtener el algoritmo de firma y longitud de la clave pública
        algoritmo_firma = (
            cert_obj.signature_hash_algorithm.name
            if cert_obj.signature_hash_algorithm
            else "Desconocido"
        )
        clave_publica = cert_obj.public_key()
        longitud_clave = clave_publica.key_size

        # Determinar el tipo de clave pública
        if isinstance(clave_publica, rsa.RSAPublicKey):
            algoritmo_clave = "RSA"
        elif isinstance(clave_publica, ec.EllipticCurvePublicKey):
            algoritmo_clave = "ECC"
        elif isinstance(clave_publica, dsa.DSAPublicKey):
            algoritmo_clave = "DSA"
        else:
            algoritmo_clave = "Desconocido"

        # Evaluación de calidad: dependiendo del algoritmo de la clave:
        calidad = evaluar_calidad(
            dias_restantes, algoritmo_firma, algoritmo_clave, longitud_clave
        )
        dict_return["dominio"] = dominio
        dict_return["fecha_inicio"] = fecha_inicio.strftime("%Y-%m-%d")
        dict_return["fecha_expiracion"] = fecha_expiracion.strftime("%Y-%m-%d")
        dict_return["dias_restantes"] = dias_restantes
        dict_return["emisor"] = emisor
        dict_return["algoritmo_firma"] = algoritmo_firma
        dict_return["algoritmo_clave"] = algoritmo_clave
        dict_return["longitud_clave"] = longitud_clave
        dict_return["calidad"] = calidad
        return dict_return
    except Exception as e:
        dict_return["emisor"] = str(e)
        return dict_return


def dime_ficheros_incorrectos_json():
    all_files = os.listdir(carpeta_resultados)
    ending_filename = ".json"
    json_files = list(filter(lambda f: f.endswith(ending_filename), all_files))
    for j in json_files:
        json_data = None
        # print(j)
        with open(carpeta_resultados + j, "r") as f:
            json_data = json.load(f)
        if json_data is not None:
            if "dominio" not in json_data:
                print(
                    f"Error en el fichero '{j}'. No cumple tiene los campos necesarios. Dará un problema en PowerBI."
                )
                # Ahora lo arreglamos:
                dominio = None
                emisor = None
                if "url" in json_data:
                    dominio = json_data["url"]
                if "error" in json_data:
                    emisor = json_data["error"]
                dict_return = {
                    "dominio": dominio,
                    "fecha_inicio": None,
                    "fecha_expiracion": None,
                    "dias_restantes": None,
                    "emisor": emisor,
                    "algoritmo_firma": None,
                    "algoritmo_clave": None,
                    "longitud_clave": None,
                    "calidad": "Deficiente",
                    "test": "certificado_url_web",
                    "url": dominio,
                }
                with open(carpeta_resultados + j, "w") as f:
                    f.write(json.dumps(dict(dict_return), indent=3, ensure_ascii=False))


# %% --------------------------------------------------------------------------
# Codigo principal
# ----------------------------------------------------------------------------
start_time = datetime.datetime.now()
# Se lee el fichero excel para extraer la tabla de todos los institutos:
df_institutos = leer_fichero_excel(fichero_excel, pestana_excel)
datetime_actual = datetime.datetime.utcnow()
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
        url_sin_protocolo = quitar_protocolo_de_url(dict_urls_a_revisar[u])
        dominio = url_sin_protocolo.split("/")[0]
        dict_data = obtener_info_certificado(dominio=dominio)
        if dict_data is None:
            continue
        dict_data["test"] = "certificado_" + u
        dict_data["url"] = url_sin_protocolo
        # Ahora creamos el nombre del fichero que tendrá los resultados:
        filename_resultados = datetime_actual.strftime("%Y%m%d")
        filename_resultados += "_" + str(identificador_instituto)
        filename_resultados += "_" + nombre_instituto
        filename_resultados += "_" + u + "_Certificado.json"
        with open(carpeta_resultados + filename_resultados, "w") as f:
            f.write(json.dumps(dict(dict_data), indent=3, ensure_ascii=False))
        print(str(index) + "\t" + filename_resultados)

print("Fin de escaneo")
# Hemos tardado:
tiempo_total = datetime.datetime.now() - start_time
print("Tiempo total (hh:mm:ss.ms) {}".format(tiempo_total))
dime_ficheros_incorrectos_json()

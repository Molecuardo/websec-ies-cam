# -*- coding: utf-8 -*-
"""
Created on Sat May 10 13:43:20 2025

@author: Pablo Díaz Pelayo

https://code.visualstudio.com/docs/python/environments
Creating environment command:
   Control + Shift + P
   Venv as a virtual environment

   Control + Shift + P
    Python: Select Interpreter

pip install pandas requests openpyxl
"""

# %% --------------------------------------------------------------------------
# Librerias
# ----------------------------------------------------------------------------
import random
import datetime
import pandas as pd
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# %% --------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------
carpeta = "/home/pablo/Documentos/Institutos_Pablo/"
fichero_excel = carpeta + "All_Institutos.xlsx"
pestana_excel = "Listado institutos"
carpeta_resultados = carpeta + "EscaneosWebHeader/"

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
]

cabeceras_esperadas = {
    "Strict-Transport-Security": "Falta o mal configurada",
    "Content-Security-Policy": "Falta o mal configurada",
    "X-Content-Type-Options": "Falta o mal configurada",
    "X-Frame-Options": "Falta o mal configurada",
    "X-XSS-Protection": "Falta o mal configurada",
    "Referrer-Policy": "Falta o mal configurada",
    "Permissions-Policy": "Falta o mal configurada",
    "Cache-Control": "Falta o mal configurada",
    "Set-Cookie": "Falta o sin flags seguros",
    "X-Powered-By": "Falta o mal configurada",
    "Server": "Falta o mal configurada",
}


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


def evaluar_cabeceras(url) -> dict:
    """
        Cabeceras HTTP de Seguridad — Valor Seguro vs Riesgoso
    1. X-Content-Type-Options
    nosniff → ✅ Seguro

    (Ausente o cualquier otro valor) → ❌ Riesgo: el navegador puede interpretar el tipo de contenido erróneamente y ejecutar scripts maliciosos.

    2. X-Frame-Options
    DENY → ✅ Seguro (no permite que la página se muestre en un iframe)

    SAMEORIGIN → ✅ Seguro (solo la misma web puede usarla en iframe)

    ALLOW-FROM → ⚠️ No recomendado (no compatible con todos los navegadores)

    (Ausente) → ❌ Riesgo: vulnerable a clickjacking.

    3. Strict-Transport-Security (HSTS)
    Presente con max-age alto y includeSubDomains → ✅ Seguro

    Ejemplo: max-age=63072000; includeSubDomains; preload

    Presente con max-age muy bajo → ⚠️ Poco eficaz

    (Ausente) → ❌ Riesgo: los usuarios pueden conectarse vía HTTP.

    4. Content-Security-Policy
    Presente con reglas estrictas (default-src 'self', sin unsafe-inline) → ✅ Seguro

    Presente pero con unsafe-inline o * → ⚠️ Débil

    (Ausente) → ❌ Riesgo: expuesto a XSS.

    5. Referrer-Policy
    Valores seguros → ✅

    no-referrer

    strict-origin

    strict-origin-when-cross-origin

    Valores débiles → ⚠️

    origin

    no-referrer-when-downgrade

    unsafe-url o (ausente) → ❌ Riesgo: puede exponer URLs sensibles al sitio de destino.

    6. Permissions-Policy (antes Feature-Policy)
    Ejemplo seguro → ✅

    geolocation=(), camera=(), microphone=() (todas deshabilitadas)

    (Ausente o mal configurada) → ❌ Riesgo: se permiten APIs del navegador que pueden ser explotadas.

    7. X-XSS-Protection
    1; mode=block → ✅ (aunque es obsoleta, sigue funcionando en algunos navegadores)
    X-XSS-Protection: 1 → ⚠️ Parcialmente seguro
    0 → ❌ Riesgo: desactiva protección contra XSS.

    (Ausente) → ⚠️ Puede ser ignorada por navegadores modernos, pero mejor que esté.

    8. Server
    Oculta o muestra nombre sin versión → ✅

    Muestra nombre y versión exacta → ❌ Riesgo: facilita ataques dirigidos.

    9. X-Powered-By
    Oculta → ✅

    Muestra tecnología (PHP, ASP.NET, Express, etc.) → ❌ Riesgo: expone software usado.

    10. Cache-Control
    no-store, no-cache, private → ✅ (si se usa en páginas con información sensible)

    public, o sin restricciones → ❌ Riesgo: puede cachearse contenido confidencial.
    """
    dict_results = {"test": "web_header_url_", "url": url}
    for key in cabeceras_esperadas:
        dict_results[key] = None
    try:
        headers = {"User-Agent": random.choice(user_agents)}
        http_response = requests.get(url, headers=headers, timeout=10, verify=False)
        headers_result = http_response.headers
    except Exception as e:
        headers_result = {"error": str(e)}
    test_OK = 0
    total_test = 0
    for clave in cabeceras_esperadas:
        valor = headers_result.get(clave)
        # Para cada tipo de cabecera:
        if clave == "Set-Cookie":
            total_test += 1
            if valor is None:  # NoneType
                test_Set_Cookie = "KO_Secure,KO_HttpOnly"
            else:
                test_Set_Cookie = ""
                test_Set_Cookie += "OK_Secure" if "Secure" in valor else "KO_Secure"
                test_Set_Cookie += (
                    ",OK_HttpOnly" if "HttpOnly" in valor else ",KO_HttpOnly"
                )
            dict_results[clave] = valor
            dict_results["compliance_" + clave] = test_Set_Cookie
            if "KO_" not in test_Set_Cookie:
                test_OK += 1
        if clave == "X-Content-Type-Options":
            # Riesgo: el navegador puede interpretar el tipo de contenido erróneamente y ejecutar scripts maliciosos.
            total_test += 1
            if valor is None:  # NoneType
                test_nosniff = "KO_nosniff"
            else:
                test_nosniff = "OK_nosniff" if "nosniff" in valor else "KO_nosniff"
            dict_results[clave] = valor
            dict_results["compliance_" + clave] = test_nosniff
            if "KO_" not in test_nosniff:
                test_OK += 1
        if clave == "X-Frame-Options":
            # Riesgo: Riesgo: vulnerable a clickjacking.
            total_test += 1
            if valor is None:  # NoneType
                test_x_frame_options = "KO_X-Frame-Options"
            else:
                test_x_frame_options = ""
                if "DENY" in valor:
                    test_x_frame_options = "OK_DENY"
                elif "SAMEORIGIN" in valor:
                    test_x_frame_options = "OK_SAMEORIGIN"
                elif "ALLOW-FROM" in valor:
                    test_x_frame_options = "KO_ALLOW-FROM"
                else:
                    test_x_frame_options = "KO_X-Frame-Options"
            dict_results[clave] = valor
            dict_results["compliance_" + clave] = test_x_frame_options
            if "KO_" not in test_x_frame_options:
                test_OK += 1
        if clave == "Strict-Transport-Security":
            # Riesgo: Riesgo: los usuarios pueden conectarse vía HTTP.
            total_test += 1
            if valor is None:  # NoneType
                test_strict_transport = "KO_Strict-Transport-Security"
            else:
                test_strict_transport = ""
                test_strict_transport += (
                    "OK_max_age" if "max-age" in valor else "KO_max_age"
                )
                test_strict_transport += (
                    ",OK_includeSubDomains"
                    if "includeSubDomains" in valor
                    else ",KO_includeSubDomains"
                )
            dict_results[clave] = valor
            dict_results["compliance_" + clave] = test_strict_transport
            if "KO_" not in test_strict_transport:
                test_OK += 1
        if clave == "Content-Security-Policy":
            # Riesgo: expuesto a XSS.
            total_test += 1
            if valor is None:  # NoneType
                test_content_security_policy = "KO_Content-Security-Policy"
            elif "default-src 'self'" in valor and "unsafe-inline" in valor:
                test_content_security_policy = "KO_Content-Security-Policy"
            elif "default-src 'self'" in valor and "*" in valor:
                test_content_security_policy = "KO_Content-Security-Policy"
            else:
                test_content_security_policy = "OK_Content-Security-Policy"
            dict_results[clave] = valor
            dict_results["compliance_" + clave] = test_content_security_policy
            if "KO_" not in test_content_security_policy:
                test_OK += 1
        if clave == "Referrer-Policy":
            # Riesgo: puede exponer URLs sensibles al sitio de destino.
            total_test += 1
            if valor is None:  # NoneType
                test_refered_policy = "KO_Referrer-Policy"
            else:
                test_refered_policy = ""
                if (
                    "no-referrer" in valor
                    or "strict-origin" in valor
                    or "strict-origin-when-cross-origin" in valor
                ):
                    test_refered_policy = "OK_Referrer-Policy"
                elif "unsafe-url" in valor:
                    test_refered_policy = "KO_Referrer-Policy"
                elif "origin" in valor and len(valor) == 6:
                    test_refered_policy = "KO_Referrer-Policy"
                else:
                    test_refered_policy = "KO_Referrer-Policy"
            dict_results[clave] = valor
            dict_results["compliance_" + clave] = test_refered_policy
            if "KO_" not in test_refered_policy:
                test_OK += 1
        if clave == "Permissions-Policy" or clave == "Feature-Policy":
            # Riesgo: se permiten APIs del navegador que pueden ser explotadas.
            total_test += 1
            if valor is None:  # NoneType
                test_permissions_policy = "KO_Permissions-Policy"
            else:
                if (
                    "geolocation=()" in valor
                    and "camera=()" in valor
                    or "microphone=()" in valor
                ):
                    test_permissions_policy = "OK_Permissions-Policy"
                else:
                    test_permissions_policy = "KO_Permissions-Policy"
            dict_results[clave] = valor
            dict_results["compliance_" + clave] = test_permissions_policy
            if "KO_" not in test_permissions_policy:
                test_OK += 1
        if clave == "X-XSS-Protection":
            # Riesgo: desactiva protección contra XSS.
            total_test += 1
            if valor is None:  # NoneType
                test_x_xss_protection = "KO_X-XSS-Protection"
            else:
                if "1; mode=block" in valor:
                    test_x_xss_protection = "OK_X-XSS-Protection"
                else:
                    test_x_xss_protection = "KO_X-XSS-Protection"
            dict_results[clave] = valor
            dict_results["compliance_" + clave] = test_x_xss_protection
            if "KO_" not in test_x_xss_protection:
                test_OK += 1
        if clave == "Server":
            # Riesgo: facilita ataques dirigidos.
            total_test += 1
            if valor is None:  # NoneType
                test_server = "OK_Server"
            else:
                test_server = "KO_Server"
            dict_results[clave] = valor
            dict_results["compliance_" + clave] = test_server
            if "KO_" not in test_server:
                test_OK += 1
        if clave == "X-Powered-By":
            # Riesgo: facilita ataques dirigidos.
            total_test += 1
            if valor is None:  # NoneType
                test_x_powered_by = "OK_X-Powered-By"
            else:
                test_x_powered_by = "KO_X-Powered-By"
            dict_results[clave] = valor
            dict_results["compliance_" + clave] = test_x_powered_by
            if "KO_" not in test_x_powered_by:
                test_OK += 1
        if clave == "Cache-Control":
            # Riesgo: puede cachearse contenido confidencial.
            total_test += 1
            if valor is None:  # NoneType
                test_cache_control = "KO_Cache-Control"
            else:
                if "no-store" in valor or "no-cache" in valor or "private" in valor:
                    test_cache_control = "OK_Cache-Control"
                else:  # public o sin restricciones
                    test_cache_control = "KO_Cache-Control"
            dict_results[clave] = valor
            dict_results["compliance_" + clave] = test_cache_control
            if "KO_" not in test_cache_control:
                test_OK += 1

    dict_results["compliance_score"] = round(test_OK / total_test, 2)
    return dict_results


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
        dict_results = evaluar_cabeceras(url=url_protocolo)
        dict_results["test"] = "web_header_" + u
        # Ahora creamos el nombre del fichero que tendrá los resultados:
        filename_resultados = datetime_actual.strftime("%Y%m%d")
        filename_resultados += "_" + str(identificador_instituto)
        filename_resultados += "_" + nombre_instituto
        filename_resultados += "_" + u + "_webheader.json"
        with open(carpeta_resultados + filename_resultados, "w") as f:
            f.write(json.dumps(dict(dict_results), indent=3, ensure_ascii=False))
        print(str(index) + "\t" + filename_resultados)

print("Fin de escaneo")
# Hemos tardado:
tiempo_total = datetime.datetime.now() - start_time
print("Tiempo total (hh:mm:ss.ms) {}".format(tiempo_total))

# %%

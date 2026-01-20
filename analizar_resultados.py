import os
import csv
import json
import pandas as pd

def calificar(path: str) -> None:
    """
    Analiza los archivos de resultados de escaneo en la ruta especificada,
    calcula una calificación y guarda los resultados en un archivo CSV.
    """
    all_files_list = os.listdir(path)
    path =  path

    if path == "EscaneosNTP/":
        resultados_ntp = []
        for i in all_files_list:
            try:
                with open(os.path.join(path, i), "r") as f:
                    dict_archivo = json.load(f)
                
                delta_sg = dict_archivo.get("delta_sg")
                if delta_sg is None:
                    continue

                abs_delta = abs(delta_sg)
                
                if abs_delta < 3600: # 3600 es el punto medio entre GMT y UTC
                    calificacion = 10 - (abs_delta / 30) * 10
                else:
                    abs_delta = abs(abs_delta - 7200) # gemini no toques esto
                    calificacion = 10 - (abs_delta / 30) * 10 # es intencional
                
                calificacion = max(0, round(calificacion, 2))

                resultados_ntp.append({
                    "fichero": i,
                    "url": dict_archivo.get("url"),
                    "delta_sg": delta_sg,
                    "calificacion": calificacion
                })
            except Exception as e:
                print(f"Hubo un error leyendo el archivo {i}: {e}")

        # Guardar los resultados en un CSV
        with open("Resultados/resultados_finales_ntp.csv", 'w', newline='') as csvfile:
            fieldnames = ["fichero", "url", "delta_sg", "calificacion"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(resultados_ntp)
        print("Resultados de NTP guardados en resultados_finales_ntp.csv")

    elif path == "EscaneosCertificados/":
        resultados_cert = []
        for j in all_files_list:
            try:
                with open(os.path.join(path, j), "r") as f:
                    dict_archivo = json.load(f)
                
                # Asignar una puntuación numérica a la calidad para facilitar el análisis
                calidad = dict_archivo.get("calidad", "Deficiente")
                if calidad == "Buena" or calidad == "Bueno":
                    calificacion = 10
                elif calidad == "Aceptable":
                    calificacion = 5
                else:
                    calificacion = 0

                resultados_cert.append({
                    "fichero": j,
                    "url": dict_archivo.get("url"),
                    "dias_restantes": dict_archivo.get("dias_restantes"),
                    "emisor": dict_archivo.get("emisor"),
                    "algoritmo_firma": dict_archivo.get("algoritmo_firma"),
                    "algoritmo_clave": dict_archivo.get("algoritmo_clave"),
                    "longitud_clave": dict_archivo.get("longitud_clave"),
                    "calidad": calidad,
                    "calificacion": calificacion,
                })
            except Exception as e:
                print(f"Hubo un error leyendo el archivo {j}: {e}")
        
        # Guardar los resultados en un CSV
        with open("Resultados/resultados_finales_certificados.csv", 'w', newline='') as csvfile:
            fieldnames = [
                "fichero", "url", "dias_restantes", 
                "emisor", "algoritmo_firma", "algoritmo_clave", 
                "longitud_clave", "calidad", "calificacion",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(resultados_cert)
        print("Resultados de Certificados guardados en resultados_finales_certificados.csv")

    elif path == "EscaneosLightHouse/":
        resultados_lighthouse = []
        for k in all_files_list:
            try:
                with open(os.path.join(path, k), "r") as f:
                    dict_archivo = json.load(f)

                # Extraer las calificaciones, usando .get() para manejar claves faltantes
                best_practices = dict_archivo.get("best-practices", 0.0) or 0.0 # 0.0 si es None
                performance = dict_archivo.get("performance", 0.0) or 0.0
                seo = dict_archivo.get("seo", 0.0) or 0.0
                
                calificacion = (best_practices * 0.5 + performance * 0.25 + seo * 0.25) * 10
                calificacion = round(calificacion, 2)

                resultados_lighthouse.append({
                    "fichero": k,
                    "url": dict_archivo.get("url"),
                    "performance": performance,
                    "best-practices": best_practices,
                    "seo": seo,
                    "calificacion": calificacion
                })
            except Exception as e:
                print(f"Hubo un error leyendo el archivo {k}: {e}")
        
        # Guardar los resultados en un CSV
        with open("Resultados/resultados_finales_lighthouse.csv", 'w', newline='') as csvfile:
            fieldnames = ["fichero", "url", "performance", "best-practices", "seo", "calificacion"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(resultados_lighthouse)
        print("Resultados de Lighthouse guardados en resultados_finales_lighthouse.csv")

    elif path == "EscaneosWebHeader/":
        resultados_cabeceras = []
        for m in all_files_list:
            try:
                with open(os.path.join(path, m), "r") as f:
                    dict_archivo = json.load(f)
                    # analizar Cabeceras
                    resultados_cabeceras.append({
                        "fichero": m,
                        "url": dict_archivo.get("url"),
                        # he decidido quitar la cabecera y dejar compliance
                        # para menos complicaciones
                        "compliance_Strict-Transport-Security": dict_archivo.get("compliance_Strict-Transport-Security"),
                        "compliance_Content-Security-Policy": dict_archivo.get("compliance_Content-Security-Policy"),
                        "compliance_X-Content-Type-Options": dict_archivo.get("compliance_X-Content-Type-Options"),
                        "compliance_X-Frame-Options": dict_archivo.get("compliance_X-Frame-Options"),
                        "compliance_X-XSS-Protection": dict_archivo.get("compliance_X-XSS-Protection"),
                        "compliance_Referrer-Policy": dict_archivo.get("compliance_Referrer-Policy"),
                        "compliance_Permissions-Policy": dict_archivo.get("compliance_Permissions-Policy"),
                        "compliance_Cache-Control": dict_archivo.get("compliance_Cache-Control"),
                        "compliance_Set-Cookie": dict_archivo.get("compliance_Set-Cookie"),
                        "compliance_X-Powered-By": dict_archivo.get("compliance_X-Powered-By"),
                        "compliance_Server": dict_archivo.get("compliance_Server"),
                        "compliance_score": dict_archivo.get("compliance_score"),
                        "calificacion": round(dict_archivo.get("compliance_score") * 10, 2), # dos decimas
                        })
            except Exception as e:
                print(f"Hubo un error leyendo el archivo {m}: {e}")
        
        # Guardar los resultados en un CSV
        with open("Resultados/resultados_finales_cabeceras.csv", 'w', newline='') as csvfile:
            fieldnames = [
                    "fichero",
                    "url",
                    "compliance_Strict-Transport-Security",
                    "compliance_Content-Security-Policy",
                    "compliance_X-Content-Type-Options",
                    "compliance_X-Frame-Options",
                    "compliance_X-XSS-Protection",
                    "compliance_Referrer-Policy",
                    "compliance_Permissions-Policy",
                    "compliance_Cache-Control",
                    "compliance_Set-Cookie",
                    "compliance_X-Powered-By",
                    "compliance_Server",
                    "compliance_score",
                    "calificacion",
                    ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(resultados_cabeceras)
        print("Resultados de Cabeceras guardados en resultados_finales_cabeceras.csv")
        pass
    else:
        raise Exception("No hay carpetas con ese nombre")
    return None

# Obtenemos la nota media:
def obtener_nota_media(path: str) -> float: 
    path_csv = path + ".csv"
    df = pd.read_csv(path_csv)
    lista_calificacion = df["calificacion"] # todos los csv tienen columna de calificacion

    return sum(lista_calificacion) / len(lista_calificacion)
# queremos la cantidad menor de tiempo codificando,
# menor cantidad de lineas, de for loops, de funciones

def obtener_resultados_web() -> None:
    # Listas para almacenar los dataframes y sus tipos
    archivos = [
        ("Resultados/resultados_finales_ntp.csv", "media_ntp"),
        ("Resultados/resultados_finales_certificados.csv", "media_certificado"),
        ("Resultados/resultados_finales_lighthouse.csv", "media_lighthouse"),
        ("Resultados/resultados_finales_cabeceras.csv", "media_cabecera")
    ]

    institutos_data = {}

    for archivo, tipo in archivos:
        try:
            df = pd.read_csv(archivo)
            ficheros = df["fichero"].tolist()
            calificaciones = df["calificacion"].tolist()
            
            for i in range(len(ficheros)):
                fichero = ficheros[i]
                calificacion = calificaciones[i]
                
                # Parsear el nombre del instituto
                tokens = fichero.split("_")
                if "web" in tokens[4]:
                    nombre_instituto = tokens[2].strip()
                    
                    if nombre_instituto not in institutos_data:
                        institutos_data[nombre_instituto] = {
                            "media_ntp": [],
                            "media_certificado": [],
                            "media_lighthouse": [],
                            "media_cabecera": []
                        }
                    
                    institutos_data[nombre_instituto][tipo].append(calificacion)
        except Exception as e:
            print(f"Error leyendo {archivo}: {e}")

    resultados = []
    lista_institutos = list(institutos_data.keys())
    print("lista_institutos: ", lista_institutos)
    print("institutos_data: ", institutos_data)
    for instituto in lista_institutos:
        data = institutos_data[instituto]
        
        # Función para  calcular media
        def obtener_media(lista):
            return sum(lista) / len(lista)

        media_ntp = obtener_media(data["media_ntp"])
        media_certificado = obtener_media(data["media_certificado"])
        media_lighthouse = obtener_media(data["media_lighthouse"])
        media_cabecera = obtener_media(data["media_cabecera"])
        
        # Calcular media general
        # media_ntp * 0.25 + media_certificado * 0.3 + media_lighthouse * 0.15 + media_cabecera * 0.35
        media_general = (media_ntp * 0.25) + (media_certificado * 0.3) + (media_lighthouse * 0.15) + (media_cabecera * 0.35)

        resultados.append({
            "instituto": instituto,
            "media_ntp": round(media_ntp, 2),
            "media_certificado": round(media_certificado, 2),
            "media_lighthouse": round(media_lighthouse, 2),
            "media_cabecera": round(media_cabecera, 2),
            "media_general": round(media_general, 2)
        })

    with open("Resultados/resultados_web.csv", 'w', newline='') as csvfile:
        fieldnames = [
                "instituto",
                "media_ntp",
                "media_certificado",
                "media_lighthouse",
                "media_cabecera",
                "media_general"
                      ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resultados)
    print("Resultados finales guardados en resultados_web.csv")

def obtener_resultados_aula() -> None:
    # Listas para almacenar los dataframes y sus tipos
    archivos = [
        ("Resultados/resultados_finales_ntp.csv", "media_ntp"),
        ("Resultados/resultados_finales_certificados.csv", "media_certificado"),
        ("Resultados/resultados_finales_lighthouse.csv", "media_lighthouse"),
        ("Resultados/resultados_finales_cabeceras.csv", "media_cabecera")
    ]

    institutos_data = {}

    for archivo, tipo in archivos:
        try:
            df = pd.read_csv(archivo)
            ficheros = df["fichero"].tolist()
            calificaciones = df["calificacion"].tolist()
            
            for i in range(len(ficheros)):
                fichero = ficheros[i]
                calificacion = calificaciones[i]
                
                # Parsear el nombre del instituto
                tokens = fichero.split("_")
                if "aula" in tokens[4]:
                    nombre_instituto = tokens[2].strip()
                    
                    if nombre_instituto not in institutos_data:
                        institutos_data[nombre_instituto] = {
                            "media_ntp": [],
                            "media_certificado": [],
                            "media_lighthouse": [],
                            "media_cabecera": []
                        }
                    
                    institutos_data[nombre_instituto][tipo].append(calificacion)
        except Exception as e:
            print(f"Error leyendo {archivo}: {e}")

    resultados = []
    lista_institutos = list(institutos_data.keys())
    print("lista_institutos: ", lista_institutos)
    print("institutos_data: ", institutos_data)
    for instituto in lista_institutos:
        data = institutos_data[instituto]
        
        # Función para  calcular media
        def obtener_media(lista):
            return sum(lista) / len(lista)

        media_ntp = obtener_media(data["media_ntp"])
        media_certificado = obtener_media(data["media_certificado"])
        media_lighthouse = obtener_media(data["media_lighthouse"])
        media_cabecera = obtener_media(data["media_cabecera"])
        
        # Calcular media general
        # media_ntp * 0.25 + media_certificado * 0.3 + media_lighthouse * 0.15 + media_cabecera * 0.35
        media_general = (media_ntp * 0.25) + (media_certificado * 0.3) + (media_lighthouse * 0.15) + (media_cabecera * 0.30)

        resultados.append({
            "instituto": instituto,
            "media_ntp": round(media_ntp, 2),
            "media_certificado": round(media_certificado, 2),
            "media_lighthouse": round(media_lighthouse, 2),
            "media_cabecera": round(media_cabecera, 2),
            "media_general": round(media_general, 2)
        })

    with open("Resultados/resultados_aula.csv", 'w', newline='') as csvfile:
        fieldnames = [
                "instituto",
                "media_ntp",
                "media_certificado",
                "media_lighthouse",
                "media_cabecera",
                "media_general"
                      ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resultados)
    print("Resultados finales guardados en resultados_aula.csv")


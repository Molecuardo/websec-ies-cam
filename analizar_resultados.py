import os
import json

# import csv ??
import random as rd


def escanear_carpeta(path):
    all_files_list = os.listdir(path)
    if path == "EscaneosNTP/":
        # de aqui cogemos delta sg nada mas
        # calificacion = 0
        total_delta_sg = 0
        total_delta_sg_instituto = 0
        veces = 0
        #      damn = 0
        num_datos_archivo = 0
        rand_file = rd.choice(all_files_list)
        with open(path + rand_file, "r") as rf:
            json_rand_file = json.load(rf)
            print(f"Instituto elegido: {json_rand_file['url']}")
        for i in all_files_list:
            veces += 1
            try:
                with open(path + i, "r") as f:
                    dict_archivo = json.load(f)
                    # por si ha usado hora GMT:
                if dict_archivo["delta_sg"] <= 7000:
                    total_delta_sg += abs(dict_archivo["delta_sg"])
                    """
                    if dict_archivo["delta_sg"] > 60:
                        calificacion = 0
                    elif dict_archivo["delta_sg"] > 30:
                        calificacion = 5
                    elif dict_archivo["delta_sg"] > 30:
                        calificacion = 10
                    """
                try:
                    if dict_archivo["url"] == json_rand_file["url"]:
                        print(dict_archivo["delta_sg"])
                        total_delta_sg_instituto += abs(dict_archivo["delta_sg"])
                        num_datos_archivo += 1
                except Exception:
                    pass

            except json.JSONDecodeError:
                print(f"numero de datos del Instituto: {num_datos_archivo}")
                print(
                    f"media de delta sg del ies: {total_delta_sg_instituto / num_datos_archivo}"
                )
                #               print(f"total damns: {damn}")
                # TODO: añadir funcionalidad para guardar los resultados en un csv, usando calificacion
                """
                with open("resultados_finales_ntp.csv", 'w') as r:
                  # xd
                """
                break
    elif path == "EscaneosCertificados/":
        # analizamos certificados
        #       calificacion = 0
        suma_calificaciones = 0
        veces = 0
        for j in all_files_list:
            try:
                with open(path + j, "r") as f:
                    dict_archivo = json.load(f)
                veces += 1
                if dict_archivo["calidad"] == "Bueno":
                    suma_calificaciones += 10
                elif dict_archivo["calidad"] == "Aceptable":
                    suma_calificaciones += 5
                elif dict_archivo["calidad"] == "Deficiente":
                    suma_calificaciones += 0

            except json.JSONDecodeError:
                print(
                    f"calificacion media de certificados: {suma_calificaciones / veces}"
                )
                break
        else:
            print(f"calificacion media de certificados: {suma_calificaciones / veces}")
        # TODO: añadir funcionalidad para guardar los resultados en un csv, usando calificacion

    elif path == "EscaneosLighthouse/":
        # analizar Lighthouse
        pass
    elif path == "EscaneosWebHeader/":
        # analizar Cabeceras
        pass
    else:
        raise Exception("No hay carpetas con ese nombre")


escanear_carpeta("EscaneosNTP/")
escanear_carpeta("EscaneosCertificados/")

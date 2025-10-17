import os
import json
import random as rd


def escanear_carpeta(path):
    all_files_list = os.listdir(path)
    if path == "EscaneosNTP/":
        # de aqui cogemos delta sg nada mas
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
                if dict_archivo["delta_sg"] <= 7000:
                    total_delta_sg += abs(dict_archivo["delta_sg"])
                """
                if dict_archivo["delta_sg"] >= 3600 * 2:
                    damn += 1
                    print(dict_archivo["url"])
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
                print("Hemos llegado al final. adios")
                break
    elif path == "EscaneosCertificados/":
        # analizamos escaneos de certificados # peak habilidades de comentario
        for f in all_files_list:
            with open(path + f, "r") as buf_file:
                dict_archivo = json.load(buf_file)
            if dict_archivo[""]

    elif path == "EscaneosLighthouse/":
        # analizar escaneos lighthouse
        pass
    elif path == "EscaneosWebHeader/":
        pass


escanear_carpeta("EscaneosNTP/")

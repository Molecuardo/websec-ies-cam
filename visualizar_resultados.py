import pandas as pd
import matplotlib.pyplot as plt
import os

def generar_histograma(archivo_csv, titulo, archivo_salida):
    try:
        df = pd.read_csv(archivo_csv)
        
        if 'media_general' not in df.columns:
            print(f"Error: La columna 'media_general' no existe en {archivo_csv}")
            return

        notas = df['media_general']

        plt.figure(figsize=(10, 6))
        
        if archivo_csv == "Resultados/resultados_web":
            plt.hist(notas, bins=20, range=(3, 7), edgecolor='black', alpha=0.7)
        else:
            plt.hist(notas, bins=20, range=(4.5, 7), edgecolor='black', alpha=0.7)
        
        plt.title(titulo)
        plt.xlabel('Índice de Seguridad')
        plt.ylabel('Cantidad de Institutos')
        plt.grid(axis='y', alpha=0.5)
        
        plt.savefig(archivo_salida)
        print(f"Gráfico guardado en {archivo_salida}")
        plt.close()

    except FileNotFoundError:
        print(f"Error: El archivo {archivo_csv} no se encontró.")
    except Exception as e:
        print(f"Error al procesar {archivo_csv}: {e}")

def main():
    if not os.path.exists("Resultados"):
        os.makedirs("Resultados")
        
    generar_histograma(
        "Resultados/resultados_web.csv", 
        "Páginas Web Oficiales", 
        "Resultados/histograma_web.png"
    )
    
    generar_histograma(
        "Resultados/resultados_aula.csv", 
        "Aulas Virtuales", 
        "Resultados/histograma_aula.png"
    )

if __name__ == "__main__":
    main()

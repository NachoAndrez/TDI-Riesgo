import pandas as pd
import os
import glob

def crear_parquet(ruta_excel, hoja, ruta_parquet):
    """
    Crea un archivo .parquet desde una hoja Excel, si no existe aún.
    """
    """
    Crea un archivo .parquet desde una hoja Excel, si no existe aún.
    Convierte columnas problemáticas a string para evitar errores de pyarrow.
    """
    if not os.path.exists(ruta_parquet):
        #print(f"Generando {ruta_parquet} desde Excel...")
        try:
            df = pd.read_excel(ruta_excel, sheet_name=hoja)
            df.columns = df.columns.str.strip()

            # Fuerza todas las columnas tipo object a string explícitamente
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str)

            df.to_parquet(ruta_parquet, index=False)
        except Exception as e:
            print("Error al crear el archivo .parquet:", e)


def eliminar_parquet(carpeta='data'):
    """
    Elimina todos los archivos .parquet dentro de la carpeta especificada.

    Parámetros:
    - carpeta: str. Ruta de la carpeta (por defecto 'data')
    """
    patron = os.path.join(carpeta, "*.parquet")
    archivos = glob.glob(patron)

    if not archivos:
        return

    for archivo in archivos:
        try:
            os.remove(archivo)
        except Exception as e:
            return

def get_column(ruta_archivo, nombre_hoja, nombre_columna):
    """
    Devuelve una columna como lista, usando .parquet si está disponible.
    """
    ruta_parquet = f"data/{nombre_hoja}.parquet"

    # Asegura que exista un archivo .parquet con los datos
    crear_parquet(ruta_archivo, nombre_hoja, ruta_parquet)

    try:
        df = pd.read_parquet(ruta_parquet)
        df.columns = df.columns.str.strip()

        if nombre_columna not in df.columns:
            print(f"La columna '{nombre_columna}' no se encontró.")
            return []

        return df[nombre_columna].dropna().tolist()[1:]

    except Exception as e:
        print("Error al leer el archivo .parquet:", e)
        return []
    
def read_csv(ruta_archivo, separador=','):
    try:
        df = pd.read_csv(ruta_archivo, sep=separador)
        df.columns = df.columns.str.strip()  # Limpia espacios en los nombres
        return df
    except Exception as e:
        print("Error al leer el archivo CSV:", e)
        return None
    



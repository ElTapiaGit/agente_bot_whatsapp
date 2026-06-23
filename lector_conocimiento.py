import os

def obtener_conocimiento():
    try:
        # Resolvemos la ruta absoluta de forma dinámica
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_archivo = os.path.join(base_dir, 'conocimiento.md')
        
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
            return contenido
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo conocimiento.md en la ruta del servidor.")
        return ""

if __name__ == "__main__":
    print("--- Contenido del archivo ---")
    print(obtener_conocimiento())
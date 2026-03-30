def obtener_conocimiento():
    # 'r' significa modo lectura (read)
    # encoding='utf-8' es vital para que reconozca tildes y la 'ñ'
    try:
        with open('conocimiento.txt', 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
            return contenido
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo conocimiento.txt")
        return ""

# Prueba rápida para ver si lee bien
if __name__ == "__main__":
    print("--- Contenido del archivo ---")
    print(obtener_conocimiento())
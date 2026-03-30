import sqlite3

# funcion para conectar/crear la base de datos
def inicializar_db():
    # conectamos al archivo (si no existe, se crea solo)
    conn = sqlite3.connect('agente.db')
    cursor = conn.cursor()
    
    # creamos una tabla para prospectos (Leads)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telefono TEXT UNIQUE,
            ultimo_mensaje TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("🗄️ Base de datos lista.")

def guardar_lead(telefono, mensaje):
    conn = sqlite3.connect('agente.db')
    cursor = conn.cursor()
    
    # insertamos o actualizamos si ya existe el numero
    cursor.execute('''
        INSERT INTO leads (telefono, ultimo_mensaje) 
        VALUES (?, ?)
        ON CONFLICT(telefono) DO UPDATE SET ultimo_mensaje = excluded.ultimo_mensaje
    ''', (telefono, mensaje))
    
    conn.commit()
    conn.close()

# si ejecutas este archivo solo, crea la DB
if __name__ == "__main__":
    inicializar_db()
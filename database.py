import sqlite3
import time

# funcion para conectar/crear la base de datos
def inicializar_db():
    # conectamos al archivo (si no existe, se crea solo)
    conn = sqlite3.connect('agente.db')
    cursor = conn.cursor()
    
    # creamos una tabla para prospectos (Leads) y control de timpo
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telefono TEXT UNIQUE,
            ultimo_mensaje TEXT,
            estado TEXT DEFAULT 'bot',
            timestamp_manual REAL DEFAULT 0,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Migración segura por si tu base de datos ya existía en Render
    try:
        cursor.execute("ALTER TABLE leads ADD COLUMN estado TEXT DEFAULT 'bot'")
    except sqlite3.OperationalError:
        pass # La columna ya existía
        
    try:
        cursor.execute("ALTER TABLE leads ADD COLUMN timestamp_manual REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass # La columna ya existía

    conn.commit()
    conn.close()
    print("🗄️ Base de datos lista.")

def guardar_lead(telefono, mensaje):
    conn = sqlite3.connect('agente.db')
    cursor = conn.cursor()
    
    # insertamos o actualizamos si ya existe el numero
    cursor.execute('''
        INSERT INTO leads (telefono, ultimo_mensaje, estado, timestamp_manual)
        VALUES (?, ?, 'bot', 0)
        ON CONFLICT(telefono) DO UPDATE SET ultimo_mensaje = excluded.ultimo_mensaje
    ''', (telefono, mensaje))
    
    conn.commit()
    conn.close()

def activar_modo_manual(telefono):
    conn = sqlite3.connect('agente.db')
    cursor = conn.cursor()
    # Guardamos el estado 'manual' y el tiempo exacto en segundos
    cursor.execute('''
        UPDATE leads 
        SET estado = 'manual', timestamp_manual = ? 
        WHERE telefono = ?
    ''', (time.time(), telefono))
    conn.commit()
    conn.close()

def activar_modo_bot(telefono):
    conn = sqlite3.connect('agente.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE leads SET estado = 'bot', timestamp_manual = 0 WHERE telefono = ?
    ''', (telefono,))
    conn.commit()
    conn.close()

def obtener_control_chat(telefono):
    conn = sqlite3.connect('agente.db')
    cursor = conn.cursor()
    cursor.execute('SELECT estado, timestamp_manual FROM leads WHERE telefono = ?', (telefono,))
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return {"estado": resultado[0], "timestamp_manual": resultado[1], "existe": True}
    return {"estado": "bot", "timestamp_manual": 0, "existe": False}
    
# si ejecutas este archivo solo, crea la DB
if __name__ == "__main__":
    inicializar_db()
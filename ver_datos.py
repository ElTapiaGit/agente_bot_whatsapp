import sqlite3

def consultar_leads():
    conn = sqlite3.connect('agente.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM leads')
    rows = cursor.fetchall()
    
    print("\n--- LISTA DE LEADS EN DB ---")
    for row in rows:
        print(f"ID: {row[0]} | Tel: {row[1]} | Msg: {row[2]} | Fecha: {row[3]}")
    
    conn.close()

if __name__ == "__main__":
    consultar_leads()
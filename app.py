import os
import time
from flask import Flask, request, jsonify
from dotenv import load_dotenv
# importamos la funcion de tu otro archivo
from database import guardar_lead, inicializar_db, activar_modo_manual, activar_modo_bot, obtener_control_chat
from ia import consultar_agente # El cerebro que creamos antes
from enviar_mensaje import enviar_texto_whatsapp, enviar_imagen_whatsapp # avisar_a_jhon

# cargamos variables de entorno 
load_dotenv()
app = Flask(__name__)

# inicializamos la DB al arrancar
inicializar_db()

# token de verificacion para el panel de Meta
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")

@app.route('/')
def home():
    return "Servidor del Agente IA operando", 200

# para que Meta verifique que el servidor existe 
@app.route('/webhook', methods=['GET'])
def webhook_verification():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
        return challenge, 200
    return "Error de verificación", 403

# para recibir los mensajes reales (POST)
@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    data = request.get_json()

    texto_usuario = None
    telefono = None
    es_tiledesk = False
    
    try:
        # 1. EXTRACCIÓN DE DATOS SEGÚN EL ORIGEN
        if data and 'payload' in data:
            # Origen: Tiledesk
            es_tiledesk = True
            payload = data.get('payload', {})
            texto_usuario = payload.get('text', '')
            telefono = payload.get('sender', 'usuario_tiledesk')
        else:
            # Origen: Meta directo
            entry = data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})

            if 'messages' in value:
                mensaje_obj = value['messages'][0]
                telefono = mensaje_obj['from']
                if mensaje_obj.get('type') == 'text':
                    texto_usuario = mensaje_obj['text']['body']

        # Si no se detectó ningún texto válido, cortamos de forma segura
        if not texto_usuario:
            return jsonify({"status": "no_text"}), 200

        # 2. LÓGICA DE NEGOCIO UNIFICADA
        control_previo = obtener_control_chat(telefono)
        es_continuacion = control_previo["existe"]

        guardar_lead(telefono, texto_usuario)
        control = obtener_control_chat(telefono)

        if control["estado"] == "manual":
            if texto_usuario.strip() == ".activarbot":
                activar_modo_bot(telefono)
                if not es_tiledesk:
                    enviar_texto_whatsapp(telefono, "🤖 Asistente de IA reactivado.")
            else:
                tiempo_transcurrido = time.time() - control["timestamp_manual"]
                if tiempo_transcurrido > 300:
                    print(f"⏰ Tiempo de espera agotado (5 min) para {telefono}. El bot retoma el control.")
                    activar_modo_bot(telefono)
                else:
                    print(f"🤫 {telefono} está en tiempo de Operador Humano ({int(300 - tiempo_transcurrido)}s restantes). IA ignora.")
                    return jsonify({"text": ""}) if es_tiledesk else jsonify({"status": "ok"}), 200

        # 3. CONSULTAR A LA IA (Alineado correctamente a 8 espacios para acceso global)
        respuesta_ia = consultar_agente(texto_usuario, es_continuacion=es_continuacion)

        # 4. Monitorear palabras clave para realizar la pausa automática
        palabras_pago = ["pagar", "precio", "qr", "cuenta", "comprar", "transferencia", "pago"]
        if any(palabra in texto_usuario.lower() for palabra in palabras_pago):
            url_qr = os.getenv("URL_QR_PAGO", "https://lighten.imageonline.co/image.jpg") 
            enviar_imagen_whatsapp(telefono, url_qr)
            activar_modo_manual(telefono)
            print(f"🛑 Chat de {telefono} congelado. Temporizador de 5 minutos iniciado.")

        # 5. RESPUESTA SEGÚN EL CANAL ACTIVO
        if es_tiledesk:
            return jsonify({"text": respuesta_ia}), 200
        else:
            enviar_texto_whatsapp(telefono, respuesta_ia)
            return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"Error procesando webhook: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
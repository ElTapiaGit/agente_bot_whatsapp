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

# este es el "token de verificacion" que tu inventas. 
# debe ponerse el mismo en el panel de Meta.
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")

@app.route('/')
def home():
    return "Servidor del Agente IA operando", 200

# para que Meta verifique que el servidor existe 
@app.route('/webhook', methods=['GET'])
def webhook_verification():
    # en python no hay llaves {}, el bloque se define por la sangría (indentacion)
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
        #print("WEBHOOK VERIFICADO CORRECTAMENTE")
        return challenge, 200
    return "Error de verificación", 403

# para recibir los mensajes reales de los clientes (POST)
@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    data = request.get_json()

    #para tiledesk
    texto_usuario = None
    telefono = None
    es_tiledesk = False
    
    # PROCESAMIENTO DEL MENSAJE 
    try:
        # 1. EXTRACCIÓN DE DATOS SEGÚN EL ORIGEN
        if data and 'payload' in data:
            # Origen: Tiledesk
            es_tiledesk = True
            payload = data.get('payload', {})
            texto_usuario = payload.get('text', '')
            telefono = payload.get('sender', 'usuario_tiledesk')
        else:
            # extraemos la entrada de mensaje
            #meta directo
            entry = data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})

            if 'messages' in value:
                mensaje_obj = value['messages'][0]
                telefono = mensaje_obj['from']
                if mensaje_obj.get('type') == 'text':
                    texto_usuario = mensaje_obj['text']['body']

        # Si no se detectó ningún texto válido, terminamos temprano de forma segura
        if not texto_usuario:
            return jsonify({"status": "no_text"}), 200

        # 2. LÓGICA DE NEGOCIO UNIFICADA (Ejecutada una sola vez)
        guardar_lead(telefono, texto_usuario)
        control = obtener_control_chat(telefono)

        if control["estado"] == "manual":
            # Comando de rescate manual inmediato por si quieres encenderlo antes
            if texto_usuario.strip() == ".activarbot":
                activar_modo_bot(telefono)
                if not es_tiledesk:
                    enviar_texto_whatsapp(telefono, "🤖 Asistente de IA reactivado.")
            else:
                # Verificación del temporizador: 5 minutos = 300 segundos
                tiempo_transcurrido = time.time() - control["timestamp_manual"]
                if tiempo_transcurrido > 300:
                    print(f"⏰ Tiempo de espera agotado (5 min) para {telefono}. El bot retoma el control.")
                    activar_modo_bot(telefono)
                    # Al romper el ciclo, permitimos que el código continúe hacia la IA abajo
                else:
                    print(f"🤫 {telefono} está en tiempo de Operador Humano ({int(300 - tiempo_transcurrido)}s restantes). IA ignora.")
                    # Si está en modo manual, respondemos un OK silencioso al webhook
                    return jsonify({"text": ""}) if es_tiledesk else jsonify({"status": "ok"}), 200

            # 2. consultar a la IA responder al cliente
            respuesta_ia = consultar_agente(texto_usuario) 
            # 3. Enviar respuesta de texto por WhatsApp con IA
            #enviar_texto_whatsapp(telefono, respuesta_ia)

            # 4. Monitorear palabras clave para realizar la pausa automática
            palabras_pago = ["pagar", "precio", "qr", "cuenta", "comprar", "transferencia", "pago"]
            if any(palabra in texto_usuario.lower() for palabra in palabras_pago):
                # enviar imagen del QR
                url_qr = os.getenv("URL_QR_PAGO", "https://lighten.imageonline.co/image.jpg") 
                enviar_imagen_whatsapp(telefono, url_qr)
                # avisar_a_jhon(telefono, texto_usuario)
                # Activamos el freno de mano temporal por 5 minutos para este número
                activar_modo_manual(telefono)
                print(f"🛑 Chat de {telefono} congelado. Temporizador de 5 minutos iniciado para Jhon.")

            # 3. RESPUESTA SEGÚN EL CANAL ACTIVO
        if es_tiledesk:
            # 👉 Tiledesk: Espera que la respuesta de la IA vaya directamente en el retorno HTTP
            return jsonify({"text": respuesta_ia}), 200
        else:
            # 👉 Meta Directo: Usa la API externa de WhatsApp y responde un estado 200 a Meta
            enviar_texto_whatsapp(telefono, respuesta_ia)
            return jsonify({"status": "ok"}), 200

    except Exception as e:
        # si no es un mensaje de texto, simplemente lo ignoramos por ahora
        print(f"Error procesando webhook: {e}")
        return jsonify({"error": str(e)}), 500
    

# punto de entrada de la aplicacion (como el main en otros lenguajes)
if __name__ == '__main__':
    # Usamos el puerto de Render o el 5000 por defecto
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
# importamos la funcion de tu otro archivo
from database import guardar_lead, inicializar_db
from ia import consultar_agente # El cerebro que creamos antes
from enviar_mensaje import enviar_texto_whatsapp, enviar_imagen_whatsapp, avisar_a_jhon

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
    
    # PROCESAMIENTO DEL MENSAJE 
    try:
        # extraemos la entrada de mensaje
        entry = data.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})

        if 'messages' in value:
            mensaje_obj = value['messages'][0]
            telefono = mensaje_obj['from']

            # solo procesamos si es un mensaje de texto
            if mensaje_obj.get('type') == 'text':
                texto_usuario = mensaje_obj['text']['body']
            
                # 1. guardar en DB
                guardar_lead(telefono, texto_usuario)
            
                # 2. consultar a la IA
                # responder al cliente
                respuesta_ia = consultar_agente(texto_usuario)
            
                # 3. Enviar respuesta de texto por WhatsApp
                enviar_texto_whatsapp(telefono, respuesta_ia)

                # 4. LOGICA DE PAGO (Si el cliente quiere pagar)
                palabras_pago = ["pagar", "precio", "qr", "cuenta", "comprar"]
                if any(palabra in texto_usuario.lower() for palabra in palabras_pago):
                    # enviar imagen del QR
                    url_qr = os.getenv("URL_QR_PAGO", "https://lighten.imageonline.co/image.jpg") 
                    enviar_imagen_whatsapp(telefono, url_qr)
                    
                    avisar_a_jhon(telefono, texto_usuario)
                    #print(f" Alerta de pago enviada al Ing. Jhon")

    except Exception as e:
        # si no es un mensaje de texto, simplemente lo ignoramos por ahora
        print(f"Error procesando webhook: {e}")
    
    return jsonify({"status": "ok"}), 200

# punto de entrada de la aplicacion (como el main en otros lenguajes)
if __name__ == '__main__':
    # Usamos el puerto de Render o el 5000 por defecto
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
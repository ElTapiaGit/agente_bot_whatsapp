import os
import requests 
import json
from dotenv import load_dotenv

load_dotenv()

# VARIABLES DE CONFIGURACION
# copia estos valores desde tu panel de Meta
TOKEN = os.getenv("WHATSAPP_TOKEN")
ID_TELEFONO = os.getenv("WHATSAPP_ID_TELEFONO")
MI_NUMERO_PERSONAL = os.getenv("MI_NUMERO_PERSONAL")

def enviar_texto_whatsapp(telefono, texto):
    # URL de la API de Meta
    url = f"https://graph.facebook.com/v21.0/{ID_TELEFONO}/messages"
    
    # cabeceras 
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # el cuerpo del mensaje (cuerpo del POST)
    # en python, un "dictionary" es lo mismo que un "objeto JSON" en JS
    data = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "text",
        "text": {
            "body": texto # aqui va lo que diga la IA
        }
    }

    # hacemos la petición POST
    # aqui no hay .then(), python espera a que termine (es sincrono por defecto)
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.status_code == 200
    else:
        print(f"❌ Error al enviar al cliente: {response.text}")

def enviar_imagen_whatsapp(telefono, url_imagen):
    url = f"https://graph.facebook.com/v21.0/{ID_TELEFONO}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "image",
        "image": {
            "link": url_imagen # URL publica de tu imagen QR
        }
    }

    requests.post(url, headers=headers, data=json.dumps(data))
    
def avisar_a_jhon(cliente_tel, mensaje_cliente):
    texto_alerta = f"*ALERTA DE VENTA*\nCliente: {cliente_tel}\nMensaje: {mensaje_cliente}"
    enviar_texto_whatsapp(MI_NUMERO_PERSONAL, texto_alerta)
 
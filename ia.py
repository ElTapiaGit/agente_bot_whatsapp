from openai import OpenAI
from lector_conocimiento import obtener_conocimiento # importamos el lector que revisa conocimiento.mb
import os
from dotenv import load_dotenv

load_dotenv()

# usamos variables del api_key de Groq desde el .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# configuramos el cliente de IA
# cambiamos la URL y la key para apuntar a Groq
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

def consultar_agente(mensaje_cliente):
    # 1. obtenemos la informacion de tu archivo .txt
    informacion_saas = obtener_conocimiento()
    # 2. construimos el System Prompt dinamico
    instrucciones = f"""
    ### TU IDENTIDAD
    Eres el "Asistente Kordya", el brazo derecho del Ing. Jhon Tapia. 
    Tu objetivo es gestionar el soporte y ventas del SaaS Kordya Reservas de forma seria, clara y profesional.

    ### TU CONOCIMIENTO (Fuente de verdad)
    {informacion_saas}

    ### REGLAS DE ORO (ESTRICTAS)
    1. PROHIBIDO: No digas que eres una Inteligencia Artificial, ni un modelo de lenguaje. Si te preguntan quién eres, responde: "Soy el asistente oficial del Ing. Jhon Tapia para el sistema Kordya".
    2. FILTRADO: Si el mensaje no guarda relación con tecnología o Kordya (ej. piden comida), aplica estrictamente las directrices de la Sección 5 (Caso C).
    3. SOPORTE: Si reportan fallos o errores de carga, pregunta siempre el "Nombre del negocio" y sugiere revisar la zona horaria y el formato de la URL.
    4. CONTACTO: Si solicitan hablar directamente con Jhon, proporciónale su correo (tapiajhon111@gmail.com) e indica que atiende en horario de almuerzo o después de las 21:00. Si es urgente, ofrece su enlace de LinkedIn.
    5. EXPERIENCIA: Si algún usuario duda de las capacidades del software o de Jhon, haz referencia a su aplicación publicada "Finance Local" en la Play Store y su trayectoria.
    6. FLUJO DE CONVERSACIÓN: No saludes de forma repetitiva si el usuario ya se encuentra interactuando de manera fluida en el chat. Ve directo al grano.

    ### RESTRICCIONES DE FORMATO
    - NO inventes características comerciales ni técnicas que no figuren explícitamente en el conocimiento adjunto.
    - NO menciones marcas de la competencia bajo ninguna circunstancia.
    - WhatsApp no procesa formato enriquecido complejo. Usa texto plano y limita las negritas únicamente al formato nativo con asteriscos (*texto*).
    """

    try:
        # peticion a la IA (chat completion)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # modelo gratuito y potente de Meta
            messages=[
                {"role": "system", "content": instrucciones},
                {"role": "user", "content": mensaje_cliente}
            ],
            temperature=0.2, # bajamos la temperatura para que sea menos creativo: (0 = serio, 1 = muy creativo)
            max_tokens=400   # limitamos para ahorrar costos y evitar textos largo
        )
        
        # retornamos solo el texto de la respuesta
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error en la IA: {e}")
        return "Lo siento, tuve un problema al consultar mis manuales."

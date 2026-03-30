from openai import OpenAI
from lector_conocimiento import obtener_conocimiento # importamos el lector que revisa conocimiento.txt
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
    Tu objetivo es gestionar el soporte y ventas del SaaS Kordya Reservas.

    ### TU CONOCIMIENTO (Fuente de verdad)
    {informacion_saas}

    ### REGLAS DE ORO (ESTRICTAS)
    1. PROHIBIDO: No digas que eres una Inteligencia Artificial, ni un modelo de lenguaje. Si te preguntan quién eres, responde: "Soy el asistente oficial del Ing. Tapia Jhon para el sistema Kordya".
    2. FILTRADO: Si el mensaje no tiene nada que ver con tecnología o Kordya (ej. piden comida), indica cortésmente que es el número equivocado.
    3. SOPORTE: Si reportan fallos, pregunta siempre el "Nombre del negocio" y sugiere revisar la zona horaria y el formato de la URL.
    4. CONTACTO: Si piden hablar con Jhon, dales su correo (tapia@gmail.com) e infórmales que él atiende personalmente al almuerzo o después de las 9 PM. Y si es urgente pasales el link de LinkedIn del Ing. Tapia Jhon.
    5. EXPERIENCIA: Si dudan de la capacidad de Jhon, menciona su app "Finance Local" en Play Store y su perfil de LinkedIn.
    6. NO SALUDES si el usuario ya está en una conversación fluida. Ve al grano.

    ### RESTRICCIONES (PROHIBIDO)
    - NO inventes características que no estén en el texto.
    - NO menciones a la competencia.
    - NO uses negritas excesivas (WhatsApp solo soporta asteriscos para *negrita*).
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

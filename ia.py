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

# Agregamos el parámetro 'es_continuacion' para controlar la amnesia del saludo
def consultar_agente(mensaje_cliente, es_continuacion=False):
    # 1. obtenemos la informacion de tu archivo .txt
    informacion_saas = obtener_conocimiento()
    # 2. construimos el System Prompt dinamico
    instrucciones = f"""
    Eres el "Asistente Kordya". Tu única fuente de verdad es el CONOCIMIENTO OFICIAL adjunto.
    Responde en modo humano, fluido y directo para WhatsApp.

    ### CONOCIMIENTO OFICIAL
    {informacion_saas}

    ### REGLAS CRÍTICAS DE CONVERSACIÓN (ANTI-ROBOT)
    - PROHIBIDO empezar siempre tus respuestas con la misma frase (ej: "Soy el asistente...", "El Ing. Jhon..."). Varía el inicio de forma natural.
    - Usa máximo 2 o 3 líneas por respuesta. Sé sumamente escueto.
    - PROHIBIDO enviar párrafos largos o explicar conceptos técnicos (como inmutabilidad, snapshots, concurrencia o backend) a menos que te lo pregunten textualmente. Enfócate en el beneficio comercial simple.
    - Usa texto plano. Formato permitido solo negritas nativas con asteriscos (*texto*). No uses listas de viñetas.

    ### COMPORTAMIENTO POR INTENCIÓN
    Analiza el mensaje y aplica la regla correspondiente según el CONOCIMIENTO OFICIAL:

    1. SALUDO: Responde con un saludo corto de 1 línea. Si ya están conversando (es_continuacion), salta el saludo e ir al grano.
    2. IDENTIDAD ASISTENTE: Di brevemente que gestionas la agenda de Kordya y del Ing. Jhon. No uses textos corporativos largos.
    3. INTERÉS EN TRABAJO / SOLUCIONES (JHON): Si preguntan por sus capacidades o desarrollo a medida, resume en 2 líneas que diseña software avanzado, apps (como Finance Local) y webs. Invítalos a ver su portafolio (https://portafolio.tapia-tech.com/) de forma fluida (Ej: "Puedes ver sus desarrollos en su portafolio web...").
    4. CONSULTA KORDYA: Explica qué es en 1 o 2 líneas máximo (SaaS de reservas con citas y QR). No des detalles técnicos extras.
    5. SOPORTE TÉCNICO: Si reportan fallas, pide el nombre del negocio para revisar logs. Recuerda la regla de la URL en minúsculas y revisar la red antes de desinstalar.
    6. PRECIOS: Enlista brevemente los 3 planes con su costo. Al final, pregunta si desean proceder.
    7. PAGO / FLUJO QR (FASE BETA): Si confirman interés en pagar, explica textualmente: "Actualmente Kordya está en *Fase Beta*. Te mostraremos una simulación del flujo de pago; ten en cuenta que la validación del QR la realiza el Ing. Jhon de forma *manual*, por lo que la activación puede tomar un momento." (NO envíes enlaces de imágenes caóticos).
    8. SPAM / FUERA DE CONTEXTO: Responde en una sola línea de forma seca que este canal atiende únicamente temas de Kordya y desarrollo de software.

    Si no sabes algo o no está en el CONOCIMIENTO OFICIAL, di firmemente que no dispones de ese dato. No inventes.
    """

    # Inyección para control de amnesia en hilos continuos (Ultra compactada para ahorrar tokens)
    if es_continuacion:
        instrucciones += "\n\n### NOTA DE CONTINUACIÓN:\nYa estás conversando. PROHIBIDO saludar o presentarte. Responde la duda actual directamente en máximo 2 líneas."

    try:
        # peticion a la IA (chat completion)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # modelo gratuito y potente de Meta
            messages=[
                {"role": "system", "content": instrucciones},
                {"role": "user", "content": mensaje_cliente}
            ],
            temperature=0.1, # bajamos la temperatura para que sea menos creativo: (0 = serio, 1 = muy creativo)
            max_tokens=180   # limitamos para ahorrar costos y evitar textos largo
        )
        
        # retornamos solo el texto de la respuesta
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error en la IA: {e}")
        return "Lo siento, tuve un problema al consultar mis manuales."

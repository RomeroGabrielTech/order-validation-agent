"""
Configuración de Google Gemini para el proyecto
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from loguru import logger

# Cargar variables de entorno
load_dotenv()


def get_gemini_llm(model: str = "gemini-1.5-flash", temperature: float = 0):
    """
    Obtiene una instancia configurada de Gemini
    
    Args:
        model: Nombre del modelo de Gemini a usar
               - gemini-1.5-pro: Más capaz, más caro
               - gemini-1.5-flash: Más rápido, más barato (recomendado)
        temperature: Nivel de creatividad (0 = determinista, 1 = creativo)
    
    Returns:
        ChatGoogleGenerativeAI: Instancia del LLM
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        logger.error("GOOGLE_API_KEY no encontrada en las variables de entorno")
        raise ValueError(
            "Por favor configura GOOGLE_API_KEY en tu archivo .env\n"
            "Obtén tu clave en: https://makersuite.google.com/app/apikey"
        )
    
    logger.info(f"Inicializando Gemini con modelo: {model}")
    
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature,
        convert_system_message_to_human=True  # Compatibilidad con system messages
    )
    
    return llm


# Configuraciones predefinidas
def get_gemini_for_validation():
    """LLM configurado para validaciones (determinista)"""
    return get_gemini_llm(model="gemini-1.5-flash", temperature=0)


def get_gemini_for_analysis():
    """LLM configurado para análisis (más flexible)"""
    return get_gemini_llm(model="gemini-1.5-pro", temperature=0.3)


# Ejemplo de uso con Tools
if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    
    llm = get_gemini_for_validation()
    
    # Test simple
    response = llm.invoke([
        HumanMessage(content="Di 'Hola' si estás funcionando correctamente")
    ])
    
    print(f"Respuesta de Gemini: {response.content}")
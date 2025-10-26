"""
Script para probar la configuración de Gemini
Ejecutar: python test_gemini.py
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

# Cargar variables de entorno
load_dotenv()

def test_gemini_connection():
    """Prueba la conexión con Gemini"""
    
    print("🔍 Verificando configuración de Gemini...\n")
    
    # Verificar API Key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY no encontrada")
        print("   Por favor configura tu API key en el archivo .env")
        print("   Obtén tu clave en: https://makersuite.google.com/app/apikey")
        return False
    
    print(f"✅ API Key encontrada: {api_key[:10]}...")
    
    # Intentar conexión
    try:
        print("\n🤖 Conectando con Gemini...")
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0
        )
        
        # Test simple
        messages = [
            SystemMessage(content="Eres un asistente que valida pedidos."),
            HumanMessage(content="Responde con un simple 'OK' si estás funcionando.")
        ]
        
        response = llm.invoke(messages)
        
        print(f"✅ Conexión exitosa!")
        print(f"📝 Respuesta de Gemini: {response.content}\n")
        
        # Test con un ejemplo de validación
        print("🧪 Probando análisis de pedido...")
        
        validation_messages = [
            HumanMessage(content="""
Analiza este pedido y di si parece válido:
- Cliente: CUST001
- Monto: $1500
- Items: Laptop (1x $1500)

Responde solo: VÁLIDO o INVÁLIDO y una breve razón.
            """)
        ]
        
        validation_response = llm.invoke(validation_messages)
        print(f"📊 Análisis: {validation_response.content}\n")
        
        print("=" * 50)
        print("✨ ¡Gemini está configurado correctamente!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error al conectar con Gemini:")
        print(f"   {str(e)}")
        print("\n💡 Posibles soluciones:")
        print("   1. Verifica que tu API key sea correcta")
        print("   2. Asegúrate de tener internet")
        print("   3. Revisa que hayas activado la API de Gemini")
        return False


if __name__ == "__main__":
    test_gemini_connection()
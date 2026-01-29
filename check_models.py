import os
import google.generativeai as genai
from dotenv import load_dotenv

def check_gemini_models():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file.")
        return

    print(f"🔑 Checking models for API Key: {api_key[:6]}...{api_key[-4:]}")
    
    try:
        genai.configure(api_key=api_key)
        
        print("\n📡 Fetching available models from Google API...")
        print("-" * 40)
        
        found_any = False
        for m in genai.list_models():
            # filter for text generation models
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ {m.name}")
                found_any = True
                
        print("-" * 40)
        
        if not found_any:
            print("⚠️ No models found that support 'generateContent'. Check your API Key permissions.")
        else:
            print("💡 Tip: Update 'LLM_MODEL' in your .env with one of the names above (e.g., 'gemini-pro').")
            
    except Exception as e:
        print(f"\n❌ API Error: {e}")
        print("Possible causes:")
        print("1. Invalid API Key.")
        print("2. API Key does not have access to Generative AI (check Google AI Studio).")
        print("3. Network issues or region restrictions.")

if __name__ == "__main__":
    check_gemini_models()

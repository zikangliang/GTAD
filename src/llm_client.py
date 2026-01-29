import os
import json
import google.generativeai as genai
from openai import OpenAI
from typing import Dict, Any

class LLMAnalyzer:
    def __init__(self):
        # 1. Try OpenAI Compatible Config (DeepSeek, Moonshot, etc.)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.openai_model = os.getenv("LLM_MODEL", "gpt-3.5-turbo") # Default, can be deepseek-chat etc.
        
        # 2. Try Google Gemini Config
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model_name = os.getenv("LLM_MODEL", "gemini-pro")

        self.client_type = None

        if self.openai_api_key:
            self.client_type = "openai"
            self.client = OpenAI(
                api_key=self.openai_api_key,
                base_url=self.openai_base_url
            )
            print(f"LLM initialized with OpenAI-compatible mode. Model: {self.openai_model}, Base URL: {self.openai_base_url}")
        
        elif self.gemini_api_key:
            self.client_type = "gemini"
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel(self.gemini_model_name)
            print(f"LLM initialized with Google Gemini mode. Model: {self.gemini_model_name}")
        
        else:
            raise ValueError("No valid API Key found. Please set OPENAI_API_KEY or GEMINI_API_KEY.")

    def analyze_readme(self, readme_content: str) -> Dict[str, Any]:
        """
        Analyzes the README content and returns a structured JSON summary.
        """
        # Truncate content to avoid token limits
        truncated_content = readme_content[:10000]

        system_prompt = """
        You are a senior technical technology analyst. 
        Analyze the provided GitHub project README content and provide a structured summary in simplified Chinese (简体中文).
        
        Return the result strictly as a valid JSON object with the following fields:
        - `one_sentence_summary`: A concise one-sentence introduction (in Chinese).
        - `core_features`: A list of 3 key functional features (in Chinese).
        - `tech_stack`: A list of key technologies/languages/frameworks used.
        - `use_case`: A description of the primary use case or problem it solves (in Chinese).
        - `score`: A recommendation score from 1 to 5 (integer).

        Do not include markdown formatting (like ```json) in the response, just the raw JSON string.
        """
        
        user_prompt = f"README Content:\n{truncated_content}"

        try:
            text_response = ""

            if self.client_type == "openai":
                response = self.client.chat.completions.create(
                    model=self.openai_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"} # Most newer models support this
                )
                text_response = response.choices[0].message.content
            
            elif self.client_type == "gemini":
                full_prompt = system_prompt + "\n" + user_prompt
                response = self.model.generate_content(
                    full_prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                text_response = response.text

            # Clean up potential markdown code blocks
            text_response = text_response.strip()
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]
            
            return json.loads(text_response)
            
        except Exception as e:
            print(f"Error during LLM analysis: {e}")
            return {
                "one_sentence_summary": "AI 分析失败",
                "core_features": ["无法获取", "无法获取", "无法获取"],
                "tech_stack": [],
                "use_case": f"分析错误: {str(e)}",
                "score": 0
            }

if __name__ == "__main__":
    # Test execution
    from dotenv import load_dotenv
    load_dotenv()
    
    # Mock README content for testing
    mock_readme = """
    # SuperFastDB
    
    SuperFastDB is a high-performance key-value store written in Rust.
    
    ## Features
    - **Speed**: 100k OPS.
    - **Persistence**: AOF and RDB support.
    - **Cluster**: Built-in sharding.
    
    ## Usage
    Suitable for caching and real-time analytics.
    """
    
    try:
        analyzer = LLMAnalyzer()
        result = analyzer.analyze_readme(mock_readme)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(e)

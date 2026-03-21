import requests
from config import OLLAMA_URL, MODEL_NAME, OllamaConfig

class OllamaModel:
    
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.config = OllamaConfig.get_generation_config()
        self.api_url = OLLAMA_URL
    
    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            **self.config
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return ""
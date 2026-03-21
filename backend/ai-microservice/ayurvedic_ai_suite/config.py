import requests
from typing import Dict, Any

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"


class OllamaConfig:
    
    @staticmethod
    def check_model_available() -> bool:
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(MODEL_NAME in model.get('name', '') for model in models)
            return False
        except:
            return False
    
    @staticmethod
    def get_generation_config() -> Dict[str, Any]:
        return {
            "temperature": 0.1,
            "top_p": 0.9,
            "top_k": 40,
            "max_tokens": 2048,
            "stop": ["\n\nHuman:", "\n\nAssistant:", "</s>", "User:", "\n\nUser:"]
        }
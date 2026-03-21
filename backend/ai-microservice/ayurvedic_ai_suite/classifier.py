from typing import Dict, Any, Optional
from models import OllamaModel


class SymptomToSpecialistOllama:
    
    def __init__(self):
        self.model = OllamaModel()
        
    def classify(self, symptoms: str) -> Dict[str, Any]:
        
        emergency_check = self._check_emergency(symptoms)
        if emergency_check:
            return emergency_check
        
        return self._rule_based_classification(symptoms)
    
    def _check_emergency(self, symptoms: str) -> Optional[Dict[str, Any]]:
        s = symptoms.lower()
        
        emergency_keywords = [
            "suicidal", "self-harm", "hurt myself", "kill myself",
            "unconscious", "not breathing", "severe bleeding",
            "heart attack", "stroke", "paralyzed", "cant breathe",
            "chest pain", "heavy bleeding"
        ]
        
        for keyword in emergency_keywords:
            if keyword in s:
                return {
                    "primary_specialist": "emergency",
                    "specialist_name": "EMERGENCY - Go to Hospital Immediately",
                    "confidence": 1.0,
                    "reasoning": f"Patient reported '{keyword}' - requires immediate emergency care",
                    "urgency": "emergency",
                    "dosha": None
                }
        return None
    
    def _rule_based_classification(self, symptoms: str) -> Dict[str, Any]:
        s = symptoms.lower()
        
        mental_keywords = {
            "hallucinat": "Patient reports hallucinations - requires mental health evaluation",
            "delusion": "Patient reports delusional thoughts - requires mental health evaluation",
            "paranoi": "Patient reports paranoid feelings - requires mental health evaluation",
            "hearing voices": "Patient reports auditory hallucinations - requires mental health evaluation",
            "seeing things": "Patient reports visual hallucinations - requires mental health evaluation",
            "depress": "Patient reports depression - requires mental health evaluation",
            "anxiety": "Patient reports anxiety - requires mental health evaluation",
            "panic": "Patient reports panic attacks - requires mental health evaluation"
        }
        
        for keyword, reasoning in mental_keywords.items():
            if keyword in s:
                return {
                    "primary_specialist": "manasaroga",
                    "specialist_name": "Manasaroga (Mental Health Specialist)",
                    "confidence": 0.95,
                    "reasoning": reasoning,
                    "urgency": "urgent",
                    "dosha": ["vata", "pitta"]
                }
        
        if any(word in s for word in ["cough", "cold", "throat", "nose", "ear", "sneeze", "sinus"]):
            return {
                "primary_specialist": "shalakya",
                "specialist_name": "Shalakya Tantra (ENT Specialist)",
                "confidence": 0.9,
                "reasoning": "Respiratory/ENT symptoms detected",
                "urgency": "soon",
                "dosha": ["kapha"]
            }
        
        if any(word in s for word in ["fever", "temperature", "hot", "chills", "body pain", "weakness"]):
            return {
                "primary_specialist": "kayachikitsa",
                "specialist_name": "Kayachikitsa (Internal Medicine)",
                "confidence": 0.9,
                "reasoning": "Fever/body pain indicates internal medicine consultation",
                "urgency": "soon",
                "dosha": ["pitta"]
            }
        
        if any(word in s for word in ["joint", "arthritis", "pain", "ache", "swelling", "back pain"]):
            return {
                "primary_specialist": "kayachikitsa",
                "specialist_name": "Kayachikitsa (Internal Medicine)",
                "confidence": 0.85,
                "reasoning": "Pain symptoms suggest internal medicine consultation",
                "urgency": "soon",
                "dosha": ["vata"]
            }
        
        if any(word in s for word in ["pregnancy", "pregnant", "menstrual", "period", "fertility", "women"]):
            return {
                "primary_specialist": "prasuti_tantra",
                "specialist_name": "Prasuti Tantra (Gynecology)",
                "confidence": 0.9,
                "reasoning": "Women's health symptoms detected",
                "urgency": "soon",
                "dosha": ["vata", "pitta"]
            }
        
        if any(word in s for word in ["child", "baby", "kid", "infant", "pediatric"]):
            return {
                "primary_specialist": "balaroga",
                "specialist_name": "Balaroga (Pediatrics)",
                "confidence": 0.9,
                "reasoning": "Pediatric case detected",
                "urgency": "soon",
                "dosha": None
            }
        
        if any(word in s for word in ["fertility", "libido", "sexual", "sperm", "impotence"]):
            return {
                "primary_specialist": "vajikarana",
                "specialist_name": "Vajikarana (Reproductive Health)",
                "confidence": 0.9,
                "reasoning": "Reproductive health symptoms detected",
                "urgency": "routine",
                "dosha": ["vata"]
            }
        
        return {
            "primary_specialist": "kayachikitsa",
            "specialist_name": "Kayachikitsa (Internal Medicine)",
            "confidence": 0.7,
            "reasoning": "General symptoms - internal medicine recommended for initial evaluation",
            "urgency": "routine",
            "dosha": None
        }
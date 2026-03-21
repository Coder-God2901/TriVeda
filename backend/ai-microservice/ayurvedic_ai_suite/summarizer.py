import json
from typing import Dict, List, Any, Optional
from models import OllamaModel


class MedicalRecordsSummarizerOllama:
    
    def __init__(self):
        self.model = OllamaModel()
        
    def summarize(self, raw_text: str) -> Dict[str, Any]:
        
        basic_info = self._extract_basic_info(raw_text)
        
        prompt = f"""You are a medical scribe. Take this messy medical record and convert it into 3 clean, professional bullet points.

Messy Record:
{raw_text}

Requirements:
- Exactly 3 bullet points
- Professional medical language
- Remove filler words
- Include: main problem, duration, key findings
- Be concise but informative

IMPORTANT INSTRUCTIONS:
- Return ONLY valid JSON
- Do NOT include any explanations or additional text

Expected JSON format:
{{
    "summary_points": [
        "First professional bullet point",
        "Second professional bullet point",
        "Third professional bullet point"
    ],
    "key_findings": [
        "Key finding 1",
        "Key finding 2"
    ],
    "missing_info": [
        "Missing information 1",
        "Missing information 2"
    ]
}}

Your JSON response:"""
        
        try:
            response = self.model.generate(prompt)
            if response:
                json_str = self._extract_json(response)
                if json_str:
                    try:
                        result = json.loads(json_str)
                        return result
                    except:
                        pass
            
            return self._enhanced_manual_summary(raw_text, basic_info)
                
        except Exception:
            return self._enhanced_manual_summary(raw_text, basic_info)
    
    def _extract_json(self, text: str) -> Optional[str]:
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return text[start:end]
        except:
            pass
        return None
    
    def _extract_basic_info(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        info = {
            "symptoms": [],
            "conditions": []
        }
        
        symptom_keywords = {
            "hallucinat": "Hallucinations",
            "vomit": "Vomiting",
            "stomach ache": "Abdominal pain",
            "pain": "Pain",
            "cant see": "Vision problems",
            "night": "Night blindness",
            "fever": "Fever",
            "cough": "Cough",
            "headache": "Headache"
        }
        
        for keyword, symptom in symptom_keywords.items():
            if keyword in text_lower:
                info["symptoms"].append(symptom)
        
        return info
    
    def _enhanced_manual_summary(self, text: str, basic_info: Dict) -> Dict[str, Any]:
        text_lower = text.lower()
        points = []
        findings = []
        
        symptom_map = {
            "hallucinat": ("Patient reports experiencing hallucinations", "Hallucinations present"),
            "vomit": ("Patient reports episodes of vomiting", "Vomiting"),
            "stomach ache": ("Patient complains of abdominal pain", "Abdominal pain"),
            "pain": ("Patient reports pain", "Pain"),
            "cant see": ("Patient reports vision problems", "Visual disturbance"),
            "night": ("Patient reports night blindness", "Night blindness"),
            "fever": ("Patient reports fever", "Fever"),
            "cough": ("Patient reports cough", "Cough"),
            "headache": ("Patient reports headaches", "Headache")
        }
        
        for keyword, (point, finding) in symptom_map.items():
            if keyword in text_lower:
                if point not in points:
                    points.append(point)
                if finding not in findings:
                    findings.append(finding)
        
        if "mental" in text_lower or "psych" in text_lower or "hallucinat" in text_lower:
            if "Patient requires mental health evaluation" not in points:
                points.append("Patient requires mental health evaluation")
            if "Mental health concerns" not in findings:
                findings.append("Mental health concerns")
        
        default_points = [
            "Patient presents with multiple symptoms requiring evaluation",
            "Complete history needed for comprehensive assessment",
            "Further diagnostic workup recommended"
        ]
        
        while len(points) < 3:
            points.append(default_points[len(points)])
        
        default_findings = [
            "Multiple symptoms reported",
            "Further evaluation needed",
            "Clinical assessment required"
        ]
        
        while len(findings) < 3:
            findings.append(default_findings[len(findings)])
        
        missing = []
        if "duration" not in text_lower:
            missing.append("Duration of symptoms")
        if "severe" not in text_lower:
            missing.append("Symptom severity")
        if "age" not in text_lower:
            missing.append("Patient age")
        
        default_missing = ["Duration of symptoms", "Symptom severity", "Associated symptoms"]
        while len(missing) < 3:
            missing.append(default_missing[len(missing)])
        
        return {
            "summary_points": points[:3],
            "key_findings": findings[:3],
            "missing_info": missing[:3]
        }
import datetime
import json
from typing import Dict, List, Any, Optional
from enum import Enum
from models import OllamaModel


class EmailTone(str, Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    CASUAL = "casual"
    URGENT = "urgent"
    EMPATHETIC = "empathetic"


class EmailPurpose(str, Enum):
    APPOINTMENT_CONFIRMATION = "appointment_confirmation"
    APPOINTMENT_REMINDER = "appointment_reminder"
    FOLLOW_UP = "follow_up"
    PRESCRIPTION = "prescription"
    REPORT = "report"
    GENERAL = "general"
    MARKETING = "marketing"
    WELCOME = "welcome"


class EmailLength(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    DETAILED = "detailed"


class EmailGeneratorOllama:
    
    def __init__(self):
        self.model = OllamaModel()
        
        self.system_prompt = """You are an expert medical writer for an Ayurvedic clinic. Your role is to generate professional, clear, and compassionate emails for patients.

RULES:
1. Generate emails based on the specified purpose, tone, and recipient
2. Include all necessary details: appointment time, doctor name, clinic address, etc.
3. Use proper email structure: subject line, salutation, body, closing, signature
4. Be concise but include all essential information
5. Match the tone to the purpose
6. Include clinic branding elements naturally
7. Proofread for errors and clarity
8. Return ONLY valid JSON, no other text

CLINIC DETAILS:
- Name: Ayurveda Wellness Center
- Address: 123 Healing Street, Wellness City, WC 12345
- Phone: (555) 123-4567
- Email: info@ayurvedawellness.com
- Website: www.ayurvedawellness.com
- Doctors: Dr. Arya Sharma (Panchakarma), Dr. Vikram Patel (Kayachikitsa), Dr. Priya Singh (Women's Health)

OUTPUT FORMAT (STRICT JSON):
{
    "subject": "Email subject line",
    "salutation": "Dear [Patient Name],",
    "body": "Main email content with proper paragraphs",
    "closing": "Warm regards,",
    "signature": "Dr. Arya Sharma\\nPanchakarma Specialist\\nAyurveda Wellness Center",
    "full_email": "Complete email with all parts combined",
    "character_count": 0,
    "estimated_read_time": "1 min"
}"""
        
        self.generation_history: List[Dict[str, Any]] = []
    
    def generate_email(self, 
                      purpose: EmailPurpose,
                      recipient_name: str,
                      recipient_email: str,
                      doctor_name: Optional[str] = None,
                      appointment_date: Optional[str] = None,
                      appointment_time: Optional[str] = None,
                      tone: EmailTone = EmailTone.PROFESSIONAL,
                      length: EmailLength = EmailLength.MEDIUM,
                      additional_notes: Optional[str] = None,
                      custom_instructions: Optional[str] = None) -> Dict[str, Any]:
        
        purpose_context = self._get_purpose_context(purpose)
        
        prompt = f"""{self.system_prompt}

Generate a {tone.value} email for {purpose_context}.

RECIPIENT:
Name: {recipient_name}
Email: {recipient_email}

APPOINTMENT DETAILS:
{self._format_appointment_details(doctor_name, appointment_date, appointment_time)}

EMAIL SPECIFICATIONS:
- Tone: {tone.value}
- Length: {length.value}
{self._format_additional_notes(additional_notes)}
{custom_instructions if custom_instructions else ''}

Generate a complete email following the JSON format specified.

Your JSON response:"""
        
        try:
            print(f"Generating email...")
            response = self.model.generate(prompt)
            
            if response:
                email_data = self._extract_json(response)
                
                if email_data:
                    required_fields = ['subject', 'salutation', 'body', 'closing', 'signature']
                    for field in required_fields:
                        if field not in email_data:
                            email_data[field] = self._get_default_field(field, recipient_name, doctor_name)
                    
                    if 'full_email' not in email_data:
                        email_data['full_email'] = self._build_full_email(email_data)
                    
                    email_data['character_count'] = len(email_data.get('full_email', ''))
                    
                    email_data["purpose"] = purpose.value
                    email_data["tone"] = tone.value
                    email_data["recipient_name"] = recipient_name
                    email_data["recipient_email"] = recipient_email
                    email_data["generated_at"] = datetime.datetime.now().isoformat()
                    email_data["estimated_read_time"] = self._calculate_read_time(email_data['character_count'])
                    
                    self.generation_history.append({
                        "timestamp": datetime.datetime.now().isoformat(),
                        "purpose": purpose.value,
                        "recipient": recipient_email,
                        "subject": email_data.get("subject", "")
                    })
                    
                    return email_data
            
            print(f"AI generation failed. Using fallback template.")
            return self._fallback_email(purpose, recipient_name, doctor_name, appointment_date, appointment_time, additional_notes)
                
        except Exception as e:
            print(f"Error: {e}")
            return self._fallback_email(purpose, recipient_name, doctor_name, appointment_date, appointment_time, additional_notes)
    
    def _get_default_field(self, field: str, recipient_name: str, doctor_name: Optional[str]) -> str:
        defaults = {
            'subject': 'Message from Ayurveda Wellness Center',
            'salutation': f'Dear {recipient_name},',
            'body': 'Thank you for choosing Ayurveda Wellness Center. We look forward to serving you.',
            'closing': 'Warm regards,',
            'signature': f'{doctor_name or "The Ayurveda Wellness Team"}\nAyurveda Wellness Center\n(555) 123-4567'
        }
        return defaults.get(field, '')
    
    def _build_full_email(self, email_data: Dict[str, Any]) -> str:
        parts = []
        
        if email_data.get('salutation'):
            parts.append(email_data['salutation'])
            parts.append('')
        
        if email_data.get('body'):
            parts.append(email_data['body'])
            parts.append('')
        
        if email_data.get('closing'):
            parts.append(email_data['closing'])
        
        if email_data.get('signature'):
            parts.append(email_data['signature'])
        
        return '\n'.join(parts)
    
    def _calculate_read_time(self, char_count: int) -> str:
        words = char_count / 5
        minutes = max(1, round(words / 200))
        return f"{minutes} min"
    
    def _get_purpose_context(self, purpose: EmailPurpose) -> str:
        contexts = {
            EmailPurpose.APPOINTMENT_CONFIRMATION: "appointment confirmation email confirming the patient's upcoming visit",
            EmailPurpose.APPOINTMENT_REMINDER: "appointment reminder email to be sent 24 hours before the visit",
            EmailPurpose.FOLLOW_UP: "follow-up email after a patient's appointment, checking on their progress",
            EmailPurpose.PRESCRIPTION: "email containing prescription information and instructions",
            EmailPurpose.REPORT: "email with attached lab reports or test results",
            EmailPurpose.GENERAL: "general informational email",
            EmailPurpose.MARKETING: "marketing email about special offers, new services, or health tips",
            EmailPurpose.WELCOME: "welcome email for new patients joining the clinic"
        }
        return contexts.get(purpose, "general email")
    
    def _format_appointment_details(self, doctor_name: Optional[str], date: Optional[str], time: Optional[str]) -> str:
        details = []
        if doctor_name:
            details.append(f"Doctor: {doctor_name}")
        if date:
            details.append(f"Date: {date}")
        if time:
            details.append(f"Time: {time}")
        
        if not details:
            return "No specific appointment details provided."
        
        return "\n".join(details)
    
    def _format_additional_notes(self, notes: Optional[str]) -> str:
        if notes:
            return f"Additional Instructions:\n{notes}\n"
        return ""
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
        except:
            pass
        return None
    
    def _fallback_email(self, purpose: EmailPurpose, recipient_name: str, 
                       doctor_name: Optional[str], date: Optional[str], 
                       time: Optional[str], additional_notes: Optional[str] = None) -> Dict[str, Any]:
        
        templates = {
            EmailPurpose.APPOINTMENT_CONFIRMATION: {
                "subject": f"Appointment Confirmation - {doctor_name or 'Your Visit'}",
                "body": f"Your appointment has been confirmed for {date or 'your scheduled date'} at {time or 'your scheduled time'} with {doctor_name or 'your doctor'}. Please arrive 10 minutes early and bring any relevant medical records.\n\nIf you need to reschedule or have any questions, please contact us at (555) 123-4567."
            },
            EmailPurpose.APPOINTMENT_REMINDER: {
                "subject": "Reminder: Upcoming Appointment Tomorrow",
                "body": f"This is a friendly reminder of your appointment tomorrow, {date} at {time} with {doctor_name or 'your doctor'}. We look forward to seeing you!\n\nPlease remember to bring any relevant medical records and arrive 10 minutes early."
            },
            EmailPurpose.FOLLOW_UP: {
                "subject": "Following Up on Your Recent Appointment",
                "body": f"I hope this email finds you well. I wanted to follow up on your recent appointment at Ayurveda Wellness Center with {doctor_name or 'your doctor'}. We discussed your health concerns and developed a personalized treatment plan to support your wellness journey.\n\nPlease let me know if you have experienced any improvement or if you have any questions about your treatment plan. If you need any additional guidance or would like to schedule a follow-up visit, please don't hesitate to reach out.\n\n{additional_notes if additional_notes else ''}"
            },
            EmailPurpose.WELCOME: {
                "subject": "Welcome to Ayurveda Wellness Center",
                "body": f"Welcome to our clinic! We're delighted to have you as a patient. Dr. {doctor_name or 'our team'} looks forward to supporting you on your wellness journey.\n\nAs a new patient, you'll experience our holistic approach to healthcare that combines ancient Ayurvedic wisdom with modern medical knowledge. Our team is here to support you every step of the way.\n\nPlease feel free to contact us if you have any questions before your visit."
            },
            EmailPurpose.GENERAL: {
                "subject": "Message from Ayurveda Wellness Center",
                "body": f"Thank you for choosing Ayurveda Wellness Center. We look forward to serving you.\n\n{additional_notes if additional_notes else 'Please contact us if you have any questions or would like to schedule an appointment.'}"
            }
        }
        
        template = templates.get(purpose, templates[EmailPurpose.GENERAL])
        
        salutation = f"Dear {recipient_name},"
        closing = "Warm regards,"
        signature = f"{doctor_name or 'The Ayurveda Wellness Team'}\nAyurveda Wellness Center\n(555) 123-4567\ninfo@ayurvedawellness.com"
        
        full_email = f"""{salutation}

{template['body']}

{closing}
{signature}"""
        
        return {
            "subject": template['subject'],
            "salutation": salutation,
            "body": template['body'],
            "closing": closing,
            "signature": signature,
            "full_email": full_email,
            "character_count": len(full_email),
            "estimated_read_time": "1 min",
            "purpose": purpose.value,
            "tone": "professional",
            "recipient_name": recipient_name,
            "generated_at": datetime.datetime.now().isoformat()
        }
    
    def get_history(self) -> List[Dict[str, Any]]:
        return self.generation_history
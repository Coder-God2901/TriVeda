import datetime
import re
import random
from typing import Dict, List, Any, Optional
from enum import Enum
from models import OllamaModel
from utils import format_time_input


class TimePreference(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"


class AIReceptionistOllama:
    
    def __init__(self):
        self.model = OllamaModel()
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
        
        self.farewell_phrases = [
            "thank you", "thanks", "thank you so much", "thanks a lot",
            "goodbye", "bye", "see you", "take care", "have a great day",
            "that's all", "that is all", "i'm done", "i am done", "all done"
        ]
        
        self.system_prompt = """You are an AI Receptionist for an Ayurvedic clinic. Your role is to help patients book appointments with the right specialists.

RULES:
1. Be friendly, professional, and helpful
2. When a patient wants to book an appointment, ask for:
   - The type of specialist they need
   - Preferred date
   - Preferred time of day
3. After gathering this information, provide available slots from the dummy database
4. Present slots clearly and ask which one they prefer
5. Confirm the booking when they select a time
6. Keep responses concise and helpful
7. When the patient expresses gratitude, respond warmly
8. When the patient says goodbye, end the conversation gracefully

AVAILABLE DOCTORS AND SPECIALTIES:
- Panchakarma Specialist - Dr. Arya Sharma
- Kayachikitsa (Internal Medicine) - Dr. Vikram Patel
- Women's Health - Dr. Priya Singh
- ENT Specialist - Dr. Rajesh Kumar
- Mental Health - Dr. Anjali Mehta

DUMMY AVAILABILITY DATABASE:
- Morning slots (9:00 AM - 12:00 PM): Available for all specialists
- Afternoon slots (2:00 PM - 5:00 PM): Available for all specialists
- Evening slots (5:00 PM - 8:00 PM): Limited availability

Always respond in a natural, conversational way. Do not use JSON in your responses to patients."""
    
    def search_doctor_availability(self, specialty: str, date: str, time_preference: str) -> List[str]:
        print(f"Searching for {specialty} on {date} ({time_preference})...")
        
        available_slots = {
            ("Panchakarma Specialist", "morning"): ["09:00 AM", "10:30 AM"],
            ("Panchakarma Specialist", "afternoon"): ["02:00 PM", "03:30 PM"],
            ("Panchakarma Specialist", "evening"): ["05:00 PM", "06:30 PM"],
            ("Kayachikitsa", "morning"): ["09:30 AM", "11:00 AM"],
            ("Kayachikitsa", "afternoon"): ["02:00 PM", "04:00 PM"],
            ("Women's Health", "morning"): ["10:00 AM", "11:30 AM"],
            ("Women's Health", "afternoon"): ["03:00 PM", "04:30 PM"],
            ("ENT Specialist", "morning"): ["09:00 AM", "10:00 AM", "11:30 AM"],
            ("ENT Specialist", "afternoon"): ["02:30 PM", "04:00 PM"],
            ("Mental Health", "morning"): ["09:00 AM", "11:00 AM"],
            ("Mental Health", "afternoon"): ["02:00 PM", "03:30 PM", "05:00 PM"],
        }
        
        normalized_specialty = specialty
        key = (normalized_specialty, time_preference)
        
        if key in available_slots:
            return available_slots[key]
        else:
            if time_preference == "morning":
                return ["09:00 AM", "10:30 AM", "11:30 AM"]
            elif time_preference == "afternoon":
                return ["02:00 PM", "03:30 PM", "04:30 PM"]
            else:
                return ["05:00 PM", "06:30 PM", "07:30 PM"]
    
    def check_conversation_end(self, message: str) -> bool:
        message_lower = message.lower().strip()
        
        if message_lower in ['exit', 'quit', 'bye', 'goodbye', 'end', 'stop', 'menu', 'main menu', 'back', 'done']:
            return True
        
        for phrase in self.farewell_phrases:
            if phrase in message_lower and len(message_lower) < 30:
                return True
        
        return False
    
    def extract_appointment_info(self, message: str) -> Dict[str, Any]:
        message_lower = message.lower()
        info = {
            "specialty": None,
            "date": None,
            "time_preference": None
        }
        
        specialties = {
            "panchakarma": "Panchakarma Specialist",
            "kayachikitsa": "Kayachikitsa",
            "internal medicine": "Kayachikitsa",
            "women": "Women's Health",
            "gynecology": "Women's Health",
            "ent": "ENT Specialist",
            "ear": "ENT Specialist",
            "nose": "ENT Specialist",
            "throat": "ENT Specialist",
            "mental": "Mental Health",
            "psych": "Mental Health",
            "depression": "Mental Health",
            "anxiety": "Mental Health"
        }
        
        for keyword, specialty in specialties.items():
            if keyword in message_lower:
                info["specialty"] = specialty
                break
        
        if any(word in message_lower for word in ["morning", "am"]):
            info["time_preference"] = "morning"
        elif any(word in message_lower for word in ["afternoon", "pm"]):
            if "afternoon" in message_lower or ("pm" in message_lower and not any(w in message_lower for w in ["evening", "night"])):
                info["time_preference"] = "afternoon"
        elif any(word in message_lower for word in ["evening", "night"]):
            info["time_preference"] = "evening"
        
        today = datetime.datetime.now()
        
        if "tomorrow" in message_lower:
            tomorrow = today + datetime.timedelta(days=1)
            info["date"] = tomorrow.strftime("%Y-%m-%d")
        elif "next week" in message_lower:
            next_week = today + datetime.timedelta(days=7)
            info["date"] = next_week.strftime("%Y-%m-%d")
        elif "monday" in message_lower:
            days_ahead = 0 - today.weekday() + 0
            if days_ahead <= 0:
                days_ahead += 7
            next_day = today + datetime.timedelta(days=days_ahead)
            info["date"] = next_day.strftime("%Y-%m-%d")
        elif "tuesday" in message_lower:
            days_ahead = 1 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_day = today + datetime.timedelta(days=days_ahead)
            info["date"] = next_day.strftime("%Y-%m-%d")
        elif "wednesday" in message_lower:
            days_ahead = 2 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_day = today + datetime.timedelta(days=days_ahead)
            info["date"] = next_day.strftime("%Y-%m-%d")
        elif "thursday" in message_lower:
            days_ahead = 3 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_day = today + datetime.timedelta(days=days_ahead)
            info["date"] = next_day.strftime("%Y-%m-%d")
        elif "friday" in message_lower:
            days_ahead = 4 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_day = today + datetime.timedelta(days=days_ahead)
            info["date"] = next_day.strftime("%Y-%m-%d")
        elif "today" in message_lower:
            info["date"] = today.strftime("%Y-%m-%d")
        
        return info
    
    def process_message(self, message: str, conversation_id: Optional[str] = None, state: Dict[str, Any] = None) -> Dict[str, Any]:
        
        if self.check_conversation_end(message):
            farewell_responses = [
                "Thank you for visiting! Have a great day!",
                "It was a pleasure helping you. Take care!",
                "Goodbye! Feel free to come back if you need anything else.",
                "Have a wonderful day! Come back anytime."
            ]
            response_text = random.choice(farewell_responses)
            
            return {
                "response": response_text,
                "available_slots": None,
                "booking_complete": True,
                "conversation_state": "ended",
                "conversation_id": conversation_id,
                "conversation_ended": True,
                "state": state
            }
        
        if not conversation_id:
            conversation_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            self.conversations[conversation_id] = []
            state = {"stage": "initial", "info": {}}
        
        self.conversations[conversation_id].append({
            "role": "user",
            "content": message
        })
        
        if state is None:
            state = {"stage": "initial", "info": {}}
        
        if state["stage"] == "initial":
            info = self.extract_appointment_info(message)
            state["info"].update(info)
            
            if state["info"].get("specialty") and state["info"].get("date") and state["info"].get("time_preference"):
                available_slots = self.search_doctor_availability(
                    state["info"]["specialty"],
                    state["info"]["date"],
                    state["info"]["time_preference"]
                )
                
                slots_text = ", ".join(available_slots)
                response_text = f"I found {len(available_slots)} slot{'s' if len(available_slots) > 1 else ''} for a {state['info']['specialty']} on {state['info']['date']} ({state['info']['time_preference']}): {slots_text}. Which time works best for you?"
                
                state["stage"] = "awaiting_time_selection"
                state["available_slots"] = available_slots
                
            elif state["info"].get("specialty") and state["info"].get("date") and not state["info"].get("time_preference"):
                response_text = f"I see you'd like to see a {state['info']['specialty']} on {state['info']['date']}. What time of day works best for you - morning, afternoon, or evening?"
                state["stage"] = "awaiting_time_preference"
                
            elif state["info"].get("specialty") and not state["info"].get("date") and state["info"].get("time_preference"):
                response_text = f"I see you'd like a {state['info']['time_preference']} appointment with a {state['info']['specialty']}. What date works for you? (e.g., tomorrow, next Monday, or a specific date)"
                state["stage"] = "awaiting_date"
                
            elif state["info"].get("specialty") and not state["info"].get("date") and not state["info"].get("time_preference"):
                response_text = f"Great! I can help you book an appointment with a {state['info']['specialty']}. What date works for you, and do you prefer morning, afternoon, or evening?"
                state["stage"] = "awaiting_date_time"
                
            elif not state["info"].get("specialty") and state["info"].get("date") and state["info"].get("time_preference"):
                response_text = f"I see you'd like a {state['info']['time_preference']} appointment on {state['info']['date']}. Which specialist would you like to see? We have Panchakarma Specialist, Kayachikitsa, Women's Health, ENT, and Mental Health."
                state["stage"] = "awaiting_specialty"
                
            else:
                response_text = "I'd be happy to help you book an appointment! Which specialist would you like to see? We have Panchakarma Specialist, Kayachikitsa (Internal Medicine), Women's Health, ENT, and Mental Health specialists."
                state["stage"] = "awaiting_specialty"
        
        elif state["stage"] == "awaiting_specialty":
            info = self.extract_appointment_info(message)
            if info.get("specialty"):
                state["info"]["specialty"] = info["specialty"]
                
                if state["info"].get("date") and state["info"].get("time_preference"):
                    available_slots = self.search_doctor_availability(
                        state["info"]["specialty"],
                        state["info"]["date"],
                        state["info"]["time_preference"]
                    )
                    
                    slots_text = ", ".join(available_slots)
                    response_text = f"I found {len(available_slots)} slot{'s' if len(available_slots) > 1 else ''} for a {state['info']['specialty']} on {state['info']['date']} ({state['info']['time_preference']}): {slots_text}. Which time works best for you?"
                    
                    state["stage"] = "awaiting_time_selection"
                    state["available_slots"] = available_slots
                elif state["info"].get("date") and not state["info"].get("time_preference"):
                    response_text = f"Great! What time of day works best for you - morning, afternoon, or evening?"
                    state["stage"] = "awaiting_time_preference"
                elif state["info"].get("time_preference") and not state["info"].get("date"):
                    response_text = f"Great! What date works for your {state['info']['time_preference']} appointment?"
                    state["stage"] = "awaiting_date"
                else:
                    response_text = f"Great! Now, what date works for you, and do you prefer morning, afternoon, or evening?"
                    state["stage"] = "awaiting_date_time"
            else:
                response_text = "I didn't catch which specialist you need. We have Panchakarma Specialist, Kayachikitsa, Women's Health, ENT, and Mental Health. Which one would you like to see?"
        
        elif state["stage"] == "awaiting_date":
            info = self.extract_appointment_info(message)
            if info.get("date"):
                state["info"]["date"] = info["date"]
                
                if state["info"].get("time_preference"):
                    available_slots = self.search_doctor_availability(
                        state["info"]["specialty"],
                        state["info"]["date"],
                        state["info"]["time_preference"]
                    )
                    
                    slots_text = ", ".join(available_slots)
                    response_text = f"I found {len(available_slots)} slot{'s' if len(available_slots) > 1 else ''} for a {state['info']['specialty']} on {state['info']['date']} ({state['info']['time_preference']}): {slots_text}. Which time works best for you?"
                    
                    state["stage"] = "awaiting_time_selection"
                    state["available_slots"] = available_slots
                else:
                    response_text = f"Thanks! And do you prefer morning, afternoon, or evening?"
                    state["stage"] = "awaiting_time_preference"
            else:
                response_text = "I didn't catch the date. Could you please specify when you'd like to come? (e.g., tomorrow, next Monday, or a specific date like 2024-03-15)"
        
        elif state["stage"] == "awaiting_time_preference":
            info = self.extract_appointment_info(message)
            if info.get("time_preference"):
                state["info"]["time_preference"] = info["time_preference"]
                
                if state["info"].get("date"):
                    available_slots = self.search_doctor_availability(
                        state["info"]["specialty"],
                        state["info"]["date"],
                        state["info"]["time_preference"]
                    )
                    
                    slots_text = ", ".join(available_slots)
                    response_text = f"I found {len(available_slots)} slot{'s' if len(available_slots) > 1 else ''} for a {state['info']['specialty']} on {state['info']['date']} ({state['info']['time_preference']}): {slots_text}. Which time works best for you?"
                    
                    state["stage"] = "awaiting_time_selection"
                    state["available_slots"] = available_slots
                else:
                    response_text = f"Thanks! And what date works for your {state['info']['time_preference']} appointment?"
                    state["stage"] = "awaiting_date"
            else:
                response_text = "I didn't catch your time preference. Do you prefer morning, afternoon, or evening?"
        
        elif state["stage"] == "awaiting_date_time":
            info = self.extract_appointment_info(message)
            if info.get("date") and info.get("time_preference"):
                state["info"]["date"] = info["date"]
                state["info"]["time_preference"] = info["time_preference"]
                
                available_slots = self.search_doctor_availability(
                    state["info"]["specialty"],
                    state["info"]["date"],
                    state["info"]["time_preference"]
                )
                
                slots_text = ", ".join(available_slots)
                response_text = f"I found {len(available_slots)} slot{'s' if len(available_slots) > 1 else ''} for a {state['info']['specialty']} on {state['info']['date']} ({state['info']['time_preference']}): {slots_text}. Which time works best for you?"
                
                state["stage"] = "awaiting_time_selection"
                state["available_slots"] = available_slots
            elif info.get("date") and not info.get("time_preference"):
                state["info"]["date"] = info["date"]
                response_text = f"Thanks! And do you prefer morning, afternoon, or evening?"
                state["stage"] = "awaiting_time_preference"
            elif info.get("time_preference") and not info.get("date"):
                state["info"]["time_preference"] = info["time_preference"]
                response_text = f"Thanks! And what date works for your {state['info']['time_preference']} appointment?"
                state["stage"] = "awaiting_date"
            else:
                response_text = "I still need your preferred date and time. What date works for you, and do you prefer morning, afternoon, or evening?"
        
        elif state["stage"] == "awaiting_time_selection":
            selected_time = message.strip()
            
            if selected_time.lower() in ['cancel', 'back', 'menu', 'main menu']:
                response_text = "No problem! Let's start over. Which specialist would you like to see?"
                state = {"stage": "awaiting_specialty", "info": {}}
            else:
                formatted_time = format_time_input(selected_time)
                response_text = f"Great! I've booked your appointment with {state['info']['specialty']} on {state['info']['date']} at {formatted_time}. You'll receive a confirmation shortly. Is there anything else I can help with?"
                state["stage"] = "confirmed"
                state["booking_complete"] = True
        
        elif state["stage"] == "confirmed":
            if any(word in message.lower() for word in ['yes', 'another', 'more', 'also']):
                response_text = "Sure! What else would you like help with? You can book another appointment or ask about our services."
                state = {"stage": "initial", "info": {}}
            else:
                response_text = "Okay! Feel free to reach out if you need anything else. Have a great day!"
                state["stage"] = "ended"
        
        elif state["stage"] == "ended":
            response_text = "Thank you for visiting! Goodbye!"
            return {
                "response": response_text,
                "available_slots": None,
                "booking_complete": True,
                "conversation_state": "ended",
                "conversation_id": conversation_id,
                "conversation_ended": True,
                "state": state
            }
        
        else:
            response_text = "How can I help you with your appointment booking today?"
            state = {"stage": "initial", "info": {}}
        
        self.conversations[conversation_id].append({
            "role": "assistant",
            "content": response_text
        })
        
        return {
            "response": response_text,
            "available_slots": state.get("available_slots"),
            "booking_complete": state.get("booking_complete", False),
            "conversation_state": state["stage"],
            "conversation_id": conversation_id,
            "conversation_ended": state["stage"] == "ended",
            "state": state
        }
    
    def confirm_booking(self, conversation_id: str, selected_time: str, state: Dict[str, Any]) -> Dict[str, Any]:
        if conversation_id not in self.conversations:
            return {
                "response": "I couldn't find your conversation. Please start over.",
                "booking_complete": False,
                "conversation_id": conversation_id
            }
        
        formatted_time = format_time_input(selected_time)
        
        confirmation_text = f"Great! I've booked your appointment with {state['info']['specialty']} on {state['info']['date']} at {formatted_time}. You'll receive a confirmation email shortly. Is there anything else I can help with?"
        
        self.conversations[conversation_id].append({
            "role": "assistant",
            "content": confirmation_text
        })
        
        return {
            "response": confirmation_text,
            "booking_complete": True,
            "conversation_id": conversation_id
        }
    
    def call_nodejs_backend(self, specialty: str, date: str, time_preference: str) -> List[str]:
        return self.search_doctor_availability(specialty, date, time_preference)
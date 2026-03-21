import json
import os
import datetime
from typing import Dict, Any


from config import OLLAMA_URL, MODEL_NAME, OllamaConfig
from receptionist import AIReceptionistOllama
from email_generator import EmailGeneratorOllama, EmailTone, EmailPurpose
from questionnaire import DynamicQuestionnaireOllama
from summarizer import MedicalRecordsSummarizerOllama
from classifier import SymptomToSpecialistOllama
from utils import clear_screen, get_user_input_with_exit


class UnifiedAyurvedicApp:
    
    def __init__(self):
        print("Initializing Unified Ayurvedic AI System...")
        
        if not OllamaConfig.check_model_available():
            print("\nWARNING: Ollama not found or Llama 3.2 not available!")
            print("Please ensure:")
            print("1. Ollama is installed and running (run 'ollama serve')")
            print("2. Llama 3.2 is pulled (run 'ollama pull llama3.2')")
            print("\nStarting in fallback mode (limited functionality)...")
        
        self.receptionist = AIReceptionistOllama()
        self.email_generator = EmailGeneratorOllama()
        self.questionnaire = DynamicQuestionnaireOllama()
        self.summarizer = MedicalRecordsSummarizerOllama()
        self.classifier = SymptomToSpecialistOllama()
        
        self.current_conversation_id = None
        self.current_state = None
        print("All AI Modules Ready!\n")
    
    def print_main_header(self):
        clear_screen()
        print("=" * 70)
        print("AYURVEDIC AI ASSISTANT SUITE - OLLAMA EDITION")
        print("=" * 70)
        print(f"Model: {MODEL_NAME} (via Ollama)")
        print(f"Server: {OLLAMA_URL}")
        print("-" * 70)
        print("COMMANDS:")
        print("  • Type 'menu', 'exit', or 'back' anytime to return to main menu")
        print("  • Type 'done' to finish current task")
        print("=" * 70)
    
    def run(self):
        while True:
            self.print_main_header()
            print("\nMAIN MENU")
            print("-" * 70)
            print("1. AI Receptionist (Book Appointments)")
            print("2. Email Generator (Create Clinic Emails)")
            print("3. Dynamic Health Questionnaire (AI asks, you answer)")
            print("4. Medical Records Summarizer (Paste messy notes)")
            print("5. Symptom Classifier (Get specialist recommendation)")
            print("6. Exit")
            print("=" * 70)
            
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == '1':
                self.run_receptionist()
            elif choice == '2':
                self.run_email_generator()
            elif choice == '3':
                self.run_questionnaire()
            elif choice == '4':
                self.run_summarizer()
            elif choice == '5':
                self.run_classifier()
            elif choice == '6':
                print("\nThank you for using Ayurvedic AI Assistant Suite!")
                print("Namaste!\n")
                break
            else:
                print("Invalid choice. Press Enter to try again...")
                input()
    
    def run_receptionist(self):
        clear_screen()
        print("=" * 70)
        print("AI RECEPTIONIST - APPOINTMENT BOOKING")
        print("=" * 70)
        print("\nCOMMANDS:")
        print("  • Type 'menu' or 'exit' anytime to return to main menu")
        print("  • Type 'done' when finished with booking")
        print("-" * 70)
        print("\nYou can ask about appointments, e.g.:")
        print("  • 'I need to see a Panchakarma specialist tomorrow morning'")
        print("  • 'Do you have any appointments next Monday afternoon?'")
        print("  • 'I want to book with a mental health specialist'")
        print("=" * 70)
        
        self.current_conversation_id = None
        self.current_state = None
        conversation_active = True
        
        while conversation_active:
            print("\nYou:")
            user_input = input("  ").strip()
            
            if user_input.lower() in ['menu', 'exit', 'quit', 'main', 'back']:
                print("\nReturning to main menu...")
                break
            
            if not user_input:
                continue
            
            print("\nAI is thinking...")
            
            result = self.receptionist.process_message(
                user_input, 
                self.current_conversation_id,
                self.current_state
            )
            
            self.current_conversation_id = result["conversation_id"]
            self.current_state = result.get("state")
            
            print("\nRAW JSON OUTPUT:")
            print("-" * 70)
            output_json = {
                "response": result["response"],
                "available_slots": result.get("available_slots"),
                "booking_complete": result["booking_complete"],
                "conversation_state": result["conversation_state"],
                "conversation_id": result["conversation_id"]
            }
            print(json.dumps(output_json, indent=2))
            
            print("\nReceptionist:")
            print(f"  {result['response']}")
            
            if result.get("conversation_ended", False):
                print("\nConversation ended.")
                
                while True:
                    next_action = input("\nWould you like to book another appointment? (yes/no): ").strip().lower()
                    if next_action in ['no', 'n', 'menu', 'exit', 'back']:
                        print("\nReturning to main menu...")
                        conversation_active = False
                        break
                    elif next_action in ['yes', 'y']:
                        print("\nStarting new conversation...")
                        self.current_conversation_id = None
                        self.current_state = None
                        break
                    else:
                        print("Please answer 'yes' or 'no'")
        
        input("\nPress Enter to continue...")
    
    def run_email_generator(self):
        while True:
            clear_screen()
            print("=" * 70)
            print("AI EMAIL GENERATOR")
            print("=" * 70)
            print("\nCOMMANDS:")
            print("  • Choose 7 to return to main menu")
            print("-" * 70)
            print("\nEMAIL GENERATION MENU")
            print("-" * 70)
            print("1. Appointment Confirmation")
            print("2. Appointment Reminder")
            print("3. Follow-up Email")
            print("4. Welcome Email")
            print("5. Custom Email")
            print("6. View Generation History")
            print("7. Return to Main Menu")
            print("-" * 70)
            
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == '1':
                self.generate_appointment_email(EmailPurpose.APPOINTMENT_CONFIRMATION)
            elif choice == '2':
                self.generate_appointment_email(EmailPurpose.APPOINTMENT_REMINDER)
            elif choice == '3':
                self.generate_followup_email()
            elif choice == '4':
                self.generate_welcome_email()
            elif choice == '5':
                self.generate_custom_email()
            elif choice == '6':
                self.show_email_history()
            elif choice == '7':
                break
            else:
                print("Invalid choice. Press Enter to try again...")
                input()
    
    def generate_appointment_email(self, purpose: EmailPurpose):
        clear_screen()
        print("=" * 70)
        print(f"{'CONFIRMATION' if purpose == EmailPurpose.APPOINTMENT_CONFIRMATION else 'REMINDER'} EMAIL")
        print("=" * 70)
        print("\nType 'menu' at any prompt to return to email menu")
        print("-" * 70)
        
        recipient_name = get_user_input_with_exit("Patient name")
        if recipient_name == "EXIT_COMMAND": return
        
        recipient_email = get_user_input_with_exit("Patient email")
        if recipient_email == "EXIT_COMMAND": return
        
        doctor_name = get_user_input_with_exit("Doctor name", required=False, default="Dr. Arya Sharma")
        if doctor_name == "EXIT_COMMAND": return
        
        appointment_date = get_user_input_with_exit("Appointment date (e.g., March 15, 2024)")
        if appointment_date == "EXIT_COMMAND": return
        
        appointment_time = get_user_input_with_exit("Appointment time (e.g., 10:00 AM)")
        if appointment_time == "EXIT_COMMAND": return
        
        print("\nSelect tone:")
        print("  1. Professional")
        print("  2. Friendly")
        print("  3. Formal")
        tone_choice = input("Enter choice (1-3) or 'menu' to return: ").strip()
        
        if tone_choice.lower() in ['menu', 'exit', 'back']:
            return
        
        tone_map = {
            "1": EmailTone.PROFESSIONAL,
            "2": EmailTone.FRIENDLY,
            "3": EmailTone.FORMAL
        }
        tone = tone_map.get(tone_choice, EmailTone.PROFESSIONAL)
        
        print("\nGenerating email...")
        
        result = self.email_generator.generate_email(
            purpose=purpose,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            doctor_name=doctor_name,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            tone=tone
        )
        
        self.display_email(result)
    
    def generate_followup_email(self):
        clear_screen()
        print("=" * 70)
        print("FOLLOW-UP EMAIL")
        print("=" * 70)
        
        recipient_name = get_user_input_with_exit("Patient name")
        if recipient_name == "EXIT_COMMAND": return
        
        recipient_email = get_user_input_with_exit("Patient email")
        if recipient_email == "EXIT_COMMAND": return
        
        doctor_name = get_user_input_with_exit("Doctor name", required=False, default="Dr. Arya Sharma")
        if doctor_name == "EXIT_COMMAND": return
        
        notes = get_user_input_with_exit("Any specific follow-up notes?", required=False)
        if notes == "EXIT_COMMAND": return
        
        print("\nGenerating email...")
        
        result = self.email_generator.generate_email(
            purpose=EmailPurpose.FOLLOW_UP,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            doctor_name=doctor_name,
            additional_notes=notes
        )
        
        self.display_email(result)
    
    def generate_welcome_email(self):
        clear_screen()
        print("=" * 70)
        print("WELCOME EMAIL")
        print("=" * 70)
        
        recipient_name = get_user_input_with_exit("New patient name")
        if recipient_name == "EXIT_COMMAND": return
        
        recipient_email = get_user_input_with_exit("Patient email")
        if recipient_email == "EXIT_COMMAND": return
        
        doctor_name = get_user_input_with_exit("Primary doctor", required=False, default="Dr. Arya Sharma")
        if doctor_name == "EXIT_COMMAND": return
        
        print("\nGenerating email...")
        
        result = self.email_generator.generate_email(
            purpose=EmailPurpose.WELCOME,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            doctor_name=doctor_name
        )
        
        self.display_email(result)
    
    def generate_custom_email(self):
        clear_screen()
        print("=" * 70)
        print("CUSTOM EMAIL")
        print("=" * 70)
        
        recipient_name = get_user_input_with_exit("Recipient name")
        if recipient_name == "EXIT_COMMAND": return
        
        recipient_email = get_user_input_with_exit("Recipient email")
        if recipient_email == "EXIT_COMMAND": return
        
        print("\nSelect purpose:")
        purposes = ["Appointment Confirmation", "Appointment Reminder", "Follow-up", "Welcome", "General"]
        for i, p in enumerate(purposes, 1):
            print(f"  {i}. {p}")
        purpose_choice = input("Enter choice (1-5) or 'menu' to return: ").strip()
        
        if purpose_choice.lower() in ['menu', 'exit', 'back']:
            return
        
        purpose_map = {
            "1": EmailPurpose.APPOINTMENT_CONFIRMATION,
            "2": EmailPurpose.APPOINTMENT_REMINDER,
            "3": EmailPurpose.FOLLOW_UP,
            "4": EmailPurpose.WELCOME,
            "5": EmailPurpose.GENERAL
        }
        purpose = purpose_map.get(purpose_choice, EmailPurpose.GENERAL)
        
        custom_instructions = get_user_input_with_exit("Custom instructions (what should the email say?)")
        if custom_instructions == "EXIT_COMMAND": return
        
        print("\nGenerating email...")
        
        result = self.email_generator.generate_email(
            purpose=purpose,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            custom_instructions=custom_instructions
        )
        
        self.display_email(result)
    
    def display_email(self, email_data: Dict[str, Any]):
        print("\n" + "=" * 70)
        print("GENERATED EMAIL")
        print("=" * 70)
        
        print("\nRAW JSON OUTPUT:")
        print("-" * 70)
        print(json.dumps(email_data, indent=2, default=str))
        
        print("\nFINAL EMAIL:")
        print("-" * 70)
        print(f"\n{email_data.get('full_email', '')}")
        print("-" * 70)
        print(f"Stats: {email_data.get('character_count', 0)} characters | Read time: {email_data.get('estimated_read_time', '1 min')}")
        
        input("\nPress Enter to continue...")
    
    def show_email_history(self):
        clear_screen()
        print("=" * 70)
        print("GENERATION HISTORY")
        print("=" * 70)
        
        history = self.email_generator.get_history()
        
        if not history:
            print("No emails generated yet.")
        else:
            for i, entry in enumerate(history[-10:], 1):
                print(f"\n{i}. {entry['timestamp']}")
                print(f"   Purpose: {entry['purpose']}")
                print(f"   Recipient: {entry['recipient']}")
                print(f"   Subject: {entry.get('subject', 'N/A')}")
        
        input("\nPress Enter to continue...")
    
    def run_questionnaire(self):
        clear_screen()
        print("=" * 70)
        print("DYNAMIC HEALTH QUESTIONNAIRE")
        print("=" * 70)
        print("\nCOMMANDS:")
        print("  • Type 'menu' or 'exit' anytime to return to main menu")
        print("  • Type 'done' to finish the questionnaire early")
        print("-" * 70)
        print("The AI will ask you questions about your health.")
        print("Answer naturally. Type 'done' to finish early.\n")
        
        conversation = []
        
        print("Please describe your main health concern:")
        initial = input("You: ").strip()
        
        if initial.lower() in ['menu', 'exit', 'quit', 'main', 'back']:
            return
        
        conversation.append({"role": "user", "content": initial})
        
        question_count = 0
        while question_count < 10:
            print("\nAI is thinking...")
            result = self.questionnaire.get_next_question(conversation)
            
            print("\nRAW JSON:")
            print(json.dumps(result, indent=2))
            
            if result.get('assessment_complete'):
                print("\nAssessment complete!")
                break
            
            question = result.get('question', "Can you tell me more?")
            options = result.get('options')
            
            print(f"\nAI: {question}")
            if options:
                print(f"Options: {', '.join(options)}")
            
            answer = input("You: ").strip()
            
            if answer.lower() in ['menu', 'exit', 'quit', 'main', 'back']:
                print("\nReturning to main menu...")
                break
            elif answer.lower() == 'done':
                print("\nQuestionnaire ended early.")
                break
            
            conversation.append({"role": "assistant", "content": question})
            conversation.append({"role": "user", "content": answer})
            question_count += 1
        
        input("\nPress Enter to return to main menu...")
    
    def run_summarizer(self):
        clear_screen()
        print("=" * 70)
        print("MEDICAL RECORDS SUMMARIZER")
        print("=" * 70)
        print("\nCOMMANDS:")
        print("  • Type 'menu' or 'exit' on a new line to return to main menu")
        print("  • Type 'DONE' on a new line when finished pasting")
        print("-" * 70)
        print("Paste your messy medical records below.\n")
        
        lines = []
        print("Enter your medical records (type 'DONE' on new line to finish):")
        while True:
            line = input()
            if line.strip().upper() == 'DONE':
                break
            if line.strip().lower() in ['menu', 'exit', 'quit', 'main', 'back']:
                print("\nReturning to main menu...")
                return
            lines.append(line)
        
        if not lines:
            print("No input provided.")
            input("\nPress Enter to return...")
            return
        
        raw_text = "\n".join(lines)
        
        print("\nAI is summarizing...")
        summary = self.summarizer.summarize(raw_text)
        
        print("\nRAW JSON:")
        print(json.dumps(summary, indent=2))
        
        print("\nSUMMARY:")
        print("-" * 40)
        for i, point in enumerate(summary.get('summary_points', []), 1):
            print(f"{i}. {point}")
        
        print("\nKey Findings:")
        for finding in summary.get('key_findings', []):
            print(f"  • {finding}")
        
        print("\nMissing Information:")
        for missing in summary.get('missing_info', []):
            print(f"  • {missing}")
        
        input("\nPress Enter to return to main menu...")
    
    def run_classifier(self):
        clear_screen()
        print("=" * 70)
        print("SYMPTOM-TO-SPECIALIST CLASSIFIER")
        print("=" * 70)
        print("\nCOMMANDS:")
        print("  • Type 'menu' or 'exit' to return to main menu")
        print("-" * 70)
        print("Describe your symptoms, and I'll recommend the right Ayurvedic specialist.\n")
        
        while True:
            print("Enter your symptoms (or 'menu' to return):")
            symptoms = input("You: ").strip()
            
            if symptoms.lower() in ['menu', 'exit', 'quit', 'main', 'back']:
                print("\nReturning to main menu...")
                break
            
            if not symptoms:
                print("Please enter your symptoms or 'menu' to return.")
                continue
            
            print("\nAI is analyzing...")
            result = self.classifier.classify(symptoms)
            
            print("\nRAW JSON:")
            print(json.dumps(result, indent=2))
            
            print("\nRECOMMENDATION:")
            print("-" * 40)
            
            urgency = result.get('urgency', 'routine')
            if urgency == 'emergency':
                print(f"Specialist: {result.get('specialist_name', 'N/A')}")
            else:
                print(f"Specialist: {result.get('specialist_name', 'N/A')}")
            
            print(f"Confidence: {result.get('confidence', 0) * 100:.0f}%")
            print(f"Reasoning: {result.get('reasoning', 'N/A')}")
            
            if urgency == 'emergency':
                print(f"Urgency: {urgency.upper()}")
            elif urgency == 'urgent':
                print(f"Urgency: {urgency.upper()}")
            else:
                print(f"Urgency: {urgency.upper()}")
            
            if result.get('dosha'):
                print(f"Dosha Imbalance: {', '.join(result['dosha'])}")
            
            while True:
                again = input("\nWould you like to check another symptom? (yes/no): ").strip().lower()
                if again in ['no', 'n', 'menu', 'exit']:
                    print("\nReturning to main menu...")
                    return
                elif again in ['yes', 'y']:
                    print("\n" + "-" * 40)
                    break
                else:
                    print("Please answer 'yes' or 'no'")


if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 70)
    print("STARTING UNIFIED AYURVEDIC AI ASSISTANT SUITE")
    print("=" * 70)
    print(f"Model: {MODEL_NAME} (via Ollama)")
    print(f"Server: {OLLAMA_URL}")
    print(f"Modules: Receptionist + Email Generator + Assessment Tools")
    print("=" * 70)
    print("\nIMPORTANT: Make sure Ollama is running!")
    print("If not started yet, open a terminal and run:")
    print("  ollama serve")
    print("  ollama pull llama3.2")
    print("=" * 70 + "\n")
    
    app = UnifiedAyurvedicApp()
    app.run()